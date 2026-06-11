# Algorithms — Sources

Download date: 2026-06-11

Model implementations for the choice-prediction competitions.

## cpc18-official-baselines/
The official CPC18 baseline model code (BEAST.sd, Psychological Forest, Track II).
These were hosted on the (now login-walled / decommissioned classic) Google Site
`https://sites.google.com/site/baselinemodelsexamples/`. The live links now return
a Google sign-in HTML page, NOT the zip. All 9 archives were recovered from the
Internet Archive Wayback Machine (snapshot 2020-10-22) via the
`aad53b62-a-...sites.googlegroups.com` attachment URLs. All verified with `unzip -t` = OK.

| File | Size | Contents |
|------|------|----------|
| CPC18_BEASTsd_Python.zip | 13 KB | BEAST.sd reference impl (Python): pred, simulation, EstSet.csv, getDist, distSample, Readme |
| CPC18_BEASTsd_Matlab.zip | 23 KB | BEAST.sd (MATLAB) + EstSet .mat files |
| CPC18_BEASTsd_R.zip | 30 KB | BEAST.sd (R) + EstSet/full-dist CSVs |
| CPC18_BEASTsd_SAS.zip | 38 KB | BEAST.sd (SAS) + .sas7bdat datasets |
| CPC18_PsychForest_Python.zip | 49 KB | Psychological Forest (Python) + TrainData.csv, TrainData210.csv, feature eng |
| CPC18_PsychForest_Matlab.zip | 71 KB | Psychological Forest (MATLAB) + PF_TrainSet .mat |
| CPC18_PsychForest_R.zip | 64 KB | Psychological Forest (R) + PF_TrainSet .RData |
| CPC18_Track2_Python.zip | 669 KB | Track II baseline (Python) + individualBlockAvgs.csv (~15 MB unzipped) |
| CPC18_Track2_R.zip | 669 KB | Track II baseline (R) + individualBlockAvgs.csv |

Original (dead) URL pattern:
`https://sites.google.com/site/baselinemodelsexamples/CPC18%20<name>.zip?attredirects=0&d=1`
Recovered via: `http://web.archive.org/web/2020/<that-url>`

License: not stated on the source site; academic competition baseline code, cite
Erev et al. (2017) for BEAST / Plonsky & Erev (2017) for Psychological Forest.

## beast-gb/
BEAST-GB (BEAST gradient boosting), the CPC18-winning hybrid model.
Plonsky, Apel et al., "Predicting human decisions with behavioural theories and
machine learning", Nature Human Behaviour (2025), DOI 10.1038/s41562-025-02267-6.
Materials on OSF project "vw2su" (DOI 10.17605/OSF.IO/VW2SU).

| File | Size | Source |
|------|------|--------|
| BEAST_GB demo code.zip | 79 KB | https://osf.io/download/2nfwk/ — BEAST_GB.R, CPC18_data.csv, "funcs for feature engineering.R", README.pdf (verified unzip OK) |
| Figures.R | 25 KB | https://osf.io/download/7tc3s/ |
| tSNE for all tasks.R | 1.7 KB | https://osf.io/download/y26ve/ |
| feature labels.csv | 3.1 KB | https://osf.io/download/yk7th/ |

NOT downloaded (over the 2 GB bandwidth cap):
- `Replication package BEAST-GB R1.zip` — 2.20 GB — https://osf.io/download/2h9rx/
  (full replication package; the demo code zip above is the practical self-contained
  implementation). Also skipped: `data for tSNE.RData` (364 KB) and the "Figures" /
  "Extensive form games" OSF subfolders (figure assets, not model code).

License: OSF project; cite the Nature Human Behaviour paper.

## Not found
- No standalone public GitHub repo for BEAST-GB was found (searched GitHub repos +
  Plonsky's site + the paper). The canonical release is the OSF project above.
- A pip-installable BEAST behavior-modeling package exists separately
  (`ofiryakobi/debm` on GitHub, "Decision from Experience Behavior Modeling") but is
  a general DfE toolbox, not the CPC18 BEAST-GB code; not cloned here.
