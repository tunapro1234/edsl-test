"""Re-fit the GSA construction dials for OUR model (the GSA 'construction' step).

Replicates Manning & Horton (arXiv:2508.17407) Appendix A.2 with one change
that makes the search cheaper AND wider. The paper Bayesian-optimizes over
SETS of 3 dial vectors, re-querying the LLM for every candidate set (20 sets
x 3 agents x 6 games x 30 reps). But in one-shot dictator games agents never
interact, so a set's choice distribution is EXACTLY the average of its
members' individual distributions. We therefore (1) probe each candidate
vector once, then (2) search ALL 3-subsets locally for free — 4,060 sets
scored vs the paper's 20, at a sixth of the LLM calls.

Probe: each candidate plays the paper's six Charness & Rabin (2002) unilateral
dictator games REPS times (plus a bare-model "baseline" row, kept out of the
fit, mirroring the paper's red bars). Fit: enumerate every 3-subset, score the
uniform mixture by mean absolute error against the human shares choosing
"Left", keep the best.

Human targets: Left shares (.52, .67, .27, 1.00, .78, .31) for (Barc2, Barc8,
Berk15, Berk23, Berk26, Berk29) — Charness & Rabin 2002 Table I / Horton 2023
Figure 3; payoffs as printed in GSA Fig. A1 = Horton Fig. 3. Notes: in Berk23
"Right" = (0,0) is Pareto-dominated, so ALL humans chose Left (target 1.00);
in Berk29 Horton's in-text v_CR says .68 but his Figure 3 says 31% — we use
the figure/primary source (see HUMAN_LEFT comment).

Discipline: the fitted dials.json must NOT be trusted over the paper's
validated dials just because its in-sample MAE is lower — at REPS=10 the
exhaustive subset search has ~+0.03 winner's-curse optimism (verifier
simulation). Validate on held-out games (GSA's 20 two-stage CR games) or
bump REPS before letting dials.json drive real experiments.

Writes probe.json (raw per-vector behavior; delete it to re-probe — EDSL's
remote cache makes re-running already-probed vectors free, so densifying GRID
later only pays for the new vectors) and dials.json (the fitted vectors;
sample() prefers dials.json over the paper's GPT-4o optimum).

Run from repo root:  .venv/bin/python -m personas.construction.calibrate
Cost: (27 grid + 3 paper + 1 baseline) x 6 games x REPS = 1,860 interviews.
"""

import itertools
import json
import os

from edsl import QuestionMultipleChoice, Agent, Model, Scenario, ScenarioList

from . import PAPER_DIALS, render

HERE = os.path.dirname(os.path.abspath(__file__))
REPS = 10
GRID = (1, 5, 10)  # coarse 1-10 grid; densify later if the fit looks tight
K = 3              # mixture size, as in the paper

# CR unilateral dictator games: name -> ((A_left, B_left), (A_right, B_right)).
# Person B is the dictator. Payoffs: GSA Fig. A1 (p. 49) = Horton 2023 Fig. 3.
GAMES = {
    "Barc2": ((400, 400), (750, 375)),
    "Barc8": ((300, 600), (700, 500)),
    "Berk15": ((200, 700), (600, 600)),
    "Berk23": ((800, 200), (0, 0)),
    "Berk26": ((0, 800), (400, 400)),
    "Berk29": ((400, 400), (750, 400)),
}
# Human share choosing Left (Charness & Rabin 2002 Table I; Horton 2023 Fig. 3).
# WARNING: Horton's in-text v_CR ends ".68" for Berk29 — that is a typo (it is
# the share choosing RIGHT). His own Figure 3 and GSA Fig. A1 both put the
# Berk29 human Left share at ~0.31; we calibrate on the primary sources.
HUMAN_LEFT = {"Barc2": 0.52, "Barc8": 0.67, "Berk15": 0.27,
              "Berk23": 1.00, "Berk26": 0.78, "Berk29": 0.31}

