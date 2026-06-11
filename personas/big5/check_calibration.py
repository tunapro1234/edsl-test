"""Local sanity check for personas/big5 — no network, no EDSL, stdlib only.

Run:  .venv/bin/python personas/big5/check_calibration.py

Checks, against Soto & John (2017) Internet-sample values hard-coded in the
module: (1) sample(n, seed) is deterministic; (2) recovered trait-score
means/SDs match the published norms (after the 1-5 -> 0-10 rescale);
(3) pairwise correlations of sampled scores match the published domain
intercorrelations (Table 2); (4) prints one example persona.
"""

import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from personas.big5 import NORMS, CORR, TRAITS, _scores, sample  # noqa: E402

N = 20_000

# 1. determinism
assert sample(5, seed=42) == sample(5, seed=42), "sample() is not deterministic"
print("determinism: OK (sample(5, 42) twice -> identical)")

# 2. + 3. recover moments and correlations from raw draws
rng = random.Random(7)
draws = [_scores(rng) for _ in range(N)]

print(f"\ntrait moments over {N} draws (0-10 scale; expected = rescaled norms):")
for t in TRAITS:
    xs = [d[t] for d in draws]
    mean = sum(xs) / N
    sd = math.sqrt(sum((x - mean) ** 2 for x in xs) / N)
    em, esd = NORMS[t]
    em10, esd10 = (em - 1) / 4 * 10, esd / 4 * 10
    print(f"  {t:18s} mean {mean:5.2f} (expect ~{em10:4.2f})   "
          f"sd {sd:4.2f} (expect ~{esd10:4.2f}, minus truncation/rounding)")

print("\npairwise correlations (expected = Soto & John Table 2):")
for i in range(len(TRAITS)):
    for j in range(i + 1, len(TRAITS)):
        a = [d[TRAITS[i]] for d in draws]
        b = [d[TRAITS[j]] for d in draws]
        ma, mb = sum(a) / N, sum(b) / N
        cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / N
        sa = math.sqrt(sum((x - ma) ** 2 for x in a) / N)
        sb = math.sqrt(sum((y - mb) ** 2 for y in b) / N)
        r = cov / (sa * sb)
        print(f"  {TRAITS[i][:5]:5s}-{TRAITS[j][:5]:5s}  r = {r:+.2f}  "
              f"(expect {CORR[i][j]:+.2f})")

print("\nexample persona (seed 1):\n")
print(sample(1, seed=1)[0])
