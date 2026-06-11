"""Compute human prevalence weights for the 19 Schwartz value anchors.

Question answered: "what share of people hold each value as their MOST
important one?" — that share is the probability that sample() picks the
matching anchor, so the agent population mirrors the human population.

Data: Lee et al. (2019), "Testing and extending Schwartz refined value
theory using a best-worst scaling approach", Assessment 26(2):166-180 —
the SAME instrument (BWVr) the anchor texts come from. Table 2, Study 2
column (diverse sample of American immigrants, N=439): mean and SD of each
value's best-worst score. A best-worst score is (#times chosen most
important - #times chosen least important) / 5, so it runs from -1 to +1
and measures importance by repeated forced choice. Accepted draft (Table 2
on manuscript p.40): https://api.research-repository.uwa.edu.au/ws/files/
74676908/Lee_et_al_Refined_Values_ASSESSMENT_accepted_draft.pdf

Model: draw a random person's 19 best-worst scores as independent normals
with the published means/SDs; their anchor value is the highest-scoring
one. Repeating this many times gives each value's prevalence.

Checks we ran before trusting Study 2 (see NOTES.md for numbers): its value
ordering matches Study 1's general-adult samples (Spearman .97 USA, .92
Australia) and the 49-country PVQ-RR human benchmark in Rozen et al.
Table 2 (.91); adding the human between-value correlations (Schwartz &
Cieciuch 2022, OSF Table S10) moves every weight by < 0.017, so we keep
independence for simplicity.

Run:  python3 personas/value_anchor/prep_weights.py   (stdlib only, ~10 s)
"""

import json
import os
import random

# Lee et al. (2019) Table 2, Study 2 (N=439): {value: (mean, sd)}.
# The 20th BWVr value, universalism-animals (-.09, .46), is dropped: it is
# not one of the 19 Schwartz values (see Appendix E of Rozen et al.).
LEE_2019_STUDY2 = {
    "self-direction-thought":     ( .18, .39),
    "self-direction-action":      ( .32, .39),
    "stimulation":                ( .07, .43),
    "hedonism":                   ( .18, .45),
    "achievement":                ( .07, .50),
    "power-resources":            (-.33, .48),  # money & possessions anchor
    "power-dominance":            (-.48, .36),  # authority-over-others anchor
    "face":                       (-.29, .37),
    "security-personal":          ( .24, .34),
    "security-societal":          ( .23, .33),
    "tradition":                  (-.30, .47),
    "conformity-rules":           (-.25, .39),
    "conformity-interpersonal":   (-.36, .42),
    "humility":                   (-.15, .35),
    "benevolence-dependability":  ( .42, .37),
    "benevolence-caring":         ( .41, .35),
    "universalism-concern":       ( .18, .40),
    "universalism-nature":        (-.04, .43),
    "universalism-tolerance":     ( .14, .40),
}

DRAWS = 1_000_000
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    rng = random.Random(0)
    values = list(LEE_2019_STUDY2)
    counts = dict.fromkeys(values, 0)
    for _ in range(DRAWS):
        top, top_score = None, float("-inf")
        for v, (mean, sd) in LEE_2019_STUDY2.items():
            score = rng.gauss(mean, sd)
            if score > top_score:
                top, top_score = v, score
        counts[top] += 1

    weights = {v: round(counts[v] / DRAWS, 4) for v in values}
    for v in sorted(values, key=weights.get, reverse=True):
        print(f"  {v:>26}: {weights[v]:.4f}")

    with open(os.path.join(HERE, "weights.json"), "w") as f:
        json.dump({"weights": weights, "draws": DRAWS,
                   "source": "Lee et al. 2019, Table 2, Study 2 (N=439)"}, f, indent=2)
    print("saved weights.json")


if __name__ == "__main__":
    main()
