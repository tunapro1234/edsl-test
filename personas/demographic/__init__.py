"""A1/A2 — Argyle silicon sampling from real GSS 2024 rows (paper 08).

Each persona is a first-person backstory built from ONE real respondent of the
GSS 2024 cross-section (NORC public-use microdata; prepared into gss_sample.csv
by prepare.py). Fragment style follows Argyle et al. Fig. 1 ("Racially, I am
white. I am male. Financially, I am upper-class.") and App. C.1: survey answers
translated into short first-person declarations, age inserted directly, and a
missing answer simply drops its fragment. Because every backstory is a real
row, the JOINT distribution of traits is the real one — that is the method.

Rows are drawn with the GSS survey weight WTSSNRPS (NORC's recommended weight,
GSS 2024 Codebook R3, Weights section), so the sampled population matches US
adults, not the raw respondent pool. Draws avoid repeating a respondent while
unused rows remain. Deterministic given seed; stdlib only.

One adaptation: Argyle conditioned a base model on the bare backstory; our
chat model gets the same verbatim fragments wrapped in a two-line role frame,
otherwise it reads "I am female..." as the experimenter describing themselves.
"""

import csv
import os
import random

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gss_sample.csv")

# Value -> fragment maps. Keys are the exact GSS 2024 category labels found in
# gss_sample.csv (verified against the data); unmapped or missing -> omit.
RACE = {  # race + hispanic are collapsed ANES-style, see _fragments()
    "white": "Racially, I am white.",
    "black": "Racially, I am Black.",
    "other": "Racially, I am of another race.",
}
SEX = {"male": "I am male.", "female": "I am female."}
REGION = {
    "northeast": "I live in the Northeast of the United States.",
    "midwest": "I live in the Midwest of the United States.",
    "south": "I live in the South of the United States.",
    "west": "I live in the West of the United States.",
}
MARITAL = {
    "married": "I am married.",
    "widowed": "I am widowed.",
    "divorced": "I am divorced.",
    "separated": "I am separated.",
    "never married": "I have never been married.",
}
DEGREE = {
    "less than high school": "I did not finish high school.",
    "high school": "I have a high school diploma.",
    "associate/junior college": "I have an associate degree.",
    "bachelor's": "I have a bachelor's degree.",
    "graduate": "I have a graduate degree.",
}
WRKSTAT = {
    "working full time": "I work full time.",
    "working part time": "I work part time.",
    "with a job, but not at work because of temporary illness, vacation, strike":
        "I have a job but am temporarily not at work.",
    "unemployed, laid off, looking for work": "I am unemployed and looking for work.",
    "retired": "I am retired.",
    "in school": "I am in school.",
    "keeping house": "I keep house.",
    # "other" carries no usable description -> omitted like a missing value
}
CLASS = {  # GSS asks which class "you belong in"; Argyle's financial fragment
    "lower class": "Financially, I belong to the lower class.",
    "working class": "Financially, I belong to the working class.",
    "middle class": "Financially, I belong to the middle class.",
    "upper class": "Financially, I belong to the upper class.",
}
RELIG = {
    "protestant": "Religiously, I am Protestant.",
    "catholic": "Religiously, I am Catholic.",
    "christian": "Religiously, I am Christian.",
    "orthodox-christian": "Religiously, I am Orthodox Christian.",
    "inter-nondenominational": "Religiously, I belong to an interdenominational church.",
    "jewish": "Religiously, I am Jewish.",
    "muslim/islam": "Religiously, I am Muslim.",
    "buddhism": "Religiously, I am Buddhist.",
    "hinduism": "Religiously, I am Hindu.",
    "other eastern religions": "Religiously, I follow an Eastern religion.",
    "native american": "Religiously, I follow a Native American religion.",
    "other": "Religiously, I belong to another religion.",
    "none": "I have no religion.",
}
ATTEND = {
    "never": "I never attend religious services.",
    "less than once a year": "I attend religious services less than once a year.",
    "about once or twice a year": "I attend religious services about once or twice a year.",
    "several times a year": "I attend religious services several times a year.",
    "about once a month": "I attend religious services about once a month.",
    "2-3 times a month": "I attend religious services two or three times a month.",
    "nearly every week": "I attend religious services nearly every week.",
    "every week": "I attend religious services every week.",
    "several times a week": "I attend religious services several times a week.",
}
PARTYID = {
    "strong democrat": "Politically, I am a strong Democrat.",
    "not very strong democrat": "Politically, I am a not very strong Democrat.",
    "independent, close to democrat": "Politically, I am an independent who leans Democratic.",
    "independent (neither, no response)": "Politically, I am an independent.",
    "independent, close to republican": "Politically, I am an independent who leans Republican.",
    "not very strong republican": "Politically, I am a not very strong Republican.",
    "strong republican": "Politically, I am a strong Republican.",
    "other party": "Politically, I support a third party.",
}
POLVIEWS = {
    "extremely liberal": "Ideologically, I describe myself as extremely liberal.",
    "liberal": "Ideologically, I describe myself as liberal.",
    "slightly liberal": "Ideologically, I describe myself as slightly liberal.",
    "moderate, middle of the road": "Ideologically, I describe myself as moderate, middle of the road.",
    "slightly conservative": "Ideologically, I describe myself as slightly conservative.",
    "conservative": "Ideologically, I describe myself as conservative.",
    "extremely conservative": "Ideologically, I describe myself as extremely conservative.",
}

