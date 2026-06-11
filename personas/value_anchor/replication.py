"""Mini-replication of Rozen et al. (arXiv:2407.12878) Section 4.1 — value anchoring.

The paper's finding (S4.1 pp.7-8, Fig. 4 p.9): prompting "Answer as a person
that is [value]" makes the model give the ANCHORED value the highest likeness
score, nearby values (on the Schwartz circle, Fig. 1 p.2) similarly high, and
values ~180 degrees away the lowest. We re-run a miniature: 4 anchors spread
around the circle x rate all 19 BWVr value descriptions (1-6 likeness scale)
x REPS reps, on the paper's own Llama 3.1 8B Instruct.

Mini-instrument deviation: the paper's 57-item PVQ-RR is not freely
redistributable, so the rating items are the 19 verbatim Appendix E BWVr
descriptions (the same texts the anchors use; p.4: they "refer conceptually
to the same values that are measured using the PVQ-RR"). One item per call =
serial prompting, which the paper validates for Llama models (Appendix H,
Fig. 6 / Table 5 p.19). Full deviation list: REPLICATION.md.

Dry run (prints design + cost, no API calls):
    .venv/bin/python personas/value_anchor/replication.py
Real run (writes replication.json, costs money — main agent only):
    .venv/bin/python personas/value_anchor/replication.py --run
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from personas.value_anchor import ANCHORS

# ---- design constants (all fixed BEFORE any model call = pre-registered) ----
MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"  # exact paper model (p.4)
SERVICE = "deep_infra"
TEMPERATURE = 0.7   # one of the paper's two settings; Llama-8B Value Anchor
                    # results are ~identical at 0.0 vs 0.7 (Table 1 p.8)
REPS = 3

# ANCHORS is in Appendix E order = the refined-theory circle order (Fig. 1 p.2),
# so index distance = circle distance (19 steps of ~18.9 degrees).
CIRCLE = list(ANCHORS)

# 4 anchors spread across the 4 quadrants of the circle.
TEST_ANCHORS = ["stimulation", "power-resources", "security-personal",
                "benevolence-caring"]
# "Circle-opposite" = offsets 9, 10, 11 around the 19-circle (170.5, 170.5 and
# 151.6 degrees away — the maximally distant values; offset 8 ties offset 11,
# we take the clockwise three). E.g. power-resources -> benevolence-dep,
# benevolence-caring, universalism-concern.
OPPOSITE_OFFSETS = (9, 10, 11)

CRITERIA = ("for >= 3 of 4 anchors, the anchored value's own mean rating "
            "exceeds the mean rating of its 3 circle-opposite values "
            "(offsets 9-11 on the 19-value Schwartz circle)")
MIN_ANCHORS_PASSING = 3

PAPER_TARGETS = {
    "effect": "anchored value scores highest, ~180-degree values lowest "
              "(S4.1 pp.7-8; Fig. 4 p.9)",
    "fig4_peak_mean_centered": "~+1.3 to +2.0 at 0 degrees (all models except "
                               "Gemma-2-9B; read from Fig. 4 p.9)",
    "fig4_trough_mean_centered": "~-0.8 to -1.2 at 150-180 degrees (Fig. 4 p.9)",
    "spearman_vs_human_informational": 0.80,  # Llama 8B serial Value Anchor,
                                              # Fig. 6 p.19 (not a pass gate)
}

# Human benchmark value means (49 cultural groups, Schwartz & Cieciuch 2022),
# as printed in the paper's Table 2 p.14 (acronyms decoded via Appendix C p.17).
HUMAN_MEANS = {
    "benevolence-caring": 0.79, "benevolence-dependability": 0.72,
    "self-direction-action": 0.60, "self-direction-thought": 0.58,
    "universalism-concern": 0.50, "universalism-tolerance": 0.37,
    "security-societal": 0.32, "security-personal": 0.28, "hedonism": 0.23,
    "achievement": 0.08, "face": 0.05, "universalism-nature": -0.10,
    "stimulation": -0.11, "conformity-interpersonal": -0.16,
    "humility": -0.20, "conformity-rules": -0.26, "tradition": -0.72,
    "power-resources": -1.33, "power-dominance": -1.40,
}

N_CALLS = len(TEST_ANCHORS) * len(CIRCLE) * REPS
PRICE_IN, PRICE_OUT = 0.02, 0.05   # deep_infra $/1M tokens
TOKENS_IN, TOKENS_OUT = 450, 80    # rough per-call (prompt + EDSL boilerplate)
COST_ESTIMATE = N_CALLS * (TOKENS_IN * PRICE_IN + TOKENS_OUT * PRICE_OUT) / 1e6


def opposites(anchor):
    i = CIRCLE.index(anchor)
    return [CIRCLE[(i + off) % len(CIRCLE)] for off in OPPOSITE_OFFSETS]


def probe():
    """4 anchors x 19 items x REPS -> mean rating per (anchor, item) cell."""
    from edsl import Agent, Model, QuestionLinearScale, Scenario, ScenarioList

    # Question = the paper's verbatim Value Anchor prompt (p.4); the rated
    # description reuses the paper's own "a person that is [value]" frame so
    # the Appendix E texts stay verbatim. Persona sentence matches sample()
    # in __init__.py exactly.
    q = QuestionLinearScale(
        question_name="rating",
        question_text=(
            "For each of the following descriptions, please answer how much "
            "the person described is like you from 1 (Not like me at all) to "
            "6 (Very much like me), without elaborating on your reasoning. "
            "{{ scenario.persona }}\n"
            "Description: a person that is {{ scenario.item_text }}."
        ),
        question_options=[1, 2, 3, 4, 5, 6],
        option_labels={1: "Not like me at all", 6: "Very much like me"},
    )
    scenarios = ScenarioList([
        Scenario({"anchor": a, "persona": f"Answer as a person that is {ANCHORS[a]}.",
                  "item": v, "item_text": ANCHORS[v]})
        for a in TEST_ANCHORS for v in CIRCLE
    ])
    model = Model(MODEL_NAME, service_name=SERVICE,
                  temperature=TEMPERATURE, max_tokens=2048)
    res = q.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)
    rows = res.select("anchor", "item", "rating").to_dicts()

    means, n_eff = {}, 0
    for a in TEST_ANCHORS:
        for v in CIRCLE:
            picks = [r["rating"] for r in rows
                     if r["anchor"] == a and r["item"] == v
                     and r["rating"] is not None]
            if not picks:
                raise RuntimeError(f"no answers for {a}/{v} — re-run the probe")
            means[(a, v)] = sum(picks) / len(picks)
            n_eff += len(picks)
    return means, n_eff


def spearman(x, y):
    """Rank correlation (informational only; no tie averaging)."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    rx, ry = ranks(x), ranks(y)
    m = (len(x) - 1) / 2
    return (sum((a - m) * (b - m) for a, b in zip(rx, ry))
            / sum((a - m) ** 2 for a in rx))


