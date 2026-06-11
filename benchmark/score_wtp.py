"""Score who-to-punish runs against the Ertan-Page-Putterman human benchmarks.

Reads every experiments/07_who_to_punish/results/<ts>_<method>/ run (summary.txt
+ saved punish-stage data) and scores 9 criteria, each 0-1, weighted into one
human-likeness index. Criteria and weights follow ROADMAP Step-1 metrics:
institutional/treatment fidelity first, levels and spread second.

Targets come from benchmark/human_targets.json (extracted from the paper by a
verified agent pass); inline defaults document each number's meaning.

Run:  .venv/bin/python benchmark/score_wtp.py [--since 15-00] [--csv out.csv]
"""

import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "experiments", "07_who_to_punish", "results")
ENDOWMENT = 10

# (name, weight) — weights: 3 = institutional/treatment (primary),
# 2 = behavioral mechanics, 1 = distributional shape
CRITERIA = [
    ("never_punish_high", 3),   # Ertan R1: 160/160 group votes never allow it
    ("final_vote_punish_low", 3),  # Ertan R2: nearly all final votes = punish-low
    ("no_dismantling", 2),      # humans move TOWARD punish-low, not away
    ("treatment_effect", 3),    # contributions higher under punish-low than none
    ("period1_level", 2),       # P1 mean ~40-60% of endowment (PGG regularity)
    ("sustain_under_punish_low", 2),  # rising/flat under punish-low (decay = bad)
    ("punishment_usage", 2),    # costly punishment actually paid when allowed
    ("punishment_targeting", 2),  # aimed at below-average contributors (~80%+)
    ("heterogeneity", 1),       # P1 spread; humans are heterogeneous
]


