"""A6 — GPS persona: the Global Preferences Survey, used as its own persona format.

Each agent is one draw of the six GPS preferences — patience, risk taking,
positive reciprocity, negative reciprocity, altruism, trust — sampled JOINTLY
from the published individual-level correlation structure, then written out as
that person's answers to the GPS's own eight qualitative survey items
(verbatim wordings, verbatim scale anchors).

Sources (all opened and verified):
- Item wordings + scale anchors: Falk, Becker, Dohmen, Enke, Huffman & Sunde,
  "Global Evidence on Economic Preferences", NBER WP 23943, Appendix A.6
  (pp. 50-53).  https://www.nber.org/system/files/working_papers/w23943/w23943.pdf
  (published as QJE 2018, 133(4), 1645-1692; the WP appendix = the paper's
  Online Appendix. Item-combination weights, if ever needed for composites,
  are in Appendix A.9 — not used here because we render items, not composites.)
- Correlations: NBER WP 23943 Appendix C, Table 12 (printed p. 62): pairwise partial
  correlations between the six preference measures across ~80,000 individuals,
  conditional on country fixed effects; all significant at 1%. The appendix
  notes the unconditional structure is "quantitatively very similar".
- Scale of the latent traits: QJE 2018 p. 1653 — each composite preference is
  standardized to mean 0, sd 1 in the world individual-level sample. Our
  latent z's live on that scale.

Documented assumptions (ours, not GPS's):
- z -> 0-10 answer is round(5 + 2*z) clipped to [0, 10] (i.e. +-2.5 sd spans
  the scale): raw item means/sds are not published. TODO: replace with the
  empirical item distributions once the GPS microdata is downloaded (free
  researcher registration at https://gps.econ.uni-bonn.de/ -> Data; also
  unlocks the Turkey subset, idea B9).
- All items of one preference get the same answer (within-preference item
  correlations are unpublished), so negative reciprocity shows the same
  number on its three items.
- The "(far) above/below the world average" tags bucket the latent z at
  +-0.5 and +-1.5 sd — sd units are how the GPS paper itself reports
  differences; within our sampled population the tags are true by construction.
- We render only the eight qualitative items, not the four quantitative tasks
  (staircases, gift choice, 1,000-euro donation): those are choice tasks, not
  self-descriptions, and mapping z to their answer scales needs the microdata.

Design decision — the old 7th "prosociality (SVO)" dial was REMOVED: it is not
part of the GPS instrument, and drawn independently it could contradict
altruism (same construct, different number — e.g. old seed-1 Player A had
altruism 5 but prosociality 3). The prosocial channel is carried by altruism,
positive reciprocity and trust, which are now properly correlated
(altruism x positive reciprocity r = 0.329).

Sanity checks: run  python personas/gps/check_gps.py
"""

import math
import random

PREFS = ["patience", "risk", "posrec", "negrec", "altruism", "trust"]

# Pairwise correlations between the six preferences at the individual level
# (NBER WP 23943, Appendix C, Table 12, p. 62). NOTE: these are correlations
# between the COMPOSITE preference measures (qualitative + quantitative items
# combined, per A.9); we apply them to the qualitative-item z-scores as an
# approximation. Order matches PREFS.
R = [
    [1.000, 0.210, 0.084, 0.112, 0.098, 0.044],  # patience
    [0.210, 1.000, 0.068, 0.228, 0.106, 0.047],  # risk taking
    [0.084, 0.068, 1.000, 0.010, 0.329, 0.114],  # positive reciprocity
    [0.112, 0.228, 0.010, 1.000, 0.067, 0.075],  # negative reciprocity
    [0.098, 0.106, 0.329, 0.067, 1.000, 0.151],  # altruism
    [0.044, 0.047, 0.114, 0.075, 0.151, 1.000],  # trust
]


def _cholesky(m):
    """Lower-triangular L with L*L^T = m (fails if m is not positive definite)."""
    n = len(m)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(m[i][i] - s) if i == j else (m[i][j] - s) / L[j][j]
    return L


_L = _cholesky(R)


def _draw_traits(rng):
    """One person: six correlated z-scores (world mean 0, sd 1 per trait)."""
    e = [rng.gauss(0, 1) for _ in PREFS]
    return {p: sum(_L[i][j] * e[j] for j in range(i + 1))
            for i, p in enumerate(PREFS)}


def _answer(z):
    """Latent z -> 0-10 integer survey answer (assumes item mean 5, sd 2)."""
    return max(0, min(10, round(5 + 2 * z)))


def _level(z):
    """Relative standing in sd units, the way the GPS paper reports differences."""
    if z < -1.5:
        return "far below the world average"
    if z < -0.5:
        return "below the world average"
    if z <= 0.5:
        return "close to the world average"
    if z <= 1.5:
        return "above the world average"
    return "far above the world average"


# The GPS qualitative module, verbatim (NBER WP 23943, Appendix A.6).
# Four "willingness to act" items (0 = "completely unwilling to do so",
# 10 = "very willing to do so"):
WILLINGNESS_ITEMS = [
    ("patience", "How willing are you to give up something that is beneficial "
                 "for you today in order to benefit more from that in the future?"),
    ("altruism", "How willing are you to give to good causes without expecting "
                 "anything in return?"),
    ("negrec", "How willing are you to punish someone who treats you unfairly, "
               "even if there may be costs for you?"),
    ("negrec", "How willing are you to punish someone who treats others unfairly, "
               "even if there may be costs for you?"),
]
# The risk item, with its own scale anchors:
RISK_ITEM = ("Please tell me, in general, how willing or unwilling you are to "
             "take risks.")
# Three "self-assessment" statements (0 = "does not describe me at all",
# 10 = "describes me perfectly"):
SELF_ASSESSMENT_ITEMS = [
    ("posrec", "When someone does me a favor I am willing to return it."),
    ("negrec", "If I am treated very unjustly, I will take revenge at the first "
               "occasion, even if there is a cost to do so."),
    ("trust", "I assume that people have only the best intentions."),
]


def _one(rng):
    z = _draw_traits(rng)
    a = {p: _answer(z[p]) for p in PREFS}
    lines = ["You answered the Global Preferences Survey (the standard worldwide "
             "survey of economic preferences) as follows."]
    lines.append('Your willingness to act, from 0 ("completely unwilling to do '
                 'so") to 10 ("very willing to do so"):')
    for p, item in WILLINGNESS_ITEMS:
        lines.append(f'- "{item}" — your answer: {a[p]} ({_level((a[p] - 5) / 2)}).')
    lines.append(f'- "{RISK_ITEM}" From 0 ("completely unwilling to take risks") '
                 f'to 10 ("very willing to take risks") — your answer: '
                 f'{a["risk"]} ({_level((a["risk"] - 5) / 2)}).')
    lines.append('How well each statement describes you as a person, from 0 '
                 '("does not describe me at all") to 10 ("describes me perfectly"):')
    for p, item in SELF_ASSESSMENT_ITEMS:
        lines.append(f'- "{item}" — your answer: {a[p]} ({_level((a[p] - 5) / 2)}).')
    lines.append("You are this person; in every decision, act as they would.")
    return "\n".join(lines)


def sample(n, seed=None):
    rng = random.Random(seed)
    return [_one(rng) for _ in range(n)]