def analyse(means):
    out, n_passing, gaps = {"anchors": {}}, 0, []
    for a in TEST_ANCHORS:
        opp = opposites(a)
        own = means[(a, a)]
        opp_mean = sum(means[(a, v)] for v in opp) / len(opp)
        ok = own > opp_mean
        n_passing += ok
        gaps.append(own - opp_mean)
        out["anchors"][a] = {"own": round(own, 2),
                             "opposite_mean": round(opp_mean, 2),
                             "gap": round(own - opp_mean, 2),
                             "opposites": opp, "pass": bool(ok)}
    out["n_anchors_passing"] = n_passing
    out["mean_gap"] = round(sum(gaps) / len(gaps), 2)
    # informational: pooled profile vs the human hierarchy (expected < the
    # paper's 0.80 — we pool 4 anchored runs, the paper pools all 19)
    pooled = [sum(means[(a, v)] for a in TEST_ANCHORS) / len(TEST_ANCHORS)
              for v in CIRCLE]
    out["spearman_vs_human_informational"] = round(
        spearman(pooled, [HUMAN_MEANS[v] for v in CIRCLE]), 2)
    return out, n_passing >= MIN_ANCHORS_PASSING


def main():
    print(__doc__.split("\n\n")[0])
    print(f"model:        {SERVICE}/{MODEL_NAME} @ temperature {TEMPERATURE}")
    print(f"design:       {len(TEST_ANCHORS)} anchors x {len(CIRCLE)} items "
          f"x {REPS} reps = {N_CALLS} calls")
    for a in TEST_ANCHORS:
        print(f"  anchor {a:<18} vs opposite-3 {opposites(a)}")
    print(f"pass rule:    {CRITERIA}")
    print(f"cost:         ~${COST_ESTIMATE:.4f} "
          f"(~{TOKENS_IN}+{TOKENS_OUT} tokens/call at "
          f"${PRICE_IN}/{PRICE_OUT} per 1M)")
    if "--run" not in sys.argv:
        print("\ndry run only — pass --run to execute (real API calls)")
        return

    means, n_eff = probe()
    results, passed = analyse(means)
    results["n_effective_answers"] = n_eff
    print(f"\n{'anchor':<20} {'own':>5} {'opp3':>5} {'gap':>6}  pass")
    for a, r in results["anchors"].items():
        print(f"{a:<20} {r['own']:>5} {r['opposite_mean']:>5} "
              f"{r['gap']:>6}  {r['pass']}")
    print(f"anchors passing: {results['n_anchors_passing']}/4   "
          f"mean gap: {results['mean_gap']}   "
          f"spearman vs human (info): "
          f"{results['spearman_vs_human_informational']}")
    print(f"REPLICATION {'PASS' if passed else 'FAIL'}")

    artifact = {
        "method": "value_anchor",
        "model": f"{SERVICE}/{MODEL_NAME} @ temperature {TEMPERATURE}",
        "experiment": "Rozen et al. S4.1 mini: 4 BWVr anchors x 19 BWVr "
                      "value descriptions rated 1-6 (PVQ-RR likeness scale) "
                      f"x {REPS} reps, serial prompting",
        "paper_targets": PAPER_TARGETS,
        "results": results,
        "pass": bool(passed),
        "criteria": CRITERIA,
        "n_calls": N_CALLS,
        "cost_estimate_usd": round(COST_ESTIMATE, 4),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    path = os.path.join(HERE, "replication.json")
    with open(path, "w") as f:
        json.dump(artifact, f, indent=2)
    print(f"saved {path}")


if __name__ == "__main__":
    main()
