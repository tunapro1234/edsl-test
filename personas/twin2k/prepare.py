"""One-time prep: extract Twin-2K-500 persona summaries into a small local JSON.

Run with SYSTEM python3 (it has pyarrow 23; the project .venv has no pyarrow,
no pandas, and no pip):

    python3 personas/twin2k/prepare.py [dataset_dir] [out_json]

Source: local HuggingFace clone of LLM-Digital-Twin/Twin-2K-500 (Toubia et al.
2025, arXiv:2505.17479) at research/datasets/twin2k500/, config `full_persona`:
2,058 real US respondents, columns pid / persona_text / persona_summary /
persona_json. We keep `persona_summary` (~13k chars: demographics + ~40 scale
scores with percentile and plain-language explanations + the person's own
open-ended answers) — the same field the authors' own demo notebook
(Digital-Twin-Simulation/notebooks/demo_simple_simulation.ipynb) injects for
simulation. `persona_text` (~128k chars, all 500 raw Q&As) is far too big to
prepend to every game question.

Output: personas_sample.json — a fixed seed-2025 sample of 500 respondents
(~6.6 MB), sorted by pid. Also prints a gender / age / party cross-check so
you can see the 500 match the full panel.
"""

import glob
import json
import os
import random
import sys

import pyarrow as pa
import pyarrow.ipc as ipc

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATASET_DIR = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "research", "datasets", "twin2k500",
    "LLM-Digital-Twin___twin-2k-500", "full_persona"))
DEFAULT_OUT = os.path.join(HERE, "personas_sample.json")

SAMPLE_SIZE = 500
PREP_SEED = 2025  # fixed: everyone re-running this gets the same 500 people


def load_summaries(dataset_dir):
    """Read all .arrow shards (HF cache = Arrow streaming format) -> [(pid, summary)]."""
    shards = sorted(glob.glob(os.path.join(dataset_dir, "**", "*.arrow"), recursive=True))
    if not shards:
        sys.exit(f"no .arrow files under {dataset_dir}")
    tables = []
    for path in shards:
        with pa.memory_map(path, "r") as src:
            tables.append(ipc.open_stream(src).read_all().select(["pid", "persona_summary"]))
    t = pa.concat_tables(tables)
    rows = list(zip(t.column("pid").to_pylist(), t.column("persona_summary").to_pylist()))
    return [(pid, s) for pid, s in rows if s and s.strip()]


def field(summary, label):
    """Pull e.g. 'Gender: Male' out of the summary's demographics block."""
    for line in summary.splitlines():
        if line.startswith(label + ":"):
            return line.split(":", 1)[1].strip()
    return "?"


def crosstab(rows, label):
    counts = {}
    for _, s in rows:
        v = field(s, label)
        counts[v] = counts.get(v, 0) + 1
    total = len(rows)
    return {v: round(c / total, 3) for v, c in sorted(counts.items())}


def main():
    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET_DIR
    out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    rows = load_summaries(dataset_dir)
    rows.sort(key=lambda r: int(r[0]))  # deterministic order before sampling
    print(f"loaded {len(rows)} respondents with a persona_summary")

    picked = random.Random(PREP_SEED).sample(rows, SAMPLE_SIZE)
    picked.sort(key=lambda r: int(r[0]))

    for label in ("Gender", "Age", "Political affiliation"):
        print(f"{label:>22}  full: {crosstab(rows, label)}")
        print(f"{'':>22}  500 : {crosstab(picked, label)}")

    payload = {
        "source": "LLM-Digital-Twin/Twin-2K-500 full_persona.persona_summary "
                  "(Toubia et al. 2025, arXiv:2505.17479)",
        "prep_seed": PREP_SEED,
        "n": len(picked),
        "personas": [{"pid": pid, "summary": s} for pid, s in picked],
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"wrote {len(picked)} personas -> {out_path} "
          f"({os.path.getsize(out_path) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
