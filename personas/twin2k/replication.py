"""Paper replication for the twin2k persona method (A11).

Source: Toubia, Gui, Peng, Merlau, Li & Chen (2025), *Twin-2K-500*,
arXiv:2505.17479 (research/papers-to-read/07-twin-2k-500-benchmark.pdf).

The paper builds LLM "digital twins" of 2,058 real US respondents and has
them answer 88 HOLDOUT heuristics-and-biases questions that were excluded
from the persona. Accuracy metric (Sec. 3, p.6): binary question -> exact
match; non-binary -> 1 - |prediction - truth| / answer range. Predictions
are scored against the person's wave 1-3 answers ("compared with the Wave
1-3 ground truth", Sec. 4, p.7); the person's wave-4 re-answers give a
human test-retest ceiling. Table 2 (p.7): Persona Summary + GPT-4.1-mini
68.02%, Text Persona 71.72%, Random Guessing 59.17%, Human Test/Retest
81.72%; twin/test-retest ratio 87.67% (Sec. 5.1, p.7).

Miniature here: N_PERSONS real people from our fixed 500-person pool x
N_QUESTIONS single-answer multiple-choice holdout questions each (wave_split
config). The persona is injected exactly as personas.twin2k builds it
(HEADER + persona_summary + FOOTER) — that is the implementation under test.
Temperature 0 as in all the paper's baseline conditions (App. A.1, p.13).

Usage (from repo root):
  python3 -m personas.twin2k.replication --prepare   # one-time, SYSTEM python3
                                                     # (needs pyarrow), no API
  .venv/bin/python -m personas.twin2k.replication    # print design+cost, exit
  .venv/bin/python -m personas.twin2k.replication --run   # REAL BILLING
"""

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
from personas import twin2k  # noqa: E402  (HEADER/FOOTER + pool under test)

PROBE_PATH = os.path.join(HERE, "replication_probe.json")
OUT_PATH = os.path.join(HERE, "replication.json")
WAVE_SPLIT = os.path.normpath(os.path.join(
    REPO, "..", "research", "datasets", "twin2k500",
    "LLM-Digital-Twin___twin-2k-500", "wave_split"))

MODEL_NAME, SERVICE = "gpt-4o", "openai"   # paper used GPT-4.1(-mini): see
TEMPERATURE = 0      # paper App. A.1 p.13  # REPLICATION.md deviation #1
MAX_TOKENS = 2048
REPS = 1
N_PERSONS, N_QUESTIONS = 5, 8              # 40 calls
SKIP_BLOCK = "Product Preferences - Pricing"  # 41 qs would swamp the probe
PRICE_IN, PRICE_OUT = 2.5 / 1e6, 10 / 1e6  # gpt-4o $/token (EP live price)

# Every paper number below was read from the PDF (page cites above).
PAPER = {
    "persona_summary_accuracy": 0.6802,  # Table 2, p.7 — closest condition
    "text_persona_accuracy": 0.7172,     # Table 2, p.7   to ours (we inject
    "random_guessing": 0.5917,           # Table 2, p.7   persona_summary)
    "human_test_retest": 0.8172,         # Table 2, p.7 / Sec. 3 p.6
    "relative_accuracy": 0.8767,         # Sec. 5.1, p.7 (twin / test-retest)
}

# PRE-REGISTERED pass rule, fixed before any model call:
#   paper-metric accuracy vs wave 1-3 truth must (a) reach the paper's
#   Persona Summary number minus 0.15 small-N slack, (b) beat the analytic
#   uniform-random baseline on our exact 40 questions (computed from the
#   probe file, no API; this is the binding constraint at ~0.54 — a scrambled
#   persona/template scores at random), and (c) have >=90% of calls answered.
PASS_FLOOR = PAPER["persona_summary_accuracy"] - 0.15
CRITERIA = ("paper-metric holdout accuracy (vs wave 1-3 truth) >= 0.6802 - "
            "0.15 = 0.5302 AND > analytic random baseline on the same 40 "
            "questions, with >= 90% of calls answered")


def paper_metric(pred_pos, truth_pos, k):
    """Paper's accuracy (Sec. 3, p.6) on a k-option ordinal scale, 1-based
    positions: 1 - |dev| / range. For k=2 this is exact match."""
    return 1.0 if k == 1 else 1 - abs(pred_pos - truth_pos) / (k - 1)


