# homo_silicus — results

## Calibration (2026-06-11, weights.json)

Dictator probe, 3 types × 10 reps, gpt-oss-120b:

| type | mean give | P(give 0) | P(give 50) |
|---|---|---|---|
| self_interested | 0.00 | 1.00 | 0.00 |
| efficient | 0.00 | 1.00 | 0.00 |
| inequity_averse | 0.50 | 0.00 | 1.00 |

Human target (Engel 2011): mean 0.2835, P(0)=0.36, P(50)=0.17.
Fitted: `{self_interested: 0.00, efficient: 0.58, inequity_averse: 0.42}`, SSE=0.116.

Lessons:
- **Identification failure**: self_interested and efficient behave IDENTICALLY in the
  dictator (total is constant, so "efficient" collapses to keeping) — the probe cannot
  split their weights; the 0.58 assignment to efficient is arbitrary. A second probe
  game where they differ (e.g. a Charness-Rabin menu with efficiency-equality tradeoff)
  would pin them down.
- **Poor fit is structural**: with only "give 0" and "give 50" behaviors available, no
  mixture matches all three human moments (humans give intermediate amounts). This is
  GSA's argument for richer type libraries / construction.
- Types are perfectly deterministic at temp 1 — decision locked, mixture is the ONLY
  source of population variance.

## Who-to-punish verification

(two runs, seed 1)

### Run A — Horton default weights (population: 2× self_interested, 2× efficient)
TBD

### Run B — calibrated weights (population: 2× efficient, 2× inequity_averse)
TBD
