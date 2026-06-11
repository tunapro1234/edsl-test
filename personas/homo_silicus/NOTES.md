# homo_silicus — notes & results

## v1 calibration (2026-06-11 morning) — what went wrong

Dictator probe only, 3 types x 10 reps, gpt-oss-120b:

| type | mean give | P(give 0) | P(give 50) |
|---|---|---|---|
| self_interested | 0.00 | 1.00 | 0.00 |
| efficient | 0.00 | 1.00 | 0.00 |
| inequity_averse | 0.50 | 0.00 | 1.00 |

Human target as recorded in v1 weights.json (rounded): [0.2835, 0.36, 0.17].
Fitted: `{self_interested: 0.00, efficient: 0.58, inequity_averse: 0.42}`, SSE=0.116.

Three structural failures (all fixed in v2 below):
1. **Identification failure**: in a dictator game the pie is constant, so the
   "efficient" type is indifferent and collapses to keeping — identical to
   self_interested ([0,1,0] both). The grid search tied and its iteration order
   silently gave their whole joint weight to `efficient`, zeroing the MODAL
   human type (36.11% of humans give nothing). Reproduced locally: same inputs
   always return exactly {0, .58, .42}.
2. **No intermediate behavior**: only "give 0" and "give 50" existed, so no
   mixture could hit the human mean of 28.35% (SSE 0.116 is structural).
3. **No validation**: weights fitted to 3 moments of one game, fit failure
   saved without warning.

## Who-to-punish verification (both seed 1, 2 votes x 3 periods)

### Run A — Horton GPT-4o weights -> 2x self_interested + 2x efficient
(`results/2026-06-11_14-21-39_homo_silicus`; the 10% inequity_averse type was
absent — under multinomial sampling that happens 0.9^4 = 66% of the time at n=4)

- **Vote 1**: punish-low passes 4-0 — human-like institution choice (matches
  Ertan-Page-Putterman: groups allow punishing low contributors only).
- **Play**: efficient B, C always contribute 10. Self-interested A free-rides
  from period 1; self-interested D contributes 10 in p1 *fearing punishment*,
  observes none, and is at 0 from p3 (its p2 "0" was a clamped None — the
  reasoned defection is only visible from p3, so read the learning story
  with that caveat).
- **Punishment**: every punish decision = $0. Efficient: "each $1 of punishment
  destroys $1.25 of total welfare" — type-consistent. Self-interested: pure
  cost. **No type in the library can ever pay to punish**, so the institution
  is an empty threat regardless of weights.
- **Vote 2**: punish-low fails 1-3 (A self-protects, B welfare-logic, C yes,
  D votes No with free-riding-protection reasoning; D's None votes were on the
  avg/high items only) — institution dismantled, same anti-human endpoint as
  the bare model (humans retain and use punish-low; it wins on efficiency).
- Type-consistency: every non-None reasoning trace matches its assigned type.
- Data quality: 3 None contributions (A p2, D p2, A p3 — clamped to $0 by the
  old code, materially shaping p2; D's "defection" is only genuinely observed
  from p3 on), 2 None votes, 1 reasoning trace wrapped in an HTML comment.

### Run B — v1 degenerate weights -> 2x efficient + 2x inequity_averse
(`results/2026-06-11_14-31-10_homo_silicus`)

- **Vote 1**: NO punishment allowed at all — efficient types vote No on every
  ballot item (welfare logic); punish-low ties 2-2 and the game treats ties as
  not-allowed.
- **Play**: 10/10/10/10 in all six periods, zero variance, $16 each — a fully
  type-consistent utopia with no human resemblance (humans contribute
  intermediate, decaying amounts without sanctions and never start at 100%).
- **Vote 2**: punish-low passes 3-1 (fairness types + one efficient who flips
  to deterrence logic) but never binds.

**Verdict**: persona ADHERENCE is excellent in both runs — Horton's core
fidelity claim reproduces on gpt-oss-120b. The failures live entirely in the
3-type library (no punisher, no intermediate type) and the degenerate weights.

## v2 redesign (this version)

