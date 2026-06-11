"""Dictator game — measures altruism (reference implementation for b.01)."""

GAME = {
    "game": "dictator",
    "role": "dictator",
    "holdout": False,
    "measures": "altruism",
    "conditions": [{"id": "base", "pot": 100}],
    "text": (
        "You have ${pot}. You may give any amount of it to a stranger and keep "
        "the rest. The stranger has no say in the matter and you will never "
        "meet them. How many dollars do you give to the stranger (0 to {pot})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": 100,
    "belief": None,
    "references": {
        "mean_give_share": "0.2835 of the pie — Engel 2011 dictator meta-analysis, MPI preprint 2010/07 ('dictators on average give 28.35 % of the pie')",
        "share_give_zero": "0.3611 — Engel 2011, same source",
        "share_equal_split": "0.1674 — Engel 2011, same source",
    },
}
