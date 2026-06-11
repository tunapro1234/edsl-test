# personas/ roadmap

## Now: implement the EXISTING methods (A-family from METHODS.md), one by one

One folder per method, each exposing `sample(n, seed) -> list[str]` (persona texts);
`personas/__init__.py` is the selection API (`from personas import sample_personas`).
Verification per method: sampling sanity check, then a full who-to-punish run with 4
sampled personas (results land in `experiments/07_who_to_punish/results/<ts>_<method>/`).

| Folder | Method | Status |
|---|---|---|
| `baseline/` | empty persona (control) | done |
| `homo_silicus/` | A8 one-liners + A9 Horton mixture sampling | done |
| `big5/` | A5 numeric dials from population norms | done |
| `value_anchor/` | A7 Schwartz value anchor | done |
| `gps/` | A6 Falk 6 preferences + SVO dials | done (placeholder marginals) |
| `construction/` | A10 GSA-style generic trait dials | in progress |
| `demographic/` | A1/A2 Argyle template from GSS microdata rows | planned |
| `anthology/` | A3 narrative backstories from dataset | planned |
| `twin2k/` | A11 real-person summaries from Twin-2K-500 | planned |

Parked from A-family: A4 (Park transcripts gated), A12 (EDSL re-injects persona every
question anyway — drift countermeasure is free), A13/A14 (set-level calibration needs
probe data from the bake-off first).

## Later: the NEW ideas (B-family) — to develop together

| id | Idea | One-line | Parents |
|---|---|---|---|
| B1 | GPS-anchored narratives | backstory whose life events *imply* a sampled GPS preference vector; verify by re-surveying the text | Anthology × GPS |
| B2 | Revealed-preference resampling | set-level calibration (IS+OT) probed with cheap one-shot GAMES against Mei human distributions, validate held-out | pop-aligned × Mei × GSA bar |
| B3 | Econ trait dials | Big5Scaler format with φ = (CRRA, δ, β, Fehr-Schmidt α/β, SVO, level-k, noise λ) sampled from published empirical distributions | Big5Scaler × GSA construction × econ-traits.md |
| B4 | Memory-as-persona | inject fabricated choice HISTORY consistent with the trait instead of trait labels; reuses our history-in-scenario machinery | PD mechanism × Park facts>style |
| B5 | Belief surgery | separate preferences from first-order beliefs; inject calibrated human beliefs ("most people contribute about half") | VBN × belief elicitation |
| B6 | QRE noise dial | explicit decision-noise instruction or post-hoc quantal-response softening with human-fitted λ | econ-traits compute × our zero-variance findings |
| B7 | Method-mixture population | fit mixture weights over METHODS to human data; weights = how much of the public each family captures | GSA selection, one level up |
| B8 | Sufficiency pre-pass | per game, LLM lists which persona dimensions matter; flag underdetermined personas | paper 15 × construct-coverage matrix |
| B9 | GPS-Turkey population | sample a Turkish general public from GPS Turkey data; compare to world/US | GPS × prof angle |

## General-public requirement (applies to every method)

A method is only bake-off-ready when its `sample()` draws from a defensible
approximation of the general public's distribution — real microdata rows where
available (GSS, GPS, Twin-2K), published norms otherwise, with the source noted
in the module docstring. Uniform-over-types is a placeholder, never a claim.