def analytic_random(entry):
    """Expected paper-metric accuracy of a uniform-random answer."""
    k = len(entry["options"])
    return sum(paper_metric(p, entry["truth_pos"], k) for p in range(1, k + 1)) / k


def probe_stats(probe):
    rnd = sum(analytic_random(e) for e in probe) / len(probe)
    retest = sum(paper_metric(e["retest_pos"], e["truth_pos"], len(e["options"]))
                 for e in probe) / len(probe)
    return rnd, retest


def prepare():
    """Extract the probe from the wave_split HF shards (system python3 only:
    needs pyarrow). For the N_PERSONS lowest pids in our 500-person pool,
    keep the first N_QUESTIONS single-answer MC holdout questions."""
    import glob
    import pyarrow as pa
    import pyarrow.ipc as ipc

    want = set(sorted(int(p["pid"]) for p in twin2k._load())[:N_PERSONS])
    rows = {}
    for path in sorted(glob.glob(os.path.join(WAVE_SPLIT, "**", "*.arrow"),
                                 recursive=True)):
        with pa.memory_map(path, "r") as src:
            t = ipc.open_stream(src).read_all().select(
                ["pid", "wave4_Q_wave1_3_A", "wave4_Q_wave4_A"])
        for r in t.to_pylist():
            if r["pid"] in want:
                rows[r["pid"]] = r
    assert set(rows) == want, f"missing pids: {want - set(rows)}"

    probe = []
    for pid in sorted(rows):
        picked = 0
        blocks13 = json.loads(rows[pid]["wave4_Q_wave1_3_A"])  # truth
        blocks4 = json.loads(rows[pid]["wave4_Q_wave4_A"])     # retest
        for b13, b4 in zip(blocks13, blocks4):
            if b13["BlockName"].strip() == SKIP_BLOCK or picked >= N_QUESTIONS:
                continue
            for q13, q4 in zip(b13["Questions"], b4["Questions"]):
                if q13.get("QuestionType") != "MC" or picked >= N_QUESTIONS:
                    continue
                a13, a4 = q13.get("Answers") or {}, q4.get("Answers") or {}
                if not (isinstance(a13.get("SelectedText"), str)
                        and isinstance(a4.get("SelectedText"), str)):
                    continue
                assert q13["Options"] == q4["Options"], q13["QuestionID"]
                probe.append({
                    "pid": str(pid), "qid": q13["QuestionID"],
                    "block": b13["BlockName"].strip(),
                    "text": q13["QuestionText"], "options": q13["Options"],
                    "truth_pos": a13["SelectedByPosition"],   # wave 1-3
                    "retest_pos": a4["SelectedByPosition"],   # wave 4
                })
                picked += 1
        assert picked == N_QUESTIONS, f"pid {pid}: only {picked} MC questions"

    with open(PROBE_PATH, "w") as f:
        json.dump({"source": "Twin-2K-500 wave_split holdout questions "
                             "(Toubia et al. 2025, arXiv:2505.17479)",
                   "probe": probe}, f, ensure_ascii=False, indent=1)
    rnd, retest = probe_stats(probe)
    print(f"wrote {len(probe)} questions ({N_PERSONS} people x {N_QUESTIONS}) "
          f"-> {PROBE_PATH}")
    print(f"probe analytic random={rnd:.4f}  human test-retest={retest:.4f}")


def load_probe():
    if not os.path.exists(PROBE_PATH):
        sys.exit(f"{PROBE_PATH} missing — run `python3 -m "
                 "personas.twin2k.replication --prepare` with SYSTEM python3")
    with open(PROBE_PATH) as f:
        return json.load(f)["probe"]


def personas_by_pid():
    return {str(p["pid"]): twin2k.HEADER + p["summary"].strip() + twin2k.FOOTER
            for p in twin2k._load()}


def cost_estimate(probe, personas):
    """Chars/4 input tokens + ~500/call EDSL template overhead, ~120 out."""
    tok_in = sum(len(personas[e["pid"]]) + len(e["text"])
                 + len(" ".join(e["options"])) for e in probe) / 4 \
        + 500 * len(probe)
    tok_out = 120 * len(probe)
    return REPS * (tok_in * PRICE_IN + tok_out * PRICE_OUT)


