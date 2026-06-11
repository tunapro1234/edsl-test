"""One-time prep: build backstories.json for the anthology persona method.

Source data: the ~11k LLM-generated backstories released by the Anthology paper
(Moon et al. 2024, arXiv:2407.06576, paper 01). Each is a davinci-002 (base
model, T=1.0) completion of "Tell me about yourself..." — see paper App. B.1.
Download: https://huggingface.co/datasets/SuhongMoon/anthology_backstory
(single file anthology_backstory_list.json, 24.6 MB, 11,364 strings of the form
"Question: <interview question>\n\nAnswer: <life story>").

What this script does (each step justified in NOTES.md):
 1. download the raw file if missing (stdlib urllib, ~25 MB)
 2. split each string into (question, answer); drop broken/meta/placeholder texts
 3. trim answers that end mid-sentence back to the last sentence boundary
 4. extract the narrator's age with regexes; keep only stories where it's found
 5. bucket into the 4 ATP age brackets and cap each bracket (deterministic)
 6. write backstories.json (the small file the module reads at sample() time)

Age stratification stands in for the paper's Step 2+3 (LLM demographic survey +
greedy matching): the raw pool is heavily young-skewed (59% age 18-29, 0.7%
65+ among extractable), so unstratified draws would NOT look like the public.

Run:  python personas/anthology/prep.py          (stdlib only)
      python personas/anthology/prep.py --gss    (also recompute GSS weights;
          needs pandas -> use research/datasets/.venv/bin/python)
"""

import json
import os
import re
import random
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "_raw_backstories.json")  # 24.6 MB, ok to delete after
OUT = os.path.join(HERE, "backstories.json")
URL = ("https://huggingface.co/datasets/SuhongMoon/anthology_backstory"
       "/resolve/main/anthology_backstory_list.json")
GSS_DTA = os.path.join(HERE, "..", "..", "..", "research", "datasets", "gss",
                       "gss7224_r3.dta")

PER_BRACKET_CAP = 200  # keeps backstories.json ~1 MB; 65+ only has ~32 anyway
MIN_WORDS = 50         # paper repo drops <=40 *tokens* (backstory.py); ~same bar
PREP_SEED = 0          # which stories make the cap is deterministic

# Texts that are not usable life stories: placeholder brackets like "[city]",
# meta-comments about the question, or AI self-reference. Found by inspection
# of the raw file (30 placeholder/meta + a handful of "(see above)" stories).
BAD = re.compile(
    r"\[(?:city|state|town|name|insert|your)"
    r"|Answer honestly|\(see above\)|\(paraphrased\)|paragraph diatribe"
    r"|\bAs an AI\b|\blanguage model\b",
    re.I,
)

# --- age extraction -------------------------------------------------------
# Patterns tried in order on the first 600 chars (where intros live).
# Tested on the real data: bracket counts 18-29: 2663, 30-49: 1679,
# 50-64: 194, 65+: 32 (40% of stories have an extractable age).
FILLER = (r"(?:a |an |now |currently |already |almost |nearly |over "
          r"|about to turn |just turned |recently turned |more than )*")
P_SELF = re.compile(  # "I am 56," / "I'm a 30 year old" / "I'm 55 and"
    r"\b(?:I am|I'm|I’m) " + FILLER +
    r"(\d{1,2})(?:[\s-]*years?[\s-]old\b|\s*[,.]|\s+and\b| year old\b)", re.I)
P_TURNED = re.compile(r"\bI (?:just|recently) turned (\d{1,2})\b", re.I)
P_DECADE = re.compile(  # "in my early 50s" -> bracket midpoint
    r"\bin my (?:early |mid |late |mid-|early-|late-)?"
    r"(teens|twenties|thirties|forties|fifties|sixties|seventies|eighties"
    r"|20s|30s|40s|50s|60s|70s|80s)\b", re.I)
P_BARE = re.compile(  # "65 years old" only in a first-person clause: requires
    # I/I'm/I am within the preceding few words; excludes "He's 80 years old",
    # "the town is 65 years old" (verifier-found false positives)
    r"\b(?:I am|I'm|I’m|I)\b[^.!?\n]{0,40}?"
    r"\b(\d{1,2})[\s-]+years?[\s-]old\b", re.I)
