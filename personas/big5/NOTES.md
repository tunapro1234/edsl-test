# big5 — results

## ⚠ Run 2026-06-11_14-22-10 is PARTIALLY CORRUPTED
Periods 3-6 contributions came back mostly None (17/69 answers; failed interviews from
the model's output-token cap truncating answers as history grew) and the old
clamp(None)→$0 wrote FABRICATED "$0 contributions" into every player's history. The
apparent P4-6 collapse was an artifact. Fixed since: max_tokens=8192 in common.py +
run_and_save now raises on persistent Nones instead of fabricating. Only P1-P2 and the
votes of this run are trustworthy. Re-run pending with the champion-upgraded module.

## What the CLEAN part showed (P1-P2 + votes, old wording, seed 1)
The most human-like dynamics of any method so far:
- Vote 1: unanimous punish-low (matches Ertan et al. humans).
- P1: contributions 5/10/10/0 — mean 62.5% of endowment, heterogeneous, human-scale.
- **Costly punishment occurred** (first method ever): B and C paid to punish the low
  contributors (D took $10, A took $4). Non-punishers were trait-consistent: A had
  agreeableness 9 ("I'm very cooperative and caring").
- P2: contributions ROSE to 8/5/10/6 — the classic punishment-sustains-cooperation
  rebound; punishment continued (B took $9).
- Vote 2: punish-low RETAINED 3-1 (baseline had dismantled the institution). Bonus
  human-like datum: low contributor B voted to allow punishing HIGH contributors
  "so I can free-ride more effectively" — strategic perverse voting.

## Champion upgrades applied (2026-06-11)
- Exact Soto & John 2017 Table 5 internet-sample norms (E 3.23/0.80, A 3.68/0.64,
  C 3.43/0.77, NE 3.07/0.87, OM 3.92/0.65) — champion downloaded and read the paper.
- Correlated sampling: published Table 2 domain intercorrelations via stdlib Cholesky;
  verified with 20k draws (all r within 0.02, means within 0.04).
- Verbatim Big5-Scaler Simple Prompt (Figure 2) wording, O-C-E-A-N order, paper trait
  names, verbatim closing line; ONE documented deviation: low pole described neutrally
  per trait (counters neuroticism suppression; low scores otherwise undefined).
- personas/big5/check_calibration.py — offline sanity check (determinism, moments,
  correlations).
