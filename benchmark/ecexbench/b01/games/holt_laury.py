"""Holt-Laury price list — measures risk aversion (Holt & Laury 2002 AER)."""

GAME = {
    "game": "holt_laury",
    "role": "chooser",
    "holdout": False,
    "measures": "risk_aversion",
    # Table 1 (low payoffs): row k gives the high payoff a k-in-10 chance in BOTH options.
    "conditions": [
        {"id": f"row{k}", "p": k, "q": 10 - k,
         "a_hi": "2.00", "a_lo": "1.60", "b_hi": "3.85", "b_lo": "0.10"}
        for k in range(1, 11)
    ],
    "text": (
        "You must choose between two lotteries. Option A pays ${a_hi} with a "
        "{p} in 10 chance and ${a_lo} with a {q} in 10 chance. Option B pays "
        "${b_hi} with a {p} in 10 chance and ${b_lo} with a {q} in 10 chance. "
        "You will be paid the outcome of the lottery you choose. Which do you "
        "choose: Option A or Option B?"
    ),
    "question_type": "mc",
    "options": ["Option A", "Option B"],
    "belief": None,
    "references": {
        "option_a_payoffs": "$2.00 / $1.60 — Holt & Laury 2002, AER 92(5), Table 1 p.1645 (low-payoff treatment)",
        "option_b_payoffs": "$3.85 / $0.10 — Holt & Laury 2002, Table 1 p.1645",
        "risk_neutral_safe_choices": "4 (switches to B at row 5) — Holt & Laury 2002 pp.1645-46: 'a risk-neutral person would choose A four times before switching to B'",
        "share_risk_averse": "~2/3 make more than 4 safe choices at low real payoffs — Holt & Laury 2002 p.1648",
        "modal_safe_choices": "4 and 5 (0.26 each; 4-6 covers 0.75) — Holt & Laury 2002, Table 3 p.1649, 'low real' column",
    },
}
