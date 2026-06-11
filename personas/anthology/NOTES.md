# Anthology (A3) — implementation notes

## Data provenance (all verified locally)
- Backstory texts: HF dataset `SuhongMoon/anthology_backstory` (linked from the
  paper repo README, `research/datasets/anthology/README.md`). One file,
  `anthology_backstory_list.json`, 24.6 MB, **11,364** strings of the form
  `"Question: <interview q>\n\nAnswer: <life story>"`. Two question variants
  (6,240 standard / 5,124 with "Please describe in detail."). davinci-002
  completions at T=1.0 (paper App. B.1). The repo clone in
  `research/datasets/anthology/` contains **no** backstory texts — only code
  and ATP question configs.
- Age targets: GSS 2024 (`research/datasets/gss/gss7224_r3.dta`, year==2024,
  n=3,208 with age, weighted by `wtssps`): 18-29 20.1%, 30-49 33.8%,
  50-64 23.7%, 65+ 22.4%. Recompute: `prep.py --gss` (needs pandas — use
  `research/datasets/.venv/bin/python`).

## Pipeline fidelity vs the paper (arXiv:2407.06576)
| Paper step | Here |
|---|---|
| 1. Generate backstories (davinci-002, T=1) | use their released anthology unchanged |
| 2. LLM demographic survey per story (App. F) | stage 1: regex age extraction (40% coverage, spot-checked); stage 2: `demographic_survey.py` (real EP job, paper-verbatim ATP questions) |
| 3. Greedy matching to target population (Sec. 2.4) | stage 1: age-stratified draws against GSS 2024 shares; stage 2 enables full 5-variable greedy matching to GSS rows |
| 4. Prefix backstory (+ matched demographics) to every question | persona text = original `Question:/Answer:` block + one bridging line (see below); games re-prepend it on every question, which also counters persona drift over the 6-period game (2 votes x 3 periods) |

## Why stratify by age (the one local deviation that MATTERS)
The raw pool is wildly young-skewed: of the 4,568 stories with an extractable
age, 58% read as 18-29 and only 0.7% as 65+ (US adults: 20% / 22%). The paper
itself flags the young-skew (Sec. 4.2) and corrects demographics via matching.
Uniform draws would simulate a college sample, not the public.

## Other deliberate choices
- **Instruct-model bridge.** The paper conditions BASE models by raw prefix
  continuation and shows instruct models do worse (App. A.2, Table 4 —
  Llama-3-70B-Instruct Anthology NA/greedy WD on ATP W34 = 0.413 vs base
  Llama-3-70B 0.227; gpt-oss-120b is instruction-tuned, so this is our main
  risk). Mitigation: keep the paper's literal `Question:/Answer:` block but
  add one line telling the model it IS that person and must decide as they
  would.
- **Filters** (prep.py): 33 placeholder/meta texts (e.g. "[city] [state]",
  "(see above)"), 9 stories under 50 words (paper repo drops <=40 tokens, see
  `anthology/backstory/backstory.py`), mid-sentence endings trimmed to the
  last sentence boundary (532 affected). No length cap: median story is ~300
  words; the paper treats length as signal.
- **Pool cap** 200/bracket (65+ has only 32) -> 626 stories, 1.49 MB,
  md5 `bea18fd48c3764b172894be391721fd7` with PREP_SEED=0. Within-bracket
  draws are without replacement; reuse after exhaustion mirrors the paper's
  greedy matching (many humans -> one story is allowed there too).
- **No demographics appended yet**: the paper appends the MATCHED human's
  demographics after the backstory. Appending unmatched GSS rows could
  contradict the story (age clash), so stage 1 sends the story alone.

## Stage 2 (main agent, costs money)
`demographic_survey.py` dry-run: 626 stories x 5 questions x 3 samples =
9,390 calls, ~6.7M input + ~0.6M output tokens. Check against EP pricing
(price_audit.py) before `--run`. Then: greedy-match stories to GSS 2024 rows
on all five variables and append matched demographics in the paper's Bio
format — that is the full-fidelity Anthology (NA, greedy), its best
configuration (Table 1: WD 0.227 vs 0.254 for demographic templates).

## Who-to-punish v1 run (seed 1, clean) — 2026-06-11_15-37-18
- BOTH votes banned ALL punishment — narrative-backstory people are too prosocial to
  legalize sanctions (paper 14's positive-sentiment bias, live).
- Contributions: the classic NO-punishment VCM decay, start high → unravel:
  means 9.25 / 9.25 / 7.5 / 5.0 / 5.0 / 2.5 as defectors (B p3, C p4, D p6) go
  unpunished. The most human-like *no-sanctions* trajectory of any method; the
  institutional choice itself is the anti-human part (humans adopt punish-low).
