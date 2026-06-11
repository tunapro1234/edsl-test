"""A10 — GSA construction: numeric trait dials (Manning & Horton, arXiv:2508.17407).

Source: "General Social Agents", Appendix A (pp. 48-53 of the arXiv PDF).
One FIXED prompt template with three 1-10 trait dials taken from Charness &
Rabin (2002)'s social-preference model: efficiency, self-interest, inequity
aversion. TEMPLATE below is verbatim from Appendix A.2 (p. 49); between agents
only the numbers vary (fixed wording = no prompt-sensitivity noise, and the
paper shows atheoretical dials like "love of taxidermy" do NOT work — the
theory grounding is what matters).

The population is a uniform mixture over K=3 distinct dial vectors: the paper
assigns the three optimized vectors to three agents and has each play equally
often (50 of 150 reps, p. 50). Vectors come from dials.json when calibrate.py
has been run against OUR model (gpt-oss-120b); until then we use the paper's
published optimum for GPT-4o, found by Bayesian optimization on six CR
unilateral dictator games and validated out-of-sample on 20 two-stage CR games
and 8 novel preregistered three-player games (p. 50):

    (eff, self, ineq) = (7, 10, 10), (3, 1, 3), (1, 10, 2)
"""

import json
import os
import random

# Appendix A.2 (p. 49), quoted verbatim — the dials are the only variable parts.
TEMPLATE = (
    "On a scale from 1 to 10, your efficiency level is: {eff}. 10 means you "
    "strongly prioritize maximizing combined payoffs, and 1 means you don't care. "
    "On a scale from 1 to 10, your self-interest level is: {self}. 10 means you "
    "strongly prioritize your own payoffs, and 1 means you don't care. "
    "On a scale from 1 to 10, your inequity aversion level is: {ineq}. 10 means "
    "you strongly prioritize fairness between players, and 1 means you don't care."
)

# phi* from the paper (p. 50; optimized for GPT-4o); order is (eff, self, ineq).
PAPER_DIALS = [(7, 10, 10), (3, 1, 3), (1, 10, 2)]


def render(d):
    eff, self_, ineq = d
    return TEMPLATE.format(eff=eff, self=self_, ineq=ineq)


def dials():
    """Dial vectors calibrated for our model if available, else the paper's."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dials.json")
    if os.path.exists(path):
        with open(path) as f:
            return [tuple(d) for d in json.load(f)["dials"]]
    return PAPER_DIALS


def sample(n, seed=None):
    """n persona texts, balanced across the K dial vectors, in random order.

    Balanced (not iid) draws mirror the paper's equal play counts and keep a
    4-player group from missing a type by luck.
    """
    rng = random.Random(seed)
    pool = dials()
    chosen = pool * (n // len(pool)) + rng.sample(pool, n % len(pool))
    rng.shuffle(chosen)
    return [render(d) for d in chosen]