q_choose = QuestionMultipleChoice(
    question_name="choice",
    question_text=(
        "{{ scenario.persona }}\n"
        "You are Person B. You alone decide how money is divided between you "
        "and Person A; Person A has no say and you will never meet them.\n"
        "Left: Person A gets {{ scenario.a_left }} and you get {{ scenario.b_left }}.\n"
        "Right: Person A gets {{ scenario.a_right }} and you get {{ scenario.b_right }}.\n"
        "Which do you choose?"
    ),
    question_options=["Left", "Right"],
)


def key(d):
    return "-".join(str(x) for x in d)  # (7, 10, 10) -> "7-10-10"


def unkey(s):
    return tuple(int(x) for x in s.split("-"))


def candidates():
    """Grid vectors + the paper's published optimum (deduplicated, sorted)."""
    cands = {(e, s, i) for e in GRID for s in GRID for i in GRID}
    cands.update(PAPER_DIALS)
    return sorted(cands)


def probe():
    """Every candidate (and the bare model) plays all six games REPS times."""
    texts = {key(c): render(c) for c in candidates()}
    texts["baseline"] = ""  # bare model, shown for reference, never fitted
    scenarios = ScenarioList([
        Scenario({"who": w, "persona": p, "game": g,
                  "a_left": L[0], "b_left": L[1],
                  "a_right": R[0], "b_right": R[1]})
        for w, p in texts.items() for g, (L, R) in GAMES.items()
    ])
    # max_tokens generous: the reasoning chain eats output tokens before the
    # answer; the default cap produced answer=None (see experiments/common.py)
    model = Model("openai/gpt-oss-120b", service_name="deep_infra",
                  temperature=1, max_tokens=8192)
    res = q_choose.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)

    rows = res.select("who", "game", "choice").to_dicts()
    p_left = {w: {} for w in texts}
    for w in texts:
        for g in GAMES:
            picks = [r["choice"] for r in rows
                     if r["who"] == w and r["game"] == g and r["choice"] is not None]
            if not picks:
                raise RuntimeError(f"no valid answers for {w} in {g}; re-run probe")
            p_left[w][g] = sum(c == "Left" for c in picks) / len(picks)
    return p_left


def mae(vectors):
    """Mean abs. error of the uniform mixture's P(Left) vs the human shares."""
    return sum(
        abs(sum(v[g] for v in vectors) / len(vectors) - HUMAN_LEFT[g])
        for g in GAMES
    ) / len(GAMES)


def fit_dials(p_left, k=K, top=5):
    """Score every k-subset of candidates (exhaustive — no LLM calls needed)."""
    names = [w for w in p_left if w != "baseline"]
    scored = sorted(
        (mae([p_left[w] for w in combo]), combo)
        for combo in itertools.combinations(names, k)
    )
    return scored[:top]


def main():
    path = os.path.join(HERE, "probe.json")
    if os.path.exists(path):
        print("using existing probe.json (delete it to re-probe)")
        with open(path) as f:
            p_left = json.load(f)["p_left"]
    else:
        p_left = probe()
        with open(path, "w") as f:
            json.dump({"reps": REPS, "grid": GRID, "p_left": p_left}, f, indent=2)
        print("saved probe.json")

    base_mae = mae([p_left["baseline"]])
    paper_mae = mae([p_left[key(d)] for d in PAPER_DIALS])
    print(f"baseline (no persona) MAE: {base_mae:.3f}   (paper's GPT-4o: 0.42)")
    print(f"paper dials on our model MAE: {paper_mae:.3f} (paper's GPT-4o: 0.20)")

    top = fit_dials(p_left)
    print("best fitted sets:")
    for err, combo in top:
        print(f"  MAE {err:.3f}  {combo}")

    err, combo = top[0]
    with open(os.path.join(HERE, "dials.json"), "w") as f:
        json.dump({"dials": [list(unkey(w)) for w in combo], "mae": err,
                   "baseline_mae": base_mae, "paper_dials_mae": paper_mae,
                   "human_target": HUMAN_LEFT, "reps": REPS,
                   "model": "openai/gpt-oss-120b"}, f, indent=2)
    print(f"saved dials.json: {combo}  MAE {err:.3f}")


if __name__ == "__main__":
    main()
