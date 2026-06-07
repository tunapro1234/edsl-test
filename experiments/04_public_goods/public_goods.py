"""Public goods game — N players, ONE simultaneous stage.

Each of N players privately chooses how much of their $ENDOWMENT to put in a
shared fund. The fund is multiplied (x MULT) and split equally among all players,
regardless of who contributed. Each keeps what they didn't contribute.

Because all players decide at once and independently, this is a single question
run n=PLAYERS times (no stage 1 -> stage 2 feeding like trust/ultimatum).

Output layout (same convention as the other games):
  results/<YYYY-MM-DD_HH-MM-SS>/
    REASONING.md        every player's contribution + reasoning
    summary.txt         table of contributions + payoffs
    <stage>/            full data (.json.gz, .csv, coop.txt)
"""

import os
from datetime import datetime

from edsl import QuestionNumerical, Agent, Model

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_ROOT = os.path.join(HERE, "results")

PLAYERS = 4
ENDOWMENT = 20
MULT = 2  # MPCR = MULT / PLAYERS = 0.5


def make_model():
    return Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)


def build_question():
    return QuestionNumerical(
        question_name="contribution",
        question_text=(
            f"You and {PLAYERS - 1} other people each have ${ENDOWMENT}. Each of you "
            f"privately and at the same time decides how much of your ${ENDOWMENT} to "
            f"put into a shared group fund. The total fund is then multiplied by "
            f"{MULT} and split equally among all {PLAYERS} of you, no matter how much "
            f"each person contributed. You keep any money you do not contribute. "
            f"How much do you contribute?"
        ),
    )


def append_reasoning(results, run_dir, tag):
    """Append every result row's answer + reasoning to run-level REASONING.md."""
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
            bits.append(f"player {row.get('iteration')}")
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
    """Run a job n times, save full local results + reasoning, push to Coop for a link."""
    results = job.run(n=n)

    stage_dir = os.path.join(run_dir, tag)
    os.makedirs(stage_dir, exist_ok=True)
    results.save(os.path.join(stage_dir, tag))
    results.to_csv(os.path.join(stage_dir, f"{tag}.csv"))

    try:
        url = results.push(visibility="unlisted")["url"]
    except Exception as e:
        url = f"(push failed: {e})"
    with open(os.path.join(stage_dir, "coop.txt"), "w") as f:
        f.write(f"url: {url}\n")

    append_reasoning(results, run_dir, tag)
    return results


def play_public_goods(run_dir, players=PLAYERS):
    model = make_model()
    q = build_question()
    res = run_and_save(q.by(Agent(name="player")).by(model), run_dir, "contributions", n=players)
    contributions = res.select("contribution").to_list()

    total = sum(contributions)
    pool = total * MULT
    share = pool / players
    return [
        {"player": i, "contribution": c, "kept": ENDOWMENT - c, "share": share,
         "final": (ENDOWMENT - c) + share}
        for i, c in enumerate(contributions)
    ]


def main():
    run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(RESULTS_ROOT, run_name)
    os.makedirs(run_dir, exist_ok=True)

    players = play_public_goods(run_dir)

    contribs = [p["contribution"] for p in players]
    lines = [f"Public goods — {PLAYERS} players, ${ENDOWMENT} each, x{MULT} — {run_name}", ""]
    lines.append(f"{'player':>6} {'contrib':>7} {'kept':>5} {'share':>6} {'final':>6}")
    for p in players:
        lines.append(
            f"{p['player']:>6} {p['contribution']:>7} {p['kept']:>5} "
            f"{p['share']:>6.1f} {p['final']:>6.1f}"
        )
    mean = lambda xs: sum(xs) / len(xs) if xs else 0
    lines += [
        "",
        f"total contributed: {sum(contribs)} / {ENDOWMENT * PLAYERS}   "
        f"mean contribution: {mean(contribs):.1f} (${ENDOWMENT} max)",
    ]
    summary = "\n".join(lines) + "\n"

    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(summary)
    print(summary)
    print(f"Saved to: {run_dir}/  (see REASONING.md)")


if __name__ == "__main__":
    main()
