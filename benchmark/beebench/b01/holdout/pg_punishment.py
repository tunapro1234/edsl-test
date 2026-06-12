"""One-shot Fehr-Gächter public goods game WITH punishment — HOLDOUT.

The repeated FG design is decomposed into three one-shot decisions, one per
condition: "contribute" is the contribution stage; "punish_freerider" and
"punish_cooperator" are punishment-stage vignettes in which you contributed
$15 and the target contributed $2 (far below the others' average) or $18
(above it — the perverse-punishment probe). Stage wording is written ONCE
below and pre-filled into each condition's `stage` param.

Bounds: contribute is 0-20 but the punish conditions are 0-10; GAME min/max
are 0-20 so the runner's single validity check covers every condition, and
each condition's true range is stated in the question text. A punish answer
in (10, 20] passes the runner's check — re-flag it at analysis time.

Belief: the runner asks the belief question before EVERY condition's decision
(belief is game-level); it is only meaningful for "contribute" — filter on
condition == "contribute" when analysing beliefs.
"""

_BASE = {"n": 4, "endow": 20, "mpcr": "0.40", "cost": 1, "fine": 3,
         "tol": 1, "bonus": 2}
_PMAX = 10  # max deduction points per target (FG 2002 Nature technology)

_RULES = (
    "You are in a group of {n} people, playing exactly once and anonymously. "
    "Each player gets ${endow} and chooses how many dollars (0 to {endow}) "
    "to put into a group project, keeping the rest. Every dollar put into "
    "the project pays out ${mpcr} to EACH of the {n} players, no matter who "
    "put it in. After everyone has chosen, all contributions are revealed "
    "and each player may assign deduction points to any other player: each "
    "point costs the punisher ${cost} and reduces the punished player's "
    "earnings by ${fine}. "
)
_ASK_CONTRIBUTE = (
    "It is now the contribution stage. How many dollars do you put into the "
    "group project (0 to {endow})?"
)
_ASK_PUNISH = (
    "The contribution stage is over: you put in ${own}, and the other "
    "players put in ${c1}, ${c2}, and ${c3}. It is now the punishment "
    "stage. How many deduction points do you assign to the player who put "
    "in ${target} (0 to {pmax})?"
)

GAME = {
    "game": "pg_punishment",
    "role": "group_member",
    "holdout": True,
    "measures": "cooperation + altruistic punishment",
    "conditions": [
        {"id": "contribute", **_BASE,
         "stage": _ASK_CONTRIBUTE.format(**_BASE)},
        {"id": "punish_freerider", "max": 10,  # per-condition bound (reviewer #4)
         **_BASE,
         "stage": _ASK_PUNISH.format(own=15, c1=2, c2=18, c3=15,
                                     target=2, pmax=_PMAX)},
        {"id": "punish_cooperator", "max": 10, **_BASE,
         "stage": _ASK_PUNISH.format(own=15, c1=18, c2=15, c3=15,
                                     target=18, pmax=_PMAX)},
    ],
    "text": _RULES + "{stage}",
    "question_type": "numerical",
    "min": 0,
    "max": _BASE["endow"],
    "belief": {
        "text": _RULES + (
            "Before anything is decided, predict the average number of "
            "dollars the other players will put into the group project "
            "(0 to {endow}). If your prediction is within ${tol} of the "
            "true average you earn an extra ${bonus}. What is your "
            "prediction (0 to {endow})?"
        ),
        "min": 0,
        "max": _BASE["endow"],
    },
    "references": {
        "design_params": "n=4, endowment y=20, marginal payoff a=0.4, up to ten punishment points per target — Fehr & Gächter 2000 AER 90(4):980-994, Section II.C pp. 982-983",
        "punish_technology": "each point costs the punisher 1 MU and the punished member 3 MUs, 0-10 points — Fehr & Gächter 2002 Nature 415:137-140, p. 137. NOTE: FG2000 AER instead used a convex point-cost schedule (Table 2, p. 983); b.01 adopts the simpler linear 2002 technology",
        "contrib_share_with_punishment": "0.58 of endowment (Stranger-treatment average) — FG2000 AER Result 1, p. 984; free-riders raise contributions by 10-12 tokens (50-60% of endowment) vs no punishment, p. 992",
        "punishment_rises_with_negative_deviation": "received points per token below others' average: +0.2428*** Stranger / +0.4168*** Partner, positive deviation insignificant — FG2000 AER Result 7 + Table 5, pp. 990-991; FG2002 Nature p. 138: Tobit coef on negative deviation 0.622 (z=18.1)",
        "punish_freerider_level": "a Partner-treatment subject contributing 14-20 tokens below others' average received on average 6.8 punishment points — FG2000 AER Figure 5, p. 991",
        "perverse_punishment_share": "~0.20 of punishments target above-average contributors across VCM-with-punishment studies — Ertan, Page & Putterman 2005 WP printed p. 1, citing FG2000 p. 990; see benchmark/human_targets.json",
    },
}