_ROWS, _WEIGHTS = None, None  # loaded once per process


def _load():
    global _ROWS, _WEIGHTS
    if _ROWS is None:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(
                f"{CSV_PATH} not found — run personas/demographic/prepare.py first "
                "(needs pandas, e.g. system python3)")
        with open(CSV_PATH, newline="") as f:
            _ROWS = list(csv.DictReader(f))
        _WEIGHTS = [float(r["weight"]) for r in _ROWS]
    return _ROWS, _WEIGHTS


def _age_fragment(age):
    if age == "89+":
        return "I am 89 years old or older."
    return f"I am {age} years old."


def _children_fragment(childs):
    if childs == "0":
        return "I have no children."
    if childs == "1":
        return "I have one child."
    if childs == "8+":
        return "I have eight or more children."
    return f"I have {childs} children."


def _fragments(r):
    """One respondent row -> list of Argyle-style first-person fragments."""
    out = []
    # race/ethnicity collapsed like the ANES variable Argyle used: any Hispanic
    # origin -> "Hispanic" (his Fig. 1 shows "Racially, I am hispanic."),
    # otherwise the GSS race answer.
    if r["hispanic"] and r["hispanic"] != "not hispanic":
        out.append("Racially, I am Hispanic.")
    elif r["race"]:
        out.append(RACE.get(r["race"], ""))
    if r["born"] == "no":  # mention only the marked case
        out.append("I was not born in the United States.")
    out.append(SEX.get(r["sex"], ""))
    if r["age"]:
        out.append(_age_fragment(r["age"]))
    out.append(REGION.get(r["region"], ""))
    out.append(MARITAL.get(r["marital"], ""))
    if r["childs"]:
        out.append(_children_fragment(r["childs"]))
    out.append(DEGREE.get(r["degree"], ""))
    out.append(WRKSTAT.get(r["wrkstat"], ""))
    if r["income16"]:  # bracket text inserted directly, like Argyle's age/state
        out.append(f"My total family income is {r['income16']} a year.")
    out.append(CLASS.get(r["class"], ""))
    out.append(RELIG.get(r["relig"], ""))
    out.append(ATTEND.get(r["attend"], ""))
    out.append(PARTYID.get(r["partyid"], ""))
    out.append(POLVIEWS.get(r["polviews"], ""))
    return [f for f in out if f]


def _render(r):
    backstory = " ".join(_fragments(r))
    return ("In a survey, you described yourself in these words: "
            f'"{backstory}" You are this person, and you answer every question '
            "the way this person would.")


def sample(n, seed=None):
    rng = random.Random(seed)
    rows, weights = _load()
    chosen = []
    while len(chosen) < n:
        i = rng.choices(range(len(rows)), weights=weights, k=1)[0]
        if i in chosen and len(chosen) < len(rows):
            continue  # no duplicate respondents while unused rows remain
        chosen.append(i)
    return [_render(rows[i]) for i in chosen]
