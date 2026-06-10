"""Bomb Risk Game (BRET) — single player, one decision. Measures risk aversion.

There are 100 boxes, one (random) contains a bomb. You choose how many boxes
to open: $1 per opened box, but $0 if the bomb was in one of them.

Expected payoff = k * (100 - k) / 100 -> risk-NEUTRAL optimum is k = 50.
Opening fewer = risk-averse, more = risk-seeking. Humans average ~45.

We ask N players (run n=N) and then simulate the bomb for each.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import make_model, new_run_dir, run_and_save

from edsl import QuestionNumerical, Agent

HERE = os.path.dirname(os.path.abspath(__file__))
N = 10

q_boxes = QuestionNumerical(
    question_name="boxes",
    question_text=(
        "There are 100 closed boxes. Exactly one of them, chosen at random, "
        "contains a bomb. You choose how many boxes to open (0 to 100). "
        "You earn $1 for every box you open, but if the bomb is in any opened "
        "box, you earn $0 instead. How many boxes do you open?"
    ),
)


def main():
    run_dir = new_run_dir(os.path.join(HERE, "results"))

    res = run_and_save(
        q_boxes.by(Agent(name="player")).by(make_model()), run_dir, "choices", n=N
    )
    choices = res.select("boxes").to_list()

    lines = [f"Bomb Risk — {N} players, 100 boxes", ""]
    lines.append(f"{'player':>6} {'boxes':>6} {'bomb at':>8} {'payoff':>7}")
    for i, k in enumerate(choices):
        bomb = random.randint(1, 100)
        payoff = k if bomb > k else 0  # boxes opened are 1..k
        lines.append(f"{i:>6} {k:>6} {bomb:>8} {payoff:>7}")

    mean = sum(choices) / len(choices)
    lines += ["", f"mean boxes opened: {mean:.1f}   (risk-neutral = 50, humans ~45)"]
    summary = "\n".join(lines) + "\n"

    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(summary)
    print(summary)
    print(f"Saved to: {run_dir}/  (see REASONING.md)")


if __name__ == "__main__":
    main()
