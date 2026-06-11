"""b.01 — behavioral benchmark MVP (B1-BRIEF.md, paraphrase/language layers deferred).

One-shot games × persona methods × models → one tidy CSV. Games live in
b01/games/ (10 calibration) and b01/holdout/ (4 — NEVER used for persona
tuning). Each game module exposes a GAME dict:

GAME = {
    "game": "dictator",            # unique snake_case name
    "role": "dictator",            # decision role label
    "holdout": False,
    "measures": "altruism",        # the parameter this game identifies
    "conditions": [{"id": "base", ...params}],  # >=1; params fill the text
    "text": "...",                 # ONE canonical wording, .format(**params);
                                   # ends by asking the decision. The persona is
                                   # prepended by the runner, NOT part of text.
    "question_type": "numerical" | "mc",
    "options": [...],              # mc only: exact option strings
    "min": 0, "max": 10,           # numerical only: bounds for validation
    "belief": None | {"text": "...", "min": .., "max": ..},
                                   # numerical, asked BEFORE the decision in the
                                   # same survey; rewarded (mention "+$2 if
                                   # within $1 of the true average")
    "references": {"fact": "value + SOURCE (paper, table/page)"},
}

Conventions (zero-error rules):
- All payoffs/numbers appear ONCE, in conditions params — text has only {placeholders}.
- Multi-row instruments (Holt-Laury etc.) = one condition per row, MC choice.
- Wording_id column is always 0 in b.01 (schema stays stable for the later
  paraphrase/language phases).
- Decisions are validated against min/max or options at parse time; out-of-range
  rows are kept but flagged in the `valid` column, never silently dropped.

Output: econbench/b01/results.csv —
model, persona_method, agent_id, game, role, condition, wording_id, run,
decision, belief, valid, raw_len, timestamp, cost_usd
(raw responses live in econbench/b01/raw/<jobhash>.json.gz via EDSL save).
"""