def print_design(probe, personas):
    rnd, retest = probe_stats(probe)
    n_calls = len(probe) * REPS
    print("Twin-2K-500 replication — holdout-question accuracy (twin2k method)")
    print(f"  model: {MODEL_NAME} ({SERVICE}), temperature={TEMPERATURE}, "
          f"max_tokens={MAX_TOKENS}")
    print(f"  probe: {N_PERSONS} real people x {N_QUESTIONS} holdout MC "
          f"questions x {REPS} rep = {n_calls} calls")
    print("  persona: twin2k HEADER + persona_summary + FOOTER (~13k chars), "
          "prepended to each question")
    print("  truth: the person's wave 1-3 answer (paper Sec. 4); wave-4 "
          "answer -> test-retest ceiling")
    print(f"  paper targets: persona-summary twins {PAPER['persona_summary_accuracy']:.4f}, "
          f"random {PAPER['random_guessing']:.4f}, "
          f"test-retest {PAPER['human_test_retest']:.4f} (Table 2, p.7)")
    print(f"  probe set: analytic random={rnd:.4f}, human test-retest={retest:.4f}")
    print(f"  pre-registered pass: {CRITERIA}")
    print(f"  cost estimate: ~${cost_estimate(probe, personas):.2f} "
          f"({n_calls} calls, ~{len(personas[probe[0]['pid']]) // 4} persona "
          "tokens each)")


def run(probe, personas):
    from edsl import Agent, Model, QuestionMultipleChoice, Scenario, ScenarioList

    model = Model(MODEL_NAME, service_name=SERVICE,
                  temperature=TEMPERATURE, max_tokens=MAX_TOKENS)
    q = QuestionMultipleChoice(
        question_name="prediction",
        question_text=("{{ scenario.persona }}\n\n"
                       "## New Survey Question\n{{ scenario.qtext }}"),
        question_options="{{ scenario.options }}",
    )
    scenarios = ScenarioList([
        Scenario({"pid": e["pid"], "qid": e["qid"],
                  "persona": personas[e["pid"]],
                  "qtext": e["text"], "options": e["options"]})
        for e in probe])
    res = q.by(scenarios).by(Agent(name="probe")).by(model).run(n=REPS)
    answers = res.select("pid", "qid", "prediction").to_dicts()

    by_key = {(e["pid"], e["qid"]): e for e in probe}
    s13, s4, exact = [], [], []
    for r in answers:
        e = by_key[(r["pid"], r["qid"])]
        if r["prediction"] not in e["options"]:
            continue  # failed / refused call: drop, counted via n_answered
        pos, k = e["options"].index(r["prediction"]) + 1, len(e["options"])
        s13.append(paper_metric(pos, e["truth_pos"], k))
        s4.append(paper_metric(pos, e["retest_pos"], k))
        exact.append(pos == e["truth_pos"])

    rnd, retest = probe_stats(probe)
    n, n_ans = len(probe), len(s13)
    acc = sum(s13) / n_ans if n_ans else 0.0
    results = {
        "accuracy_paper_metric": round(acc, 4),
        "exact_match_accuracy": round(sum(exact) / n_ans, 4) if n_ans else 0.0,
        "accuracy_vs_wave4": round(sum(s4) / n_ans, 4) if n_ans else 0.0,
        "probe_random_baseline": round(rnd, 4),
        "probe_test_retest": round(retest, 4),
        "relative_accuracy": round(acc / retest, 4) if retest else None,
        "n_questions": n, "n_answered": n_ans,
    }
    passed = bool(n_ans >= 0.9 * n and acc >= PASS_FLOOR and acc > rnd)

    artifact = {
        "method": "twin2k",
        "model": f"{MODEL_NAME} ({SERVICE})",
        "experiment": "Twin-2K-500 holdout-question prediction "
                      f"({N_PERSONS} people x {N_QUESTIONS} MC questions, "
                      "paper accuracy metric vs wave 1-3 truth)",
        "paper_targets": PAPER,
        "results": results,
        "pass": passed,
        "criteria": CRITERIA,
        "n_calls": n * REPS,
        "cost_estimate_usd": round(cost_estimate(probe, personas), 2),
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    with open(OUT_PATH, "w") as f:
        json.dump(artifact, f, indent=2)
    print(json.dumps(artifact, indent=2))
    print(f"\n{'PASS' if passed else 'FAIL'} -> wrote {OUT_PATH}")


def main():
    if "--prepare" in sys.argv:
        prepare()
        return
    probe, personas = load_probe(), personas_by_pid()
    if "--run" in sys.argv:
        run(probe, personas)
    else:
        print_design(probe, personas)
        print("\nDRY RUN ONLY — pass --run to execute (real billing).")


if __name__ == "__main__":
    main()
