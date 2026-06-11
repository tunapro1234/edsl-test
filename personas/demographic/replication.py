"""Replicate Argyle et al. Study 2 in miniature (arXiv:2209.06899, paper 08).

The paper conditions GPT-3 on first-person demographic backstories built from
real ANES respondents and reads off the 2012/2016/2020 presidential vote.
Table 1 (PDF p. 11): whole-sample tetrachoric correlation between GPT-3 and
ANES vote is 0.90 (2012), 0.92 (2016), 0.94 (2020); for the strong-partisan
subgroup the 2020 tetrachoric is 1.00 with 0.97 proportion agreement.

Mini version with OUR pipeline: take the first 12 strong-Democrat and first
12 strong-Republican rows of gss_sample.csv (deterministic, no RNG), render
each with the module's own _render(), and ask the 2020 vote (Biden/Trump),
one rep at temperature 0.  Ground truth proxy = own party (the GSS extract
has no vote variable; strong partisans vote own-party near-universally, which
is exactly the paper's 0.97-1.00 strong-partisan row).  Two failure guards:
(1) pick_rows() asserts each rendered persona contains its verbatim partyid
fragment — deterministic, runs on the dry run too; needed because the
backstory also carries polviews (17/24 selected personas party-consistent),
so dropping ONLY partyid could still score ~0.75-0.9 and clear 0.80.
(2) The run criterion catches scrambled/empty/unsubstituted templates, which
collapse everyone to the model's own prior (~0.5 alignment -> fail).

Default invocation only PRINTS the design and cost estimate.
Real run (bills the API):
    .venv/bin/python -m personas.demographic.replication --run
"""

import json
import os
import sys
from datetime import datetime

from edsl import Agent, Model, QuestionMultipleChoice, Scenario, ScenarioList

if __package__:                       # python -m personas.demographic.replication
    from . import PARTYID, _load, _render
else:                                 # python personas/demographic/replication.py
    sys.path.insert(0, os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    from personas.demographic import PARTYID, _load, _render

HERE = os.path.dirname(os.path.abspath(__file__))

# Paper used GPT-3 davinci (base) — retired; this is the closest strong open
# model on Expected Parrot. Deviation documented in REPLICATION.md.
MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
SERVICE = "deep_infra"
N_PER_PARTY = 12
REPS = 1

# Paper targets — read from the PDF, page cites in REPLICATION.md.
TARGETS = {
    "tetrachoric_all_2012": 0.90,
    "tetrachoric_all_2016": 0.92,
    "tetrachoric_all_2020": 0.94,
    "tetrachoric_strong_partisans_2020": 1.00,
    "prop_agree_strong_partisans_2020": 0.97,
}

# PRE-REGISTERED pass criteria (fixed before any results exist).
# Paper-level strong-partisan agreement is 0.97-1.00; 0.80 leaves slack for
# the instruct-model swap and N=24 binomial noise, while a broken persona
# (model prior for everyone) lands near 0.50 and fails. MIN_VALID catches a
# template that breaks answer parsing outright.
THRESHOLD, MIN_VALID = 0.80, 20
CRITERIA = (f"own-party-aligned 2020 vote share >= {THRESHOLD} among >= "
            f"{MIN_VALID} valid answers (paper strong-partisan agreement 0.97)")

OWN_CANDIDATE = {"strong democrat": "Joe Biden",
                 "strong republican": "Donald Trump"}

# Paper read P("In 2020, I voted for..." -> candidate token) from a base
# model; with a chat model we ask the same two-party choice as MC and take
# the temperature-0 answer (= the paper's dichotomize-at-0.5, App. C p. 31).
q_vote = QuestionMultipleChoice(
    question_name="vote",
    question_text=("{{ scenario.persona }}\n"
                   "In the 2020 United States presidential election, "
                   "who did you vote for?"),
    question_options=["Joe Biden", "Donald Trump"],
)


def pick_rows():
    """First N_PER_PARTY rows per strong-partisan group, in CSV order."""
    rows, _ = _load()
    out = []
    for party in OWN_CANDIDATE:
        out += [r for r in rows if r["partyid"] == party][:N_PER_PARTY]
    # Deterministic guard, free, runs on dry run too: the statistical criterion
    # alone could miss a dropped partyid (polviews would carry most personas),
    # so require the verbatim partyid fragment in every rendered persona.
    for r in out:
        assert PARTYID[r["partyid"]] in _render(r), (
            f"rendered persona for row {r['id']} lost its partyid fragment")
    return out

N_CALLS = 2 * N_PER_PARTY * REPS
# Llama-3.1-70B-Turbo $0.4/$0.4 per 1M in/out; ~350 prompt + ~60 answer tokens.
COST_EST = round(N_CALLS * (350 * 0.4 + 60 * 0.4) / 1e6, 4)


def design():
    print(__doc__)
    rows = pick_rows()
    print(f"model: {SERVICE}/{MODEL}  temperature=0  max_tokens=2048")
    print(f"personas: {len(rows)} (first {N_PER_PARTY} strong Democrats + "
          f"first {N_PER_PARTY} strong Republicans of gss_sample.csv)")
    print(f"example persona (row id {rows[0]['id']}):\n  {_render(rows[0])}")
    print("question: 2020 presidential vote, options [Joe Biden, Donald Trump]")
    print(f"reps: {REPS}  ->  n_calls = {N_CALLS}   cost estimate ~${COST_EST}")
    print(f"paper targets: {TARGETS}")
    print(f"pass criteria: {CRITERIA}")
    print("\n(dry run — nothing executed; add --run to bill the API)")


def run():
    rows = pick_rows()
    scenarios = ScenarioList([
        Scenario({"pid": r["id"], "party": r["partyid"], "persona": _render(r)})
        for r in rows
    ])
    model = Model(MODEL, service_name=SERVICE, temperature=0, max_tokens=2048)
    res = q_vote.by(scenarios).by(Agent(name="replication")).by(model).run(n=REPS)

    answers = res.select("pid", "party", "vote").to_dicts()
    valid = [a for a in answers if a["vote"] in OWN_CANDIDATE.values()]
    aligned = sum(a["vote"] == OWN_CANDIDATE[a["party"]] for a in valid)
    share = aligned / len(valid) if valid else 0.0
    passed = len(valid) >= MIN_VALID and share >= THRESHOLD

    artifact = {
        "method": "demographic",
        "model": f"{SERVICE}/{MODEL}",
        "experiment": "Argyle Study 2 mini: 12+12 strong-partisan GSS-2024 "
                      "backstories (own _render) asked their 2020 presidential "
                      "vote (Biden/Trump), 1 rep, temperature 0",
        "paper_targets": TARGETS,
        "results": {
            "own_party_aligned_share": round(share, 4),
            "aligned": aligned, "n_valid": len(valid), "n_asked": len(answers),
            "votes": {a["pid"]: a["vote"] for a in answers},
        },
        "pass": passed,
        "criteria": CRITERIA,
        "n_calls": N_CALLS,
        "cost_estimate_usd": COST_EST,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(HERE, "replication.json"), "w") as f:
        json.dump(artifact, f, indent=2)

    print(f"own-party aligned: {aligned}/{len(valid)} valid = {share:.2f}  "
          f"(paper strong-partisan agreement 0.97)")
    print(f"pass: {passed}   ({CRITERIA})")
    print("saved replication.json")


if __name__ == "__main__":
    run() if "--run" in sys.argv else design()
