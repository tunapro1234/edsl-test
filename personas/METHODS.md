# Persona Injection Methods — bake-off candidates

Goal: make our game agents behave like draws from the *general public*, then score every
method on the same games. Sources: `research/papers-to-read/` (41 papers, 11 read deeply),
`replicant/` (existing code), `replicant/notes/RESEARCH.md` (35-method landscape),
`research/ROADMAP.md` Step 2, `research/econ-traits.md`.

Selection constraints:
- prompt-side only for now (we call models via API → activation steering & fine-tuning are PARKED)
- every method must define a **P(persona) we can sample from** to mimic the public
- scorable on ROADMAP Step-1 metrics (treatment-effect fidelity > heterogeneity > covariate validity)

---

## A. Existing methods (literature + what we already have)

### Family 1 — Demographic conditioning
| id | Method | Mechanism | General-public sampling | Status |
|---|---|---|---|---|
| A1 | **Argyle silicon sampling** (paper 08) | first-person template from survey microdata rows: "Racially, I am X. I am Y..." | the founding move: P(V)=Σ P(V\|B)·P(B); take B rows from GSS/census so P(B) is correct even though the LLM's own prior isn't | GSS 2024 in `datasets/` |
| A2 | **Census-joint meta personas** (paper 14, tier 1) | demographics sampled from census JOINT distributions, zero LLM freeform | best-anchored tier; paper 14 shows every extra LLM-written layer adds leftward/positive bias | template trivial |

### Family 2 — Narrative backstory
| id | Method | Mechanism | General-public sampling | Status |
|---|---|---|---|---|
| A3 | **Anthology** (paper 01) | base-model "Tell me about yourself" → 10k backstories → estimate each one's demographics → bipartite-match to target population → prefix backstory | generate-then-match decouples generation from targeting; greedy matching beat Hungarian; +18% WD vs templates | ~10k backstories in `datasets/anthology/` |
| A4 | **Park fact-dense summary** (paper 02) | full interview transcript injection (85% GSS); ablation: bullet-point factual summary ≈ as good (0.84) | transcripts gated — only the *fact-dense, not stylistic* lesson transfers; econ games were its WEAKEST domain (0.66/0.38) | `datasets/genagents/` |

