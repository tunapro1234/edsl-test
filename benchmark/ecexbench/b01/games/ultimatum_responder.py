"""Ultimatum game, responder role — measures negative reciprocity."""

GAME = {
    "game": "ultimatum_responder",
    "role": "responder",
    "holdout": False,
    "measures": "negative_reciprocity",
    "conditions": [
        {"id": "low", "pot": 100, "offer": 10, "keep": 90},
        {"id": "mid", "pot": 100, "offer": 25, "keep": 75},
        {"id": "fair", "pot": 100, "offer": 40, "keep": 60},
    ],
    "text": (
        "A stranger was given ${pot} and had to propose how to split it with "
        "you. They offered you ${offer} and kept ${keep} for themselves. If "
        "you accept, you get ${offer} and they get ${keep}. If you reject, "
        "you both get $0. This is a one-time decision and you will never "
        "meet them. Do you accept the offer (Accept or Reject)?"
    ),
    "question_type": "mc",
    "options": ["Accept", "Reject"],
    "belief": None,
    "references": {
        "reject_rate_low_offers": "offers below 20% of the pie are rejected about half the time — Camerer 2003, Behavioral Game Theory, ch. 2 stylized facts ('Offers below 20 percent are very rare and they are rejected about half of the times', quoted in PMC4934685)",
        "reject_rate_fair_offers": "offers of 40-50% of the pie are rarely rejected — Camerer 2003, Behavioral Game Theory, ch. 2 stylized facts",
        "mean_rejection_rate": "0.16 of all offers rejected — Oosterbeek, Sloof & van de Kuilen 2004 meta-analysis, Experimental Economics 7(2):171-188, abstract ('On average 16% of the offers is rejected')",
        "mean_offer_share": "0.40 of the pie — Oosterbeek et al. 2004, abstract (context: the typical offer responders face)",
    },
}
