# twin2k — provenance and design notes

## Source (all verified locally)
- Paper: Toubia, Gui, Peng, Merlau, Li & Chen (2025), *Twin-2K-500*, arXiv:2505.17479
  (`research/papers-to-read/07-twin-2k-500-benchmark.pdf`, pp. 1-3): N=2,058 US
  respondents on Prolific, launched 01/29/2025 targeting 2,500 "representative US
  respondents (sampled by age, sex, and ethnicity)"; 4 waves (2,509 -> 2,263 -> 2,252
  -> 2,058 completers), ~500 questions, avg 145.5 min total, $37 max compensation.
  Wave 4 repeats earlier tasks for a test-retest accuracy benchmark.
- Data: `research/datasets/twin2k500/LLM-Digital-Twin___twin-2k-500/full_persona/`
  (HF clone, Arrow streaming shards). Columns: pid / persona_text / persona_summary /
  persona_json; 2,058 rows, all pids unique, zero empty summaries.
  persona_summary: 11.6k-18.5k chars (median 13.0k). persona_text: ~125.6k-133.6k
  chars (median 128.7k) — too big to inject per question.
- Code: `research/datasets/Digital-Twin-Simulation/` (Apache-2.0). Their demo notebook
  injects `persona_summary`; their prompt framing = "## Persona Profile (This
  individual's past survey responses):" + question + system instruction "answer ... as
  if you are the person described in the 'Persona Profile' ... consistent with their
  previous answers and stated characteristics" (configs/openai_config.yaml). Our
  HEADER/FOOTER mirror this, moved into the persona text because our games prepend
  rather than use a system message.

## What the personas encode (computed over our 500-person sample)
Embedded real behavior the model can read directly:
- dictator_sender: mean 38.7%, median 40, P(give 0)=.11
- trustgame_sender: mean 48.6%, median 40, P(0)=.13
- ultimatum_sender: mean 46.0%, median 40, P(0)=.07
Plus per-person risk/loss aversion, discounting, present bias, Big 5, CRT, and the
person's own free-text thoughts while playing trust/dictator.

## Sampling design
- prepare.py: fixed seed 2025, 500 of 2,058, sorted by pid; prints a
  full-vs-500 cross-check (Gender F .507 vs .482; Age 30-49 .357 vs .342;
  Democrat .412 vs .428 — close).
- sample(n, seed): uniform WITHOUT replacement (distinct real people per group);
  with replacement only if n > 500. Deterministic given seed; stdlib only.

## Representativeness caveats (be honest in the writeup)
- Prolific quotas cover age, sex, ethnicity ONLY — education, income, politics are
  not quota-matched (panel: Democrat .412 vs Republican .262; self-selected online
  workers).
- 2,058 four-wave completers out of 2,509 starters -> possible attrition bias toward
  conscientious respondents.
- Survey-measured giving (dictator mean ~39%) is higher than lab meta-analytic
  giving (Engel 2011: ~28%) — hypothetical stakes; the personas inherit this.

## Cost note (who_to_punish)
~3.3-4.6k persona tokens x 48-120 questions/run = ~0.2-0.5M extra input tokens
= roughly $0.01-0.02 at deep_infra gpt-oss-120b $0.04/M input
(experiments/price_audit_results.csv); EP credit markup applies on top.

## Verification run: what to look for vs baseline (2026-06-11_07-37-23)
Baseline: votes punish-low, then nobody pays to punish, contributions collapse to 0,
vote 2 dismantles the institution. Twin2k markers of success: interior + heterogeneous
contributions across the 4 distinct people, actual paid punishment of low contributors,
punish-low rule retained in vote 2, earnings above the $10 no-cooperation floor.

## Who-to-punish v2 result (seed 1, clean: 0/72 None) — 2026-06-11_15-08-43
Textbook Fehr-Gächter/Ertan trajectory, the strongest run of any method:
- P1 interior heterogeneous contributions 5/5/10/6; low contributors punished ($2/$2).
- P2-P3 monotonic ratchet up (7/8/10/7 → 9/8/10/10) with punishment tracking laggards.
- Vote 2: punish-low RETAINED (humans do exactly this; bare model dismantled it).
- P4: 10/10/10/9 — the lone 9 still drew $5 punishment (strict norm enforcement).
- P5-P6: full cooperation 10x4, punishment no longer needed (pure deterrence).
Earnings end at $16/period (max cooperative payoff). Real-person profiles with embedded
behavioral evidence produced the complete institutional success story.
