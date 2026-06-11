"""Fit the Homo Silicus mixture weights (GSA 'selection' step), v2.

TRAIN — the 6 unilateral Charness & Rabin (2002) allocation menus that Horton
(arXiv:2301.07543, Fig. 3) calibrates on. Each type plays each menu REPS times;
its behavior is the vector of P(choose Left) across menus. We grid-search
simplex weights w so the mixture matches the human Left-shares from CR 2002
Table I ("Game-by-game results"). These menus separate self_interested from
efficient (e.g. Barc2: selfish keeps $400 > $375, efficient takes the bigger
pie) — the v1 dictator-only probe could not.

VALIDATE (held out, never fitted) — a one-shot $100 dictator game. We report
how far the fitted mixture's moments [mean give frac, P(give 0), P(give 50)]
land from Engel's 2011 dictator meta-analysis (MPI preprint pp. 7-8: mean
28.35%, 36.11% give nothing, 16.74% equal split). Train-on-one-game-format,
test-on-another is GSA's defense against overfitting one data-generating
process. If validation is poor, expand TYPES and re-run (the GSA loop).

Cost: 6 types x (6 menus + 1 dictator) x REPS interviews on gpt-oss-120b.

Run from repo root:  .venv/bin/python -m personas.homo_silicus.calibrate
"""

import json
import os

from edsl import (Agent, Model, QuestionMultipleChoice, QuestionNumerical,
                  Scenario, ScenarioList)

from . import PERSONAS, TYPES

HERE = os.path.dirname(os.path.abspath(__file__))
REPS = 10   # Horton used 100 per game per persona; raise for tighter estimates
STEP = 0.02  # weight grid resolution (2%); ~15 s for 6 types

N_EFF = {}  # effective answer count per probe cell (filled by the probes);
            # persisted in weights.json so thin cells are visible

# Charness & Rabin (2002, QJE 117(3)) Table I, two-person dictator games.
# game: ((A_left, B_left), (A_right, B_right), human share choosing Left).
# B is the decider. Berk29 Left-share is 0.31 in Table I and in Horton's Fig. 3
# ("31%"); the v_CR vector printed in Horton's text says .68 — a typo there.
CR_GAMES = {
    "Berk29": ((400, 400), (750, 400), 0.31),
    "Barc2":  ((400, 400), (750, 375), 0.52),
    "Berk23": ((800, 200), (0, 0),     1.00),
    "Barc8":  ((300, 600), (700, 500), 0.67),
    "Berk15": ((200, 700), (600, 600), 0.27),
    "Berk26": ((0, 800),   (400, 400), 0.78),
}

# Engel (2011) dictator meta-analysis: mean give 28.35% of pie, 36.11% give
# nothing, 16.74% choose the equal split (MPI Collective Goods preprint 2010/07).
DICTATOR_TARGET = [0.2835, 0.3611, 0.1674]

q_choice = QuestionMultipleChoice(
    question_name="choice",
    question_text=(
        "{{ scenario.persona }}\n"
        "You are deciding on an allocation for yourself and another person, "
        "Person A.\n"
        "Option Left: you get ${{ scenario.left_b }}, Person A gets "
        "${{ scenario.left_a }}.\n"
        "Option Right: you get ${{ scenario.right_b }}, Person A gets "
        "${{ scenario.right_a }}.\n"
        "Which option do you choose?"
    ),
    question_options=["Left", "Right"],
)

q_give = QuestionNumerical(
    question_name="give",
    question_text=(
        "{{ scenario.persona }}\n"
        "You have $100. You may give any amount of it to a stranger and keep "
        "the rest. The stranger has no say and you will never meet them. "
        "How much do you give?"
    ),
)


def probe_cr(model):
    """Each type's menu behavior -> vector of P(chose Left), in CR_GAMES order."""
    scenarios = ScenarioList([
        Scenario({"ptype": t, "persona": PERSONAS[t], "game": g,
                  "left_a": L[0], "left_b": L[1],
                  "right_a": R[0], "right_b": R[1]})
        for t in TYPES for g, (L, R, _) in CR_GAMES.items()
    ])
    res = q_choice.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)
    rows = res.select("ptype", "game", "choice").to_dicts()

    behavior = {}
    for t in TYPES:
        vec = []
        for g in CR_GAMES:
            picks = [r["choice"] for r in rows
                     if r["ptype"] == t and r["game"] == g and r["choice"]]
            if not picks:
                raise RuntimeError(f"no answers for {t}/{g} — re-run the probe")
            N_EFF[f"{t}/{g}"] = len(picks)
            vec.append(sum(1 for c in picks if c == "Left") / len(picks))
        behavior[t] = vec
    return behavior


