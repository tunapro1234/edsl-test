"""GPS replication — instrument fidelity, not a published-LLM-result replication.

The GPS source (Falk et al. 2018, QJE; NBER WP 23943) is HUMAN survey data:
there is no LLM experiment to re-run. What we can prove is that our
implementation is faithful, in two parts:

(1) OFFLINE (free): the sampler reproduces the published correlation structure
    — empirical pairwise correlations of 200k draws vs Appendix C Table 12
    (WP printed p. 62, verified against the PDF), latent traits ~ mean 0 / sd 1
    (the paper's standardization, Fig. 10 caption, WP p. 60), rare answer
    clipping, deterministic sampling.

(2) LLM READBACK PROBE (--run, real billing): inject 6 sampled personas and
    re-ask TWO of the verbatim GPS items (risk: A.6.2 p. 51; trust: A.6.6
    p. 54). The persona text literally contains the answer, so a model that
    can read should echo the stated dial back. This tests that the injection
    is readable and binding — NOT a published LLM result.

Run from repo root:
    .venv/bin/python personas/gps/replication.py          # print design + cost, exit
    .venv/bin/python personas/gps/replication.py --run    # execute, write replication.json
"""

import json
import os
import random
import re
import statistics
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from personas.gps import PREFS, R, RISK_ITEM, SELF_ASSESSMENT_ITEMS, _draw_traits, sample

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- pre-registered design + pass criteria (set BEFORE any results exist) ----
N_OFFLINE = 200_000   # draws for the distribution checks
MAX_CORR_GAP = 0.01   # worst |empirical - Table 12| over the 15 pairs
MAX_ABS_MEAN = 0.02   # latent traits should be ~N(0,1)
MAX_SD_DEV = 0.02
MAX_CLIP = 0.02       # round(5+2z) clips iff |z|>2.5 -> expected 2*Phi(-2.5)=1.24%
N_PERSONAS = 6
SEED = 27             # chosen for dial SPREAD (risk 2-8, trust 2-7) so a model that
                      # ignores the persona and answers mid-scale FAILS (selection is
                      # on inputs, before any model output — see REPLICATION.md)
REPS = 3              # answers per persona x item
PROBE_TOL = 2         # |answer - persona's stated dial| <= 2 counts as a hit
MIN_HIT_SHARE = 0.75  # share of hits required (None answers count as misses)
MIN_DIAL_CORR = 0.5   # corr(stated dial, mean answer) across the 12 cells —
                      # guards against any constant answer slipping past the tolerance
CRITERIA = ("Offline: 200k-draw correlations within 0.01 of Table 12, latent moments "
            "within 0.02 of (0,1), clip rate <2%, deterministic; LLM: >=75% of 36 "
            "readback probes within +-2 of the persona's stated dial AND "
            "dial-answer correlation >=0.5.")

MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"
SERVICE = "deep_infra"
PRICE_IN, PRICE_OUT = 0.02, 0.05  # $/1M tokens (verified live)

# The two re-asked items, verbatim from the personas' own lines (= NBER WP 23943
# A.6.2 p. 51 and A.6.6 p. 54). TRUST_ITEM is the single GPS trust item, so the
# stated dial maps 1:1 to what we re-ask.
TRUST_ITEM = SELF_ASSESSMENT_ITEMS[2][1]
assert "best intentions" in TRUST_ITEM

PAPER_TARGETS = {
    "table12_pairwise_correlations": {   # NBER WP 23943, App. C, Table 12, p. 62
        f"{PREFS[i]}~{PREFS[j]}": R[i][j]
        for i in range(len(PREFS)) for j in range(i)},
    "latent_mean": 0.0, "latent_sd": 1.0,  # standardized individual-level scale (WP p. 60, Fig. 10)
    "llm_probe": "none published — readback consistency check of our own instrument",
}


def stated_dial(persona, snippet):
    """Read the 0-10 answer printed in the persona's own line for an item."""
    line = next(l for l in persona.splitlines() if snippet in l)
    return int(re.search(r"your answer: (\d+)", line).group(1))


def offline_checks():
    """Re-run check_gps.py's distribution checks; return (results, ok)."""
    rng = random.Random(0)
    draws = [_draw_traits(rng) for _ in range(N_OFFLINE)]
    cols = {p: [d[p] for d in draws] for p in PREFS}

    worst_mean = max(abs(statistics.fmean(cols[p])) for p in PREFS)
    worst_sd = max(abs(statistics.stdev(cols[p]) - 1) for p in PREFS)

    def corr(xs, ys):
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        sx, sy = statistics.stdev(xs), statistics.stdev(ys)
        return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / ((len(xs) - 1) * sx * sy)

    worst_gap = max(abs(corr(cols[PREFS[i]], cols[PREFS[j]]) - R[i][j])
                    for i in range(len(PREFS)) for j in range(i))
    clip = (sum(1 for d in draws for p in PREFS if not 0 <= 5 + 2 * d[p] <= 10)
            / (N_OFFLINE * len(PREFS)))
    deterministic = (sample(5, seed=42) == sample(5, seed=42)
                     and sample(5, seed=42) != sample(5, seed=43))

    results = {"worst_corr_gap": round(worst_gap, 4), "worst_abs_mean": round(worst_mean, 4),
               "worst_sd_dev": round(worst_sd, 4), "clip_rate": round(clip, 4),
               "deterministic": deterministic, "n_draws": N_OFFLINE}
    ok = (worst_gap < MAX_CORR_GAP and worst_mean < MAX_ABS_MEAN
          and worst_sd < MAX_SD_DEV and clip < MAX_CLIP and deterministic)
    return results, ok


