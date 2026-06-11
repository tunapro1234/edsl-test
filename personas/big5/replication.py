"""Replicate Big5-Scaler's single-trait expression test (Cho & Cheong,
arXiv:2508.06149, Sec. 4.1 / 5.1, Table 1).

Paper, on Alpaca-7B with the Simple prompt and the 1,000-item MPI (1-5 scale):
dialing a trait up beats the neutral baseline on every trait except
Neuroticism (Table 1, p.7: Simple 4.26/4.19/4.37/4.03/2.73 vs Neutral
3.97/3.61/3.89/3.56/3.01 for O/C/E/A/N). Neuroticism under-expresses because
safety alignment discourages negative affect (Sec. 5.1, p.6).

Miniature here: 5 dialed personas (target trait 10/10, others 5) + 1 neutral
persona (all 5), built from OUR module's template (the exact text real
experiments use), each rating its target domain's 12 BFI-2 items (neutral
rates all 60), x REPS. Model: microsoft/phi-4 — the paper's best model
(Sec. 6, p.8: Phi4-14B + simple prompt + scale 10 won their sweep).
A scrambled template, broken score injection, or flipped reverse-keying
fails the pre-registered criteria below.

Default invocation only PRINTS the design and cost estimate.
Real run (bills the API):
    .venv/bin/python -m personas.big5.replication --run
"""

import csv
import json
import os
import re
import sys
from datetime import datetime

from edsl import Agent, Model, QuestionLinearScale, Scenario, ScenarioList

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
from personas.big5 import GLOSS, TRAITS, sample

HERE = os.path.dirname(os.path.abspath(__file__))
BFI2_CSV = os.path.join(HERE, "..", "..", "..", "research", "datasets",
                        "bfi2", "bfi2_items.csv")

MODEL, SERVICE = "microsoft/phi-4", "deep_infra"  # paper's best model (Sec. 6)
REPS = 10                                         # 12 items x 10 = 120 ratings/trait

# Paper targets — Table 1, p.7 (Alpaca-7B, MPI). Page cites in REPLICATION.md.
TARGETS = {
    "table1_simple": {"openness": 4.26, "conscientiousness": 4.19,
                      "extraversion": 4.37, "agreeableness": 4.03,
                      "neuroticism": 2.73},
    "table1_neutral": {"openness": 3.97, "conscientiousness": 3.61,
                       "extraversion": 3.89, "agreeableness": 3.56,
                       "neuroticism": 3.01},
}

# PRE-REGISTERED pass criteria (fixed before any results exist). The paper's
# own Table 1 passes at exactly 4/5 + 4/5: Neuroticism fails both legs there
# (2.73 < 3.01 neutral, and < 3.5) — its documented safety-suppression finding.
HIGH_BAR = 3.5
CRITERIA = ("dialed domain mean > neutral domain mean on >= 4/5 traits AND "
            "dialed mean >= 3.5/5 on >= 4/5 traits (the allowed miss is "
            "neuroticism, the paper's own safety-suppression exception, Sec. 5.1)")

# BFI-2 csv domain names -> the paper's trait names (used by our module).
PAPER_NAME = {"Open-Mindedness": "openness", "Conscientiousness": "conscientiousness",
              "Extraversion": "extraversion", "Agreeableness": "agreeableness",
              "Negative Emotionality": "neuroticism"}

N_CALLS = (5 * 12 + 60) * REPS  # 5 dialed x 12 items + neutral x 60, each x REPS
# phi-4 $0.07/$0.14 per 1M in/out; ~470 prompt + ~60 answer tokens per call.
COST_EST = round(N_CALLS * (470 * 0.07 + 60 * 0.14) / 1e6, 2)


def persona(scores):
    """Our module's template for explicit scores (mirrors big5._one)."""
    lines = []
    for trait in TRAITS:
        high, low = GLOSS[trait]
        lines.append(
            f"People with high {trait} score {high}; "
            f"people with low {trait} score {low}. "
            f"Your {trait} score is {scores[trait]} out of 10."
        )
    lines.append("From now on, you are an agent with this personality, "
                 "and you should respond based on this personality.")
    return " ".join(lines)


# Template integrity check: rebuilding a module-sampled persona from its own
# scores must reproduce it verbatim, or this replication isn't testing the
# template that experiments actually use.
_probe = sample(1, seed=0)[0]
_scores = {t: int(s) for t, s in
           zip(TRAITS, re.findall(r"score is (\d+) out of 10", _probe))}
assert persona(_scores) == _probe, "replication template drifted from big5._one"

CELLS = {t: persona({**{u: 5 for u in TRAITS}, t: 10}) for t in TRAITS}
CELLS["neutral"] = persona({t: 5 for t in TRAITS})

