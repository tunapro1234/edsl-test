"""b.01 results analyzer — descriptive stats + anomaly flags per game × method.

    .venv/bin/python -m benchmark.ecexbench.b01.analyze            # prints report
    .venv/bin/python -m benchmark.ecexbench.b01.analyze --md out.md

Flags MARK cells for inspection — they NEVER filter or drop data. Several
flagged behaviors are documented in humans (annotated with their precedent);
the interesting quantity is the RATE compared to the human rate, not existence.

Anomaly detectors (game-specific coherence rules, all deterministic):
- invalid_rate    : >10% invalid decisions in a cell
- zero_variance   : every decision identical where humans vary (non-baseline)
- hl_multi_switch : Holt-Laury non-monotone A/B pattern within one agent+run
- lg_non_monotone : loss_gambles rejecting a BETTER gamble while accepting worse
- tc_future_bias  : time_choices sooner-in-later-pair but later-in-now-pair (reverse
                    present bias) at matched amounts
- ur_incoherent   : ultimatum_responder rejects a HIGHER offer while accepting lower
- tr_overreturn   : trust_returner returns more than received (per-condition bound)
- bc_dominated    : beauty_contest guesses > 67 (iteratively dominated)
- pp_perverse     : pg_punishment punishes the high contributor more than the free rider
- tpp_inverted    : third_party punishes the fair dictator more than the unfair one
"""

