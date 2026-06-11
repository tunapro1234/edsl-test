"""Anthology replication — implementation-fidelity check (Moon et al. 2024).

The paper's headline (arXiv:2407.06576 v3, Table 1, p. 7) is a Wasserstein
distance of 0.227 between Llama-3-70B (BASE) Anthology personas and human
respondents on ATP Wave 34. We CANNOT re-run that here: the human ATP response
distributions are not local (the paper repo clone ships only question texts
and demographic marginals; `human_data_path` is empty in its analysis configs)
and Pew microdata requires registration.

FALLBACK (labeled as such): validate the one step of the paper's pipeline we
re-implemented ourselves. The paper estimates each backstory's demographics
with an LLM survey before matching (Sec. 2.3; App. F.1: GPT-4o "locates"
explicitly mentioned age at T=0 with the Fig. 17 prompt). Our prep.py replaced
that step with regex age extraction and built an age-stratified pool. Here we
run the paper's own Fig. 17 age-locating instrument over a stratified sample
of our pool and check the LLM agrees with the bracket prep.py assigned. A
scrambled pool, broken regex, or wrong bracket boundaries would show up as
systematic disagreement.

Default invocation only PRINTS the design and cost estimate.
Real run (bills the API):
    .venv/bin/python -m personas.anthology.replication --run
"""

import json
import os
import random
import sys
from datetime import datetime

from edsl import Agent, Model, QuestionMultipleChoice, Scenario, ScenarioList

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "backstories.json")

# Spec-mandated stand-in for the paper's GPT-4o locator (App. F.1); instruct
# variant of the paper's main model family. Llama-3-70B-Instruct is the
# paper's own worst case (Table 4: WD 0.413 vs base 0.227) for *opinion*
# questions, but reading off an explicitly stated age is a retrieval task
# where instruction tuning helps, not hurts.
MODEL, SERVICE = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "deep_infra"

BRACKETS = ["18-29", "30-49", "50-64", "65+"]
PER_BRACKET = 6   # 6 x 4 brackets = 24 stories
REPS = 1          # paper's locating step is deterministic: T=0 (App. F.1)
SEED = 7          # which stories get sampled is fixed before any results

# Paper anchors (read from the PDF; page cites in REPLICATION.md). The WD
# numbers are CONTEXT — they need Pew microdata we don't have. The testable,
# PRE-REGISTERED target is the agreement floor.
TARGETS = {
    "wd_w34_llama3_70b_base_anthology_greedy": 0.227,      # Table 1, p. 7
    "wd_w34_llama3_70b_instruct_anthology_greedy": 0.413,  # Table 4, p. 16
    "min_bracket_agreement": 0.80,                          # ours, pre-registered
}
CRITERIA = ("implementation-fidelity: the paper's App. F Fig. 17 age-locating "
            "prompt at T=0 returns the same age bracket prep.py's regex "
            "assigned for >= 80% of 24 stratified pool backstories "
            "('Was not mentioned' or a blank answer counts as a miss)")

# Paper Fig. 17 (p. 32) options verbatim; "First, provide evidence ..." is
# handled by EDSL's built-in comment field rather than free-form text.
OPTIONS = ["18-29", "30-49", "50-64", "65 or Above", "Was not mentioned"]
TO_BRACKET = {"18-29": "18-29", "30-49": "30-49",
              "50-64": "50-64", "65 or Above": "65+"}

q_age = QuestionMultipleChoice(
    question_name="age_bracket",
    question_text=(
        "Here is a person's essay about themselves.\n\n"
        "Essay: {{ scenario.essay }}\n\n"
        "What does the person's essay above mention about the age of the "
        "person? If the essay does not mention the person's age, answer "
        "'Was not mentioned'."
    ),
    question_options=OPTIONS,
)


def eligible(story):
    """Drop stories whose ONLY age evidence straddles a bracket boundary.

    prep.py maps decade phrases to midpoints: "in my 60s" -> 65 and "in my
    teens" -> 18 sit exactly on a bracket edge, so the true bracket is
    undefined — they can't serve as ground truth. (6 of 610 stories; the
    literal digits "65"/"18" in the head mean an exact age was stated.)
    """
    head = story["text"][:600]   # same window prep.py's extractor reads
    return ((story["age"] != 65 or "65" in head) and
            (story["age"] != 18 or "18" in head))


