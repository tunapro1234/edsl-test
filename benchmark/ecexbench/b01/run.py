"""b.01 runner — one command, one tidy CSV.

    .venv/bin/python -m benchmark.ecexbench.b01.run --games all --methods baseline,gps \\
        --models gpt-oss-120b --n 10 --runs 3 [--holdout] [--dry] [--yes]

Resume comes for free: jobs are re-submitted whole and Expected Parrot's cache
returns already-answered interviews instantly; we only append CSV rows whose
key is not already present. Cost gate: estimated cost is printed first and a
run estimated over $5 refuses to start without --yes (B1-BRIEF discipline).
"""

import argparse
import csv
import os
from datetime import datetime
from itertools import product

from edsl import Agent, QuestionMultipleChoice, QuestionNumerical, Scenario, ScenarioList, Survey

from .agents import bank
from .games import registry
from .models import EST_COST_PER_CALL, MODELS

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "results.csv")
COLUMNS = ["model", "persona_method", "agent_id", "game", "role", "condition",
           "wording_id", "run", "decision", "belief", "valid", "raw_len",
           "timestamp", "cost_usd"]
KEY = ["model", "persona_method", "agent_id", "game", "condition", "wording_id", "run"]


def existing_keys():
    if not os.path.exists(CSV_PATH):
        return set()
    with open(CSV_PATH, newline="") as f:
        return {tuple(row[k] for k in KEY) for row in csv.DictReader(f)}


def build_questions(g):
    """The decision question (and belief question, if any); text via scenario."""
    if g["question_type"] == "numerical":
        q = QuestionNumerical(question_name="decision",
                              question_text="{{ scenario.persona }}\n{{ scenario.qtext }}")
    else:
        q = QuestionMultipleChoice(question_name="decision",
                                   question_text="{{ scenario.persona }}\n{{ scenario.qtext }}",
                                   question_options=g["options"])
    if g.get("belief"):
        qb = QuestionNumerical(question_name="belief",
                               question_text="{{ scenario.persona }}\n{{ scenario.btext }}")
        return Survey([qb, q])  # belief asked BEFORE the decision
    return q


def is_valid(g, decision):
    if decision is None:
        return 0
    if g["question_type"] == "mc":
        return int(decision in g["options"])
    try:
        return int(g["min"] <= float(decision) <= g["max"])
    except (TypeError, ValueError):
        return 0


def run_game(g, model_name, methods, n_agents, runs, dry, done):
    """One EDSL job: all (method, agent, condition) scenarios x runs."""
    scenarios = []
    for method in methods:
        for agent_id, persona in bank(method, n_agents).items():
            for cond in g["conditions"]:
                params = {k: v for k, v in cond.items() if k != "id"}
                s = {"persona": persona, "agent_id": agent_id, "method": method,
                     "condition": cond["id"], "qtext": g["text"].format(**params)}
                if g.get("belief"):
                    s["btext"] = g["belief"]["text"].format(**params)
                scenarios.append(Scenario(s))
    n_calls = len(scenarios) * runs * (2 if g.get("belief") else 1)
    if dry:
        print(f"  {g['game']:24s} {len(scenarios):4d} scenarios x {runs} runs = {n_calls} calls")
        return n_calls, []

    job = build_questions(g)
    if not isinstance(job, Survey):
        job = Survey([job])
    res = job.by(ScenarioList(scenarios)).by(Agent(name="player")).by(MODELS[model_name]()).run(n=runs)
    res.save(os.path.join(HERE, "raw", f"{g['game']}_{model_name}"))

    cols = res.columns
    sel = ["scenario.method", "scenario.agent_id", "scenario.condition",
           "iteration.iteration", "answer.decision"]
    sel += ["answer.belief"] if "answer.belief" in cols else []
    sel += ["generated_tokens.decision_generated_tokens"] if "generated_tokens.decision_generated_tokens" in cols else []
    sel += ["raw_model_response.decision_cost"] if "raw_model_response.decision_cost" in cols else []
    rows = []
    now = datetime.now().isoformat(timespec="seconds")
    for r in res.select(*sel).to_dicts():
        key = (model_name, r["method"], r["agent_id"], g["game"], r["condition"],
               "0", str(r["iteration"]))
        if key in done:
            continue
        cost = r.get("decision_cost")
        rows.append({
            "model": model_name, "persona_method": r["method"],
            "agent_id": r["agent_id"], "game": g["game"], "role": g["role"],
            "condition": r["condition"], "wording_id": 0, "run": r["iteration"],
            "decision": r["decision"], "belief": r.get("belief", ""),
            "valid": is_valid(g, r["decision"]),
            "raw_len": len(str(r.get("decision_generated_tokens", ""))),
            "timestamp": now,
            "cost_usd": round(cost, 6) if isinstance(cost, (int, float)) else "",
        })
    return n_calls, rows


def append_rows(rows):
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", default="all", help="'all', 'holdout', or comma list")
    ap.add_argument("--methods", default="baseline", help="comma list of persona methods")
    ap.add_argument("--models", default="gpt-oss-120b", help="comma list")
    ap.add_argument("--n", type=int, default=10, help="agents per method")
    ap.add_argument("--runs", type=int, default=3, help="repeats per cell")
    ap.add_argument("--dry", action="store_true", help="print cells + estimate, no calls")
    ap.add_argument("--yes", action="store_true", help="approve runs estimated over $5")
    a = ap.parse_args()

    # Methods whose calibration artifacts are probe/game-specific (mixture
    # weights, dial fits) are NOT bench-ready: their numbers would need
    # re-calibration per game family. Replications still cover them.
    NEEDS_PER_GAME_CALIBRATION = {"homo_silicus", "construction"}
    blocked = NEEDS_PER_GAME_CALIBRATION & set(a.methods.split(","))
    if blocked and not a.yes:
        print(f"not bench-ready (per-game calibration): {sorted(blocked)} — "
              "drop them or pass --yes to force")
        return

    reg = registry()
    if a.games == "all":
        games = [g for g in reg.values() if not g["holdout"]]
    elif a.games == "holdout":
        games = [g for g in reg.values() if g["holdout"]]
    else:
        games = [reg[name] for name in a.games.split(",")]
    methods = a.methods.split(",")
    models = a.models.split(",")

    # cost gate
    total_calls = 0
    for g, m in product(games, models):
        calls, _ = run_game(g, m, methods, a.n, a.runs, dry=True, done=set())
        total_calls += calls
    est = sum(total_calls * EST_COST_PER_CALL[MODELS[m]().model] for m in models) / len(models)
    print(f"\nTOTAL: ~{total_calls} calls, estimated ~${est:.2f} "
          f"(EP cost_credits is authoritative — check the panel after)")
    if a.dry:
        return
    if est > 5 and not a.yes:
        print("estimate exceeds $5 — re-run with --yes to approve")
        return

    done = existing_keys()
    for g, m in product(games, models):
        print(f"\n=== {g['game']} × {m}")
        _, rows = run_game(g, m, methods, a.n, a.runs, dry=False, done=done)
        append_rows(rows)
        print(f"  +{len(rows)} new rows -> results.csv")


if __name__ == "__main__":
    main()
