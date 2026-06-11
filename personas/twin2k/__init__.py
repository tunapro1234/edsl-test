"""A11 — real-person persona summaries from Twin-2K-500 (Toubia et al. 2025).

Each persona is the verbatim `persona_summary` of one real US respondent from
the public Twin-2K-500 dataset (arXiv:2505.17479): demographics, ~40 validated
scale scores with percentile + plain-language explanations (Big 5, risk/loss
aversion, discounting, trust/dictator/ultimatum play, CRT, ...) and the
person's own open-ended self-descriptions. The panel: N=2,058 recruited on
Prolific, quota-sampled to the US population on age, sex, and ethnicity only
(paper sec. 2) — NOT a probability sample, and the 2,058 are the survivors of
2,509 wave-1 starters, so attrition bias is possible.

sample(n) draws n DISTINCT real people uniformly from a fixed 500-person
subsample (personas_sample.json, written once by prepare.py — run that with
system python3, which has pyarrow). For n > 500 it falls back to drawing
with replacement.

Framing follows the authors' own simulation pipeline
(Digital-Twin-Simulation/text_simulation: "Persona Profile" header + a
"respond as the persona described above" instruction).
"""

import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "personas_sample.json")

HEADER = "## Persona Profile (one real person's survey responses, Twin-2K-500 study)\n"
FOOTER = (
    "\n## End of profile\n"
    "You are the person described above. Answer every question as this person "
    "would, staying consistent with their survey answers and stated "
    "characteristics."
)

_pool = None


def _load():
    global _pool
    if _pool is None:
        if not os.path.exists(DATA):
            raise FileNotFoundError(
                f"{DATA} missing — run `python3 personas/twin2k/prepare.py` "
                "with SYSTEM python3 (needs pyarrow; the .venv lacks it)")
        with open(DATA) as f:
            _pool = json.load(f)["personas"]
    return _pool


def sample(n, seed=None):
    rng = random.Random(seed)
    pool = _load()
    if n <= len(pool):
        picks = rng.sample(pool, n)  # n distinct real people
    else:
        picks = rng.choices(pool, k=n)
    return [HEADER + p["summary"].strip() + FOOTER for p in picks]