def sample_stories():
    """PER_BRACKET eligible stories per bracket, deterministic under SEED."""
    with open(POOL) as f:
        pool = json.load(f)
    rng = random.Random(SEED)
    picked = []
    for b in BRACKETS:
        cands = [(i, s) for i, s in enumerate(pool)
                 if s["bracket"] == b and eligible(s)]
        picked += rng.sample(cands, PER_BRACKET)
    return picked  # list of (pool_index, story)


N_CALLS = PER_BRACKET * len(BRACKETS) * REPS
# llama-3.1-70B-Instruct-Turbo $0.4/$0.4 per 1M; ~750 prompt + ~80 answer tokens
COST_EST = round(N_CALLS * (750 * 0.4 + 80 * 0.4) / 1e6, 3)


def design():
    print(__doc__)
    print(f"model: {SERVICE}/{MODEL}  temperature=0  max_tokens=2048")
    stories = sample_stories()
    print(f"sample: {PER_BRACKET} stories x {len(BRACKETS)} brackets "
          f"(seed={SEED}), e.g.:")
    for i, s in stories[::PER_BRACKET]:   # first sampled story per bracket
        print(f"  pool[{i}] bracket={s['bracket']} age={s['age']} "
              f"text[:60]={s['text'][:60]!r}")
    print(f"reps: {REPS}  ->  n_calls = {N_CALLS}   cost estimate ~${COST_EST}")
    print(f"paper targets: {TARGETS}")
    print(f"pass criteria: {CRITERIA}")
    print("\n(dry run — nothing executed; add --run to bill the API)")


def run():
    stories = sample_stories()
    scenarios = ScenarioList([
        Scenario({"sid": i, "bracket": s["bracket"], "essay": s["text"]})
        for i, s in stories
    ])
    model = Model(MODEL, service_name=SERVICE, temperature=0, max_tokens=2048)
    res = q_age.by(scenarios).by(Agent(name="replication")).by(model).run(n=REPS)
    rows = res.select("sid", "bracket", "age_bracket").to_dicts()

    per_bracket = {b: [0, 0] for b in BRACKETS}   # bracket -> [matched, asked]
    mismatches = []
    for r in rows:
        got = TO_BRACKET.get(r["age_bracket"])    # None for "Was not mentioned"
        ok = got == r["bracket"]
        per_bracket[r["bracket"]][0] += ok
        per_bracket[r["bracket"]][1] += 1
        if not ok:
            mismatches.append({"sid": r["sid"], "expected": r["bracket"],
                               "got": r["age_bracket"]})
    agreement = sum(m for m, _ in per_bracket.values()) / N_CALLS  # blanks=miss
    passed = agreement >= TARGETS["min_bracket_agreement"]

    artifact = {
        "method": "anthology",
        "model": f"{SERVICE}/{MODEL}",
        "experiment": "implementation-fidelity: paper App. F (Fig. 17) age-"
                      "locating survey on 24 stratified pool backstories vs "
                      "the brackets prep.py's regex assigned (the human-ATP "
                      "WD comparison is not locally reproducible)",
        "paper_targets": TARGETS,
        "results": {"bracket_agreement": round(agreement, 4),
                    "n_matched": sum(m for m, _ in per_bracket.values()),
                    "n_scored": N_CALLS,
                    "per_bracket": {b: f"{m}/{n}"
                                    for b, (m, n) in per_bracket.items()},
                    "mismatches": mismatches},
        "pass": passed,
        "criteria": CRITERIA,
        "n_calls": N_CALLS,
        "cost_estimate_usd": COST_EST,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(HERE, "replication.json"), "w") as f:
        json.dump(artifact, f, indent=2)

    print(f"agreement: {agreement:.2%}  ({artifact['results']['n_matched']}"
          f"/{N_CALLS}; per bracket {artifact['results']['per_bracket']})")
    for m in mismatches:
        print(f"  miss pool[{m['sid']}]: expected {m['expected']}, "
              f"got {m['got']!r}")
    print(f"pass: {passed}   ({CRITERIA})")
    print("saved replication.json")


if __name__ == "__main__":
    run() if "--run" in sys.argv else design()
