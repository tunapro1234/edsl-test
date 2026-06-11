# Who-to-punish benchmark — final report (9 methods × 3 seeds, 27 runs)

Scored by `score_wtp.py` against agent-extracted, adversarially-verified Ertan-Page-
Putterman targets (`human_targets.json`). Index = weighted mean of 9 criteria
(institutional fidelity ×3, behavioral mechanics ×2, distributional shape ×1);
N/A criteria excluded, not zero-filled. Full per-run table: `wtp_scores.csv`.

## Ranking (mean index, n=3 seeds; ± is range)

| # | method | index | range | what drives it |
|---|---|---|---|---|
| 1 | construction | **0.813** | 0.60-0.97 | institution + full FG arcs, but seed 2 dismantled |
| 2 | demographic | **0.797** | 0.61-0.97 | stable norms; seed 3 dismantled |
| 3 | value_anchor | **0.786** | 0.66-0.97 | prevalence weights help; value-draw lottery is real variance |
| 4 | twin2k | **0.783** | 0.62-0.87 | strong arcs; loses points on punishment-intensity ratio |
| 5 | baseline | 0.694 | 0.66-0.69 | human-ish WITHIN regimes; always dismantles institution |
| 6 | big5 | 0.688 | 0.63-0.76 | dynamics yes, direction noisy |
| 6 | gps | 0.688 | 0.57-0.90 | seed 1 adoption story (0.90) didn't repeat |
| 8 | homo_silicus | 0.677 | 0.68-0.68 | seed-invariant; never legalizes punishment |
| 9 | anthology | 0.617 | 0.55-0.67 | too-prosocial narrators; P1 way above human band |

## Robust findings

1. **Ertan Result 1 is universal**: never-punish-high held in **54/54 votes** across
   every method, seed, and persona condition. The strongest replication we have.
2. **Top-4 vs the rest**: persona methods carrying real human data (demographic,
   twin2k) or theory-calibrated dials (construction, prevalence-weighted
   value_anchor) cluster at 0.78-0.81; everything else sits 0.62-0.69 with the
   bare model. With n=3 the within-cluster order is NOT statistically meaningful —
   claim the cluster, not the podium.
3. **The persona value-add is institutional**: the clean baseline already punishes
   and contributes in-band within regimes (0.69 index); what personas buy is
   keeping/adopting the punish-low institution in vote 2 (the criteria where the
   top-4 dominate and baseline scores 0 in all three seeds).
4. **Seed variance is large** (ranges up to 0.37) — single-seed rankings mislead;
   any future method comparison needs ≥3 seeds, ideally more.

## Caveats
- Same model (gpt-oss-120b), same decoding everywhere; the benchmark measures
  persona effects, not model choice.
- One game; the other 6 battery games are unscored.
- homo_silicus/baseline are cache-degenerate across seeds (effective n=1).
- Criteria weights are ours; sensitivity-check before the prof deliverable.
