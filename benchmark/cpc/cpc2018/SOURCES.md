# CPC2018 — Sources

Download date: 2026-06-11

## What CPC2018 is
Choice Prediction Competition 2018 (cpc-18.com). 270/210 risky-choice problems,
two tracks (Track I: aggregate choice rates per block; Track II: individual data).
Won by BEAST-GB (Plonsky & Apel et al.). Materials originally hosted at
cpc-18.com (= cpc18.wordpress.com).

## Files downloaded

- `cpc18-white-paper-march-update.pdf` — 772 KB, 34 pages
  - URL: https://cpc-18.com/wp-content/uploads/2018/03/cpc18-white-paper-march-update.pdf
- `cpc18-all-210-problems-detailed-distributions-aggregate-results.xlsx` — 228 KB
  - URL: https://cpc-18.com/wp-content/uploads/2018/06/cpc18-all-210-problems-detailed-distributions-aggregate-results.xlsx
  - All 210 calibration problems with full outcome distributions for both options and
    aggregate choice rates across the five 5-trial blocks.
- `all CPC18 raw data.csv` — 63 MB, 694,500 observations (694,501 lines incl. header)
  - URL: https://zenodo.org/api/records/2571510/files/all%20CPC18%20raw%20data.csv/content
  - DOI: 10.5281/zenodo.2571510 — License: CC-BY-4.0
  - Title: "All raw data for CPC18: Choice prediction competition 2018". This is the
    FULL dataset = estimation set (510,750 obs) + the competition/test set released
    after the competition. Same `Set` column distinguishes them.
- `Dictionary for the choice prediction competition 2018 raw data.pdf` — 195 KB
  - URL: https://zenodo.org/api/records/2571510/files/Dictionary%20for%20the%20choice%20prediction%20competition%202018%20raw%20data.pdf/content
  - (Identical dictionary file as in cpc2015/, kept here too for self-containment.)

## Notes
- The estimation-only set (problems 1-210, 510,750 obs) lives in `../cpc2015/All estimation raw data.csv`
  (Zenodo 845873). The combined estimation+competition data is the 2571510 record here.
- Baseline model code (BEAST.sd, PsychForest, Track II) is in `../algorithms/cpc18-official-baselines/`.
- The cpc-18.com "Data" page links only to the Zenodo records and the XLSX above; no
  separate hidden competition CSV is published beyond what is in the 2571510 record
  (the competition/test rows are merged into "all CPC18 raw data.csv").

## Not found
- A standalone "competition set only" CSV is not published separately; it is included
  inside `all CPC18 raw data.csv` (distinguished by the Set/Condition columns).
