# gps — results

## ⚠ Run 2026-06-11_14-24-31 is PARTIALLY CORRUPTED (None→$0 bug)
p3: 1/4, p4: 3/4, p5: 4/4, p6: 4/4 contributions were None (failed interviews) and the
old clamp(None)→$0 fabricated them as zero. Worst case on record: in P3, player A's
answer was None → recorded as $0 → the group punished A $14 for free-riding that NEVER
HAPPENED. Everything from P3 on is poisoned. Infra fixed since (max_tokens=8192 +
raise on None). Only P1-P2 + votes are trustworthy.

## What the CLEAN part showed (P1-P2 + votes, placeholder N(0,1) dials, seed 1)
The most human-like institutional pattern of any method:
- Vote 1 AND Vote 2: punish-low retained (humans converge here; bare model dismantled it).
- P1: heterogeneous contributions 10/5/10/5; the two $5 contributors were punished
  ($11 and $5) — costly punishment, correctly targeted at below-average contributors.
- P2: **full cooperation 10/10/10/10, zero punishment needed** — punishment worked as a
  deterrent, the exact Fehr-Gächter/Ertan mechanism. First time we observed it.

## Verdict
Even with placeholder independent-N(0,1) dials, GPS preferences produced punish→deter→
cooperate. Strongest candidate so far. Champion upgrades (exact GPS item wordings,
sourced correlations) + a clean v2 run pending.
