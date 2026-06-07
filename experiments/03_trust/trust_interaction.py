"""Trust game — two agents, two stages.

Investor sends some of $100; it is TRIPLED on the way; trustee chooses how much
to return.

Output convention (used in every experiment from now on):
  results/<YYYY-MM-DD_HH-MM-SS>/        one folder per run
    <stage>/<stage>.json.gz             full Results, lossless & reloadable
    <stage>/<stage>.csv                 every column, human-readable
    <stage>/coop.txt                    results_uuid + Coop URL
  results/<run>/summary.txt             the run's outcome

Because we use Expected Parrot remote inference, the raw model response is NOT in
the local results object — so we Results.pull(results_uuid) to fetch the full
record (raw API envelope + the text the model generated) and save THAT.
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


def run_and_save(job, run_dir, tag):
    """Run a job, pull the FULL Coop record, save it, return the full Results."""
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
    print(f"Full results saved to: {run_dir}/")


if __name__ == "__main__":
    main()
