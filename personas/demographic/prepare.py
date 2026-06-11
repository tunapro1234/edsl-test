"""One-time prep: GSS 2024 microdata -> gss_sample.csv for the demographic method.

Reads the GSS 1972-2024 cumulative Stata file (NORC public-use data,
research/datasets/gss/gss7224_r3.dta), keeps the 2024 wave (N=3,309 — matches
"3,309 GSS Core completes", GSS 2024 Codebook R3, Weights section), selects the
16 persona variables plus the survey weight, and writes one small CSV that the
module reads with stdlib csv at runtime.

Weight: WTSSNRPS. The codebook says WTSSPS/WTSSNRPS are the recommended
weights and "for years where WTSSNRPS is available, NORC recommends data users
use WTSSNRPS" (GSS 2024 Codebook R3, Weights section). Sampling rows with this
weight makes the silicon sample represent the US adult population, not just
the raw respondent pool.

Missing values stay as empty strings; the module omits those fragments, which
is exactly Argyle et al.'s rule ("If any variable for any subject was missing,
the corresponding template fragment was omitted", paper 08, App. C.1).

Needs pandas (the edsl .venv has none) — run with system python3:
    python3 personas/demographic/prepare.py [optional path to gss7224_r3.dta]
pandas warns about a latin-1 decoding fallback; that concerns other string
columns in the 575MB file, not our value labels (spot-checked, all clean).
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DEFAULT_DTA = os.path.join(os.path.dirname(REPO), "research", "datasets", "gss", "gss7224_r3.dta")
OUT = os.path.join(HERE, "gss_sample.csv")

YEAR = 2024
COLUMNS = ["year", "id", "age", "sex", "race", "hispanic", "born", "degree",
           "marital", "childs", "wrkstat", "income16", "class", "relig",
           "attend", "partyid", "polviews", "region", "wtssnrps"]


def tidy(v):
    """Category label -> plain string; NaN -> ''; numeric labels -> int string."""
    if pd.isna(v):
        return ""
    if isinstance(v, float):          # age/childs categories like 64.0
        return str(int(v))
    return str(v).strip()


def main():
    dta = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DTA
    df = pd.read_stata(dta, columns=COLUMNS, convert_categoricals=True)
    df = df[df["year"] == YEAR].copy()
    print(f"GSS {YEAR} rows: {len(df)}")

    out = pd.DataFrame()
    out["id"] = df["id"].astype(int)
    for col in COLUMNS:
        if col in ("year", "id", "wtssnrps"):
            continue
        out[col] = df[col].map(tidy)
    out["age"] = out["age"].replace({"89 or older": "89+"})
    out["childs"] = out["childs"].replace({"8 or more": "8+"})
    out["weight"] = pd.to_numeric(df["wtssnrps"]).round(4)

    out = out.sort_values("id")
    out.to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(out)} rows)")
    print("weighted female share:",
          round(out.loc[out.sex == "female", "weight"].sum() / out.weight.sum(), 3))


if __name__ == "__main__":
    main()
