# twin2k replication — Twin-2K-500 holdout-question accuracy

Validates our A11 implementation (`personas/twin2k`) by re-running a miniature
of the digital-twin evaluation in Toubia, Gui, Peng, Merlau, Li & Chen (2025),
*Twin-2K-500*, arXiv:2505.17479
(`research/papers-to-read/07-twin-2k-500-benchmark.pdf`).

## What the paper does

The paper holds out the 88 heuristics-and-biases questions from the persona,
asks the LLM twin to answer them, and scores against the person's wave 1-3
answers ("The model's completion is ... compared with the Wave 1-3 ground
truth", Sec. 4, p.7). The same questions were re-asked in wave 4, giving a
human test-retest ceiling (Sec. 2, p.4; Sec. 3, p.6). Accuracy metric
(Sec. 3, p.6): binary questions -> exact match; non-binary -> 1 − |deviation|
/ answer range, computed on response-scale positions.

## Paper targets (all read from the PDF)

| Number | Value | Where |
|---|---|---|
| Persona Summary + GPT-4.1-mini accuracy | **68.02%** | Table 2, p.7 (primary target — we inject `persona_summary`) |
| Text Persona + GPT-4.1-mini accuracy | 71.72% | Table 2, p.7 and Sec. 5.1 text, p.7 |
| Random Guessing | 59.17% | Table 2, p.7 |
| Human Test/Retest | 81.72% | Table 2, p.7; Sec. 3, p.6 ("average test-retest accuracy across the 17 tasks is 81.72%") |
| Twin / test-retest ratio | 87.67% | Sec. 5.1, p.7 |
| Temperature 0 in all baseline conditions | — | App. A.1, p.13 ("all other conditions use temperature = 0") |
| System prompt ("answer ... as if you are the individual described in the 'Persona Profile'") | — | App. A.1, p.13 |

## Our miniature

- **People:** the 5 lowest-pid respondents of our fixed 500-person pool
  (pids 1, 2, 3, 13, 14) — deterministic, no cherry-picking.
- **Questions:** per person, the first 8 single-answer multiple-choice holdout
  questions from the `wave_split` config (blocks in survey order; the 41-question
  pricing block excluded so it cannot swamp the probe). 40 calls total.
- **Persona:** built exactly as `personas.twin2k` does it — `HEADER` +
  `persona_summary` + `FOOTER` — because that code path is what we are
  validating. Verified: the summaries contain none of the holdout content
  (grep for redwood/Linda/disease/jacket/etc. comes up empty), so this is
  genuine out-of-persona prediction, same as the paper.
- **Scoring:** the paper's metric on option positions, vs the wave 1-3 answer.
  Also reported: exact-match accuracy, accuracy vs the wave-4 answer, and the
  probe's own human test-retest ceiling (wave-4 vs wave 1-3 answers on the
  same 40 questions = **0.7475**) plus the analytic uniform-random baseline on
  the same 40 questions (**0.5404** — reassuringly close to the paper's 59.17%
  random benchmark on its larger question set).

## Pre-registered pass rule (fixed in code before any API call)

Paper-metric accuracy vs wave 1-3 truth must
1. reach `0.6802 − 0.15 = 0.5302` (Table 2 Persona Summary minus small-N slack),
2. beat the analytic random baseline on our exact 40 questions (0.5404 — the
   binding constraint; a scrambled template/persona scores at random), and
3. have ≥ 90% of the 40 calls answered.

## Deviations from the paper

1. **Model: `gpt-4o` (openai), not GPT-4.1-mini.** The paper contains no
   GPT-4o run anywhere; its models are GPT-4.1-mini, GPT-4.1, and
   Gemini-flash2.5 (Table 2, p.7). gpt-4o is the only OpenAI model verified
   live on our Expected Parrot account, and Table 2 shows accuracy is flat
   across models/variants (67.88–71.92%), so the target band transfers.
2. **N = 5 people × 8 questions** vs 2,058 × 88 — this is a ~$0.5 correctness
   check, not a study. Hence the 0.15 slack in the pass floor.
3. **MC-only probe.** The paper also scores sliders, numeric text entries, and
   matrix rows (transformed to numeric). We keep only single-answer MC
   questions so the paper's position-based metric applies cleanly. Our probe's
   human test-retest (0.7475) is accordingly below the paper's 17-task average
   (0.8172) — the MC experiment items are noisier than the average task — which
   is why the pass rule keys off the twin-accuracy target, with the probe's own
   random baseline and ceiling reported alongside.
4. **Aggregation:** per-question mean over all 40, instead of the paper's
   per-task-then-per-respondent averaging (too few items per task at mini-N).
5. **Prompt framing:** persona inline in the user message via our module's
   HEADER/FOOTER (mirrors the authors' own simulation-repo framing,
   see NOTES.md), not the paper's system prompt; one MC answer per call via
   EDSL's answer-format template, not the paper's batched completion format.
   This is deliberate — the inline framing is the implementation under test.
6. **`persona_summary` (~13k chars) is the injected persona**, matching the
   paper's "Persona Summary" condition (App. A.1, p.13), not the ~128k-char
   "Text Persona" — hence 68.02% (not 71.72%) is the primary target.

## How to run

```
python3 -m personas.twin2k.replication --prepare   # one-time, system python3 (pyarrow), no API
.venv/bin/python -m personas.twin2k.replication        # dry run: design + cost, exits
.venv/bin/python -m personas.twin2k.replication --run  # 40 gpt-4o calls, writes replication.json
```

Dry-run estimate: **~$0.44** (40 calls × ~3.7k input tokens at $2.5/M +
small outputs at $10/M). EDSL's own prompt-level estimator says $1.41 because
it assumes near-max output tokens; actual outputs are one option string plus a
one-line comment. Either way under the $1.5 budget.

Artifact: `personas/twin2k/replication.json` with the schema asserted by
`tests/test_replications.py` (`pass` must be `true`).
