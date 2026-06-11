"""11-20 money request game — measures level-k reasoning depth (Arad & Rubinstein 2012)."""

GAME = {
    "game": "eleven_twenty",
    "role": "requester",
    "holdout": False,
    "measures": "level_k_depth",
    "conditions": [{"id": "base", "lo": 11, "hi": 20, "bonus": 20}],
    "text": (
        "You and another player are playing a one-shot game. The other player is "
        "anonymous and you will never meet them. Each player requests an amount "
        "of money; the amount must be an integer between {lo} and {hi} dollars. "
        "Each player receives the amount they request. A player receives an "
        "additional {bonus} dollars if they ask for exactly one dollar less than "
        "the other player. What amount of money do you request ({lo} to {hi})?"
    ),
    "question_type": "numerical",
    "min": 11,
    "max": 20,
    "belief": None,
    "references": {
        "choice_distribution_pct": "11:4, 12:0, 13:3, 14:6, 15:1, 16:6, 17:32, 18:30, 19:12, 20:6 — Arad & Rubinstein 2012 AER 102(7), Table 1 p.3565 (basic version, n=108)",
        "modal_choices": "17 (32%) and 18 (30%) — same Table 1",
        "share_17_to_19": "0.74 — 'The vast majority of subjects (74 percent) chose the actions 17-18-19' (p.3565); 17-20 = 0.80 (p.3566)",
        "level0_action": "20 — 'The choice of 20 is a natural anchor for an iterative reasoning process' (p.3562)",
        "level_k_type_estimates": "L0=0.05, L1=0.13, L2=0.39, L3=0.43, error rate 0.32 — footnote 6, p.3566",
        "wording_note": "text follows the paper's basic-version instructions (p.3562) with two spec-mandated clauses NOT in the original: 'one-shot game' and 'The other player is anonymous and you will never meet them' (in the experiment, subjects were classmates seated in the same classroom, randomly matched); original currency was shekels (Tel Aviv University students), b.01 uses dollars",
    },
}
