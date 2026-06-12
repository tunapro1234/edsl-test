"""Loss-aversion gamble series — accept/reject mixed 50-50 coin-flip bets."""

GAME = {
    "game": "loss_gambles",
    "role": "gambler",
    "holdout": False,
    "measures": "loss_aversion",
    "conditions": [
        {"id": "gain2", "gain": 2, "loss": 5},
        {"id": "gain4", "gain": 4, "loss": 5},
        {"id": "gain5", "gain": 5, "loss": 5},
        {"id": "gain6", "gain": 6, "loss": 5},
        {"id": "gain8", "gain": 8, "loss": 5},
        {"id": "gain10", "gain": 10, "loss": 5},
        # Ladder extension (reviewer finding #2): the original B1-BRIEF ladder
        # topped out at gain/loss = 2.0, RIGHT-CENSORING any agent with human
        # median lambda ~2.25 (indifference at $11.25). Ratios up to 4 follow
        # Tom, Fox, Trepel & Poldrack 2007 (Science 315:515-518: gains $10-40
        # vs losses $5-20, i.e. gain/loss spanning 0.5-8, switch points
        # straddled). gain12/16/20 = ratios 2.4 / 3.2 / 4.0.
        {"id": "gain12", "gain": 12, "loss": 5},
        {"id": "gain16", "gain": 16, "loss": 5},
        {"id": "gain20", "gain": 20, "loss": 5},
    ],
    "text": (
        "You are offered the following one-time gamble. A fair coin is flipped "
        "once: if it lands heads, you win ${gain}; if it lands tails, you lose "
        "${loss} of your own money. If you reject the gamble, the coin is not "
        "flipped and you neither win nor lose anything. Do you accept or "
        "reject this gamble (Accept or Reject)?"
    ),
    "question_type": "mc",
    "options": ["Accept", "Reject"],
    "belief": None,
    "references": {
        "lambda_median": "2.25 — Tversky & Kahneman 1992, J. Risk and Uncertainty 5:297-323, pp. 311-312: 'The median λ was 2.25, indicating pronounced loss aversion' (quoted in Regenwetter et al. 2022, doi:10.1177/25152459221074653); linear value at these stakes puts indifference near gain = 2.25 x $5 = $11.25",
        "accept_threshold": "gain ≈ 2 x loss — TK 1992 loss-aversion test: median theta = gain/loss at indifference ≈ 2 in problems 1-6 (reproduced in Regenwetter et al. 2022, Table 3); predicts a typical subject rejects gain2..gain8 and accepts only around gain10 ($10 = 2 x $5)",
        "lambda_meta": "mean 1.955, 95% interval [1.820, 2.102] — Brown, Imai, Vieider & Camerer 2024 meta-analysis of 607 estimates from 150 articles, J. Economic Literature, doi:10.1257/jel.20221698",
    },
}