def load_targets():
    path = os.path.join(HERE, "human_targets.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["_scorer_params"]
    return {}


def parse_run(run_dir):
    path = os.path.join(run_dir, "summary.txt")
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    votes = [v == "True" for v in re.findall(r"Vote \d: punish low=(\w+)", txt)]
    periods = []
    for m in re.finditer(r"Period \d+: contrib (\{[^}]*\})\s+punishment received (\{[^}]*\})"
                         r"\s+earnings (\{[^}]*\})", txt):
        periods.append({
            "contrib": ast.literal_eval(m.group(1)),
            "received": ast.literal_eval(m.group(2)),
            "earnings": ast.literal_eval(m.group(3)),
        })
    if not votes or not periods:
        return None
    per_vote = len(periods) // len(votes)
    for i, p in enumerate(periods):
        p["punish_low"] = votes[i // per_vote]
    name = os.path.basename(run_dir.rstrip("/"))
    method = name.split("_", 2)[2] if name.count("_") >= 2 else "baseline"
    seed_m = re.search(r"seed (\d+)", txt)
    return {"run": name, "method": method, "votes": votes, "periods": periods,
            "seed": seed_m.group(1) if seed_m else "?", "dir": run_dir}


def targeting_share(run_dir):
    """Share of punishment dollars aimed at below-average contributors.

    Reads the saved p*_punish stages (needs edsl). Returns (share, total$) or
    (None, 0) when no punishment data exists.
    """
    from edsl import Results
    low, total = 0.0, 0.0
    for f in glob.glob(os.path.join(run_dir, "p*_punish", "*.json.gz")):
        r = Results.load(f)
        for row in r.select("target_contribution", "avg", "punish").to_dicts():
            amt = row["punish"] or 0
            if amt <= 0:
                continue
            total += amt
            if row["target_contribution"] < row["avg"]:
                low += amt
    return (low / total, total) if total > 0 else (None, 0.0)


def clamp01(x):
    return max(0.0, min(1.0, x))


def mean_contrib(p):
    return sum(p["contrib"].values()) / len(p["contrib"])


def score_run(run, t):
    s = {}
    votes, periods = run["votes"], run["periods"]

    # In our game high/avg were never allowed by construction of the summary --
    # check the full vote lines for safety.
    txt = open(os.path.join(run["dir"], "summary.txt")).read()
    s["never_punish_high"] = 0.0 if re.search(r"high=True", txt) else 1.0

    s["final_vote_punish_low"] = 1.0 if votes[-1] else 0.0
    s["no_dismantling"] = 0.0 if (votes[0] and not votes[-1]) else 1.0

    pl = [mean_contrib(p) for p in periods if p["punish_low"]]
    npn = [mean_contrib(p) for p in periods if not p["punish_low"]]
    if pl and npn:
        # compare the LAST period of each regime (quasi steady state) — regime
        # means would punish recovery-from-decay paths where punish-low needs
        # a period or two to rebuild cooperation (e.g. the gps adoption run)
        diff = pl[-1] - npn[-1]
        # humans: punish-low clearly above no-punishment; full credit at +2 tokens
        s["treatment_effect"] = clamp01(diff / t.get("treatment_full_credit", 2.0))
    else:
        s["treatment_effect"] = None  # single-regime run: not observable

    # Ertan Fig. 3: period-1 contributions ~69-77% of endowment (Brown subjects)
    frac = mean_contrib(periods[0]) / ENDOWMENT
    lo, hi = t.get("period1_band", [0.69, 0.77])
    s["period1_level"] = 1.0 if lo <= frac <= hi else \
        clamp01(1 - (lo - frac) / lo if frac < lo else 1 - (frac - hi) / (1 - hi))

    if len(pl) >= 2:
        slope = (pl[-1] - pl[0]) / (len(pl) - 1)  # $/period under punish-low
        s["sustain_under_punish_low"] = clamp01(1 + slope / 2)  # flat=1, -2/per=0
    else:
        s["sustain_under_punish_low"] = None

    share, total = targeting_share(run["dir"])
    if any(votes):
        # Ertan Table 4: under punish-low, punishment received tracks shortfall
        # ~1:1 ($0.97-1.22 per $1 below average). Score the run's ratio.
        shortfall = punished = 0.0
        for p in periods:
            if not p["punish_low"]:
                continue
            avg = mean_contrib(p)
            for player, c in p["contrib"].items():
                if c < avg:
                    shortfall += avg - c
                    punished += p["received"][player]
        if shortfall > 0:
            ratio = punished / shortfall
            lo_r, hi_r = t.get("usage_ratio_full_band", [0.5, 1.5])
            s["punishment_usage"] = 1.0 if lo_r <= ratio <= hi_r else \
                clamp01(ratio / lo_r if ratio < lo_r else 1 - (ratio - hi_r))
        else:
            s["punishment_usage"] = None  # nobody ever below average
        s["punishment_targeting"] = share if share is not None else 0.0
    else:
        s["punishment_usage"] = None   # punishment never legal: unobservable
        s["punishment_targeting"] = None

    vals = list(periods[0]["contrib"].values())
    m = sum(vals) / len(vals)
    sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
    s["heterogeneity"] = clamp01(sd / t.get("heterogeneity_full_credit", 3.0))

    num = den = 0.0
    for name, w in CRITERIA:
        if s[name] is not None:
            num += w * s[name]
            den += w
    s["index"] = num / den
    return s


def main():
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else ""
    t = load_targets()
    rows = []
    for d in sorted(glob.glob(os.path.join(RESULTS, "*/"))):
        run = parse_run(d)
        if not run or (since and run["run"].split("_", 1)[1] < since):
            continue
        rows.append((run, score_run(run, t)))

    crit_names = [c for c, _ in CRITERIA]
    header = f"{'run':44s} {'seed':4s} " + " ".join(f"{c[:9]:>9s}" for c in crit_names) + "   INDEX"
    print(header)
    for run, s in rows:
        cells = " ".join(f"{('  -' if s[c] is None else f'{s[c]:.2f}'):>9s}" for c in crit_names)
        print(f"{run['run']:44s} {run['seed']:4s} {cells}   {s['index']:.3f}")

    # per-method mean across seeds
    by_method = {}
    for run, s in rows:
        by_method.setdefault(run["method"], []).append(s["index"])
    print("\nMETHOD RANKING (mean index across runs):")
    for m, idxs in sorted(by_method.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
        print(f"  {m:16s} {sum(idxs) / len(idxs):.3f}   (n={len(idxs)})")

    if "--csv" in sys.argv:
        out = sys.argv[sys.argv.index("--csv") + 1]
        with open(out, "w") as f:
            f.write("run,method,seed," + ",".join(crit_names) + ",index\n")
            for run, s in rows:
                f.write(f"{run['run']},{run['method']},{run['seed']},"
                        + ",".join("" if s[c] is None else f"{s[c]:.3f}" for c in crit_names)
                        + f",{s['index']:.3f}\n")
        print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
