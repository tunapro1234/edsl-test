# CPC2010 — Technion Prediction Tournament (TPT) — Sources

Download date: 2026-06-11

## What this is
Erev, Ert & Roth (2010), "A choice prediction competition: Choices from experience
and from description", Journal of Behavioral Decision Making 23(1):15-47. Three
sub-competitions: decisions from description (under risk), decisions from sampling
(experience), and repeated decisions with feedback. Each has an estimation set and
a competition set.

## Original site status
The original competition site `http://tx.technion.ac.il/~erev/Comp/` is DEAD (the
live domain no longer serves it). All files below were recovered from the Internet
Archive Wayback Machine (snapshots 2011-08 for the HTML pages, 2013-10-04 for the
data zips / xls / baseline code), using `id_` raw-content URLs:
`http://web.archive.org/web/<timestamp>id_/<original-url>`.

## Files recovered

### raw_data/  (all verified with `unzip -t` = OK)
- `RawDecExpEst.zip` — 330 KB — 5 txt files, repeated-feedback estimation raw data (RawEstExp1-5Mar08.txt).
- `RawDecRiskEstComp08.zip` — 17 KB — DesEst_*.txt, decisions-from-description estimation set (20 problems).
- `RawDecSmpEst.zip` — 14 KB — RawEstSmp1-2Mar08.txt, sampling estimation raw data.
- `RawDesComp.zip` — 17 KB — DesComp_*.txt, decisions-from-description competition set.
- `RawExpCompMay08.zip` — 350 KB — ExpComp*_*.txt, repeated-feedback competition raw data.
- `RawSmpCompMay08.zip` — 31 KB — SmpComp*_*.txt, sampling competition raw data.
- `samplingcomp.xls` — 2.6 MB — sampling competition aggregated spreadsheet.
- `samplingest.xls` — 2.0 MB — sampling estimation aggregated spreadsheet.

Original URLs (prefix `http://tx.technion.ac.il/~erev/Comp/`):
RawDecExpEst.zip, RawDecRiskEstComp08.zip, RawDecSmpEst.zip, RawDesComp.zip,
RawExpCompMay08.zip, RawSmpCompMay08.zip, samplingcomp.xls, samplingest.xls

### baselines/  (example/baseline model code shared with the competition)
- `comp1CPTexample.sas` — 4.9 KB — Cumulative Prospect Theory baseline (SAS), description track.
- `comp1exlorsam example.sas` — 4.7 KB — explorative-sampling baseline (SAS).
- `comp1prisam example.sas` — 3.3 KB — primed-sampling baseline (SAS).
- `Comp_CPT_example.m` — 4.5 KB — CPT baseline (MATLAB).
- `comp_RE_example.sas` — 3.9 KB — reinforcement/RE baseline (SAS).

### site_pages/  (HTML for reference / problem definitions)
- `Comp.html`, `Estset.html`, `Compset.html`, `CompResults.html`, `Raw.html`

## License
No explicit license was stated on the original Technion site. Data is from a
published academic competition (Erev, Ert & Roth 2010); treat as research-use,
cite the paper.

## Not found / could not recover
- Some auxiliary HTML assets (gif/bmp equation images) were skipped as non-essential.
- No machine-readable consolidated CSV exists for TPT (the era's format was per-problem
  .txt files inside the zips). The .xls files are the closest to aggregated tables.
