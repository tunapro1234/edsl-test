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

### Run A — Horton default weights (A,D = self_interested; B,C = efficient)
`results/2026-06-11_14-21-39_homo_silicus/`
- Vote 1: punish-low allowed. Vote 2: ALL punishment banned — self_interested players
  explicitly vote to protect their free-riding ("I want to avoid being punishable...").
- Contributions perfectly type-consistent: efficient B,C give $10 every period; A gives $0
  always; D (self_interested) gave $10 in P1 **under punishment threat**, saw nobody
  punishes, dropped to $0 from P2 on. Strategic, not noisy.
- Zero punishment all game (efficient types won't destroy surplus; selfish won't pay $0.25).
- Result: stable exploitation — selfish earn $18/period, efficient earn $8 and keep giving.

### Run B — calibrated weights (A,D = efficient; B,C = inequity_averse)
`results/2026-06-11_14-31-10_homo_silicus/`
- Full cooperation $10×4 every period, all 6 periods; everyone earns $16.
- Vote 1: NO punishment of anyone (no selfish types to deter); vote 2 allowed punish-low,
  but it never fired (nobody below average).
- Calibration changed the INSTITUTION: removing the selfish share removed the demand for
  punishment. Population composition → institutional choice, live.

### Verdict
Injection works and is razor type-consistent; but with these 3 types the population is a
step function (all-give or all-keep). Intermediate human behavior needs either richer types
or trait dials (see construction method). Both runs lack any punisher type — negative
reciprocity is missing from the library entirely.
