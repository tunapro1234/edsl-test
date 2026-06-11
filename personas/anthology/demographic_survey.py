"""Stage 2 (optional, costs money): demographic survey on the backstory pool.

This is the Anthology paper's Step 2 (Section 2.3): ask each backstory-
conditioned persona the demographic questions, sampling several responses to
estimate a demographic DISTRIBUTION per story. With those estimates, the
paper's Step 3 (greedy matching, Section 2.4 — it beat max-weight matching,
Table 1) can match stories to GSS respondent rows on all 5 variables instead
of the age-only stratification stage 1 uses.

Question wordings and options are VERBATIM from the paper's Appendix D,
Figure 11 (the ATP Wave 34 demographic battery).

Usage:
    python personas/anthology/demographic_survey.py            # dry run:
        builds the jobs, prints exact prompt + token counts, runs NOTHING
    python personas/anthology/demographic_survey.py --run      # real EP run
        (main agent only — check the token estimate against EP pricing first)

Output: results saved under personas/anthology/demographic_survey_results/.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "experiments"))
from common import make_model, run_and_save  # noqa: E402
from personas.anthology import TEMPLATE  # noqa: E402

from edsl import QuestionMultipleChoice, Agent, Scenario, ScenarioList  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES_PER_QUESTION = 3  # NOTE: the paper samples 40 responses per backstory/question (App. F.1); we use 3 for cost — raise for paper-grade demographic estimates

# ATP Wave 34 demographic battery, verbatim from paper Figure 11.
QUESTIONS = {
    "age": ("What is your age?", ["18-29", "30-49", "50-64", "65+"]),
    "gender": ("What is your gender?", ["Male", "Female", "Other"]),
    "race": ("Which of the following racial or ethnic groups do you identify with?",
             ["White non-Hispanic", "Black non-Hispanic", "Hispanic", "Other"]),
    "education": ("What is the highest level of education you have completed?",
                  ["Less than high school", "High school graduate",
                   "Some college, no degree", "Associate's degree",
                   "College graduate/some postgrad", "Postgraduate"]),
    "income": ("What is your annual household income?",
               ["Less than $10,000", "$10,000 to under $20,000",
                "$20,000 to under $30,000", "$30,000 to under $40,000",
                "$40,000 to under $50,000", "$50,000 to under $75,000",
                "$75,000 to under $100,000", "$100,000 to under $150,000",
                "$150,000 or more"]),
}


def build_jobs():
    with open(os.path.join(HERE, "backstories.json")) as f:
        stories = json.load(f)
    scenarios = ScenarioList([
        Scenario({"story_id": i,
                  "persona": TEMPLATE.format(question=s["question"], text=s["text"])})
        for i, s in enumerate(stories)
    ])
    jobs = {}
    for name, (text, options) in QUESTIONS.items():
        q = QuestionMultipleChoice(
            question_name=name,
            question_text="{{ scenario.persona }}\n" + text,
            question_options=options,
        )
        jobs[name] = q.by(scenarios).by(Agent(name="respondent")).by(make_model())
    return jobs, len(stories)


def main():
    jobs, n_stories = build_jobs()
    total_chars = 0
    for name, job in jobs.items():
        prompts = job.prompts().select("user_prompt").to_list()
        total_chars += sum(len(p) for p in prompts)
    calls = n_stories * len(QUESTIONS) * SAMPLES_PER_QUESTION
    tokens = total_chars * SAMPLES_PER_QUESTION / 4  # ~4 chars/token
    print(f"{n_stories} stories x {len(QUESTIONS)} questions x "
          f"{SAMPLES_PER_QUESTION} samples = {calls} calls")
    print(f"estimated input: {tokens / 1e6:.1f}M tokens "
          f"(+ ~{calls * 60 / 1e6:.2f}M output at ~60 tokens/answer)")

    if "--run" not in sys.argv:
        print("dry run only — pass --run to spend money (main agent decision).")
        return

    out_dir = os.path.join(HERE, "demographic_survey_results")
    os.makedirs(out_dir, exist_ok=True)
    for name, job in jobs.items():
        run_and_save(job, out_dir, name, n=SAMPLES_PER_QUESTION)


if __name__ == "__main__":
    main()
