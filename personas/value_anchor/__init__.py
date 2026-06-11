"""A7 — Schwartz Value Anchor (Rozen et al., arXiv:2407.12878).

Persona = one sentence anchoring the agent on ONE of the 19 refined Schwartz
values (anchor phrasings adapted from the Best-Worst Refined Values scale).
The paper showed this single anchor produces internally coherent "individuals"
whose value structure matches the human value circle.

Sampling is uniform over the 19 values, as in the paper. TODO for population
realism: reweight by human value prevalence (Schwartz & Cieciuch 2022, N=53k).
"""

import random

ANCHORS = [  # 19 refined values
    "thinking up your own original ideas",                          # self-direction (thought)
    "making your own decisions about your life",                    # self-direction (action)
    "having all sorts of new experiences",                          # stimulation
    "enjoying life's pleasures",                                    # hedonism
    "being very successful",                                        # achievement
    "having the power to make people do what you want",             # power (dominance)
    "having wealth and material possessions",                       # power (resources)
    "protecting your public image and avoiding being shamed",       # face
    "living in secure surroundings",                                # security (personal)
    "living in a country that is safe and stable",                  # security (societal)
    "maintaining traditional values and ways of thinking",          # tradition
    "obeying all rules and laws",                                   # conformity (rules)
    "never annoying or upsetting others",                           # conformity (interpersonal)
    "being humble and avoiding public attention",                   # humility
    "being a completely reliable and trustworthy friend",           # benevolence (dependability)
    "caring for and helping the people dear to you",                # benevolence (caring)
    "equal treatment and justice for everyone, even strangers",     # universalism (concern)
    "protecting the natural environment",                           # universalism (nature)
    "understanding people who are different from you",              # universalism (tolerance)
]


def sample(n, seed=None):
    rng = random.Random(seed)
    return [
        f"Answer as a person for whom {rng.choice(ANCHORS)} is the most "
        "important guiding value in life."
        for _ in range(n)
    ]