# BFI-2 response scale and item stem verbatim from the published BFI-2 form
# (semicolon variant: "Neutral; no opinion"; bfi2_scoring_key.json has a comma).
q_rate = QuestionLinearScale(
    question_name="rating",
    question_text=(
        "{{ scenario.persona }}\n"
        "Here is a characteristic that may or may not describe you. "
        "Rate how much you agree or disagree with the statement:\n"
        "I am someone who {{ scenario.item }}"
    ),
    question_options=[1, 2, 3, 4, 5],
    option_labels={1: "Disagree strongly", 2: "Disagree a little",
                   3: "Neutral; no opinion", 4: "Agree a little",
                   5: "Agree strongly"},
)


def load_items():
    """BFI-2 items grouped by paper trait name: [(item_no, text, reverse)]."""
    items = {t: [] for t in TRAITS}
    with open(BFI2_CSV) as f:
        for row in csv.DictReader(f):
            text = row["text"][0].lower() + row["text"][1:]  # mid-sentence case
            items[PAPER_NAME[row["domain"]]].append(
                (int(row["item_number"]), text, row["reverse_scored"] == "true"))
    for t in TRAITS:
        assert len(items[t]) == 12, f"expected 12 BFI-2 items for {t}"
    return items


def scenarios():
    items = load_items()
    rows = []
    for cell, text in CELLS.items():
        for t in (TRAITS if cell == "neutral" else [cell]):
            for num, item, rev in items[t]:
                rows.append(Scenario({"cell": cell, "trait": t, "item_no": num,
                                      "item": item, "reverse": int(rev),
                                      "persona": text}))
    return ScenarioList(rows)


def design():
    print(__doc__)
    print(f"model: {SERVICE}/{MODEL}  temperature=1 top_p=0.8 max_tokens=2048"
          " (paper Sec. 4: temp 1.0, top_p 0.8)")
    print(f"cells ({len(CELLS)}): " + ", ".join(CELLS))
    print("example persona (openness dialed to 10):")
    print(f"  {CELLS['openness']}")
    print("instrument: 12 BFI-2 items per domain, 1-5 agree scale, reverse-keyed"
          " items scored 6-x")
    print(f"reps: {REPS}  ->  n_calls = (5x12 + 60) x {REPS} = {N_CALLS}"
          f"   cost estimate ~${COST_EST}")
    print(f"paper targets (Table 1, p.7): {TARGETS}")
    print(f"pass criteria: {CRITERIA}")
    print("\n(dry run — nothing executed; add --run to bill the API)")


def run():
    model = Model(MODEL, service_name=SERVICE, temperature=1, top_p=0.8,
                  max_tokens=2048)
    res = q_rate.by(scenarios()).by(Agent(name="replication")).by(model).run(n=REPS)
    rows = res.select("cell", "trait", "reverse", "rating").to_dicts()

    def domain_mean(cell, trait):
        vals = [6 - r["rating"] if r["reverse"] else r["rating"] for r in rows
                if r["cell"] == cell and r["trait"] == trait
                and r["rating"] is not None]
        if len(vals) < 6 * REPS:  # under half of 12 x REPS answered
            raise RuntimeError(f"only {len(vals)} answers for {cell}/{trait}; re-run")
        return sum(vals) / len(vals), len(vals)

    dialed, neutral, n_eff = {}, {}, {}
    for t in TRAITS:
        dialed[t], n_eff[f"{t}/dialed"] = domain_mean(t, t)
        neutral[t], n_eff[f"{t}/neutral"] = domain_mean("neutral", t)

    wins = sum(dialed[t] > neutral[t] for t in TRAITS)
    highs = sum(dialed[t] >= HIGH_BAR for t in TRAITS)
    passed = wins >= 4 and highs >= 4

    print("trait              dialed  neutral | paper-simple paper-neutral")
    for t in TRAITS:
        print(f"{t:<18} {dialed[t]:>6.2f}  {neutral[t]:>7.2f} |"
              f" {TARGETS['table1_simple'][t]:>12.2f}"
              f" {TARGETS['table1_neutral'][t]:>13.2f}")
    print(f"dialed>neutral on {wins}/5, >= {HIGH_BAR} on {highs}/5  ->  pass: {passed}")

    artifact = {
        "method": "big5",
        "model": f"{SERVICE}/{MODEL}",
        "experiment": "Big5-Scaler single-trait expression (Sec. 4.1, Table 1): "
                      "each trait dialed to 10/10 (others 5) vs all-5 neutral "
                      "persona, scored on the 12 BFI-2 domain items (1-5)",
        "paper_targets": TARGETS,
        "results": {"dialed": {t: round(v, 3) for t, v in dialed.items()},
                    "neutral": {t: round(v, 3) for t, v in neutral.items()},
                    "wins": wins, "highs": highs, "n_eff": n_eff},
        "pass": passed,
        "criteria": CRITERIA,
        "n_calls": N_CALLS,
        "cost_estimate_usd": COST_EST,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(HERE, "replication.json"), "w") as f:
        json.dump(artifact, f, indent=2)
    print("saved replication.json")


if __name__ == "__main__":
    run() if "--run" in sys.argv else design()
