"""A7 — Schwartz Value Anchor (Rozen et al., arXiv:2407.12878).

Persona = the paper's verbatim template "Answer as a person that is [value]",
where [value] is one of the 19 Best-Worst Refined Values descriptions, copied
EXACTLY from the paper's Appendix E (Lee et al. 2019 BWVr; the 20th BWVr item,
animal welfare, is not part of the 19-value Schwartz set and is excluded).
A single anchor produces an internally coherent "individual" whose value
structure matches the human value circle.

Sampling is uniform over the 19 values, as in the paper. TODO for population
realism: reweight by human value prevalence (Schwartz & Cieciuch 2022, N=53k).

NOTE: Appendix E pairs power-dominance with the money/possessions text and
power-resources with the authority text (swapped vs. standard Schwartz
definitions); we keep the paper's texts verbatim — only the comments label them.
"""

import random

ANCHORS = [  # verbatim from Appendix E
    "developing your own original ideas and opinions",                 # self-direction (thought)
    "being free to act independently",                                 # self-direction (action)
    "having an exciting life; having all sorts of new experiences",    # stimulation
    "taking advantage of every opportunity to enjoy life's pleasures", # hedonism
    "being ambitious and successful",                                  # achievement
    "having the power that money and possessions can bring",           # power (dominance, sic)
    "having the authority to get others to do what you want",          # power (resources, sic)
    "protecting your public image and avoiding being shamed",          # face
    "living and acting in ways that ensure that you are personally safe and secure",  # security (personal)
    "living in a safe and stable society",                             # security (societal)
    "following cultural family or religious practices",                # tradition
    "obeying all rules and laws",                                      # conformity (rules)
    "making sure you never upset or annoy others",                     # conformity (interpersonal)
    "being humble and avoiding public recognition",                    # humility
    "being a completely dependable and trustworthy friend and family member",  # benevolence (dependability)
    "helping and caring for the wellbeing of those who are close",     # benevolence (caring)
    "caring and seeking justice for everyone especially the weak and vulnerable in society",  # universalism (concern)
    "protecting the natural environment from destruction or pollution",  # universalism (nature)
    "being open-minded and accepting of people and ideas, even when you disagree with them",  # universalism (tolerance)
]


def sample(n, seed=None):
    rng = random.Random(seed)
    return [f"Answer as a person that is {rng.choice(ANCHORS)}." for _ in range(n)]