DECADE_AGE = {"teens": 18, "twenties": 25, "20s": 25, "thirties": 35,
              "30s": 35, "forties": 45, "40s": 45, "fifties": 55, "50s": 55,
              "sixties": 65, "60s": 65, "seventies": 75, "70s": 75,
              "eighties": 85, "80s": 85}


def extract_age(text):
    head = text[:600]
    for pat in (P_SELF, P_TURNED):
        m = pat.search(head)
        if m and 18 <= int(m.group(1)) <= 95:
            return int(m.group(1))
    m = P_DECADE.search(head)
    if m:
        return DECADE_AGE[m.group(1).lower()]
    m = P_BARE.search(head)
    if m and 18 <= int(m.group(1)) <= 95:
        return int(m.group(1))
    return None


def bracket(age):  # the 4 ATP age brackets the paper uses (App. D)
    return "18-29" if age < 30 else "30-49" if age < 50 else \
           "50-64" if age < 65 else "65+"


def trim_to_sentence(text):
    """Cut a generation that stopped mid-sentence back to the last full stop."""
    if text.rstrip().endswith((".", "!", "?", '"', "'", ")")):
        return text.strip()
    cut = max(text.rfind(p) for p in (".", "!", "?"))
    return text[:cut + 1].strip() if cut > 0 else text.strip()


def gss_age_weights():
    """Recompute the GSS 2024 age-bracket shares (needs pandas).

    Source: research/datasets/gss/gss7224_r3.dta, year==2024 respondents
    (n=3,208 with age), weighted by wtssps (GSS post-stratification weight).
    """
    import pandas as pd
    df = pd.read_stata(GSS_DTA, columns=["year", "age", "wtssps"],
                       convert_categoricals=False)
    recent = df[df["year"] == df["year"].max()].dropna(subset=["age"])
    w = {b: 0.0 for b in ("18-29", "30-49", "50-64", "65+")}
    for _, row in recent.iterrows():
        w[bracket(row["age"])] += row["wtssps"]
    total = sum(w.values())
    return {b: round(v / total, 3) for b, v in w.items()}


def main():
    if not os.path.exists(RAW):
        print(f"downloading {URL} ...")
        urllib.request.urlretrieve(URL, RAW)
    with open(RAW) as f:
        raw = json.load(f)
    print(f"raw stories: {len(raw)}")

    pools = {b: [] for b in ("18-29", "30-49", "50-64", "65+")}
    dropped = {"format": 0, "meta": 0, "short": 0, "no_age": 0}
    for item in raw:
        m = re.match(r"Question:\s*(.*?)\n\nAnswer:\s*(.*)", item, re.S)
        if not m:
            dropped["format"] += 1
            continue
        question, answer = m.group(1).strip(), trim_to_sentence(m.group(2))
        if BAD.search(answer):
            dropped["meta"] += 1
            continue
        if len(answer.split()) < MIN_WORDS:
            dropped["short"] += 1
            continue
        age = extract_age(answer)
        if age is None:
            dropped["no_age"] += 1
            continue
        pools[bracket(age)].append(
            {"age": age, "bracket": bracket(age), "question": question,
             "text": answer})

    rng = random.Random(PREP_SEED)
    kept = []
    for b, pool in pools.items():
        rng.shuffle(pool)
        kept += pool[:PER_BRACKET_CAP]
        print(f"bracket {b}: {len(pool)} usable -> kept {min(len(pool), PER_BRACKET_CAP)}")
    print(f"dropped: {dropped}")

    with open(OUT, "w") as f:
        json.dump(kept, f, indent=1)
    print(f"wrote {OUT} ({os.path.getsize(OUT) / 1e6:.2f} MB, {len(kept)} stories)")

    if "--gss" in sys.argv:
        print("GSS 2024 weighted age shares:", gss_age_weights())
        print("(should match GSS_AGE_WEIGHTS in __init__.py)")


if __name__ == "__main__":
    main()
