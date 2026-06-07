"""Trust game — two agents, two stages, run N times.

Investor sends some of $100; it is TRIPLED on the way; trustee chooses how much
to return. We run the whole game N times via run(n=N) (NOT a Python loop, which
would just hit the cache and return identical answers).

Stage 1: N investors each send an amount (varied, temperature 1).
Stage 2: for each investor's tripled amount, a trustee decides what to return.

Output layout (one folder per run; agents/reps are ROWS within a stage):
  results/<YYYY-MM-DD_HH-MM-SS>/
    REASONING.md        <- every agent's answer + reasoning, labelled by rep/scenario
    summary.txt         <- table of all N games + means
    <stage>/            <- full data (.json.gz lossless, .csv, coop.txt)
"""

import os
from datetime import datetime

from edsl import QuestionNumerical, Agent, Model, Scenario, ScenarioList

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_ROOT = os.path.join(HERE, "results")

POT = 100
MULT = 3
N = 10


def make_model():
    return Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)


def build_questions():
    q_send = QuestionNumerical(
        question_name="sent",
        question_text=(
            f"You have ${POT}. You can send any amount to another person. Whatever "
            f"you send is TRIPLED before they receive it. They then decide how much, "
            f"if any, to send back to you. How much do you send?"
        ),
    )
    q_return = QuestionNumerical(
        question_name="returned",
        question_text=(
            "Another person sent you money, which was tripled to "
            "${{ scenario.received }}. You may keep all of it or send some back to "
            "them. How much do you send back?"
        ),
    )
    return q_send, q_return


def append_reasoning(results, run_dir, tag):
    """Append every result row's answer + reasoning to run-level REASONING.md.

    Scales to any number of agents/reps/scenarios: each row is one block, labelled
    by repetition (iteration) and any scenario fields.
    """
    cols = results.columns
    qnames = [c.split(".", 1)[1] for c in cols if c.startswith("answer.")]
    scen_fields = [
        c.split(".", 1)[1]
        for c in cols
        if c.startswith("scenario.") and c != "scenario.scenario_index"
    ]
    has_iter = "iteration.iteration" in cols

    sel = ["agent.agent_name"]
    if has_iter:
        sel.append("iteration.iteration")
    for q in qnames:
        sel.append(f"answer.{q}")
        if f"comment.{q}_comment" in cols:
            sel.append(f"comment.{q}_comment")
    sel += [f"scenario.{s}" for s in scen_fields]

    rows = results.select(*sel).to_dicts()
    lines = [f"\n## {tag}\n"]
    for row in rows:
        bits = []
        if has_iter:
            bits.append(f"rep {row.get('iteration')}")
        bits += [f"{s}={row.get(s)}" for s in scen_fields]
        ctx = ", ".join(bits)
        lines.append(f"### {row.get('agent_name', 'agent')}" + (f"  ({ctx})" if ctx else ""))
        for q in qnames:
            lines.append(f"- **{q} = {row.get(q)}**")
            reason = row.get(f"{q}_comment")
            if reason:
                lines.append(f"  - {reason}")
        lines.append("")

    with open(os.path.join(run_dir, "REASONING.md"), "a") as f:
        f.write("\n".join(lines))


def run_and_save(job, run_dir, tag, n=1):
    """Run a job n times, save full local results + reasoning, push to Coop for a link.

    Local results already contain the answer, comment (reasoning), and (when the
    service returns it) the raw response with chain-of-thought, so no pull needed.
    """
    results = job.run(n=n)

    stage_dir = os.path.join(run_dir, tag)
    os.makedirs(stage_dir, exist_ok=True)
    results.save(os.path.join(stage_dir, tag))             # lossless .json.gz
    results.to_csv(os.path.join(stage_dir, f"{tag}.csv"))  # all columns

    # Coop link for the shareable full record (.results_uuid is not always set)
    try:
        url = results.push(visibility="unlisted")["url"]
    except Exception as e:
        url = f"(push failed: {e})"
    with open(os.path.join(stage_dir, "coop.txt"), "w") as f:
        f.write(f"url: {url}\n")

    append_reasoning(results, run_dir, tag)
    return results


def play_trust(run_dir, n=N):
    model = make_model()
    q_send, q_return = build_questions()

    # Stage 1: N investors send
    res_send = run_and_save(
        q_send.by(Agent(name="investor")).by(model), run_dir, "stage1_send", n=n
    )
    sents = res_send.select("sent").to_list()
    receiveds = [s * MULT for s in sents]

    # Stage 2: one trustee decision per investor's tripled amount (paired by game id)
    scenarios = ScenarioList(
        [Scenario({"game": i, "received": r}) for i, r in enumerate(receiveds)]
    )
    res_return = run_and_save(
        q_return.by(scenarios).by(Agent(name="trustee")).by(model), run_dir, "stage2_return"
    )
    by_game = {row["game"]: row["returned"] for row in res_return.select("game", "returned").to_dicts()}

    return [
        {"game": i, "sent": s, "received": r, "returned": by_game.get(i)}
        for i, (s, r) in enumerate(zip(sents, receiveds))
    ]


def main():
    run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(RESULTS_ROOT, run_name)
    os.makedirs(run_dir, exist_ok=True)

    games = play_trust(run_dir)

    lines = [f"Trust game x{len(games)} — {run_name}", ""]
    lines.append(f"{'game':>4} {'sent':>5} {'recv':>5} {'ret':>5} {'inv$':>6} {'tru$':>6}")
    sents, returns = [], []
    for g in games:
        ret = g["returned"] or 0
        sents.append(g["sent"])
        if g["returned"] is not None:
            returns.append(g["returned"])
        lines.append(
            f"{g['game']:>4} {g['sent']:>5} {g['received']:>5} {str(g['returned']):>5} "
            f"{POT - g['sent'] + ret:>6} {g['received'] - ret:>6}"
        )
    mean = lambda xs: sum(xs) / len(xs) if xs else 0
    lines += ["", f"mean sent: {mean(sents):.1f}   mean returned: {mean(returns):.1f}"]
    summary = "\n".join(lines) + "\n"

    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(summary)
    print(summary)
    print(f"Saved to: {run_dir}/  (see REASONING.md)")


if __name__ == "__main__":
    main()
