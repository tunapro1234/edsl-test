"""b1 — behavioral benchmark v1 (see benchmark/B1-BRIEF.md).

One-shot games × persona methods × models, run from a single entry point into
one tidy table. Games live in b1/games/ (calibration) and b1/holdout/
(NEVER used for persona tuning). Each game module exposes a GAME dict:

GAME = {
    "game": "dictator",          # unique name
    "role": "dictator",          # decision role label
    "holdout": False,
    "conditions": [{"id": "base", **params}],  # >=1; params fill the wordings
    "wordings": [...],           # >=5 .format(**params) templates; SAME meaning,
                                 # different surface; >=1 numeric-format variant
                                 # (e.g. payoff table vs prose). Last sentence
                                 # asks the decision.
    "question_type": "numerical" | "mc",
    "options": [...],            # mc only
    "decimals": False,           # numerical: allow non-integers?
    "belief": None | {"wordings": [...], "question_type": "numerical"},
                                 # asked BEFORE the decision, rewarded ("+$2")
    "references": {"...": "human stylized fact + SOURCE"},
}

The runner prepends the persona via a scenario field, rotates wording_id
deterministically per (agent, run) — full crossing via --full-wordings —
and appends rows to benchmark/b1/results.csv (resume = skip existing keys).
"""
