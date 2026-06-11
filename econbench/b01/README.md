# b.01 — behavioral benchmark MVP

14 one-shot games (10 calibration in `games/`, 4 holdout in `holdout/` — holdout is
NEVER used for persona tuning) × persona methods × models → one tidy CSV.

## Run
    .venv/bin/python -m econbench.b01.run --games all --methods baseline,gps,twin2k --n 10 --runs 3
    .venv/bin/python -m econbench.b01.run --games holdout --methods ... [--dry] [--yes]
    python3 -m econbench.b01.plots          # histograms (system python3 has matplotlib)

- Cost estimate prints first; estimates over $5 refuse to start without `--yes`.
- Resume is free: re-running re-submits whole jobs, Expected Parrot's cache returns
  finished interviews instantly, only missing CSV rows are appended.
- Agent banks (`agents_bank/`): the SAME virtual person (agent_id) plays every game.
- `results.csv` schema: model, persona_method, agent_id, game, role, condition,
  wording_id (always 0 in b.01), run, decision, belief, valid, raw_len, timestamp,
  cost_usd. Invalid decisions are kept and flagged, never dropped.
- `references.yaml` — human reference values, generated from the GAME dicts
  (every number carries its source; regenerate after editing a game).

## Build provenance
13 of 14 games were written by champion agents (one expert per game), each verified
by two adversarial reviewers (contract/math + instrument fidelity vs the canonical
papers — Holt-Laury AER Table 1, FGF 2001, Johnson-Mislin 2011 meta, Oosterbeek 2004
meta, TK 1992, Arad-Rubinstein 2012, Fehr-Gächter 2000, Fehr-Fischbacher 2004,
Nagel 1995, Ertan-Page-Putterman). 0/26 verdicts refuted; 5 modules revised.

## Deferred to later phases (B1-BRIEF)
Paraphrase ensemble and multi-language variants (same numbers, different surface;
per-language paraphrases) — the wording_id column already reserves the schema room.
