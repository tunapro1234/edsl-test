"""Public goods + strategy method — measures cooperation and conditional-
cooperator type (Fischbacher, Gächter & Fehr 2001, Economics Letters 71).

One 'unconditional' contribution plus five strategy-method rows ("if the
others contribute $X on average...", X in 0/5/10/15/20) = one condition per
row. Rising cond-row contributions = conditional cooperator; all-zero rows =
free rider (FGF Fig. 2 typing). b.01 follows the b.01 game-6 spec (4 players,
$20, fund DOUBLED => MPCR 0.5); FGF's original used MPCR 0.4. (B1-BRIEF game 6
fixes only the strategy-method rows X in {0,5,10,15,20} and the belief layer.)

Deviation from the canonical instrument: FGF made the contribution table
incentive-compatible via a random die throw that made it payoff-relevant with
probability 1/4 (Section 2, pp. 399-400) and elicited all 21 entries (0-20);
here the table is reduced to five hypothetically framed 'Suppose...' rows —
the row reduction is per B1-BRIEF, the dropped random-payoff mechanism is not.

NOTE: the GAME contract supports only a game-level belief, so the incentivized
prediction below is asked before EVERY condition row — including conditional
rows where the others' average is then stipulated anyway. Acceptable for
typing; score the belief on the 'unconditional' row only. The "+$2 if within
$1" reward numbers are inline per the contract's own belief convention.
"""

N_PLAYERS = 4
ENDOWMENT = 20
MULTIPLIER = 2                 # the fund is doubled...
MPCR = MULTIPLIER / N_PLAYERS  # ...and split 4 ways: $0.50 back per $1 put in


def _cond(cid, info):
    return {"id": cid, "endowment": ENDOWMENT, "n_players": N_PLAYERS,
            "n_others": N_PLAYERS - 1, "multiplier": MULTIPLIER, "mpcr": MPCR,
            "info": info}


GAME = {
    "game": "public_goods_strategy",
    "role": "contributor",
    "holdout": False,
    "measures": "cooperation (conditional-cooperator type)",
    "conditions": [
        _cond("unconditional",
              "You decide without knowing what the other players contribute."),
    ] + [
        _cond(f"cond{x}",
              f"Suppose the other {N_PLAYERS - 1} players contribute ${x} "
              "each on average.")
        for x in (0, 5, 10, 15, 20)
    ],
    "text": (
        "You are in a group of {n_players} players: you and {n_others} others. "
        "Each player gets ${endowment} and decides how many dollars of it to "
        "put into a group fund, keeping the rest. The total in the fund is "
        "multiplied by {multiplier} and divided equally among all {n_players} "
        "players, no matter who contributed — so each dollar you put in pays "
        "back ${mpcr:.2f} to you and ${mpcr:.2f} to each other player. The "
        "game is played exactly once and the players are anonymous. {info} "
        "How many dollars do you put into the fund (0 to {endowment})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": ENDOWMENT,
    "belief": {
        "text": (
            "You are in a group of {n_players} players: you and {n_others} "
            "others. Each player gets ${endowment} and at the same time puts "
            "some of it into a group fund; the fund is multiplied by "
            "{multiplier} and divided equally among all {n_players} players. "
            "Before you decide, predict the average number of dollars the "
            "other {n_others} players put into the fund. If your prediction "
            "is within $1 of their true average, you earn an extra $2. What "
            "is your prediction (0 to {endowment})?"
        ),
        "min": 0,
        "max": ENDOWMENT,
    },
    "references": {
        "share_conditional_cooperators": "0.50 (22/44) — Fischbacher, Gächter & Fehr 2001, Economics Letters 71:397-404, Section 3 p. 401 & Fig. 1",
        "share_free_riders": "0.295 (13/44; schedule of all zeros) — FGF 2001, Section 3 p. 401",
        "share_hump_shaped": "0.136 (6/44) — FGF 2001, Section 3 p. 401",
        "perfect_conditional_slope": "4/44 schedules exactly on the diagonal (slope 1); only 11.9% of conditional cooperators' entries strictly above it ('conditional cooperation with a self-serving bias') — FGF 2001, p. 401",
        "mean_unconditional_contribution": "6.7 of 20 tokens = 0.335 of endowment — FGF 2001, p. 401",
        "design_difference": "FGF payoff was 20 - g_i + 0.4*sum(g_j), i.e. MPCR 0.4 (eq. 1, p. 398); b.01 uses MPCR 0.5 (fund doubled) per the b.01 game-6 spec (B1-BRIEF game 6 specifies only the strategy-method rows and belief layer, not endowment/group size/multiplier)",
    },
}
