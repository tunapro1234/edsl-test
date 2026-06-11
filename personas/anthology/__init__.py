"""A3 — Anthology narrative backstories (Moon et al. 2024, arXiv:2407.06576).

Persona = a full first-person life story ("backstory") prefixed to every
question, exactly the paper's conditioning move (Section 2.1: backstories as
prefix both explicitly and implicitly encode demographics, values and
personality). The stories are the paper's own released anthology of ~11k
davinci-002 generations (HF: SuhongMoon/anthology_backstory), prepared into
backstories.json by prep.py.

Population targeting: the paper estimates each story's demographics with an
LLM survey and greedy-matches stories to the target human population (Sections
2.3-2.4; greedy beat max-weight, Table 1). We approximate that locally with
AGE-stratified sampling: draw an age bracket from GSS 2024 weighted shares,
then a story from that bracket. Age is the dimension where the raw pool is
most off (59% of stories read as 18-29 vs 20% of US adults). Full 5-variable
matching needs one cheap EP job — see NOTES.md, stage 2.

Adaptation for an instruct model: the paper prefixes the raw
"Question: ... Answer: ..." text and lets a BASE model continue. gpt-oss-120b
is instruction-tuned, so we keep the paper's Q/A block verbatim but add one
bridging line telling the model it IS the person who gave that answer.
"""

import json
import os
import random

# GSS 2024 age-bracket shares, weighted by wtssps. Computed from
# research/datasets/gss/gss7224_r3.dta (year==2024, n=3,208 respondents with
# age) — recompute with: python personas/anthology/prep.py --gss
GSS_AGE_WEIGHTS = {"18-29": 0.201, "30-49": 0.338, "50-64": 0.237, "65+": 0.224}

TEMPLATE = (
    "Before this study you answered an interview question.\n\n"
    "Question: {question}\n\n"
    "Answer: {text}\n\n"
    "You are the person who gave this answer. In everything that follows, "
    "stay in character and decide exactly as this person would."
)

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backstories.json")


def _pools():
    with open(_PATH) as f:
        stories = json.load(f)
    pools = {b: [] for b in GSS_AGE_WEIGHTS}
    for s in stories:
        pools[s["bracket"]].append(s)
    return pools


def sample(n, seed=None):
    """n backstory personas; age brackets drawn i.i.d. from GSS 2024 shares.

    Within a bracket, stories are drawn without replacement (distinct people);
    if a bracket runs out the pool refills — reuse mirrors the paper's greedy
    matching, which also maps several humans to one backstory.
    """
    rng = random.Random(seed)
    pools = _pools()
    shuffled = {}
    for b, pool in pools.items():
        shuffled[b] = pool[:]
        rng.shuffle(shuffled[b])

    out = []
    brackets = list(GSS_AGE_WEIGHTS)
    weights = [GSS_AGE_WEIGHTS[b] for b in brackets]
    for _ in range(n):
        b = rng.choices(brackets, weights=weights)[0]
        if not shuffled[b]:                # bracket exhausted -> refill
            shuffled[b] = pools[b][:]
            rng.shuffle(shuffled[b])
        s = shuffled[b].pop()
        out.append(TEMPLATE.format(question=s["question"], text=s["text"]))
    return out
