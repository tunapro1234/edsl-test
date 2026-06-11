# construction — results

## Who-to-punish v1 run (seed 1, paper's GPT-4o dials, clean 0/78 None)
`results/2026-06-11_15-08-41_construction/` — population: balanced (7,10,10)/(3,1,3)/(1,10,2)
+ one repeat (eff/self/ineq dials).

| | V1 | P1 | P2 | P3 | V2 | P4 | P5 | P6 |
|---|---|---|---|---|---|---|---|---|
| rule | punish-low | | | | **punish-low (RETAINED)** | | | |
| contrib | | 0/0/0/10 | 5/3/10/0 | 5/5/10/5 | | 0/10/10/7 | 10/7/10/10 | **10/10/10/10** |
| punish $ | | 15 | 18 | 1 | | 14 | 3 | 0 |

The full Fehr-Gächter/Ertan arc from the WORST possible start:
- P1 near-total free-riding (textbook corner) → the lone cooperator's group punished the
  worst offender $15 (down to $0 earnings).
- Contributions climb every period under sustained, targeted punishment; relapses
  (A in P4) get hit again ($14) and reform.
- P6: full cooperation, zero punishment needed. Institution retained in both votes.
- This is Ertan's core finding — punish-low regimes RISE over time — reproduced with the
  paper's uncalibrated GPT-4o dials. The dial template carries real behavioral force.

Pending: calibrate.py (1,860 interviews) to fit our-model dials; only adopt over paper
dials if held-out validation justifies it (winner's-curse guard in docstring).
