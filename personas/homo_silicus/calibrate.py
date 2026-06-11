"""Fit the Homo Silicus mixture weights (GSA 'selection' step).

Probe: each type plays a one-shot $100 dictator game REPS times. Each type's
behavior is summarized as a feature vector [mean give fraction, share giving 0,
share giving exactly half]; we grid-search simplex weights w so the weighted
mixture matches the human targets from Engel's 2011 dictator meta-analysis.

Writes weights.json next to this file; sample() prefers it over the Horton
defaults. Re-run after changing TYPES or the probe.

Run from repo root:  .venv/bin/python -m personas.homo_silicus.calibrate
"""

import json
import os

from edsl import QuestionNumerical, Agent, Model, Scenario, ScenarioList

from . import TYPES

HERE = os.path.dirname(os.path.abspath(__file__))
REPS = 10
# Engel 2011 meta-analysis: mean give 28.35% of pie, 36% give nothing, 17% split equally
HUMAN_TARGET = [0.2835, 0.36, 0.17]

q_give = QuestionNumerical(
    question_name="give",
    question_text=(
        "{{ scenario.persona }}\n"
        "You have $100. You may give any amount of it to a stranger and keep "
        "the rest. The stranger has no say and you will never meet them. "
        "How much do you give?"
    ),
)


def probe():
    """Each type's dictator behavior -> feature vector [mean frac, P(0), P(50)]."""
    scenarios = ScenarioList(
        [Scenario({"type": t, "persona": p}) for t, p in TYPES.items()]
    )
    model = Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)
    res = q_give.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)

    behavior = {}
    rows = res.select("type", "give").to_dicts()
    for t in TYPES:
        gives = [r["give"] for r in rows if r["type"] == t and r["give"] is not None]
        behavior[t] = [
            sum(gives) / len(gives) / 100,
            sum(1 for g in gives if g == 0) / len(gives),
            sum(1 for g in gives if g == 50) / len(gives),
        ]
    return behavior


def fit_weights(behavior, target, step=0.01):
    """Grid-search 3-type simplex weights minimizing SSE to the target vector."""
    names = list(behavior)
    assert len(names) == 3, "grid is written for exactly 3 types"
    ticks = round(1 / step)
    best, best_err = None, float("inf")
    for a in range(ticks + 1):
        for b in range(ticks + 1 - a):
            w = (a / ticks, b / ticks, (ticks - a - b) / ticks)
            err = sum(
                (sum(wi * behavior[t][k] for wi, t in zip(w, names)) - target[k]) ** 2
                for k in range(len(target))
            )
            if err < best_err:
                best, best_err = dict(zip(names, w)), err
    return best, best_err


def main():
    behavior = probe()
    print("probe (mean frac, P(0), P(50)):")
    for t, v in behavior.items():
        print(f"  {t:>16}: {[round(x, 3) for x in v]}")

    weights, err = fit_weights(behavior, HUMAN_TARGET)
    print(f"fitted weights: {weights}   SSE={err:.4f}")

    with open(os.path.join(HERE, "weights.json"), "w") as f:
        json.dump({"weights": weights, "sse": err, "behavior": behavior,
                   "target": HUMAN_TARGET, "reps": REPS}, f, indent=2)
    print("saved weights.json")


if __name__ == "__main__":
    main()
