# construction — paper replication

**Paper:** Manning & Horton, *General Social Agents* (arXiv:2508.17407), Appendix A
"Predicting behavior in novel allocation games", pp. 48–53 of the local PDF
(`research/papers-to-read/41-manning-general-social-agents.pdf`).

## Claim being replicated

On GPT-4o, the trait-dial prompt template (Appendix A.2, p. 49 — verbatim in our
`__init__.py:TEMPLATE`) with the Bayesian-optimized dial set
phi\* = (7,10,10), (3,1,3), (1,10,2), played as a uniform 3-agent mixture, matches
human Left-shares on the six Charness & Rabin (2002) single-stage dictator menus far
better than the bare model.

## Paper targets (every number read from the PDF)

| target | value | where in the paper |
|---|---|---|
| baseline MAE | 0.42 | p. 49, text below Fig. A1: "we find 1/6 Σ d(P_s, P̂₀) = 0.42" |
| phi\* mixture MAE | 0.20 | p. 50, end of A.2: "the resulting distribution aligns much closer with the human responses: 1/6 Σ d(P_s, P̂_θ\*) = 0.2 … more than halving the baseline AI's error (MAE = 0.42)" |
| phi\* vectors | (7,10,10), (3,1,3), (1,10,2) | p. 50: "this optimization identifies the optimal parameter vectors as: (φ₁\*, φ₂\*, φ₃\*) = ((7,10,10), (3,1,3), (1,10,2))" |
| menu payoffs | Barc2 (400,400)/(750,375); Barc8 (300,600)/(700,500); Berk15 (200,700)/(600,600); Berk23 (800,200)/(0,0); Berk26 (0,800)/(400,400); Berk29 (400,400)/(750,400) | Fig. A1 column headers, p. 49 (= Horton 2023 Fig. 3) |
| human Left-shares | .52, .67, .27, 1.00, .78, .31 | CR 2002 Table I, plotted as the dashed human lines in Fig. A1 (p. 49) / Horton 2023 Fig. 3. NOTE: Horton's in-text v_CR ends ".68" for Berk29 — that is the *Right* share (typo); both figures put the Left share at 0.31. Documented in `calibrate.py:HUMAN_LEFT`. |
| baseline elicitation | no extra instructions, 1,000 reps/menu | pp. 48–49: "we elicited 1,000 responses per setting from GPT-4o, without any additional instructions" |
| reps during optimization | 30 per agent per menu | p. 50 top: "we query the model 30 times per agent" |
| temperature | 1 | p. 50 (A.3): "150 times each with the temperature set to 1"; assumed identical in A.1–A.2, which do not state it |

## Design

(3 phi\* personas rendered by our `render()` + 1 empty-persona baseline) × 6 menus
× REPS=10, on `openai/gpt-4o` (the paper's model), temperature 1, via the exact
EDSL question object real experiments use (`calibrate.py:q_choose`). Mixture
P(Left) per menu = mean of the three agents' P(Left) (agents never interact in a
one-shot dictator game, so the uniform mixture is exactly the average). Score =
MAE vs the human Left-shares; same for the baseline row.

**Pre-registered pass criteria** (constants in code before any result exists):

- MAE(phi\* mixture) < MAE(baseline), and
- |MAE(phi\* mixture) − 0.20| ≤ 0.15.

Rationale: with REPS=10 the per-menu mixture share averages 30 binomial draws
(SE ≈ 0.09), so the 6-menu MAE wobbles a few hundredths; 0.15 also absorbs
GPT-4o snapshot drift. But a broken implementation (scrambled template, swapped
payoffs) collapses toward baseline behavior — landing at 0.42 gives
|0.42 − 0.20| = 0.22 > 0.15 and fails, as does any phi\* MAE not beating baseline.

Calls: 4 × 6 × 10 = **240**. Cost: ~420 prompt + ~80 completion tokens per call
at gpt-4o $2.50/$10 per 1M → **≈ $0.44**.

## Deviations from the paper

1. **Mini-N.** REPS=10 per persona-menu vs the paper's 30 (and 1,000 for the
   baseline). Cost control; the pass band is sized for the extra noise.
2. **No re-optimization.** We take the published phi\* as given and verify it
   reproduces the published in-sample MAE; we do not re-run the 20-set Bayesian
   optimization (that is `calibrate.py`'s job, on our own model).
3. **Question wording.** Appendix A prints the trait template verbatim but not
   the exact game-presentation prompt. We use our repo's dictator wording
   (`calibrate.py:q_choose`: "You are Person B… Left: Person A gets X and you
   get Y…") with Fig. A1's payoffs. This is deliberate — the artifact certifies
   *our* instrument, not a reconstruction of theirs.
4. **EDSL harness.** `QuestionMultipleChoice` appends its own answer-formatting
   instructions; the paper's elicitation/parsing pipeline is unspecified.
5. **Baseline prompt.** Paper: no additional instructions at all. Ours: the same
   question with an empty persona field (one leading blank line).
6. **Model snapshot.** "GPT-4o" without a dated snapshot in the paper; Expected
   Parrot's `gpt-4o` resolves to the current snapshot — drift is possible and is
   another reason for the ±0.15 band.
7. **Temperature.** Stated as 1 only for the A.3 two-stage games; we assume the
   same for the single-stage menus.

## Verdict

Written by `replication.py --run` to `replication.json`
(`tests/test_replications.py` asserts `pass == true`).
