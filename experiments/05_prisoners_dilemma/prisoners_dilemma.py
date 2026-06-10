"""Prisoner's Dilemma — 2 players, 5 repeated rounds (Mei et al. setup).

Each round both players simultaneously choose Cooperate or Defect, then both
see what the other did. History is fed into the next round's question via a
scenario — this is how "memory" works across rounds.

Payoffs per round:
    both Cooperate -> $3 each | both Defect -> $1 each
    you Defect, they Cooperate -> you $5, they $0

Humans: ~45% cooperate in round 1, often tit-for-tat after.
Rational (backward induction): defect every round.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import make_model, new_run_dir, run_and_save

from edsl import QuestionMultipleChoice, Agent, Scenario, ScenarioList

HERE = os.path.dirname(os.path.abspath(__file__))
ROUNDS = 5
PAYOFFS = {  # (my move, their move) -> my payoff
    ("Cooperate", "Cooperate"): 3,
    ("Cooperate", "Defect"): 0,
    ("Defect", "Cooperate"): 5,
    ("Defect", "Defect"): 1,
}

q_move = QuestionMultipleChoice(
    question_name="move",
    question_text=(
        "You are Player {{ scenario.me }} playing a 5-round game against the same "
        "opponent. Each round you both simultaneously choose Cooperate or Defect.\n"
        "Payoffs per round: both Cooperate -> $3 each; both Defect -> $1 each; "
        "if one Defects while the other Cooperates -> defector gets $5, cooperator $0.\n"
        "{{ scenario.history }}\n"
        "This is round {{ scenario.round }} of 5. What do you choose?"
    ),
    question_options=["Cooperate", "Defect"],
)


def history_text(my_moves, their_moves):
    if not my_moves:
        return "This is the first round; there is no history yet."
    lines = ["History so far:"]
    for i, (mine, theirs) in enumerate(zip(my_moves, their_moves), 1):
        lines.append(f"Round {i}: you chose {mine}, your opponent chose {theirs}.")
    return "\n".join(lines)


def play_round(rnd, moves_a, moves_b, run_dir):
    """Ask both players for their move this round; return (move_a, move_b)."""
    scenarios = ScenarioList([
        Scenario({"me": "A", "round": rnd, "history": history_text(moves_a, moves_b)}),
        Scenario({"me": "B", "round": rnd, "history": history_text(moves_b, moves_a)}),
    ])
    res = run_and_save(
        q_move.by(scenarios).by(Agent(name="player")).by(make_model()),
        run_dir, f"round{rnd}",
    )
    by_player = {row["me"]: row["move"] for row in res.select("me", "move").to_dicts()}
    return by_player["A"], by_player["B"]


def main():
    run_dir = new_run_dir(os.path.join(HERE, "results"))

    moves_a, moves_b = [], []
    for rnd in range(1, ROUNDS + 1):
        a, b = play_round(rnd, moves_a, moves_b, run_dir)
        moves_a.append(a)
        moves_b.append(b)
        print(f"Round {rnd}:  A={a}  B={b}")

    score_a = sum(PAYOFFS[(a, b)] for a, b in zip(moves_a, moves_b))
    score_b = sum(PAYOFFS[(b, a)] for a, b in zip(moves_a, moves_b))

    lines = ["Prisoner's Dilemma — 5 rounds", ""]
    lines += [f"Round {i}:  A={a:<9}  B={b}" for i, (a, b) in enumerate(zip(moves_a, moves_b), 1)]
    lines += ["", f"Final score:  A=${score_a}   B=${score_b}"]
    summary = "\n".join(lines) + "\n"

    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(summary)
    print("\n" + summary)
    print(f"Saved to: {run_dir}/  (see REASONING.md)")


if __name__ == "__main__":
    main()