import argparse
import csv
import os
from collections import defaultdict
from statistics import mean, pstdev

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    rows = []
    with open(os.path.join(HERE, "results.csv"), newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def by_cell(rows):
    cells = defaultdict(list)
    for r in rows:
        cells[(r["game"], r["persona_method"])].append(r)
    return cells


def per_agent_run(rows):
    g = defaultdict(list)
    for r in rows:
        g[(r["agent_id"], r["run"])].append(r)
    return g


# Human precedent for flagged behaviors (sourced where we have numbers).
PRECEDENT = {
    "pp_perverse": "human-attested: ~20% of punishment events target high contributors (Ertan p.1 lit review; 28% by event in their unrestricted phase, p.19)",
    "tpp_inverted": "human-attested in spirit: antisocial/perverse punishment exists (Herrmann et al. 2008; Ertan ~20%)",
    "tc_future_bias": "human-attested but rare (reverse present bias / 'future bias' documented in the intertemporal literature)",
    "hl_multi_switch": "human-attested: a minority of real Holt-Laury subjects switch multiple times",
    "ur_incoherent": "rare in humans; usually noise",
    "lg_non_monotone": "rare in humans; usually noise",
    "bc_dominated": "human-attested: a small share of Nagel 1995 subjects guess above 67",
}

ROW_ORDER = {f"row{k}": k for k in range(1, 11)}
GAIN_ORDER = {f"gain{x}": x for x in (2, 4, 5, 6, 8, 10)}


def detect(game, method, rows):
    flags = []
    valid = [r for r in rows if r["valid"] == "1"]
    if rows and len(valid) / len(rows) < 0.9:
        flags.append(f"invalid_rate {1 - len(valid)/len(rows):.0%}")

    decisions = [r["decision"] for r in valid]
    if method != "baseline" and len(set(decisions)) == 1 and len(decisions) >= 6:
        flags.append(f"zero_variance (all '{decisions[0]}')")

    if game == "holt_laury":
        for (a, run), rs in per_agent_run(valid).items():
            seq = [r["decision"] for r in sorted(rs, key=lambda r: ROW_ORDER.get(r["condition"], 0))]
            switches = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
            if switches > 1:
                flags.append(f"hl_multi_switch {a}/r{run} ({switches} switches)")
    if game == "loss_gambles":
        for (a, run), rs in per_agent_run(valid).items():
            acc = {GAIN_ORDER[r["condition"]]: r["decision"] == "Accept"
                   for r in rs if r["condition"] in GAIN_ORDER}
            xs = sorted(acc)
            if any(acc[xs[i]] and not acc[xs[j]] for i in range(len(xs))
                   for j in range(i + 1, len(xs))):
                flags.append(f"lg_non_monotone {a}/r{run}")
    if game == "time_choices":
        for (a, run), rs in per_agent_run(valid).items():
            d = {r["condition"]: r["decision"] for r in rs}
            for amt in ("103", "110", "125"):
                if (d.get(f"now{amt}") == "Later payment"
                        and d.get(f"later{amt}") == "Sooner payment"):
                    flags.append(f"tc_future_bias {a}/r{run} (@{amt})")
    if game == "ultimatum_responder":
        offer_rank = {"low": 0, "mid": 1, "fair": 2}
        for (a, run), rs in per_agent_run(valid).items():
            d = {offer_rank[r["condition"]]: r["decision"]
                 for r in rs if r["condition"] in offer_rank}
            if any(d.get(i) == "Accept" and d.get(j) == "Reject"
                   for i in d for j in d if i < j):
                flags.append(f"ur_incoherent {a}/r{run}")
    if game == "trust_returner":
        received = {"low": 30, "mid": 90, "high": 150}
        for r in valid:
            v = num(r["decision"])
            cap = received.get(r["condition"])
            if v is not None and cap and v > cap:
                flags.append(f"tr_overreturn {r['agent_id']}/r{r['run']} ({v}>{cap})")
    if game == "beauty_contest":
        n_dom = sum(1 for r in valid if (num(r["decision"]) or 0) > 67)
        if n_dom:
            flags.append(f"bc_dominated x{n_dom}")
    if game == "pg_punishment":
        for (a, run), rs in per_agent_run(valid).items():
            d = {r["condition"]: num(r["decision"]) for r in rs}
            f_, c_ = d.get("punish_freerider"), d.get("punish_cooperator")
            if f_ is not None and c_ is not None and c_ > f_:
                flags.append(f"pp_perverse {a}/r{run} (coop {c_} > freerider {f_})")
    if game == "third_party_punishment":
        for (a, run), rs in per_agent_run(valid).items():
            d = {r["condition"]: num(r["decision"]) for r in rs}
            lo, hi = d.get("gave0"), d.get("gave50")
            if lo is not None and hi is not None and hi > lo:
                flags.append(f"tpp_inverted {a}/r{run} (fair {hi} > unfair {lo})")
    return flags


def cell_stats(rows):
    vals = [num(r["decision"]) for r in rows if r["valid"] == "1"]
    vals = [v for v in vals if v is not None]
    if vals:
        return f"n={len(rows):3d} mean={mean(vals):7.2f} sd={pstdev(vals):6.2f}"
    decs = [r["decision"] for r in rows if r["valid"] == "1"]
    top = max(set(decs), key=decs.count) if decs else "-"
    return f"n={len(rows):3d} modal='{top}' ({decs.count(top)}/{len(decs)})" if decs else f"n={len(rows):3d} (no valid)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", help="also write a markdown report here")
    a = ap.parse_args()

    rows = load()
    cells = by_cell(rows)
    lines = ["# b.01 anomaly report", ""]
    print(f"{'game':24s} {'method':14s} {'stats':40s} flags")
    for (game, method), rs in sorted(cells.items()):
        flags = detect(game, method, rs)
        stats = cell_stats(rs)
        flag_s = "; ".join(flags) if flags else "-"
        print(f"{game:24s} {method:14s} {stats:40s} {flag_s}")
        notes = sorted({PRECEDENT[k] for f in flags for k in PRECEDENT if f.startswith(k)})
        lines.append(f"## {game} × {method}\n{stats}\n"
                     + ("\n".join("- ⚠ " + f for f in flags) if flags else "- ok")
                     + ("".join(f"\n  - precedent: {n}" for n in notes)) + "\n")

    if a.md:
        with open(a.md, "w") as f:
            f.write("\n".join(lines))
        print(f"\nwrote {a.md}")


if __name__ == "__main__":
    main()
