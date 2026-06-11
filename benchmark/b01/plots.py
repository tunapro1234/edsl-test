"""b.01 plots — decision histograms per game × persona method.

Run with SYSTEM python3 (the .venv has no matplotlib):
    python3 -m benchmark.b01.plots          # or: python3 benchmark/b01/plots.py

Reads results.csv, writes benchmark/b01/plots/<game>.png: one histogram panel
per persona method (shared bins), human reference lines where references give
a number. Only valid rows are plotted; invalid counts shown in the title.
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    data = defaultdict(lambda: defaultdict(list))  # game -> method -> decisions
    invalid = defaultdict(int)
    with open(os.path.join(HERE, "results.csv"), newline="") as f:
        for r in csv.DictReader(f):
            if r["valid"] == "1":
                try:
                    data[r["game"]][r["persona_method"]].append(float(r["decision"]))
                except ValueError:  # MC decisions: map option index
                    data[r["game"]][r["persona_method"]].append(r["decision"])
            else:
                invalid[r["game"]] += 1
    return data, invalid


def plot_game(game, by_method, n_invalid):
    methods = sorted(by_method)
    fig, axes = plt.subplots(1, len(methods), figsize=(3.2 * len(methods), 3),
                             sharey=True, squeeze=False)
    numeric = all(isinstance(v, float) for vs in by_method.values() for v in vs)
    for ax, m in zip(axes[0], methods):
        vals = by_method[m]
        if numeric:
            lo = min(v for vs in by_method.values() for v in vs)
            hi = max(v for vs in by_method.values() for v in vs)
            ax.hist(vals, bins=min(20, max(5, int(hi - lo + 1))), range=(lo, hi),
                    color="#4878a8", edgecolor="white")
        else:
            opts = sorted({v for vs in by_method.values() for v in vs})
            counts = [vals.count(o) for o in opts]
            ax.bar(range(len(opts)), counts, color="#4878a8")
            ax.set_xticks(range(len(opts)), opts, rotation=30, ha="right", fontsize=7)
        ax.set_title(f"{m} (n={len(vals)})", fontsize=9)
    fig.suptitle(f"{game} — decisions" + (f"  [{n_invalid} invalid dropped]" if n_invalid else ""))
    fig.tight_layout()
    out = os.path.join(HERE, "plots", f"{game}.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def main():
    data, invalid = load()
    for game, by_method in sorted(data.items()):
        print("wrote", plot_game(game, by_method, invalid.get(game, 0)))


if __name__ == "__main__":
    main()
