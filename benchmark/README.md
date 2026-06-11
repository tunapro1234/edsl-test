# benchmark/ — scoring persona methods against human data

First instrument: `score_wtp.py` — scores every who-to-punish run on 9 criteria
(0-1 each) derived from Ertan-Page-Putterman 2009 + standard PGG regularities,
weighted (institutional/treatment fidelity 3, behavioral mechanics 2, shape 1)
into one human-likeness index. Criterion details in the script header;
parameter targets in `human_targets.json` (agent-extracted from the paper,
adversarially verified; inline defaults otherwise).

Run:
    .venv/bin/python benchmark/score_wtp.py --since 15-00 [--csv benchmark/wtp_scores.csv]

Notes:
- N/A criteria (e.g. punishment targeting when punishment was never legal) are
  excluded from the weighted index, not zero-filled.
- `treatment_effect` compares the LAST period of each regime (quasi steady
  state) so recovery-from-decay paths aren't punished for the rebuild time.
- **Cache degeneracy**: methods whose personas don't vary with seed (baseline:
  always empty; homo_silicus: quota composition is seed-invariant) produce
  identical runs across seeds via the EDSL remote cache — effective n=1.
  Seed variance is only meaningful for methods that sample fresh personas
  (big5, value_anchor, gps, demographic, anthology, twin2k).
- Harness floor applies: only runs at/after commit 15b9531 count (see
  personas/README.md).
