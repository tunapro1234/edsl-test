# anthology — paper replication (implementation-fidelity fallback)

**Paper:** Moon et al., *Virtual Personas for Language Models via an Anthology of
Backstories* (arXiv:2407.06576 v3, local PDF
`research/papers-to-read/01-anthology-narrative-backstory.pdf`, 34 pp.).

## Why not a Wasserstein replication

The paper's headline metric is the average Wasserstein distance (WD) between
LLM-persona and human answer distributions on Pew ATP survey questions
(Sec. 3 "Evaluation Criteria", p. 6). Reproducing even a mini version needs the
**human** per-question response marginals. They are not local:

- the paper repo clone (`research/datasets/anthology/`) ships only question
  texts (`data/questions/`, `configs/*/questionnaire/ATP/`) and *demographic*
  marginals for matching (`configs/demographic_filtering/human_survey_data/`);
- `human_data_path:` is empty in `configs/analysis/questionnaire/ATP/ATP_W34.yaml`
  — the actual ATP W34 microdata must be fetched from Pew (registration-gated).

So this replication is an **implementation-fidelity check** of the one pipeline
step we re-implemented ourselves, not a reproduction of the WD table.

## Claim being checked

The paper estimates each backstory's demographics with an LLM before matching
personas to the target population (Sec. 2.3, p. 4). For age specifically, App.
F.1 (p. 31): "we use GPT-4o to locate demographic information from the
backstory … prompt GPT-4o to retrieve the demographic trait only if the
backstory explicitly mentions related context … Decoding hyperparameters are
set to top_p = 1.0, T = 0." Our `prep.py` replaced that LLM step with regex age
extraction and built the age-stratified pool `backstories.json`. **If the
regexes and bracket boundaries are right, the paper's own locating instrument,
run over our pool, must reproduce the brackets prep.py assigned.** A scrambled
pool, broken regex, or off-by-one bracket edges would systematically disagree.

## Paper targets (every number read from the PDF)

| target | value | where in the paper |
|---|---|---|
| Anthology (NA, greedy) WD, Llama-3-70B base, ATP W34 | **0.227** | Table 1, p. 7 (also quoted in Sec. 4.2 text, p. 7: "the average Wasserstein distance for Anthology in the ATP Wave 34 survey is 0.227"). Context anchor — needs Pew microdata. |
| Anthology (NA, max weight) WD, same setting | 0.229 | Table 1, p. 7 |
| Anthology (NA, greedy) WD, Llama-3-70B-**Instruct**, ATP W34 | **0.413** | Table 4 (App. A.2), p. 16. Known direction of the instruct deviation: fine-tuning nearly doubles WD; A.2 (p. 15): "none of the fine-tuned models show better metrics in both Representativeness and Consistency criteria." |
| age-locating instrument | Fig. 17 prompt, options (A) 18-29 (B) 30-49 (C) 50-64 (D) 65 or Above (E) Was not mentioned | App. F.2, p. 32; applied at T=0, top_p=1.0 (App. F.1, p. 31) |
| age brackets used throughout | 18-29 / 30-49 / 50-64 / 65+ | Fig. 17 (p. 32), Fig. 18 (p. 33), Table 6 (p. 34) |
| pool young-skew the matching corrects | Anthology age shares 42.5 / 36.5 / 13.3 / 7.7 vs Census 17.8 / 34.2 / 25.3 / 22.7 | Table 6 + App. F.4, p. 34 — corroborates prep.py's finding (58% of extractable stories read 18-29), which is why our pool is age-stratified at all |
| pre-registered local target | bracket agreement >= **0.80** | ours, not the paper's — fixed in `replication.py:TARGETS` before any results exist |

## Design

Stratified sample of 6 stories per bracket × 4 brackets = 24 stories from
`backstories.json` (seed 7, fixed). Each story's text is shown once to
`deep_infra/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` at **temperature 0**
(matching the paper's locating step) with the Fig. 17 age question as an EDSL
`QuestionMultipleChoice` (options verbatim). Score = share of the 24 whose
answer maps to the bracket prep.py assigned; "Was not mentioned" or a blank
answer counts as a miss.

**Pre-registered pass criterion:** agreement >= 0.80 (allows 4 misses of 24 for
instrument quirks/genuinely hard phrasings; a scrambled pool would score near
the 25% chance level, and even a one-bracket systematic shift in the regex
boundaries would fail the 18-29 or 65+ rows wholesale).

**Eligibility rule (pre-registered, in code):** stories whose *only* age
evidence is a decade phrase that prep.py maps onto a bracket boundary are
excluded from sampling — "in my 60s" → midpoint 65 (50-64/65+ edge) and "in my
teens" → 18. For these, the true bracket is undefined, so they cannot serve as
ground truth either way. This drops 6 of 610 stories; all other decade phrases
("in my 40s" → 45 etc.) map strictly inside a bracket and stay eligible.

Calls: 24 × 1 rep = **24**. Cost: ~750 prompt + ~80 completion tokens per call
at $0.40/$0.40 per 1M → **≈ $0.008**.

## Deviations from the paper

1. **Fidelity check, not WD reproduction.** Human ATP marginals are not local
   (see above). The WD numbers in `paper_targets` are context anchors only;
   the testable criterion is the agreement floor.
2. **Locator model: GPT-4o → Llama-3.1-70B-Instruct-Turbo.** Spec-mandated;
   keeps the paper's main model family (Llama-3-70B). The instruct penalty the
   paper documents (Table 4: WD 0.227 → 0.413) is about *opinion expression*
   under persona conditioning; locating an explicitly stated age is a retrieval
   task where instruction tuning helps. We are replicating the paper's Step 2
   instrument, which the paper itself runs on an instruction-tuned model
   (GPT-4o), so an instruct model is the faithful choice here.
3. **Answer format.** The paper's Fig. 17 prompt asks for evidence first, then
   a letter answer parsed from free text. EDSL's `QuestionMultipleChoice`
   structures the choice and routes the evidence into its comment field; option
   strings are verbatim. (EDSL also doesn't randomize option order; the paper
   randomizes ordinal options, App. A.1, p. 15 — irrelevant at N=24 with T=0.)
4. **Mini-N.** 24 stories, 1 rep each, vs. the paper surveying all ~10k
   backstories (40 samples/question for the sampling variant, App. F.3, p. 33;
   1 deterministic call for the locating variant we mirror). Cost control;
   this is a correctness check, not a study.
5. **Regex stands in for the LLM survey in prep.py itself.** That is the very
   deviation this replication audits; full LLM survey + 5-variable greedy
   matching is stage 2 (`demographic_survey.py`, see NOTES.md).
