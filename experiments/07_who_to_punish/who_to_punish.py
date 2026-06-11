"""Who to punish? — Ertan, Page & Putterman (2009), simplified skeleton.

Public goods game + punishment + VOTING on who may be punished.
Flow (like the paper's 5-Vote design, scaled down):

    for each vote round:
        all 4 players vote on 3 ballot items (punish low / avg / high contributors?)
        majority rule decides -> the rule holds for the next PERIODS_PER_VOTE periods
        each period: contribute -> see contributions -> punish (only allowed targets)

Payoffs per period (paper's eq. 2):
    earnings = (10 - my contribution) + 0.4 * (total contributions)
               - 0.25 * (punishment I give) - (punishment I receive)   [floored at 0]

Simplifications vs the paper: 1 group (not 20), 2 votes x 3 periods (not 5 x 6),
fixed player labels (paper shuffles them each period for anonymity).

Paper's human result: NO group ever allowed punishing high contributors;
most converged to "punish low only", which beat everything on efficiency.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import make_model, new_run_dir, run_and_save

from edsl import QuestionNumerical, QuestionMultipleChoice, Agent, Scenario, ScenarioList

HERE = os.path.dirname(os.path.abspath(__file__))

LABELS = ["A", "B", "C", "D"]
ENDOWMENT = 10
MPCR = 0.4          # each $1 in the fund pays $0.40 to every player
PUNISH_COST = 0.25  # paying $0.25 reduces the target's earnings by $1
VOTES = 2
PERIODS_PER_VOTE = 3

BALLOT = {  # the 3 ballot items: who may be punished?
    "low": "LESS than the group average",
    "avg": "exactly the group average",
    "high": "MORE than the group average",
}

# NOTE: the numbers in this text must match the constants above.
RULES = (
    "You are Player {{ scenario.me }} in a fixed group of 4 playing a repeated "
    "public goods game. Each period every player receives $10 and privately "
    "decides how much to put into a group fund. Every dollar in the fund pays "
    "$0.40 to EACH of the 4 players. You keep whatever you do not contribute. "
    "After contributions are revealed, punishment may happen: paying $0.25 "
    "reduces another player's earnings by $1.00 — but only players of the kinds "
    "your group voted punishable may be punished.\n"
)

q_vote = QuestionMultipleChoice(
    question_name="vote",
    question_text=RULES
    + "{{ scenario.history }}\n"
    "Your group now votes (majority rule) on the punishment rules for the next "
    f"{PERIODS_PER_VOTE} periods.\n"
    "Ballot item: should it be ALLOWED to punish a player who contributed "
    "{{ scenario.target_group }}?",
    question_options=["Yes", "No", "No preference"],
)

q_contribute = QuestionNumerical(
    question_name="contribution",
    question_text=RULES
    + "{{ scenario.rule }}\n{{ scenario.history }}\n"
    "This is period {{ scenario.period }}. How much of your $10 do you "
    "contribute to the group fund (0-10)?",
)

q_punish = QuestionNumerical(
    question_name="punish",
    question_text=RULES
    + "{{ scenario.history }}\n"
    "This period you contributed ${{ scenario.my_contribution }}. All four "
    "contributions were {{ scenario.contributions }} (average "
    "{{ scenario.avg }}).\n"
    "Player {{ scenario.target }} contributed ${{ scenario.target_contribution }}, "
    "which the voted rules allow you to punish. By how many dollars (0-10) do "
    "you reduce their earnings? Each $1 reduction costs you $0.25.",
)


def clamp(x):
    if x is None:  # interview failed even after retries; count as 0
        return 0
    return max(0, min(int(x), ENDOWMENT))


def history_text(log):
    if not log:
        return "This is the start of the game; there is no history yet."
    return "History so far:\n" + "\n".join(log)


def category(c, avg):
    return "low" if c < avg else "high" if c > avg else "avg"


def rule_text(rule):
    if not any(rule.values()):
        return "The group voted to allow NO punishment at all."
    bits = [f"{BALLOT[k]}: {'YES' if rule[k] else 'NO'}" for k in BALLOT]
    return "Voted rules — may a player be punished for contributing... " + "; ".join(bits)


def run_vote(vote_no, logs, run_dir):
    """All players vote Yes/No on each ballot item; strict majority allows it."""
    scenarios = ScenarioList([
        Scenario({"me": L, "item": k, "target_group": BALLOT[k],
                  "history": history_text(logs[L])})
        for L in LABELS for k in BALLOT
    ])
    res = run_and_save(
        q_vote.by(scenarios).by(Agent(name="player")).by(make_model()),
        run_dir, f"vote{vote_no}",
    )
    rows = res.select("item", "vote").to_dicts()
    rule = {}
    for k in BALLOT:
        votes = [r["vote"] for r in rows if r["item"] == k]
        rule[k] = votes.count("Yes") > votes.count("No")  # tie -> not allowed
    return rule


def play_period(period_no, rule, logs, run_dir):
    """One period: contributions, then punishment (if the rule allows any)."""
    scenarios = ScenarioList([
        Scenario({"me": L, "period": period_no, "rule": rule_text(rule),
                  "history": history_text(logs[L])})
        for L in LABELS
    ])
    res = run_and_save(
        q_contribute.by(scenarios).by(Agent(name="player")).by(make_model()),
        run_dir, f"p{period_no}_contrib",
    )
    contrib = {r["me"]: clamp(r["contribution"])
               for r in res.select("me", "contribution").to_dicts()}

    total = sum(contrib.values())
    avg = total / len(LABELS)
    pre = {L: ENDOWMENT - contrib[L] + MPCR * total for L in LABELS}
    shown = sorted(contrib.values(), reverse=True)  # shown without names

    # punishment stage: only (punisher, target) pairs the voted rule allows
    pairs = [(p, t) for p in LABELS for t in LABELS
             if p != t and rule[category(contrib[t], avg)]]
    given = {L: 0 for L in LABELS}
    received = {L: 0 for L in LABELS}
    if pairs:
        scenarios = ScenarioList([
            Scenario({"me": p, "target": t, "my_contribution": contrib[p],
                      "target_contribution": contrib[t], "contributions": shown,
                      "avg": round(avg, 2), "history": history_text(logs[p])})
            for p, t in pairs
        ])
        res = run_and_save(
            q_punish.by(scenarios).by(Agent(name="player")).by(make_model()),
            run_dir, f"p{period_no}_punish",
        )
        for r in res.select("me", "target", "punish").to_dicts():
            amount = clamp(r["punish"])
            given[r["me"]] += amount
            received[r["target"]] += amount

    earnings = {L: max(0, pre[L] - PUNISH_COST * given[L] - received[L])
                for L in LABELS}
    for L in LABELS:
        logs[L].append(
            f"Period {period_no}: you contributed ${contrib[L]}, all contributions "
            f"were {shown} (avg {round(avg, 2)}); you spent "
            f"${PUNISH_COST * given[L]:.2f} on punishing and received "
            f"${received[L]} of punishment; you earned ${earnings[L]:.2f}."
        )
    return contrib, received, earnings


def main():
    run_dir = new_run_dir(os.path.join(HERE, "results"))
    logs = {L: [] for L in LABELS}
    summary = [f"Who to punish? — {VOTES} votes x {PERIODS_PER_VOTE} periods", ""]

    period = 0
    for v in range(1, VOTES + 1):
        rule = run_vote(v, logs, run_dir)
        line = f"Vote {v}: punish low={rule['low']}  avg={rule['avg']}  high={rule['high']}"
        summary += [line]
        print(line)
        for L in LABELS:
            logs[L].append(f"Vote {v} outcome: {rule_text(rule)}")

        for _ in range(PERIODS_PER_VOTE):
            period += 1
            contrib, received, earnings = play_period(period, rule, logs, run_dir)
            line = (f"  Period {period}: contrib {contrib}  "
                    f"punishment received {received}  "
                    f"earnings { {L: round(e, 2) for L, e in earnings.items()} }")
            summary += [line]
            print(line)

    summary_txt = "\n".join(summary) + "\n"
    with open(os.path.join(run_dir, "summary.txt"), "w") as f:
        f.write(summary_txt)
    print(f"\nSaved to: {run_dir}/  (see REASONING.md)")


if __name__ == "__main__":
    main()
