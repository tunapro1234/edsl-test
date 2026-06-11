# big5 — paper replication

**Paper:** Cho & Cheong (2025), *Scaling Personality Control in LLMs with Big Five
Scaler Prompts*, arXiv:2508.06149
(local: `research/papers-to-read/17-big5scaler-prompt-control.pdf`).
**What we replicate:** the single-trait expression test (Sec. 4.1, results Sec. 5.1,
Table 1) — does dialing one trait up in the prompt raise that trait's questionnaire
score above a neutral baseline?

## Paper targets (where each number was read)

Table 1, p.7 — "Trait scores of Alpaca 7B when conditioned with each prompting
method", mean trait score on the 1,000-item MPI, 1-5 scale:

| trait | Simple (dialed) | Neutral |
|---|---|---|
| Openness | 4.26 | 3.97 |
| Conscientiousness | 4.19 | 3.61 |
| Extraversion | 4.37 | 3.89 |
| Agreeableness | 4.03 | 3.56 |
| Neuroticism | 2.73 | 3.01 |

Supporting reads:
- Sec. 4.1, p.4: design — target trait set to 100 on scale n=100, other traits
  omitted; baselines NEUTRAL/NAIVE/WORDS/P2; "All prompt-based evaluations are
  conducted using the Alpaca-7B model" (footnote 1); scored with the 1,000-item MPI.
- Sec. 4 intro, p.4: generation settings `max_new_tokens = 512, temperature = 1.0,
  top_p = 0.8`.
- Sec. 5.1, p.6: "One consistent exception is the Neuroticism trait, where all
  methods, including Big5-Scaler, underperform... safety alignment objectives."
- Sec. 6 Observations, p.8: best combo = **Phi4-14B + simple prompt + scale of 10**;
  scale 10 gave the lowest RMSE across all models; simple beat specific/simspec.
- Abstract, p.1: headline "average Big Five trait scores exceeding 4.0 (max 5)".

## Our miniature (replication.py)

- **Cells (6):** for each of the 5 traits, our module's production template
  (`personas/big5/__init__.py`) with the target trait at 10/10 and the other four at
  5/10; plus one neutral persona with all five at 5/10.
- **Instrument:** the 12 BFI-2 items of the target domain (neutral persona rates all
  60), `research/datasets/bfi2/bfi2_items.csv`, "I am someone who ..." stem, 1-5
  agree scale, reverse-keyed items scored 6−x. BFI-2 "Open-Mindedness" / "Negative
  Emotionality" map to the paper's "openness" / "neuroticism".
- **Model:** `deep_infra/microsoft/phi-4`, temperature=1, top_p=0.8 (paper's
  settings), max_tokens=2048.
- **N:** (5×12 + 60) items × 10 reps = 1,200 calls ≈ $0.05.
- **Template integrity assert:** rebuilding a `big5.sample()` persona from its own
  parsed scores must reproduce the module's text verbatim — a scrambled or drifted
  template fails at import, before any money is spent.

## Pre-registered pass criteria (fixed in code before any run)

1. dialed domain mean > neutral domain mean on ≥ 4 of 5 traits, **and**
2. dialed domain mean ≥ 3.5/5 on ≥ 4 of 5 traits.

Calibration: the paper's own Table 1 passes at exactly 4/5 on both legs —
Neuroticism fails both (2.73 < neutral 3.01 and < 3.5), the paper's documented
safety-suppression finding (Sec. 5.1). A broken implementation (scrambled template,
score not injected, flipped reverse-keying — which pulls keyed means toward or below
3) fails leg 1 and/or leg 2 on multiple traits.

## Deviations from the paper (all deliberate)

1. **Model: Alpaca-7B → microsoft/phi-4.** Table 1 was produced on Alpaca-7B, which
   is not served on Expected Parrot. Phi-4 is one of the paper's three main
   evaluation models and its overall *best* (Sec. 6, p.8), so trait expression
   should be at least as strong as the Alpaca-7B targets.
2. **Instrument: 1,000-item MPI → 12 BFI-2 items/domain × 10 reps.** Cost (mini-N);
   BFI-2 is a validated Big Five inventory on the same 1-5 scale. Honest caveat:
   our module's *low-pole* glosses paraphrase BFI-2 reverse-keyed items, a mild
   circularity — but the dialed condition tests the *high* pole, whose wording is
   verbatim paper text, so the headline direction is not circular.
3. **Prompt: all five traits stated (target 10, others 5) instead of the paper's
   target-only score 100/100 on n=100.** We validate the module *as production
   experiments use it*; others-held-at-neutral mirrors the paper's own proportional
   design (Sec. 4.2: other traits constant at neutral 50), and n=10 + simple prompt
   is the paper's best configuration (Sec. 6).
4. **Neutral baseline: all-5s persona instead of no prompt.** The correctness
   question for *our* implementation is whether moving the dial 5→10 moves measured
   expression — a no-prompt baseline would confound template presence with dial
   position. (Side effect: our neutral may differ from the paper's 3.97/3.61/...
   no-prompt values; criteria only use it as the within-run contrast.)
5. **Template addition (inherited from the module, documented in `__init__.py`):
   each trait line also describes the low pole.** Counters neuroticism suppression
   and defines low scores, which the paper's high-pole-only template leaves blank.
6. **max_tokens 2048 vs paper 512.** EDSL answers carry a comment field; the cap is
   a harness convention, not a behavioral knob. Temperature/top_p matched.

## How to run

```
.venv/bin/python -m personas.big5.replication          # dry run: design + cost
.venv/bin/python -m personas.big5.replication --run    # bills the API (~$0.05)
```

Writes `personas/big5/replication.json`; `tests/test_replications.py` asserts
`pass == true`.
