"""Trust game — two agents, two stages.

Investor sends some of $100; it is TRIPLED on the way; trustee chooses how much
to return.

Output layout (one folder per run; agents are ROWS within a stage, not folders,
so this scales to many agents per run):

  results/<YYYY-MM-DD_HH-MM-SS>/
    REASONING.md        <- the important one: every agent's answer + reasoning
    summary.txt         <- numeric outcome
    <stage>/
      <stage>.json.gz   <- full Results, lossless & reloadable
      <stage>.csv       <- every column
      coop.txt          <- results_uuid + Coop URL

Because we use Expected Parrot remote inference, the raw model response is not in
the local results object, so we Results.pull(results_uuid) to fetch the full
record before saving.
"""

import os
from datetime import datetime

from edsl import QuestionNumerical, Agent, Model, Scenario, Results

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_ROOT = os.path.join(HERE, "results")

POT = 100
MULT = 3


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
    """Append every agent's answer + reasoning for this stage to run-level REASONING.md.

    Works for any number of agents/scenarios: each result row becomes its own block.
    """
    cols = results.columns
    qnames = [c.split(".", 1)[1] for c in cols if c.startswith("answer.")]
    scen_fields = [
        c.split(".", 1)[1]
        for c in cols
        if c.startswith("scenario.") and c != "scenario.scenario_index"
    ]

    sel = ["agent.agent_name"]
    for q in qnames:
        sel.append(f"answer.{q}")
        if f"comment.{q}_comment" in cols:
            sel.append(f"comment.{q}_comment")
    sel += [f"scenario.{s}" for s in scen_fields]

    rows = results.select(*sel).to_dicts()
    lines = [f"\n## {tag}\n"]
    for row in rows:
        name = row.get("agent_name", "agent")
        ctx = ", ".join(f"{s}={row.get(s)}" for s in scen_fields)
        lines.append(f"### {name}" + (f"  ({ctx})" if ctx else ""))
        for q in qnames:
            lines.append(f"- **{q} = {row.get(q)}**")
            reason = row.get(f"{q}_comment")
            if reason:
                lines.append(f"  - {reason}")
        lines.append("")

    with open(os.path.join(run_dir, "REASONING.md"), "a") as f:
        f.write("\n".join(lines))


def run_and_save(job, run_dir, tag):
    """Run a job, pull the FULL Coop record, save it + reasoning, return full Results."""
    local = job.run()
    uuid = local.results_uuid
    full = Results.pull(uuid)  # full record incl. raw response + generated text

    stage_dir = os.path.join(run_dir, tag)
    os.makedirs(stage_dir, exist_ok=True)
    full.save(os.path.join(stage_dir, tag))             # lossless .json.gz
    full.to_csv(os.path.join(stage_dir, f"{tag}.csv"))  # all columns
    with open(os.path.join(stage_dir, "coop.txt"), "w") as f:
        f.write(f"results_uuid: {uuid}\n")
        f.write(f"url: https://www.expectedparrot.com/content/{uuid}\n")

    append_reasoning(full, run_dir, tag)  # <- reasoning into run-level REASONING.md
    return full


def play_trust(run_dir):
    model = make_model()
    q_send, q_return = build_questions()

    # Stage 1: investor sends
    res_send = run_and_save(
        q_send.by(Agent(name="investor")).by(model), run_dir, "stage1_send"
    )
    sent = res_send.select("sent").to_list()[0]
    received = sent * MULT

    # Stage 2: trustee returns, given the REAL tripled amount
    res_return = run_and_save(
        q_return.by(Scenario({"received": received})).by(Agent(name="trustee")).by(model),
        run_dir,
        "stage2_return",
    )
    returned = res_return.select("returned").to_list()[0]
    return sent, received, returned


def main():
    run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(RESULTS_ROOT, run_name)
    os.makedirs(run_dir, exist_ok=True)

    sent, received, returned = play_trust(run_dir)
    investor_final = POT - sent + returned
    trustee_final = received - returned

    summary = (
        f"Trust game — {run_name}\n"
        f"Investor sent ${sent}  ->  trustee received ${received} (x{MULT})\n"
        f"Trustee returned ${returned}\n"
        f"Final:  investor ${investor_final}   |   trustee ${trustee_final}\n"
    )
    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(summary)
    print(summary)
    print(f"Saved to: {run_dir}/  (see REASONING.md)")


if __name__ == "__main__":
    main()
