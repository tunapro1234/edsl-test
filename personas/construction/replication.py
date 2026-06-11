"""Replicate the GSA construction headline (Manning & Horton, arXiv:2508.17407).

Appendix A claim, on GPT-4o (the paper's model, which we use here too):
  - bare model on the six Charness & Rabin single-stage dictator menus:
    MAE vs human Left-shares = 0.42                       (p. 49, below Fig. A1)
  - the Bayesian-optimized dial set phi* = (7,10,10), (3,1,3), (1,10,2),
    played as a uniform 3-agent mixture: MAE = 0.20       (p. 50, end of A.2)

We re-run that comparison in miniature: (3 phi* personas + 1 empty baseline)
x 6 menus x REPS, using OUR render()/template and OUR dictator question
(the exact objects real experiments use), and check both numbers come back.
A scrambled template or wrong payoffs would push the phi* MAE toward the
baseline's 0.42 and fail the pre-registered band below.

Default invocation only PRINTS the design and cost estimate.
Real run (bills the API):
    .venv/bin/python -m personas.construction.replication --run
"""

import json
import os
import sys
from datetime import datetime

from edsl import Agent, Model, Scenario, ScenarioList

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
from personas.construction import PAPER_DIALS, render
from personas.construction.calibrate import GAMES, HUMAN_LEFT, key, mae, q_choose

HERE = os.path.dirname(os.path.abspath(__file__))

MODEL, SERVICE = "gpt-4o", "openai"   # the paper's model
REPS = 10                             # paper: 30/agent/menu (1,000 for baseline)

# Paper targets — read from the PDF, page cites in REPLICATION.md.
TARGETS = {"mae_phi_star": 0.20, "mae_baseline": 0.42}

# PRE-REGISTERED pass criteria (fixed before any results exist).
# TOL=0.15: wide enough for REPS=10 binomial noise + model-snapshot drift,
# narrow enough that landing at the baseline's 0.42 (|0.42-0.20|=0.22) fails.
TOL = 0.15
CRITERIA = ("MAE(phi* mixture) < MAE(baseline) and "
            f"|MAE(phi* mixture) - {TARGETS['mae_phi_star']}| <= {TOL}")

PERSONAS = {key(d): render(d) for d in PAPER_DIALS}  # e.g. "7-10-10"
PERSONAS["baseline"] = ""                            # bare model, red bars

N_CALLS = len(PERSONAS) * len(GAMES) * REPS
# gpt-4o $2.5/$10 per 1M in/out; ~420 prompt + ~80 answer tokens per call.
COST_EST = round(N_CALLS * (420 * 2.5 + 80 * 10) / 1e6, 2)


def design():
    print(__doc__)
    print(f"model: {SERVICE}/{MODEL}  temperature=1  max_tokens=2048")
    print(f"personas ({len(PERSONAS)}): {', '.join(PERSONAS)}")
    print("menus (Person B picks Left/Right; human Left-share target):")
    for g, (L, R) in GAMES.items():
        print(f"  {g:<7} Left A={L[0]} B={L[1]}  Right A={R[0]} B={R[1]}"
              f"   human {HUMAN_LEFT[g]:.2f}")
    print(f"reps: {REPS}  ->  n_calls = {len(PERSONAS)} x {len(GAMES)} x {REPS}"
          f" = {N_CALLS}   cost estimate ~${COST_EST}")
    print(f"paper targets: {TARGETS}")
    print(f"pass criteria: {CRITERIA}")
    print("\n(dry run — nothing executed; add --run to bill the API)")


def run():
    scenarios = ScenarioList([
        Scenario({"who": w, "persona": p, "game": g,
                  "a_left": L[0], "b_left": L[1],
                  "a_right": R[0], "b_right": R[1]})
        for w, p in PERSONAS.items() for g, (L, R) in GAMES.items()
    ])
    model = Model(MODEL, service_name=SERVICE, temperature=1, max_tokens=2048)
    res = q_choose.by(scenarios).by(Agent(name="replication")).by(model).run(n=REPS)

    rows = res.select("who", "game", "choice").to_dicts()
    p_left = {w: {} for w in PERSONAS}
    for w in PERSONAS:
        for g in GAMES:
            picks = [r["choice"] for r in rows
                     if r["who"] == w and r["game"] == g and r["choice"] is not None]
            if not picks:
                raise RuntimeError(f"no valid answers for {w} in {g}; re-run")
            p_left[w][g] = sum(c == "Left" for c in picks) / len(picks)

    mae_phi = mae([p_left[key(d)] for d in PAPER_DIALS])  # uniform mixture
    mae_base = mae([p_left["baseline"]])
    passed = mae_phi < mae_base and abs(mae_phi - TARGETS["mae_phi_star"]) <= TOL

    artifact = {
        "method": "construction",
        "model": f"{SERVICE}/{MODEL}",
        "experiment": "GSA App. A: phi* dial mixture vs bare GPT-4o on the six "
                      "Charness-Rabin single-stage dictator menus (MAE vs humans)",
        "paper_targets": TARGETS,
        "results": {"mae_phi_star": round(mae_phi, 4),
                    "mae_baseline": round(mae_base, 4),
                    "p_left": p_left},
        "pass": passed,
        "criteria": CRITERIA,
        "n_calls": N_CALLS,
        "cost_estimate_usd": COST_EST,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(HERE, "replication.json"), "w") as f:
        json.dump(artifact, f, indent=2)

    print(f"MAE phi* mixture: {mae_phi:.3f}  (paper 0.20)")
    print(f"MAE baseline:     {mae_base:.3f}  (paper 0.42)")
    print(f"pass: {passed}   ({CRITERIA})")
    print("saved replication.json")


if __name__ == "__main__":
    run() if "--run" in sys.argv else design()
