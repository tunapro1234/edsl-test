"""A7 — Schwartz Value Anchor (Rozen et al., arXiv:2407.12878).

Persona = the paper's verbatim template "Answer as a person that is [value]"
(p.4, "Value Anchor prompt"), where [value] is one of the 19 Best-Worst
Refined Values descriptions copied EXACTLY from the paper's Appendix E
(Lee et al. 2019 BWVr; the 20th BWVr item, animal welfare, is not part of
the 19-value Schwartz set and is excluded). The paper shows a single bare
anchor makes the model score nearby values high and distant values low —
one coherent "individual" on the human value circle — so we add nothing
(no "most important value in life" framing) to the validated wording.

Sampling: each anchor is drawn with the probability that a real person
holds that value as their MOST important one. Weights live in weights.json
(written by prep_weights.py from Lee et al. 2019 best-worst data — see that
file for sources); without the file we fall back to uniform, as in the paper.

NOTE: Appendix E swaps the labels of items 6 and 7 — it pairs
"power-dominance" with the money/possessions text and "power-resources"
with the authority text. In every Schwartz instrument (e.g., PVQ-RR items:
power-resources = "the power that money can bring", power-dominance =
"tells others what to do") it is the other way around. We keep the paper's
TEXTS verbatim but file them under the standard value codes, so the
prevalence weights attach to the right text.
"""

import json
import os
import random

ANCHORS = {  # value code -> verbatim Appendix E description (items 1-19)
    "self-direction-thought": "developing your own original ideas and opinions",
    "self-direction-action": "being free to act independently",
    "stimulation": "having an exciting life; having all sorts of new experiences",
    "hedonism": "taking advantage of every opportunity to enjoy life's pleasures",
    "achievement": "being ambitious and successful",
    "power-resources": "having the power that money and possessions can bring",
    "power-dominance": "having the authority to get others to do what you want",
    "face": "protecting your public image and avoiding being shamed",
    "security-personal": "living and acting in ways that ensure that you are personally safe and secure",
    "security-societal": "living in a safe and stable society",
    "tradition": "following cultural family or religious practices",
    "conformity-rules": "obeying all rules and laws",
    "conformity-interpersonal": "making sure you never upset or annoy others",
    "humility": "being humble and avoiding public recognition",
    "benevolence-dependability": "being a completely dependable and trustworthy friend and family member",
    "benevolence-caring": "helping and caring for the wellbeing of those who are close",
    "universalism-concern": "caring and seeking justice for everyone especially the weak and vulnerable in society",
    "universalism-nature": "protecting the natural environment from destruction or pollution",
    "universalism-tolerance": "being open-minded and accepting of people and ideas, even when you disagree with them",
}


def weights():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["weights"]
    return {value: 1 for value in ANCHORS}  # uniform, as in the paper


def sample(n, seed=None):
    rng = random.Random(seed)
    w = weights()
    values = rng.choices(list(ANCHORS), weights=[w[v] for v in ANCHORS], k=n)
    return [f"Answer as a person that is {ANCHORS[v]}." for v in values]
