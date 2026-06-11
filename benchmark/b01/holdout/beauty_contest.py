"""Beauty contest / guessing game — measures strategic depth (level-k). HOLDOUT."""

GAME = {
    "game": "beauty_contest",
    "role": "guesser",
    "holdout": True,
    "measures": "strategic_depth",
    "conditions": [{"id": "base", "lo": 0, "hi": 100, "frac": "2/3", "prize": 20}],
    "text": (
        "You are playing a guessing game with many other players, all choosing "
        "at the same time. Each player picks a number between {lo} and {hi}. "
        "The player whose number is closest to {frac} of the average of all "
        "chosen numbers (including yours) wins ${prize}; everyone else gets "
        "nothing, and ties split the prize. What number do you pick "
        "({lo} to {hi})?"
    ),
    "question_type": "numerical",
    "min": 0,
    "max": 100,
    "belief": None,
    "references": {
        "first_period_mean": "36.73 — Nagel 1995 AER 85(5), Figure 1B (p=2/3 sessions 4-7), p. 1316",
        "first_period_median": "33 — Nagel 1995, Figure 1B, p. 1316",
        "spike_level1_33": "modal neighborhood interval 30-37 around 50*(2/3)=33 (iteration step 1) — Nagel 1995, Figure 2B, p. 1317",
        "spike_level2_22": "'about 25 percent of all observations, the second-highest frequency' in interval 20-25 around 50*(2/3)^2~22 (iteration step 2) — Nagel 1995, p. 1318",
        "share_choosing_zero": "0 — 'No subject chose 0 in the 2/3 and 1/2 sessions', Nagel 1995, p. 1316",
        "share_above_67": "0.10 chose numbers greater than 67 (weakly dominated); 0.06 chose 66 or 67 — Nagel 1995, p. 1316",
        "design_note": "original prize 20 DM (~$13) per round, winner-take-all with ties split, 15-18 subjects per session — Nagel 1995, pp. 1315-1316; b.01 uses $20",
    },
}