def probe(personas):
    """Re-ask the two verbatim items; return per-cell answers keyed (item, pidx)."""
    from edsl import Agent, Model, QuestionLinearScale, Scenario, ScenarioList

    model = Model(MODEL_NAME, service_name=SERVICE, temperature=0.7, max_tokens=2048)
    # the GPS scale-anchor introductions, condensed (A.6 intro, WP p. 50)
    items = {
        "risk": (RISK_ITEM + ' Please use a scale from 0 to 10, where 0 means '
                 '"completely unwilling to take risks" and a 10 means you are '
                 '"very willing to take risks".',
                 {0: "completely unwilling to take risks", 10: "very willing to take risks"},
                 "how willing or unwilling you are to take risks"),
        "trust": ('How well does the following statement describe you as a person? '
                  f'"{TRUST_ITEM}" Please indicate your answer on a scale from 0 to 10. '
                  'A 0 means "does not describe me at all" and a 10 means '
                  '"describes me perfectly".',
                  {0: "does not describe me at all", 10: "describes me perfectly"},
                  "best intentions"),
    }

    cells = {}
    for name, (text, labels, snippet) in items.items():
        q = QuestionLinearScale(
            question_name=name,
            question_text="{{ scenario.persona }}\n" + text,
            question_options=list(range(11)),
            option_labels=labels,
        )
        scenarios = ScenarioList([
            Scenario({"pidx": i, "dial": stated_dial(p, snippet), "persona": p})
            for i, p in enumerate(personas)])
        res = q.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)
        for r in res.select("pidx", "dial", name).to_dicts():
            cells.setdefault((name, r["pidx"], r["dial"]), []).append(r[name])
    return cells


def score(cells):
    """Pre-registered scoring: hit share (None = miss) + dial-answer correlation."""
    flat = [(dial, a) for (_, _, dial), answers in cells.items() for a in answers]
    hits = sum(1 for dial, a in flat if a is not None and abs(a - dial) <= PROBE_TOL)
    share = hits / len(flat)

    pairs = [(dial, statistics.fmean([a for a in answers if a is not None]))
             for (_, _, dial), answers in cells.items()
             if any(a is not None for a in answers)]
    ds, ms = [p[0] for p in pairs], [p[1] for p in pairs]
    if len(pairs) < 3 or statistics.stdev(ms) == 0:
        dial_corr = 0.0  # constant (or missing) answers carry no signal -> fail
    else:
        dial_corr = statistics.correlation(ds, ms)
    return share, dial_corr, sum(1 for _, a in flat if a is None)


def main():
    personas = sample(N_PERSONAS, seed=SEED)
    n_calls = 2 * N_PERSONAS * REPS
    tok_in = statistics.fmean(len(p) for p in personas) / 4 + 320  # item + EDSL wrapper
    cost = n_calls * (tok_in * PRICE_IN + 150 * PRICE_OUT) / 1e6

    print(f"GPS replication = instrument fidelity (no LLM paper exists for GPS)")
    print(f"  offline: {N_OFFLINE:,} draws vs Table 12 (15 corrs), moments, clip, determinism — free")
    print(f"  probe:   {N_PERSONAS} personas (seed {SEED}) x 2 verbatim items (risk, trust) x {REPS} reps")
    print(f"           model {MODEL_NAME} ({SERVICE}), readback tolerance +-{PROBE_TOL}")
    print(f"  pass:    {CRITERIA}")
    print(f"  n_calls: {n_calls}   est. cost: ${cost:.4f}")
    if "--run" not in sys.argv:
        print("dry run only — pass --run to execute (real billing) and write replication.json")
        return

    offline, offline_ok = offline_checks()
    print(f"\noffline: {offline}  ->  {'ok' if offline_ok else 'FAIL'}")

    cells = probe(personas)
    share, dial_corr, n_null = score(cells)
    probe_ok = share >= MIN_HIT_SHARE and dial_corr >= MIN_DIAL_CORR
    print(f"probe: hit share {share:.2f} (min {MIN_HIT_SHARE}), dial corr {dial_corr:.2f} "
          f"(min {MIN_DIAL_CORR}), {n_null} null answers  ->  {'ok' if probe_ok else 'FAIL'}")
    for (item, pidx, dial), answers in sorted(cells.items()):
        print(f"  {item:>5} persona {pidx}: dial {dial:2d} -> answers {answers}")

    artifact = {
        "method": "gps",
        "model": f"{SERVICE}/{MODEL_NAME}",
        "experiment": ("instrument fidelity: Table 12 correlation recovery (offline) "
                       "+ 2-item verbatim readback probe (LLM)"),
        "paper_targets": PAPER_TARGETS,
        "results": {
            "offline": offline,
            "probe": {"hit_share": round(share, 3), "dial_answer_corr": round(dial_corr, 3),
                      "n_null": n_null, "reps": REPS, "seed": SEED,
                      "cells": [{"item": k[0], "pidx": k[1], "dial": k[2], "answers": v}
                                for k, v in sorted(cells.items())]},
        },
        "pass": bool(offline_ok and probe_ok),
        "criteria": CRITERIA,
        "n_calls": n_calls,
        "cost_estimate_usd": round(cost, 4),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    path = os.path.join(HERE, "replication.json")
    with open(path, "w") as f:
        json.dump(artifact, f, indent=2)
    print(f"\n{'PASS' if artifact['pass'] else 'FAIL'} — wrote {path}")


if __name__ == "__main__":
    main()
