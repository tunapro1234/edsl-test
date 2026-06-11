"""Replicate Horton's Homo Silicus persona-fidelity result (arXiv:2301.07543).

Sec. 2.2 / Fig. 3 (pp. 11-12 of the local PDF): GPT-4o agents endowed with
the three theory personas play the six Charness-Rabin unilateral dictator
menus, 100 reps each at temperature 1, and follow their persona almost
perfectly — e.g. the measured efficient vector is v_E = (0,0,0,1,0,0) over
(Barc2, Barc8, Berk15, Berk23, Berk26, Berk29) (pp. 13-14). That fidelity is
the foundation of the whole method (the .53/.37/.10 mixture our module ships).

We re-run it in miniature with OUR shipped personas and OUR calibrate.py
question on the same menus, and check each type's P(Left) vector lands on the
paper's per-persona "Expected" pattern (Fig. 3 gold bars). Scrambled payoffs
or a broken template would push some type off its corner and fail the
pre-registered criteria below: a MAD band plus a per-cell cap, so even a
single fully flipped game (a 1.0 deviation in one cell) fails outright.

Default invocation only PRINTS the design and cost estimate.
Real run (bills the API):
    .venv/bin/python -m personas.homo_silicus.replication --run
"""

import json
import os
import sys
from datetime import datetime

from edsl import Agent, Model, Scenario, ScenarioList

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
from personas.homo_silicus import PERSONAS
from personas.homo_silicus.calibrate import CR_GAMES, q_choice

HERE = os.path.dirname(os.path.abspath(__file__))

MODEL, SERVICE = "gpt-4o", "openai"   # the paper's Fig. 3 model
REPS = 10                             # paper: 100 plays per persona per game

# Paper targets — Fig. 3 "Expected" gold bars (p. 12): P(choose Left) a
# perfectly adherent agent shows per game. None = the paper prints
# "Ambiguous" there (efficient: equal totals in Berk26; self-interested:
# own payoff tied in Berk29) — those cells are excluded from scoring.
# Cross-check: Horton's MEASURED GPT-4o efficient vector v_E = (0,0,0,1,0,0)
# (pp. 13-14) equals the expected pattern below.
PAPER_TARGETS = {
    "efficient":       {"Barc2": 0.0, "Barc8": 0.0, "Berk15": 0.0,
                        "Berk23": 1.0, "Berk26": None, "Berk29": 0.0},
    "inequity_averse": {"Barc2": 1.0, "Barc8": 0.0, "Berk15": 0.0,
                        "Berk23": 0.0, "Berk26": 0.0, "Berk29": 1.0},
    "self_interested": {"Barc2": 1.0, "Barc8": 1.0, "Berk15": 1.0,
                        "Berk23": 1.0, "Berk26": 1.0, "Berk29": None},
}
HORTON_TYPES = list(PAPER_TARGETS)    # the paper's 3 types, not our full 6

# PRE-REGISTERED pass criteria (fixed before any results exist).
# (1) MAD <= 0.2 per type over its non-ambiguous games: at REPS=10 that
#     tolerates ~2 stray picks per game (binomial noise + our GSA humanizing
#     prefix).
# (2) Per-cell cap: any single scored cell with |P(Left) - target| >= 0.5
#     fails. A fully flipped game (wrong payoff column) puts that cell at a
#     1.0 deviation — REPS=10 binomial noise essentially never does — whereas
#     under MAD alone one flipped game would sit exactly at 1/5 = 0.2 (1/6
#     for inequity-averse) and squeak through.
MAD_MAX = 0.2
CELL_MAX = 0.5
CRITERIA = (f"each persona's P(Left) vector is within mean-absolute-deviation "
            f"<= {MAD_MAX} of its Fig. 3 'Expected' pattern AND no scored "
            f"cell deviates from its target by >= {CELL_MAX}; ambiguous cells "
            f"excluded")

N_CALLS = len(HORTON_TYPES) * len(CR_GAMES) * REPS
# gpt-4o $2.5/$10 per 1M in/out; ~420 prompt + ~80 answer tokens per call.
COST_EST = round(N_CALLS * (420 * 2.5 + 80 * 10) / 1e6, 2)


