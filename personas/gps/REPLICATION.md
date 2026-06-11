# GPS replication — instrument fidelity

**What this is NOT:** a replication of a published LLM result. The GPS source —
Falk, Becker, Dohmen, Enke, Huffman & Sunde, "Global Evidence on Economic
Preferences" (QJE 2018; NBER WP 23943) — is human survey data; nobody ran it
through an LLM. **What we claim instead:** our persona sampler reproduces the
published statistics it is built on (offline), and the persona text it renders
is readable and binding for a model (LLM readback probe). All page numbers
below are the WP's printed page numbers, verified directly against
https://www.nber.org/system/files/working_papers/w23943/w23943.pdf.

## Part 1 — offline distribution checks (free)

200,000 joint draws from the sampler, compared against:

| target | value | source (verified in the PDF) |
|---|---|---|
| 15 pairwise correlations | 0.210 (patience~risk), 0.084, 0.112, 0.098, 0.044, 0.068 (risk~posrec), 0.228, 0.106, 0.047, 0.010 (posrec~negrec), 0.329, 0.114, 0.067 (negrec~altruism), 0.075, 0.151 (altruism~trust) | WP Appendix C, **Table 12, p. 62** ("Partial correlations between preferences at individual level conditional on country fixed effects"; all marked \*\*\* p<0.01) |
| latent traits mean 0, sd 1 | 0 / 1 per trait | WP **p. 60, Fig. 10 caption**: "All data are standardized at the level of the individual in the full sample" (same standardization as QJE 2018 p. 1653) |
| answer clipping rare | < 2% (expected 1.24%) | NOT a paper number — follows from OUR documented z→round(5+2z) mapping (`__init__.py`); clips iff \|z\|>2.5 |
| determinism | sample(n, seed) reproducible | our requirement, not the paper's |

Pass thresholds (pre-registered in `replication.py` before any results): worst
correlation gap < 0.01, worst \|mean\| < 0.02, worst \|sd−1\| < 0.02, clip
rate < 2%, deterministic. A scrambled correlation matrix or broken Cholesky
fails the gap check; a broken answer mapping fails the clip check.

## Part 2 — LLM readback probe (--run, real billing)

6 personas (seed 27) × 2 verbatim GPS items × 3 reps = **36 calls** on
`meta-llama/Meta-Llama-3.1-8B-Instruct` (deep_infra), est. **$0.0008**.
EDSL pattern copied from `personas/homo_silicus/calibrate.py`
(QuestionLinearScale + ScenarioList + `.by(model).run(n=REPS)`; persona in a
scenario field).

Items re-asked, verbatim from the paper (and from the persona's own lines):

- **Risk** — "Please tell me, in general, how willing or unwilling you are to
  take risks." + its own 0–10 anchors: WP **A.6.2, p. 51**.
- **Trust** — "I assume that people have only the best intentions.", a
  self-assessment under the intro "How well do the following statements
  describe you as a person? … 0 means 'does not describe me at all' … 10 means
  'describes me perfectly'": item WP **A.6.6, p. 54**; intro wording WP
  **A.6, p. 50**. Trust is the GPS's single-item preference, so the persona's
  stated dial maps 1:1 to the re-asked item.

The persona text literally contains each answer ("— your answer: 7 …"), so a
model that reads the injection should echo the dial back. Pre-registered pass
criteria:

1. ≥ 75% of the 36 probes within ±2 of the persona's stated dial
   (None/failed answers count as misses), **and**
2. correlation(stated dial, mean answer per persona×item cell) ≥ 0.5.

Criterion 2 exists because criterion 1 alone is gameable: seed 27's dials are
risk [2,6,8,2,8,6] / trust [7,4,2,5,3,4], and a persona-ignoring model that
always answers "4" would hit exactly 75% — but its dial correlation is 0, so
it fails. A faithful reader with ±1 noise scores ~1.0 share and r≈0.99
(simulated in the local checks); a scrambled template (answering 10−dial)
scores 0.42 / r=−1.

## Deviations from the paper (all of them)

1. **No LLM target exists** — the paper is human data; "pass" certifies our
   implementation, not agreement with a published LLM experiment.
2. **Composite vs item correlations** — Table 12 correlates the *composite*
   preference measures (qualitative + quantitative items, A.9 weights, p. 59);
   our sampler applies that structure to qualitative-item z-scores. Inherited,
   documented assumption of `__init__.py`.
3. **z→0–10 mapping is ours** — round(5+2z) clipped; the paper does not
   publish raw item distributions. The 2% clip threshold tests our mapping's
   internal consistency, not a paper statistic.
4. **Model choice is arbitrary** (no paper model to match):
   Llama-3.1-8B-Instruct picked as the cheapest verified instruct model — also
   a *harder* test: if an 8B model can read the dial back, the injection is
   legible.
5. **Mini-N** — 6 personas × 2 of the 8 qualitative items × 3 reps; cost
   control. Risk and trust chosen because each has unambiguous own anchors and
   trust is single-item (no within-preference ambiguity).
6. **Seed 27 selected for dial spread** — selection on *inputs* (persona
   dials), fixed before any model output, to defeat constant-answer passes;
   see criterion 2 above.
7. **Item framing** — items asked through EDSL's QuestionLinearScale wrapper;
   the A.6 scale introductions are condensed into one sentence each (anchor
   wordings kept verbatim).

## How to run

```
.venv/bin/python personas/gps/replication.py        # design + cost, no billing
.venv/bin/python personas/gps/replication.py --run  # ~$0.001, writes replication.json
```

`tests/test_replications.py::test_replication_gps` asserts the artifact's
`pass == true`.