### Family 3 — Trait dials (numeric → text)
| id | Method | Mechanism | General-public sampling | Status |
|---|---|---|---|---|
| A5 | **Big5Scaler** (paper 17) | "Your openness score is 7 out of 10" + trait glosses; coarse scale (0-10) beats fine; short beats facet-level | sample OCEAN vectors from human norms (means/SDs/covariance); warning: Neuroticism suppressed by safety training; BFI factor-invalid in LLMs (paper 04) — include as *control*, expected weak | replicant has binary version (`personallm`) + Gaussian sampler (`sampling/big5.py`) |
| A6 | **GPS economic-preference profile** (ROADMAP #4) | Falk et al. 6 preferences (risk, patience, altruism, trust, ±reciprocity) + SVO as numeric dials in one template | THE economic option: GPS = 80k people, 76 countries (incl. Turkey), individual-level joint distribution downloadable → sample real preference vectors | data: register at briq; possibly underexplored = novelty |
| A7 | **Schwartz Value Anchor** (paper 03) | "Answer as a person that is [one of 19 values]" — single anchor → coherent persona; reproduces human value-circle structure | uniform-over-values ≠ human prevalence → reweight by human value distributions (Schwartz & Cieciuch N=53k) | prompt is one line |

### Family 4 — Theory-grounded discrete + calibration
| id | Method | Mechanism | General-public sampling | Status |
|---|---|---|---|---|
| A8 | **Homo Silicus one-liners** (paper 10) | "You only care about fairness between players" — preference types as single sentences | population = mixture over types | **already in replicant** (`ALLOCATION_PERSONAS`, `POLITICAL_PERSONAS`) |
| A9 | **GSA selection** (paper 41 §3) | fit mixture weights over discrete theory prompts to human data (simplex grid search) | weights ARE the population composition; calibrate on game A, validate on held-out game B | **already in replicant** (`calibrate.fit_weights`) |
| A10 | **GSA construction** (paper 41 App. A) | one template with numeric trait dials φ, Bayesian-optimized against human data | optimized φ* population (their frozen 1,000 agents from 10 level-k prompts) | one file away (skopt) |

### Family 5 — Identity grounding for long games
| id | Method | Mechanism | Use here | 
|---|---|---|---|
| A11 | **Real-respondent injection + VBN harness** (papers 11-data, 38) | demographics + the person's PAST ANSWERS in context; answer-time chain "values → beliefs → norms → choose"; +2-4% acc; naive CoT *hurts* | Twin-2K-500 in `datasets/` = 2,058 real people as a persona bank |
| A12 | **ID-RAG** (paper 27) | re-inject identity snippets every step against drift | relevant for who-to-punish (30 periods) — persona drift is real (paper 23: drift huge without countermeasures) |

### Family 6 — Population-level set calibration (orthogonal: applies ON TOP of any family)
| id | Method | Mechanism |
|---|---|---|
| A13 | **Population-aligned resampling** (paper 37) | probe every persona with a questionnaire via the LLM → importance-sample + optimal-transport the SET against a human reference distribution (1M-response IPIP); −38-50% distributional error vs all public pools; IS alone captures most of the gain |
| A14 | **Diversity hygiene** (paper 21) | MinHash + embedding dedup on the persona pool; PersonaHub itself = raw material only, anchored to nothing |

### Critiques to design around (papers 04, 06, 13, 14, 31, 32, 33, 35 + COO finding)
1. **Self-report ≠ behavior** — trait scores don't predict decisions; calibrate in *behavior* space.
2. **Individual-level accuracy <5%** in econ games — claim population level only.
3. **Persona noise distracts**: ONE irrelevant attribute flips 30-40% of predictions → inject only relevant dimensions.
4. **LLM-written personas are positive-sentiment biased** → would inflate giving/fairness in our games exactly where we measure.
5. **Prompt sensitivity** (Gupta): small rewording → big shifts → fix templates, vary content only.
6. Instruct/RLHF models collapse persona diversity (Anthology used base models) — relevant: our gpt-oss is reasoning-trained, the rational-corner problem.

---

## B. New ideas (ours — not in the literature as far as we know)

| id | Idea | Parents (cross-pollination) |
|---|---|---|
| B1 | **GPS-anchored narratives**: sample a real GPS preference vector → generate a backstory whose life events *imply* those preferences (risk-taking job changes, lending to friends...) → verify by re-surveying the backstory with the GPS module, estimate-then-match | A3 Anthology × A6 GPS |
| B2 | **Revealed-preference resampling**: paper 37's recipe but probe personas with cheap ONE-SHOT GAMES instead of questionnaires; resample the pool against Mei human game distributions; calibrate on split A of the battery, validate on held-out split B | A13 × Mei data × GSA bar — directly answers critique #1 |
| B3 | **Econ trait dials**: Big5Scaler format, economic parameters — φ = (CRRA, δ, β, Fehr-Schmidt α/β, SVO angle, level-k τ, noise λ); sample φ from published empirical distributions (Holt-Laury, Arad-Rubinstein level-k frequencies) | A5 format × A10 construction × `econ-traits.md` taxonomy |
| B4 | **Memory-as-persona**: don't *tell* traits — inject a fabricated personal HISTORY of past choices consistent with the trait ("in past games you typically contributed about half"). We already have history-in-scenario machinery (PD, who-to-punish). Counters "rhetoric ≠ strategy" (persona steering shifts talk, not play) and Park's facts>style finding | our PD mechanism × A4 × paper 33 |
| B5 | **Belief surgery**: bare models defect because they *believe* others defect. Split persona into preferences + first-order beliefs; inject calibrated human beliefs ("most people contribute about half") separately from values. VBN harness adapted to econ: background → values → beliefs about others → choose | A11 VBN × econ belief elicitation (`econ-traits.md` #17) |
| B6 | **QRE noise dial**: humans are noisy, bare models are deterministic (10/10 identical bomb-risk answers). Add decision-noise as an explicit dial ("you don't fully optimize") OR post-process choice probabilities toward quantal response with human-fitted λ | `econ-traits.md` compute family × our zero-variance findings |
| B7 | **Method-mixture population**: GSA selection logic one level up — population = mixture over METHODS {bare, GPS, narrative, ...}; fit mixture weights to human distributions; weights tell us *which persona family captures how much of the public*. Free: reuses all bake-off data | A9 applied at method level |
| B8 | **Sufficiency pre-pass**: before each game, LLM lists which persona dimensions drive behavior in THIS game; flag personas missing them (paper 15's question, our games). Tooling layer for the bake-off | paper 15 × `econ-traits.md` construct-coverage matrix |
| B9 | **GPS-Turkey population**: GPS includes Turkey → sample a Turkish general public, compare to world/US. Natural gift for the prof | A6 × prof angle |

---

## C. Games inventory (current + benchmark candidates)

### Implemented (experiments/, all verified on bare gpt-oss-120b)
| Game | Folder | Measures (econ-traits #) | Bare-model result |
|---|---|---|---|
| Dictator | 01 | altruism (6) | $0 |
| Ultimatum sweep + interaction | 02 | neg. reciprocity (10), fairness | accepts everything / offers low |
| Trust | 03 | trust (13), pos. reciprocity (9) | sends $0 |
| Public goods | 04 | cooperation, free-riding | contributes $0 |
| Prisoner's dilemma (5 rounds) | 05 | cooperation, strategic depth | always defects |
| Bomb risk (BRET) | 06 | risk preference (1) | exactly 50, zero variance |
| Who to punish (vote + punish) | 07 | punishment propensity (10), norm compliance (16), institution choice | votes human-like, never punishes, dismantles institution |

### Benchmark candidates (from `econ-traits.md` instruments; * = single-shot & cheap → ideal B2 probes)
- *Holt-Laury price list (risk, CRRA), *TK92 lottery battery (prob. weighting, loss aversion λ)
- *Time-choice lists / CTB (δ, β present bias)
- *11-20 game, *beauty contest (level-k τ) — also the GSA bridge
- *Die-roll honesty (Fischbacher), *SVO slider (Murphy), *Ellsberg urns (ambiguity)
- *Charness-Rabin allocation menus (already coded in replicant!)
- Gift exchange, money burning (spite), Niederle-Vesterlund (competitiveness), Krupka-Weber norms
- Mei human distributions = our marginal targets for the 6 shared games

### Benchmark folder idea (to discuss)
`benchmark/` = each game refactored to: standard agent interface in, standardized score out
(distance to Mei/GPS human distributions per game + treatment-effect direction checks).
Then methods × games = one matrix run.

---

## Proposed bake-off (Step 2 of ROADMAP, concretized)
Phase 1 (cheap, single-shot games): {bare, A1, A3, A5-control, A6, A7, A8} × {dictator, ultimatum, bomb risk, 11-20} × n=20.
Phase 2 (winners + B-ideas): add B3/B4/B5 hybrids, run interactive games (trust, PG, PD, who-to-punish).
Phase 3: A13/B2 set-level resampling on the best family; held-out validation (GSA bar).
