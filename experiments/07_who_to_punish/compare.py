"""Uniform cross-method table from who-to-punish runs.

Reads every results/<ts>_<method>/summary.txt (+ checks data cleanliness in the
saved stage files) and prints one row per run: votes, per-period contribution
means, punishment dollars, and whether the punish-low institution survived.

Run:  .venv/bin/python experiments/07_who_to_punish/compare.py [--since 15-00]
"""

import ast
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_run(run_dir):
    path = os.path.join(run_dir, "summary.txt")
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    votes = re.findall(r"Vote \d: punish low=(\w+)", txt)
    periods = []
    for m in re.finditer(r"Period \d+: contrib (\{[^}]*\})\s+punishment received (\{[^}]*\})", txt):
        contrib, punish = ast.literal_eval(m.group(1)), ast.literal_eval(m.group(2))
        periods.append((sum(contrib.values()) / len(contrib),
                        sum(punish.values())))
    name = os.path.basename(run_dir.rstrip("/"))
    method = name.split("_", 2)[2] if name.count("_") >= 2 else "baseline(old)"
    return {"run": name, "method": method, "votes": votes, "periods": periods}


def main():
    since = ""
    if "--since" in sys.argv:
        since = sys.argv[sys.argv.index("--since") + 1]
    runs = sorted(glob.glob(os.path.join(HERE, "results", "*/")))
    rows = [r for d in runs if (r := parse_run(d))
            and (not since or r["run"].split("_", 1)[1] >= since)]

    print(f"{'run':42s} {'votes':12s} {'mean contrib by period':32s} {'punish $':12s} {'instit.'}")
    for r in rows:
        contribs = "/".join(f"{c:.1f}" for c, _ in r["periods"])
        punish = "/".join(f"{p:.0f}" for _, p in r["periods"])
        instit = "RETAINED" if all(v == "True" for v in r["votes"]) else \
                 "dismantled" if r["votes"] and r["votes"][-1] == "False" else \
                 "-".join(r["votes"])
        print(f"{r['run']:42s} {'→'.join(r['votes']):12s} {contribs:32s} {punish:12s} {instit}")


if __name__ == "__main__":
    main()
