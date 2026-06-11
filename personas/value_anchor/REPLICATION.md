# value_anchor — paper replication

**Paper**: Rozen, Bezalel, Elidan, Globerson & Daniel, *Do LLMs have Consistent Values?*
(arXiv:2407.12878v3; local copy `research/papers-to-read/03-schwartz-values-llm.pdf`).
**Replicated effect**: §4.1 "Understanding Value Anchoring" (pp. 7–8) — *"anchoring on a
value not only increases the score the model assigns to the value … values that are close
to the anchored value (on the value circle, Figure 1) tend to receive high scores. On the
other hand, values that are far from the anchor receive consistently lower scores."*

## Design (mini)

| | paper | this replication |
|---|---|---|
| model | Llama 3.1 8B Instruct (one of six, p. 4) | same, via deep_infra (exact match) |
| temperature | 0.0 and 0.7 (p. 4) | 0.7 only |
| anchors | all 19 BWVr descriptions (p. 4, App. E p. 18) | 4 spread across the circle: stimulation, power-resources, security-personal, benevolence-caring |
| instrument | 57-item PVQ-RR, 3 items/value, batch (pp. 4–5) | the 19 BWVr descriptions themselves, 1 item/call (serial) |
| scale | 1 (Not like me at all) – 6 (Very much like me) (p. 4, Fig. 5 p. 17) | identical |
| N | 300 runs per prompt/model (p. 4) | 3 reps × 76 cells = 228 calls |
| analysis | mean-centered "anchored score curve", sine fit (Fig. 4 p. 9) | anchored value's own rating vs mean of the 3 circle-opposite values |

Prompt = the paper's verbatim Value Anchor wording (p. 4): *"For each of the following
descriptions, please answer how much the person described is like you from 1 (Not like me
at all) to 6 (Very much like me), without elaborating on your reasoning. Answer as a person
that is [value]."* followed by one description per call, framed with the paper's own
"a person that is [text]" phrase so the Appendix E texts stay verbatim.

## Paper targets (all read from the PDF)

1. **Anchored value scores highest; ~180°-away values lowest** — §4.1 pp. 7–8 ("As
   expected, the anchored value receives the highest score… values farther away (e.g., 180
   degrees apart) receive the lower values"), Fig. 4 p. 9.
2. **Magnitudes (context, not gated)** — Fig. 4 p. 9, read off the plot: peak ≈ +1.3 to
   +2.0 mean-centered at 0° for all models except Gemma-2-9B; trough ≈ −0.8 to −1.2 at
   ±150–180°. So own-minus-opposite gaps of ~2–3 points on the 6-point scale.
3. **Serial prompting validity** — Appendix H pp. 18–19: for Llama 3.1 8B, serial Value
   Anchor Spearman vs human ranking = **0.80** at both temperatures (Fig. 6 p. 19) and MDS
   SSD = 0.18 (Table 5 p. 19), ≈ batch (0.75/0.80 Spearman, Fig. 6 p. 19 batch rows —
   Table 1 p. 8 holds only the MDS SSDs, 0.18/0.16; main-text Fig. 2a prints 0.76/0.79
   for the same cell, but Fig. 6 is the Appendix-H batch-vs-serial comparison invoked
   here).
4. **Human benchmark means** (for the informational Spearman) — Table 2 p. 14, "Human
   Data" column (Schwartz & Cieciuch 2022, 49 cultural groups), acronyms via App. C p. 17.

## Pre-registered pass rule

> For ≥ 3 of 4 anchors, the anchored value's own mean rating exceeds the mean rating of
> its 3 circle-opposite values (offsets 9–11 on the 19-value circle, i.e. 151–171° away).

Defined in `replication.py` constants before any model call. Ordinal rather than
magnitude-based because mean-centered magnitudes from a 57-item PVQ-RR (Fig. 4) are not
comparable to a 19-item mini-instrument; the ordering own > opposite is the core §4.1
claim and would break under a scrambled anchor template or a swapped scale. It would
NOT catch a shuffled circle order: if anchoring works, the anchored value is the top
score (Fig. 4), so own > mean(any 3 other values) passes no matter which 3 `opposites()`
picks. The circle geometry is therefore pinned offline —
`tests/test_personas_offline.py::test_value_anchor_opposites_pinned` asserts all four
opposite sets (e.g. opposites("power-resources") == [benevolence-dependability,
benevolence-caring, universalism-concern]). The 3-of-4 margin tolerates one noisy
anchor at REPS=3.

## Deviations from the paper (all intentional)

1. **Instrument swap**: rating items are the 19 BWVr descriptions (App. E p. 18, items
   1–19) instead of the 57 PVQ-RR items — PVQ-RR items are not freely redistributable;
   the paper itself states the BWVr anchors "refer conceptually to the same values that
   are measured using the PVQ-RR" (p. 4). Consequence: 1 item/value instead of 3, and
   item wording = anchor wording (likeness ratings of the anchor's own text may be
   inflated — fine, the criterion compares within-run own vs opposite).
2. **Serial administration** (1 item/call) instead of batch (all 57 in one context) —
   EDSL's one-question-per-interview pattern; validated by the paper's own Appendix H
   (target 3 above).
3. **Mini-N**: 4 anchors (not 19) × 3 reps (not 300) — correctness check under the $1.5
   budget, not a study. The 4 anchors cover all four quadrants (openness,
   self-enhancement, conservation, self-transcendence).
4. **Temperature 0.7 only** — the paper's Llama-8B Value Anchor results are nearly
   identical at 0.0 vs 0.7 (Table 1 p. 8: MDS 0.18 vs 0.16); 0.7 makes the 3 reps
   informative rather than near-duplicates.
5. **No male/female questionnaire versions** (paper split runs 50/50, p. 4) — BWVr texts
   are ungendered.
6. **Power label swap** (module docstring): App. E pairs the power-dominance label with
   the money text and vice versa; we keep texts verbatim under standard codes. This
   shifts one member of the power-resources anchor's opposite set: index 5 (as
   implemented) gives {benevolence-dependability, benevolence-caring,
   universalism-concern}; the standard-circle position (index 6) would give
   {benevolence-caring, universalism-concern, universalism-nature}. Both variants are
   151–171° away (maximally distant), so the gate is unaffected.
7. **Informational Spearman vs human hierarchy** is reported but NOT gated: pooling 4
   uniform anchored runs (the paper pools all 19) over-weights power-resources, a value
   humans rank 18/19, so we expect a value below the paper's 0.80.

## Cost

228 calls × ~450 prompt + ~80 completion tokens on deep_infra Llama 3.1 8B
($0.02/$0.05 per 1M) ≈ **$0.003** — negligible.

## How to run

```
.venv/bin/python personas/value_anchor/replication.py        # dry run: design + cost
.venv/bin/python personas/value_anchor/replication.py --run  # real run, writes replication.json
```

`tests/run.py` then picks up `replication.json` via `tests/test_replications.py`.
