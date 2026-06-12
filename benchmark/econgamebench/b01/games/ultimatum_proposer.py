"""Ultimatum game, proposer role — measures strategic fairness."""

GAME = {
    "game": "ultimatum_proposer",
    "role": "proposer",
    "holdout": False,
    "measures": "strategic_fairness",
    "conditions": [{"id": "base", "pot": 100}],
    "text": (
        "You have ${pot} to split with a stranger. You propose how many "
        "dollars to offer them and keep the rest. The stranger then either "
        "accepts or rejects your proposal: if they accept, the money is split "
        "exactly as you proposed; if they reject, you BOTH get $0. This "
        "happens once and you will never meet them. How many dollars do you "
        "offer to the stranger (0 to {pot})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": 100,
    "belief": None,
    "references": {
        "mean_offer_share": "0.40 of the pie — Oosterbeek, Sloof & van de Kuilen 2004 meta-analysis (37 papers, 75 results), Experimental Economics 7(2):171-188, abstract: 'on average the proposer offers 40% of the pie'",
        "share_offers_rejected": "0.16 — Oosterbeek, Sloof & van de Kuilen 2004, same source, abstract: 'On average 16% of the offers is rejected'",
    },
}
