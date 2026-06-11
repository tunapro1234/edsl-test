"""Trust game, returner role — measures positive reciprocity (trustworthiness)."""

# NOTE on "max": the GAME dict has one global min/max, so "max" is set to the
# LARGEST received amount across conditions (150, the "high" condition). The
# true per-condition bound is stated inside the text ("0 to {received}"); in
# the low/mid conditions a decision above {received} but <= 150 would still
# pass the global validity check — flag such rows at analysis time.

GAME = {
    "game": "trust_returner",
    "role": "returner",
    "holdout": False,
    "measures": "positive_reciprocity",
    "conditions": [
        {"id": "low", "endow": 50, "sent": 10, "received": 30},
        {"id": "mid", "endow": 50, "sent": 30, "received": 90},
        {"id": "high", "endow": 50, "sent": 50, "received": 150},
    ],
    "text": (
        "A stranger was given ${endow} and chose to send you ${sent} of it. "
        "Every dollar sent was tripled, so you received ${received}. The "
        "stranger kept what they did not send. You now choose how many "
        "dollars of the ${received} to return to the stranger; you keep "
        "whatever you do not return, and the game ends. You will never meet "
        "the stranger. How many dollars do you return to the stranger "
        "(0 to {received})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": 150,
    "belief": None,
    "references": {
        "mean_return_share_of_available": "0.37 of the tripled amount — Johnson & Mislin 2011, 'Trust games: A meta-analysis', J. Econ. Psychology 32(5):865-889 (162 replications); their working-paper version ('Cultures of Kindness', Mercatus/GMU) Table 1: retavail mean 0.3651, sd 0.0942, N=75",
        "mean_sent_share_of_endowment": "0.51 of endowment — same source, Table 1: sentfraction mean 0.5088, sd 0.1377, N=84",
        "trustworthiness_measure": "amount returned / amount available to return (= sent x multiplier), following Glaeser et al. 2000 — Johnson & Mislin 2011, Data section",
    },
}
