"""Third-party punishment — measures norm enforcement (Fehr & Fischbacher 2004 TP-DG).

HOLDOUT game: never used for persona tuning. Original is in points (1 point =
CHF 0.3); we use dollars with the same structure. As in the original, A's
transfer is capped at half the pot ($50) and C is told this cap (F&F 2004,
p. 66 + footnote 1); the text says "up to ${cap}" accordingly.

Documented deviations from F&F 2004:
- Condition gave25 is NOT a canonical transfer level: the paper restricted A's
  transfers to multiples of 10 ({0, 10, 20, 30, 40, 50}); gave25 is mandated
  by the b01 spec. When scoring against human targets, the nearest F&F
  Fig. 1/2 comparison points are the 20 and 30 transfer levels.
- Because gave25 is not a multiple of 10, the text states only the $50 cap,
  not the paper's multiples-of-10 grid.
"""

_C = {"pot": 100, "cap": 50, "endow": 50, "mult": 3}

GAME = {
    "game": "third_party_punishment",
    "role": "third_party",
    "holdout": True,
    "measures": "norm_enforcement",
    "conditions": [
        {"id": "gave0", "gave": 0, **_C},
        {"id": "gave10", "gave": 10, **_C},
        {"id": "gave25", "gave": 25, **_C},
        {"id": "gave50", "gave": 50, **_C},
    ],
    "text": (
        "Two strangers, Person A and Person B, just played the following game: "
        "Person A received ${pot} and could give any amount of it, up to "
        "${cap}, to Person B, "
        "who started with nothing and had no say in the matter. Person A gave "
        "${gave} to Person B and kept the rest. You observed this but were not "
        "part of it; you have ${endow} of your own money and the split does not "
        "affect you. You may now spend any amount of your money to reduce "
        "Person A's earnings: each $1 you spend takes ${mult} away from Person "
        "A. The money you spend is gone; neither you nor Person B receives it. "
        "How many dollars do you spend on reducing Person A's earnings "
        "(0 to {endow})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": 50,
    "belief": None,
    "references": {
        "design": "A endowed 100 points, transfers in {0,10,...,50}; C endowed 50 points; each deduction point costs C 1 and cuts A by 3; strategy method over all transfer levels — Fehr & Fischbacher 2004, Evol. Human Behav. 25(2), Sec. 2.1, pp. 66-67",
        "share_punish_below_50": "roughly 0.60 of third parties punish at EACH transfer level below 50 (n=22) — F&F 2004, Sec. 2.2, p. 68 and Fig. 1 (p. 69)",
        "mean_spend_gave0": "14 deduction points when A gave nothing (cuts A's income by 42) — F&F 2004, p. 68",
        "punish_slope": "OLS: punishment = .28 x (50 - transfer), constant -0.45 n.s. (P=.230); each 10-point drop in transfer adds 2.8 deduction points (8.4 cut to A) — F&F 2004, p. 68",
        "punish_at_equal_split": "near zero: punishment at transfer 50 occurred but its average was not significantly different from zero — F&F 2004, p. 68 and Fig. 1 (~5% punish)",
    },
}
