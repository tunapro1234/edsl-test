"""Time choices — measures patience + present bias (quasi-hyperbolic beta).

Six matched pairs: now-pairs (today vs in 30 days) and later-pairs (in 30 vs
in 60 days), same amounts. The per-30-day premiums are 3%, 10%, 25%.
Present bias = choosing "Sooner payment" in a now-pair but "Later payment"
in the matched later-pair (beta < 1 in the beta-delta model, Laibson 1997).
"""

GAME = {
    "game": "time_choices",
    "role": "chooser",
    "holdout": False,
    "measures": "patience + present bias",
    "conditions": [
        {"id": "now103", "sooner_amount": 100, "sooner_when": "today", "later_amount": 103, "later_when": "in 30 days"},
        {"id": "now110", "sooner_amount": 100, "sooner_when": "today", "later_amount": 110, "later_when": "in 30 days"},
        {"id": "now125", "sooner_amount": 100, "sooner_when": "today", "later_amount": 125, "later_when": "in 30 days"},
        {"id": "later103", "sooner_amount": 100, "sooner_when": "in 30 days", "later_amount": 103, "later_when": "in 60 days"},
        {"id": "later110", "sooner_amount": 100, "sooner_when": "in 30 days", "later_amount": 110, "later_when": "in 60 days"},
        {"id": "later125", "sooner_amount": 100, "sooner_when": "in 30 days", "later_amount": 125, "later_when": "in 60 days"},
    ],
    "text": (
        "You are choosing between two payments. If you choose the sooner "
        "payment, you receive ${sooner_amount} {sooner_when}. If you choose "
        "the later payment, you receive ${later_amount} {later_when}. Both "
        "payments are completely certain and will be paid exactly on time. "
        "Which do you choose: 'Sooner payment' (${sooner_amount} "
        "{sooner_when}) or 'Later payment' (${later_amount} {later_when})?"
    ),
    "question_type": "mc",
    "options": ["Sooner payment", "Later payment"],
    "belief": None,
    "references": {
        "present_bias_beta_money": "0.82, 95% CI [0.74, 0.90] (0.87 [0.82, 0.92] after correcting for selective reporting) — Cheung, Tymula & Wang 2021, 'Quasi-Hyperbolic Present Bias: A Meta-Analysis', IZA DP 14625, abstract",
        "canonical_beta_delta": "beta=0.7, delta=0.957 — canonical quasi-hyperbolic parameterization (Laibson 1997 tradition) in Cohen, Ericson, Laibson & White, 'Measuring Time Preferences', JEL 2020, Figure 2 caption; field structural estimate beta=0.50, delta=0.96 (Laibson, Maxted, Repetto & Tobacman 2017, as reported ibid., p. 22)",
        "discount_rate_spread": "implicit annual discount rates across studies range from -6 percent to infinity — Frederick, Loewenstein & O'Donoghue 2002, 'Time Discounting and Time Preference: A Critical Review', JEL 40(2), p. 377 and Table 1 pp. 378-79",
    },
}
