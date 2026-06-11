# CPC2015 — Sources

Download date: 2026-06-11

## What CPC2015 is
The Choice Prediction Competition 2015 (Erev, Ert, Plonsky, Cohen & Cohen, "From
anomalies to forecasts", Psych Review 2017). Decisions under risk, ambiguity, and
from experience. 270 problems (estimation + competition sets), 5 feedback blocks.

## Files downloaded

### Top level (Zenodo record 845873 — "Calibration Data for CPC18", which IS the CPC15+ext estimation set)
- `All estimation raw data.csv` — 46 MB, 510,750 observations (header + 510,750 rows = 510,751 lines).
  - URL: https://zenodo.org/api/records/845873/files/All%20estimation%20raw%20data.csv/content
  - DOI: 10.5281/zenodo.845873 — License: CC-BY-4.0
  - This is the combined estimation set used for CPC18 (CPC15 problems 1-150 + Experiment-1 problems 151-210). Matches the "510,750 observations" target.
- `Dictionary for the choice prediction competition 2018 raw data.pdf` — 195 KB
  - URL: https://zenodo.org/api/records/845873/files/Dictionary%20for%20the%20choice%20prediction%20competition%202018%20raw%20data.pdf/content
  - Column dictionary for the raw-data CSVs (SubjID, Ha, pHa, La, LotShape, Feedback, block, etc.).

### zenodo321652_cpc15_original/  (Zenodo record 321652 — the original CPC2015 raw data, 3 experiments)
- `RawDataExperiment1sorted.csv` — 7.3 MB
- `RawDataExperiment2sorted.csv` — 10 MB
- `RawDataExperiment3.csv` — 11 MB
  - URLs: https://zenodo.org/api/records/321652/files/<name>/content
  - DOI: 10.5281/zenodo.321652 — License: CC-BY-4.0
  - Title: "Raw data for CPC2015: A Choice Prediction Competition for decisions under
    risk, under Ambiguity, and from experience". These are the three source
    experiments behind the 2015 competition.

## Verification
All CSVs open with a valid header row (SubjID,Location,Gender,Age,...). The
`All estimation raw data.csv` row count = 510,751 lines = 510,750 observations, as expected.

## Notes / not found
- The official CPC2015 competition site (http://departments.agri.huji.ac.il/cpc2015)
  was not scraped for additional files; the canonical raw data is the Zenodo
  records above (both CC-BY-4.0).
