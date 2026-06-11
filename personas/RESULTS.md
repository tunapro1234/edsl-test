# Bake-off round 1 — who-to-punish, all 9 methods, clean harness (seed 1)

All runs ≥ commit 15b9531 (max_tokens=8192 + raise-on-None). Table from
`experiments/07_who_to_punish/compare.py --since 15-00`. Human benchmark
(Ertan-Page-Putterman 2009): groups converge to punish-low, contributions
rise/sustain under it, **no group ever allows punishing high contributors**.

| method | votes (low) | mean contrib by period | punish $ | institution |
|---|---|---|---|---|
| twin2k | ✓→✓ | 6.5/8.0/9.2/9.8/10/10 | 4/5/11/5/0/0 | **RETAINED** |
| construction | ✓→✓ | 2.5/4.5/6.2/6.8/9.2/10 | 15/18/1/14/3/0 | **RETAINED** |
| value_anchor v3 | ✓→✓ | 5.0/7.5/6.8/8.2/6.8/7.0 | 0/6/15/0/5/5 | **RETAINED** |
| demographic | ✓→✓ | 5.0 flat (stable norm) | 5/0/0/0/0/0 | **RETAINED** |
| gps v2 | ✗→✓ | 5.0/4.8/2.8 → 4.2/3.8/5.0 | 0/0/0/7/7/0 | **ADOPTED** after decay |
| big5 | ✓→✗ | 7.0/8.5/9.0/6.8/6.0/6.0 | 9/11/7/0/0/0 | dismantled, gradual decay |
| baseline | ✓→✗ | 7.5/6.5/5.2/0/0/0 | 10/10/10/0/0/0 | dismantled, collapse |
| anthology | ✗→✗ | 9.2/9.2/7.5/5.0/5.0/2.5 | 0 | never allowed; no-sanctions decay |
| homo_silicus v2 | ✗→✗ | 5.0 bimodal frozen | 0 | never allowed; frozen exploitation |

## Headline findings

1. **Ertan Result 1 replicates universally**: across ALL 9 conditions and 18 votes,
   punishing HIGH contributors was never allowed — same as 160/160 human group votes.
2. **Methods carrying real human data or calibrated dials keep the institution alive**
   (twin2k, demographic, construction, value_anchor-with-prevalence); twin2k and
   construction additionally reproduce the full Fehr-Gächter arc (punish → deter →
   full cooperation).
3. **gps v2 reproduced Ertan Result 2** (institutional LEARNING): the group banned
   punishment, experienced the decay, then adopted punish-low and recovered to a norm.
4. **anthology reproduced the no-sanctions human pattern** (high start, gradual decay)
   but its warm narrators ban punishment — paper 14's positive-sentiment bias, live.
5. **homo_silicus is the honest failure**: type adherence is perfect, but no punisher
   type survives a calibration whose probes lack prior unfair behavior. Library/probe
   design is the binding constraint (GSA loop continues).
6. **Harness lesson**: decoding params are a treatment (clean baseline punishes;
   default-cap baseline never did), and None→$0 fabrication poisoned all pre-15:00
   runs — see personas/README.md harness floor.

## Caveats
- One 4-player group per method, seed 1 only — population claims need seeds 2-3+.
- Single game; the battery's other 6 games await the same treatment.
- construction runs on the paper's GPT-4o dials (our-model calibration pending).
