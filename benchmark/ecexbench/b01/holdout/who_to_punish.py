"""Who to punish — Ertan-Page-Putterman vote on punishment rules (HOLDOUT).

One ballot item per condition, paraphrasing the paper's voting screen
(verbatim screen text: "I vote to allow a person's earnings to be reduced if
that person assigns less than the average amount / the average amount / more
than the average amount to the group account", boxes Yes / No / No preference
— Section 1.3, printed pp. 7-8 of the 2005 WP; PDF page = printed + 1).
"""

BALLOT = {  # who may be punished?
    "low": "LESS than the group average",
    "avg": "exactly the group average",
    "high": "MORE than the group average",
}

# money rates as strings so str.format keeps two-decimal formatting
COMMON = {"endowment": 10, "group_size": 4, "multiplier": 1.6,
          "return_each": "0.40", "punish_cost": "0.25", "punish_reduction": "1.00"}

GAME = {
    "game": "who_to_punish",
    "role": "voter",
    "holdout": True,
    "measures": "punishment norms (which contributors deserve punishment)",
    "conditions": [{"id": f"ballot_{k}", "target_group": v, **COMMON}
                   for k, v in BALLOT.items()],
    "text": (
        "You are in a fixed group of {group_size} people playing a repeated "
        "public goods game. Each period every player receives ${endowment} and "
        "privately decides how much to put into a group fund, keeping the rest. "
        "The fund total is multiplied by {multiplier} and split equally, so each "
        "dollar contributed pays ${return_each} to every one of the {group_size} "
        "players. After contributions are revealed, punishment may happen: "
        "paying ${punish_cost} reduces another player's earnings by "
        "${punish_reduction} — but only players of the kinds your group votes "
        "punishable may be punished. Your group now votes (majority rule) on "
        "the punishment rules. Ballot item: should it be ALLOWED to punish a "
        "player who contributed {target_group}? Answer Yes, No, or No preference."
    ),
    "question_type": "mc",
    "options": ["Yes", "No", "No preference"],
    "belief": None,
    "references": {
        "indiv_yes_punish_low": "0.641 (410 Yes of 640 individual votes) — Ertan, Page & Putterman 2005 WP (publ. EER 2009), Table 2, p. 10; mirrored in benchmark/human_targets.json",
        "indiv_yes_punish_avg": "0.072 (46 of 640) — same Table 2, p. 10",
        "indiv_yes_punish_high": "0.173 (111 of 640) — same Table 2, p. 10",
        "group_votes_allow_punish_high": "0 of 160 group votes — Result 1, p. 10 ('No group ever voted to allow punishment of higher-than-average contributors')",
        "design_params": "endowment $10, each $1 contributed pays $0.40 to each of 4 (fund x1.6 split equally), punishing costs $0.25 per $1.00 reduction — Section 1.2, eqs. (1)-(2), printed p. 7 (PDF p. 8) of experiments/07_who_to_punish/ertan_page_putterman_2005_wp.pdf",
        "ballot_options": "Yes / No / No preference; majority rule, ties fail — Section 1.3, printed pp. 7-8 and footnote 9 (printed p. 8)",
    },
}
