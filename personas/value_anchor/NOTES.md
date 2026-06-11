# value_anchor — notes

## Method decisions (2026-06-11 review)
- **Anchor texts**: 19 BWVr descriptions, verbatim from Rozen et al. Appendix E (PDF pp.17-18),
  re-checked word-for-word. Animal welfare (20th BWVr item) excluded — not a Schwartz value.
- **Template**: the paper's exact Value Anchor wording "Answer as a person that is [value]"
  (p.4). We do NOT add "most important guiding value in life": all the paper's validation
  (rank correlations >.8 vs humans, MDS fit 0.11 vs 0.71 for Names) is for the bare wording,
  and §4.1 shows a bare anchor already induces a full coherent profile (nearby values scored
  high, distant low) — so single anchors are not one-note by design. The old framing
  explicitly instructs obsession and likely fed the caricature below.
- **Label swap**: Appendix E pairs "power-dominance" with the money text and "power-resources"
  with the authority text — swapped vs every Schwartz instrument (PVQ-RR por1 = "the power
  that money can bring", pod = "tells others what to do"; S&C 2022 OSF supplement Table S1).
  Texts kept verbatim, filed under standard codes so weights attach to the right text.
- **Sampling**: anchor v drawn with P(v is a person's most important value), from
  prep_weights.py (Lee et al. 2019 best-worst data — same instrument as the texts).
  weights.json is checked in; uniform fallback = the paper's own usage.

## Weights sanity (computed locally, seed 0, 1M draws)
- Top: benevolence-dependability .165, benevolence-caring .146, self-direction-action .117;
  bottom: face .003, power-dominance .0005 — benevolence highest / power lowest matches the
  pan-cultural hierarchy (Rozen et al. p.6-7, Fig 2b).
- Source cross-checks (Spearman): Lee Study 2 vs Study 1 USA general adults ~.98 (tie-corrected Spearman), vs
  Australia .92 (stimulation sub-items averaged per the paper's footnote 4); vs the
  49-country PVQ-RR human benchmark printed in Rozen Table 2 (p.14) .91.
- Sensitivity: Gaussian-copula variant with the pooled 19x19 human correlations (S&C 2022
  OSF Table S10, min eigenvalue .0098) moves every weight by < .017 → independence kept.

## Who-to-punish verification (seed 1) — OLD paraphrased wording + uniform sampling
`results/2026-06-11_14-23-48_value_anchor/` — ran BEFORE the verbatim Appendix-E fix and
before prevalence weights; re-run pending.

Players: A = achievement ("being very successful"), B = universalism-tolerance,
C = stimulation, D = security-personal.

- Vote 1: punish-low only — the human modal rule in Ertan-Page-Putterman. **First costly
  punishment we have EVER seen**: A (achievement, free-riding $0) took $10/$20/$10 across
  P1-P3; C and D paid for it.
- Heterogeneous contributions every period (0/5/6/10, 0/7/0/10, 0/0/10/10) — first
  non-degenerate distribution in this game.
- Vote 2 banned punishment (2-2 tie on "low") → contributions sagged: mean ≈4.8 (P1-3) vs
  ≈3.1 (P4-6). **Regime effect in the human direction**, but humans keep punish-low alive.
- Value-consistent reasoning in every single answer (REASONING.md): A votes No on punish-low
  in vote 2 to protect his own free-riding (and Yes on punishing HIGH contributors "more
  targets"); B never punishes, citing tolerance; D contributes 10 to stay unpunishable.
- Caricature alert: C (stimulation) contributed pi ("6.28"), then 0 "to get punished — a
  fresh experience", and max-punished "to fully experience the impact". Partly the old
  "most important guiding value in life" framing, partly uniform sampling putting a 5%
  persona in a 4-player group. New run: seed 1 now draws [self-direction-action,
  benevolence-caring, benevolence-caring, hedonism].
- Data caveat: 4 contribution interviews returned None and were silently counted as $0 by
  the game's clamp(); B's P3 "0" (a failure, not a choice) drew $10 punishment.

## Verdict
Strongest heterogeneity + only method so far producing costly punishment AND a regime
effect — under the WRONG wording. Uniform-sampling TODO now resolved with sourced
prevalence weights; verbatim-template re-run is the next test.

(The None->$0 clamp bug is FIXED as of commit 15b9531: common.py now raises on
persistent Nones; future runs cannot fabricate contributions.)

## Who-to-punish v2 (seed 1, VERBATIM template + uniform sampling, clean 0/54)
`results/2026-06-11_15-08-40_value_anchor/` — intermediate state: new wording, old sampling.
- P1: 10/5/10/10 (B=univ-tolerance gave 5, punished $10); P2 full cooperation 10x4.
- P3: C (stimulation) free-rode unpunished, earned $22 → Vote 2 DISMANTLED punishment
  → genuine collapse 0x4 in P4-6 (clean data, not artifact).
- Story: high trust early; one unpunished defection killed the institution. Next test:
  prevalence weights (benevolence-heavy draws should stabilize cooperation).
