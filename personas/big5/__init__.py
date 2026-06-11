"""A5 — Big Five numeric dials (Big5-Scaler, arXiv:2508.06149).

Persona = the paper's "Simple Prompt" (Cho & Cheong 2025, Figure 2): one
sentence per trait stating what a high score means plus "Your X score is
{s} out of 10", then the closing line — verbatim where possible. Their
best-performing configuration for EXPRESSING assigned trait scores was
exactly this: the SIMPLE trait-level prompt with the smallest scale, n = 10
(Table 7: lowest RMSE across all models; Section 6 observations).

One deliberate addition to the template: each sentence also describes the
LOW pole neutrally ("people with low X score are ..."). Reason: the paper
itself found Neuroticism is under-expressed because safety training
discourages negative affect (Section 5.1), and a population sample (unlike
their single-trait tests) draws low scores on every trait, which the
high-pole-only template leaves undefined. Low-pole wordings paraphrase the
BFI-2 reverse-keyed items (research/datasets/bfi2/bfi2_items.csv).

Scores: sampled from published human norms — Soto & John (2017), JPSP
113(1), Internet validation sample, N = 1,000 (ages 18-74, M = 28.73,
65% under 30; skews young and self-selected, the closest published
general-population norm we have; TODO: swap in nationally representative
norms if we adopt a source). Domains are sampled JOINTLY: a multivariate
normal with the published domain intercorrelations (Cholesky), then
truncated to the 1-5 BFI-2 scale and rescaled to integers 0-10 (truncation
clips up to ~5% at the openness ceiling; ~9% of openness draws round to 10).
Caveat (paper 04): BFI factor structure is not guaranteed to survive inside
an LLM — treat trait->behavior claims modestly.
BFI-2 "Negative Emotionality" / "Open-Mindedness" are the same constructs
as the paper's "neuroticism" / "openness"; we keep the paper's trait names.
"""

import random

# Paper's prompt order (Figure 2): O, C, E, A, N.
TRAITS = ["openness", "conscientiousness", "extraversion", "agreeableness",
          "neuroticism"]

# Soto & John (2017), Table 5, p.128: BFI-2 domain mean (SD) on the 1-5
# scale, Internet sample, "Combined" column (N = 1,000).
# PDF: https://www.colby.edu/wp-content/uploads/2013/08/Soto_John_2017.pdf
NORMS = {
    "openness": (3.92, 0.65),           # BFI-2 "Open-Mindedness"
    "conscientiousness": (3.43, 0.77),
    "extraversion": (3.23, 0.80),
    "agreeableness": (3.68, 0.64),
    "neuroticism": (3.07, 0.87),        # BFI-2 "Negative Emotionality"
}

# Soto & John (2017), Table 2, p.125: domain intercorrelations, Internet
# sample (the value left of each slash). Order matches TRAITS.
CORR = [
    #  O      C      E      A      N
    [1.00, -0.02,  0.20,  0.15, -0.06],   # openness
    [-0.02, 1.00,  0.22,  0.28, -0.30],   # conscientiousness
    [0.20,  0.22,  1.00,  0.14, -0.34],   # extraversion
    [0.15,  0.28,  0.14,  1.00, -0.29],   # agreeableness
    [-0.06, -0.30, -0.34, -0.29,  1.00],  # neuroticism
]

# (high-pole text, low-pole text). High poles are VERBATIM from the paper's
# Simple Prompt (Figure 2). Low poles are ours, paraphrasing BFI-2
# reverse-keyed items (e.g. "Is relaxed, handles stress well", "Tends to be
# quiet", "Prefers to have others take charge", "Has little interest in
# abstract ideas", "Tends to be disorganized").
GLOSS = {
    "openness": (
        "are imaginative, curious, and creative",
        "are practical, conventional, and prefer familiar routines"),
    "conscientiousness": (
        "are disciplined and dependable",
        "are easygoing, spontaneous, and less organized"),
    "extraversion": (
        "are outgoing, enthusiastic, and enjoy social interactions",
        "are reserved, quiet, and content to let others take charge"),
    "agreeableness": (
        "prioritize harmony and positive relationships",
        "are competitive, skeptical of others, and stand their ground"),
    "neuroticism": (
        "are more emotionally reactive and prone to mood swings",
        "are calm, secure, and emotionally stable"),
}


def _cholesky(matrix):
    """Lower-triangular L with L * L^T = matrix (must be positive definite)."""
    n = len(matrix)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                L[i][j] = (matrix[i][i] - s) ** 0.5
            else:
                L[i][j] = (matrix[i][j] - s) / L[j][j]
    return L


_L = _cholesky(CORR)


def _scores(rng):
    """One person's five trait scores as integers 0-10, jointly sampled."""
    z = [rng.gauss(0, 1) for _ in TRAITS]  # independent standard normals
    scores = {}
    for i, trait in enumerate(TRAITS):
        mean, sd = NORMS[trait]
        corr_z = sum(_L[i][k] * z[k] for k in range(i + 1))  # correlated normal
        x = min(5.0, max(1.0, mean + sd * corr_z))           # truncate to 1-5
        scores[trait] = round((x - 1) / 4 * 10)              # 1-5 -> 0-10
    return scores


def _one(rng):
    scores = _scores(rng)
    lines = []
    for trait in TRAITS:
        high, low = GLOSS[trait]
        lines.append(
            f"People with high {trait} score {high}; "
            f"people with low {trait} score {low}. "
            f"Your {trait} score is {scores[trait]} out of 10."
        )
    lines.append(  # closing line verbatim from the paper's Simple Prompt
        "From now on, you are an agent with this personality, "
        "and you should respond based on this personality."
    )
    return " ".join(lines)


def sample(n, seed=None):
    rng = random.Random(seed)
    return [_one(rng) for _ in range(n)]
