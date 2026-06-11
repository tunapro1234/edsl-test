# Clean baseline (max_tokens=8192) vs morning baseline (default cap)

MAJOR SENSITIVITY FINDING: the bare model's behavior changed qualitatively with
the output-token cap raised (no other change; empty persona line is cosmetic).

| | morning run 07-37-23 (default cap, partly None-corrupted) | this run (8192, clean) |
|---|---|---|
| P1 contributions | 10/0/0/0 | 0/10/10/10 |
| punishment paid | NEVER (9/9 decisions $0) | $10 every period at the current free-rider |
| punished player's response | — | flips to full contribution next period |
| vote 2 | dismantles punishment | dismantles punishment |
| post-vote-2 | all-0 (partly fabricated by None->$0) | all-0 (genuine) |

Interpretation: with room to reason, gpt-oss-120b treats punishment as a
strategic investment (deterrence) within the punish-low regime, but still
dismantles the institution in vote 2 and free-rides without sanctions.
The "rational corner / never punishes" claim from the morning runs conflated
model behavior with a truncation artifact. Decoding parameters are a
behavioral treatment — log them with every result (they are in the raw data).