def probe_dictator(model):
    """Each type's dictator behavior -> [mean give frac, P(give 0), P(give 50)]."""
    scenarios = ScenarioList(
        [Scenario({"ptype": t, "persona": PERSONAS[t]}) for t in TYPES]
    )
    res = q_give.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)
    rows = res.select("ptype", "give").to_dicts()

    behavior = {}
    for t in TYPES:
        gives = [r["give"] for r in rows if r["ptype"] == t and r["give"] is not None]
        if not gives:
            raise RuntimeError(f"no answers for {t}/dictator — re-run the probe")
        N_EFF[f"{t}/dictator"] = len(gives)
        behavior[t] = [
            sum(gives) / len(gives) / 100,
            sum(1 for g in gives if g == 0) / len(gives),
            sum(1 for g in gives if g == 50) / len(gives),
        ]
    return behavior


def _compositions(n_parts, ticks):
    """All ways to split `ticks` integer units over n_parts bins."""
    if n_parts == 1:
        yield (ticks,)
        return
    for first in range(ticks + 1):
        for rest in _compositions(n_parts - 1, ticks - first):
            yield (first,) + rest


def fit_weights(behavior, target, step=STEP):
    """Grid-search simplex weights minimizing SSE to the target vector."""
    names = list(behavior)
    vecs = [behavior[t] for t in names]
    ticks = round(1 / step)
    best, best_err = None, float("inf")
    for combo in _compositions(len(names), ticks):
        err = 0.0
        for j in range(len(target)):
            pred = sum(combo[i] * vecs[i][j] for i in range(len(names)) if combo[i])
            err += (pred / ticks - target[j]) ** 2
            if err >= best_err:
                break
        if err < best_err:
            best, best_err = combo, err
    return {n: c / ticks for n, c in zip(names, best)}, best_err


def mixture(weights, behavior):
    """Weighted average of the types' behavior vectors."""
    k = len(next(iter(behavior.values())))
    return [sum(weights[t] * behavior[t][j] for t in behavior) for j in range(k)]


def main():
    # max_tokens generous: reasoning tokens eat the cap before the answer
    # (see experiments/common.py make_model)
    model = Model("openai/gpt-oss-120b", service_name="deep_infra",
                  temperature=1, max_tokens=8192)
    n_jobs = len(TYPES) * (len(CR_GAMES) + 1) * REPS
    print(f"probing {len(TYPES)} types, {n_jobs} interviews total...")

    # --- TRAIN on the Charness-Rabin menus ---
    behavior_cr = probe_cr(model)
    print("\nP(Left) per type (columns: " + ", ".join(CR_GAMES) + "):")
    for t, v in behavior_cr.items():
        print(f"  {t:>16}: {[round(x, 2) for x in v]}")

    # identical rows would make the weight split between them arbitrary (v1 bug)
    seen = {}
    for t, v in behavior_cr.items():
        seen.setdefault(tuple(round(x, 2) for x in v), []).append(t)
    for ts in seen.values():
        if len(ts) > 1:
            print(f"  WARNING: {ts} behave identically — their weights are not "
                  "separately identified")

    target = [CR_GAMES[g][2] for g in CR_GAMES]
    weights, sse = fit_weights(behavior_cr, target)
    print(f"\nfitted weights: { {t: round(w, 2) for t, w in weights.items()} }")
    print(f"train SSE={sse:.4f} over {len(target)} games")
    pred = mixture(weights, behavior_cr)
    print("game      human  mixture")
    for j, g in enumerate(CR_GAMES):
        print(f"{g:<9} {target[j]:<6.2f} {pred[j]:.2f}")

    # --- VALIDATE on the held-out dictator game ---
    behavior_d = probe_dictator(model)
    print("\ndictator probe (mean frac, P(0), P(50)):")
    for t, v in behavior_d.items():
        print(f"  {t:>16}: {[round(x, 3) for x in v]}")
    pred_d = mixture(weights, behavior_d)
    val_rmse = (sum((p - h) ** 2 for p, h in zip(pred_d, DICTATOR_TARGET))
                / len(DICTATOR_TARGET)) ** 0.5
    print(f"validation — mixture {[round(x, 3) for x in pred_d]} vs "
          f"Engel {DICTATOR_TARGET}  RMSE={val_rmse:.3f}")

    with open(os.path.join(HERE, "weights.json"), "w") as f:
        json.dump({"weights": weights, "train_sse": sse, "val_rmse": val_rmse,
                   "behavior_cr": behavior_cr, "cr_target": target,
                   "behavior_dictator": behavior_d,
                   "dictator_target": DICTATOR_TARGET, "reps": REPS,
                   "n_eff": N_EFF}, f, indent=2)
    print("saved weights.json")


if __name__ == "__main__":
    main()