1. **6-type library**, all grounded in Charness & Rabin (2002, QJE) — the same
   theory Horton's personas operationalize — plus GSA's humanizing prefix
   ("You are a human being with all the cognitive biases and heuristics that
   come with it.", GSA Table 2 notes, verbatim) on every persona to break the
   deterministic corner behavior v1 documented:

   | type | one-liner source |
   |---|---|
   | self_interested | Horton Fig. 3, exact string |
   | efficient | Horton Fig. 3 ("both players" -> "all players" for n-player games) |
   | inequity_averse | Horton Fig. 3, exact string |
   | competitive | CR 2002 "competitive preferences" (sigma < rho < 0: payoff relative to others) |
   | reciprocal | CR 2002 reciprocity term; abstract: subjects "sometimes punish unfair behavior" |
   | selfish_but_fair | GSA Sec. 2.1, verbatim example of a generalizing prompt |

   `reciprocal` is the only type that can rationally pay to punish — the exact
   behavior both runs proved unreachable. `selfish_but_fair` is GSA's own
   example of a prompt producing intermediate dictator offers. `competitive`
   covers spite. GSA's level-k prompts were considered and EXCLUDED: the
   calibration probes are non-strategic, so level-k types would be
   unidentified (their fitted weights would be arbitrary — the v1 bug again).

2. **Train/validate calibration** (calibrate.py): TRAIN on the 6 unilateral
   Charness-Rabin menus (Horton's exact calibration setting; human Left-shares
   from CR 2002 Table I: Berk29 .31, Barc2 .52, Berk23 1.00, Barc8 .67,
   Berk15 .27, Berk26 .78). These menus separate self_interested from
   efficient (Barc2: selfish keeps $400 > $375, efficient takes the $1,125
   pie). VALIDATE (held out) on the $100 dictator game vs Engel's moments.
   The script warns when two types behave identically (unidentified weights)
   and stores train SSE + validation RMSE in weights.json.

3. **Quota sampling**: deterministic largest-remainder counts, seed-shuffled
   order — the most representative group of n the weights allow. (Horton
   samples randomly; at n=4 that drops 10%-types two times out of three.)

4. **Stale-weights guard**: weights.json is used only if its type keys match
   TYPES exactly; otherwise Horton's published GPT-4o fallback (.53/.37/.10,
   new types 0) with a printed notice. The shipped weights.json is that
   fallback, explicitly labeled UNCALIBRATED.

### v2 TODO (in order)
- [ ] **Calibration MUST come before any who_to_punish re-run**: with the
      shipped fallback weights, the n=4 quota is deterministically
      2x self_interested + 2x efficient for EVERY seed — reciprocal (weight 0)
      cannot appear, so a pre-calibration run cannot test the punisher type.
- [ ] Run `.venv/bin/python -m personas.homo_silicus.calibrate` (420 EP
      interviews at REPS=10, well under $1; Horton used 100 reps — raise REPS
      if budget allows).
- [ ] Check the duplicate-vector WARNING and the validation RMSE; if
      validation is poor, expand TYPES and re-run (the GSA loop).
- [ ] Re-run who_to_punish `--personas homo_silicus --seed 1`. Success vs
      runs A/B: punish-low retained in vote 2, positive punishment dollars at
      below-average contributors, contributions neither all-0 nor all-10.
- [ ] Fill in v2 results here.

## Sources (all opened while writing v2)
- `research/papers-to-read/10-horton-homo-silicus.pdf` — Fig. 3 (persona
  strings, human Left-shares, "31%" for Berk29), Sec. 2.2.1 (GPT-4o weights
  .37/.10/.53). NB: the v_CR vector printed in the TEXT ends in .68 for
  Berk29, contradicting the paper's own Fig. 3 and CR Table I — typo; we
  calibrate on the primary numbers.
- Charness & Rabin 2002, QJE 117(3) (UCSD PDF) — Table I game-by-game
  Left-shares; competitive preferences; reciprocity (theta demerit term;
  abstract: "sometimes punish unfair behavior").
- Engel 2011 dictator meta-analysis (MPI Collective Goods preprint 2010/07) —
  "dictators on average give 28.35 % of the pie"; "36.11 % of all participants
  give nothing... 16.74 % choose the equal split".
- `research/papers-to-read/41-manning-general-social-agents.pdf` — Table 2
  (level-k prompt library + the humanizing prefix, verbatim), Sec. 2.1 ("You
  are self-interested but fair."), selection method + train/validate logic.
- `replicant/replication/homo_silicus/charness_rabin.py` — Horton's exact
  scenario payoffs and allocation prompt layout.