def mad(p_left, target):
    """Mean absolute deviation over the games the paper scores (non-None)."""
    scored = [g for g in target if target[g] is not None]
    return sum(abs(p_left[g] - target[g]) for g in scored) / len(scored)


def worst_cell(p_left, target):
    """Largest single-cell |P(Left) - target| over the scored games."""
    return max(abs(p_left[g] - target[g])
               for g in target if target[g] is not None)


def design():
    print(__doc__)
    print(f"model: {SERVICE}/{MODEL}  temperature=1  max_tokens=2048")
    print(f"personas ({len(HORTON_TYPES)}, shipped = GSA prefix + Horton "
          f"one-liner):")
    for t in HORTON_TYPES:
        print(f"  {t:<16} {PERSONAS[t]}")
    print("menus (B picks Left/Right; columns = expected P(Left) per type):")
    for g, (L, R, _) in CR_GAMES.items():
        exp = "  ".join(f"{t[:4]}={PAPER_TARGETS[t][g]}" for t in HORTON_TYPES)
        print(f"  {g:<7} Left A={L[0]} B={L[1]}  Right A={R[0]} B={R[1]}   {exp}")
    print(f"reps: {REPS}  ->  n_calls = {len(HORTON_TYPES)} x {len(CR_GAMES)}"
          f" x {REPS} = {N_CALLS}   cost estimate ~${COST_EST}")
    print(f"pass criteria: {CRITERIA}")
    print("\n(dry run — nothing executed; add --run to bill the API)")


def run():
    scenarios = ScenarioList([
        Scenario({"ptype": t, "persona": PERSONAS[t], "game": g,
                  "left_a": L[0], "left_b": L[1],
                  "right_a": R[0], "right_b": R[1]})
        for t in HORTON_TYPES for g, (L, R, _) in CR_GAMES.items()
    ])
    model = Model(MODEL, service_name=SERVICE, temperature=1, max_tokens=2048)
    res = q_choice.by(scenarios).by(Agent(name="replication")).by(model).run(n=REPS)

    rows = res.select("ptype", "game", "choice").to_dicts()
    p_left, n_eff = {t: {} for t in HORTON_TYPES}, {}
    for t in HORTON_TYPES:
        for g in CR_GAMES:
            picks = [r["choice"] for r in rows
                     if r["ptype"] == t and r["game"] == g and r["choice"]]
            if not picks:
                raise RuntimeError(f"no valid answers for {t} in {g}; re-run")
            n_eff[f"{t}/{g}"] = len(picks)
            p_left[t][g] = sum(c == "Left" for c in picks) / len(picks)

    mads = {t: round(mad(p_left[t], PAPER_TARGETS[t]), 4) for t in HORTON_TYPES}
    worsts = {t: round(worst_cell(p_left[t], PAPER_TARGETS[t]), 4)
              for t in HORTON_TYPES}
    passed = (all(m <= MAD_MAX for m in mads.values())
              and all(w < CELL_MAX for w in worsts.values()))

    artifact = {
        "method": "homo_silicus",
        "model": f"{SERVICE}/{MODEL}",
        "experiment": "Horton Fig. 3: 3 theory personas x 6 Charness-Rabin "
                      "unilateral dictator menus, P(Left) per persona per game",
        "paper_targets": PAPER_TARGETS,
        "results": {"p_left": p_left, "mad": mads, "worst_cell": worsts,
                    "n_eff": n_eff},
        "pass": passed,
        "criteria": CRITERIA,
        "n_calls": N_CALLS,
        "cost_estimate_usd": COST_EST,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with open(os.path.join(HERE, "replication.json"), "w") as f:
        json.dump(artifact, f, indent=2)

    for t in HORTON_TYPES:
        print(f"{t:<16} P(Left) {[p_left[t][g] for g in CR_GAMES]}  "
              f"MAD={mads[t]:.3f} (max {MAD_MAX})  "
              f"worst cell={worsts[t]:.3f} (must be < {CELL_MAX})")
    print(f"pass: {passed}")
    print("saved replication.json")


if __name__ == "__main__":
    run() if "--run" in sys.argv else design()
