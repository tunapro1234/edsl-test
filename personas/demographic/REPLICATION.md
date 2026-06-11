# demographic — paper replication (Argyle et al., Study 2)

**Source.** Argyle, Busby, Fulda, Gubler, Rytting & Wingate, "Out of One, Many:
Using Language Models to Simulate Human Samples" (arXiv:2209.06899v1; published
in *Political Analysis* 31(3), 2023). Local PDF:
`research/papers-to-read/08-argyle-out-of-one-many.pdf`. All page numbers below
refer to that PDF (arXiv v1 layout).

## What the paper did (Study 2)

GPT-3 davinci (base) was conditioned on first-person backstories templated from
10 ANES variables per real respondent (race/ethnicity, gender, age, ideology,
party ID, political interest, church attendance, discussing politics,
flag-patriotism, state — p. 10 and Appendix C.1, p. 30). The vote was read off
as the probability that "In [year], I voted for..." completes with each
candidate's token set, dichotomized at 0.50 (p. 10; Appendix C, p. 31).
One query per ANES respondent: 5,914 (2012), 4,270 (2016), 5,442 (2020), for a
total of 15,626 queries (Appendix E "Cost Analysis", p. 50: "Study 2 consisted
of 3 experiments… for a total of 15,626 queries" — these counts appear there,
not on p. 10).

## Paper targets (every number read from the PDF)

| Quantity | Value | Where |
|---|---|---|
| Tetrachoric corr., whole sample, 2012 | 0.90 | Table 1, p. 11; also in-text p. 11: "The 2012 tetrachoric correlation across all respondents 0.90, the 2016 estimate was 0.92, and the 2020 value was 0.94." |
| Tetrachoric corr., whole sample, 2016 | 0.92 | Table 1, p. 11 (same sentence) |
| Tetrachoric corr., whole sample, 2020 | 0.94 | Table 1, p. 11 (same sentence) |
| Tetrachoric corr., strong partisans, 2020 | 1.00 | Table 1, p. 11, "Strong partisans" row (0.99 in 2012, 1.00 in 2016) |
| Prop. agreement, strong partisans, 2020 | 0.97 | Table 1, p. 11, "Strong partisans" row (0.97 in all three years) |
| 2020 marginals | GPT-3 P(Trump) 0.472 vs ANES 0.412 | p. 10, end of Study 2 intro |

## Our mini design

`replication.py` (dry-run by default; `--run` bills the API):

- **Personas**: first 12 `strong democrat` + first 12 `strong republican` rows
  of `gss_sample.csv` in file order (deterministic, no RNG), rendered with the
  module's own `_render()` — the exact object real experiments use.
- **Instrument**: `QuestionMultipleChoice`, "In the 2020 United States
  presidential election, who did you vote for?" with options
  [Joe Biden, Donald Trump]; persona in a scenario field, 1 rep, temperature 0.
- **Model**: `deep_infra/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`,
  max_tokens 2048. 24 calls, estimate ≈ $0.004.
- **Statistic**: share of valid answers that vote their own party's candidate.
- **Pre-registered pass criterion** (in code, above any results):
  own-party-aligned share ≥ 0.80 among ≥ 20 valid answers.

Why this detects a broken implementation — two layers, because the statistical
criterion alone cannot catch every bug:

- **Deterministic guard (free, runs even on dry run).** `pick_rows()` asserts
  that each rendered persona contains its row's verbatim `partyid` fragment.
  This is needed because the backstory also carries `polviews`, and 17 of the
  24 selected personas state a party-consistent ideology (5 are moderates,
  only 2 crossed) — so a bug that dropped *only* the partyid fragment would
  plausibly still score ~0.75–0.9 and could clear the 0.80 threshold. The
  assert catches that case directly, before any API call.
- **Statistical criterion (the run itself).** A template that is scrambled,
  empty, or left unsubstituted collapses every persona to the model's own
  prior — the same answer for everyone → alignment ≈ 0.50 → fail. The paper's
  strong-partisan agreement is 0.97–1.00, so 0.80 leaves room for honest noise
  (binomial N=24: a true rate of 0.95 fails < 1% of the time) without
  admitting a coin flip (a 0.5-prior responder passes with p ≈ 0.0008).

## Deviations from the paper (all of them)

1. **Model: GPT-3 davinci (base) → Llama-3.1-70B-Instruct-Turbo.** The paper's
   base model is retired and unavailable on Expected Parrot; this is the
   closest strong open model offered. Biggest deviation: an instruct/chat
   model, not a base completion model. The module already compensates — its
   `_render` wraps the verbatim Argyle-style fragments in a two-line role
   frame (see module docstring) because a chat model misreads bare "I am
   female..." text.
2. **Readout: token log-probs → sampled MC answer.** No log-prob access via
   EDSL chat APIs. Temperature 0 + forced binary choice approximates the
   paper's dichotomize-at-0.50 rule (Appendix C, p. 31).
3. **Data: ANES 2012/2016/2020 respondents → GSS 2024 rows.** The point is to
   validate OUR persona source (gss_sample.csv + `_render`), so we use it
   as-is. Side effect: the backstory uses ~16 GSS fragments (income, class,
   religion, etc.), not the paper's exact 10 ANES variables — we replicate the
   method shape (real-respondent demographic backstory → vote), not the
   variable list. Note the personas are 2024 people asked to recall a 2020
   vote; acceptable for a correctness check.
4. **Ground truth: ANES self-reported vote → party ID.** The GSS extract has
   no vote-choice column. We therefore restrict to strong partisans, for whom
   own-party voting is near-universal and for whom the paper itself reports
   0.97 agreement / 1.00 tetrachoric (Table 1, p. 11) — so "votes own party"
   is the right target for this subgroup.
5. **Statistic: tetrachoric correlation → proportion aligned.** With N=24 and
   (expected) empty off-diagonal cells the tetrachoric is degenerate/undefined;
   proportion agreement is the paper's own companion column in Table 1.
6. **N: 15,626 queries → 24.** Correctness check, not a study (~$0.004).
7. **2020 only.** The paper's strongest year (0.94) and its out-of-training-
   corpus test; one year suffices to validate the pipeline.
8. **Fixed option order** (Biden first). The paper's probability readout had
   no order; any order bias works against us symmetrically across the two
   12-persona groups.
