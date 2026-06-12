"""Trust game, sender role — measures trust (Berg-Dickhaut-McCabe investment game)."""

GAME = {
    "game": "trust_sender",
    "role": "sender",
    "holdout": False,
    "measures": "trust",
    "conditions": [{"id": "base", "pot": 100, "mult": 3, "tripled_pot": 300,
                    "belief_bonus": 2, "belief_tol": 5}],
    "text": (
        "You have ${pot}. You may send any amount of it to a stranger and keep "
        "the rest. Every dollar you send is multiplied by {mult} before the "
        "stranger receives it. The stranger then decides how much of what they "
        "received, if anything, to send back to you; whatever they send back is "
        "yours to keep. You will never meet the stranger and the game is played "
        "only once. How many dollars do you send to the stranger (0 to {pot})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": 100,
    "belief": {
        "text": (
            "You are about to play the following game: you have ${pot} and may "
            "send any amount of it to a stranger, keeping the rest. Every dollar "
            "you send is multiplied by {mult} before the stranger receives it. "
            "The stranger then decides how much of what they received, if "
            "anything, to send back to you. Before you decide, predict how many "
            "dollars the stranger will send back to you; a prediction within "
            "${belief_tol} of the true amount earns you a ${belief_bonus} bonus. "
            "How many dollars do you predict the stranger will send back "
            "(0 to {tripled_pot})?"
        ),
        "min": 0,
        "max": 300,
    },
    "references": {
        "mean_sent_share": "0.50 of endowment — Johnson & Mislin 2011, 'Trust games: A meta-analysis', J. Econ. Psychology 32(5):865-889 (162 replications, >23,000 subjects); authors' WP version ('Cultures of Kindness', Mercatus) Table 1: mean sentfraction = 0.509 (SD 0.138, n=84 replications)",
        "mean_return_share_of_available": "0.37 of the amount available to the receiver (belief target: ~0.37 x tripled amount) — Johnson & Mislin 2011, same source; WP Table 1: mean retavail = 0.365 (SD 0.094, n=75)",
    },
}
