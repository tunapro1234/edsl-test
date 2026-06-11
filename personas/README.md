# personas/ — conventions (the bake-off contract)

Every method folder exposes `sample(n, seed) -> list[str]`:
- deterministic for a fixed seed; no network and stdlib-only at import/runtime
  (heavy prep lives in a per-folder `prepare.py`/`prep.py`, run once, output committed)
- persona text is prepended to EVERY game question via `{{ scenario.persona }}`
  (so each player keeps their persona for the whole game — drift countermeasure built in)
- second-person framing ("You ...") so the text reads as the player's identity
- closing lines and prefixes follow each method's SOURCE PAPER, not a house style:
  big5 ends "you are an agent with this personality" (Big5-Scaler verbatim),
  homo_silicus carries GSA's humanizing prefix (part of THAT method's recipe).
  These differences are method-inherent, not confounds to be equalized.
- groups: methods sample n DISTINCT people where the source is a real pool
  (demographic, twin2k, anthology); mixture methods use quota (homo_silicus) or
  balanced (construction) assignment — documented in each module docstring.
- A2 (census-joint) is implemented inside `demographic/` — GSS microdata rows ARE
  a real joint distribution; no separate module.

## Harness floor
Only who-to-punish runs at/after commit `15b9531` (max_tokens=8192 + raise-on-None)
count for cross-method comparison. Earlier runs fabricated $0 for failed interviews
(None→$0) — their late periods are poisoned; see each NOTES.md.
Decoding parameters are a behavioral treatment: the bare model punishes free-riders
at max_tokens=8192 but never did at the default cap (see the baseline ANALYSIS.md).

## Where things are
- `METHODS.md` — the method survey (A-family = literature, B-family = our ideas)
- `ROADMAP.md` — status + the B-family backlog
- `<method>/NOTES.md` — per-method provenance, decisions, and run results
- `experiments/07_who_to_punish/compare.py` — uniform cross-method results table
- Calibrations: `homo_silicus/calibrate.py` (CR menus, 420 interviews),
  `construction/calibrate.py` (CR grid, 1,860) — never trust in-sample MAE over
  held-out validation (winner's curse at low REPS; see docstrings).
