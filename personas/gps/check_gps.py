"""Sanity checks for the GPS persona sampler (stdlib only, no network, no cost).

Run from anywhere:  python personas/gps/check_gps.py
Checks: (1) R is positive definite (Cholesky succeeded at import),
(2) empirical correlations of 200k draws match Table 12, (3) latent traits
have mean 0 / sd 1, (4) answer clipping is rare, (5) sample() is
deterministic given a seed.
"""

import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from personas.gps import PREFS, R, _draw_traits, _answer, sample

N = 200_000
rng = random.Random(0)
draws = [_draw_traits(rng) for _ in range(N)]

print("=== latent means / sds (target 0 / 1) ===")
for p in PREFS:
    xs = [d[p] for d in draws]
    print(f"{p:10s} mean {statistics.fmean(xs):+.3f}  sd {statistics.stdev(xs):.3f}")


def corr(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx, sy = statistics.stdev(xs), statistics.stdev(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / ((len(xs) - 1) * sx * sy)


print("\n=== empirical vs target correlations (Table 12) ===")
worst = 0.0
for i, p in enumerate(PREFS):
    for j in range(i):
        q = PREFS[j]
        r = corr([d[p] for d in draws], [d[q] for d in draws])
        worst = max(worst, abs(r - R[i][j]))
        print(f"{p:10s} x {q:10s} empirical {r:+.3f}  target {R[i][j]:+.3f}")
print(f"worst gap: {worst:.4f} (should be < 0.01)")

print("\n=== answer distribution (patience item) ===")
answers = [_answer(d["patience"]) for d in draws]
for v in range(11):
    print(f"{v:3d}: {answers.count(v) / N:6.1%}")
clipped = sum(1 for d in draws for p in PREFS if not (0 <= 5 + 2 * d[p] <= 10))
print(f"share of clipped answers: {clipped / (N * len(PREFS)):.2%}")

print("\n=== determinism ===")
assert sample(5, seed=42) == sample(5, seed=42), "not deterministic!"
assert sample(5, seed=42) != sample(5, seed=43), "seed ignored!"
print("ok")

print("\n=== example persona (seed 1, first of 4) ===")
print(sample(4, seed=1)[0])
