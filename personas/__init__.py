"""Persona injection methods — pick one, get persona texts.

Each method lives in its own folder and exposes:  sample(n, seed) -> list[str]
returning n persona texts (empty string = no persona). Games prepend the text
to every question via a scenario field, so each player keeps their persona for
the whole game.

Usage (repo root on sys.path):
    from personas import sample_personas, METHODS
    texts = sample_personas("big5", n=4, seed=1)

See METHODS.md for what each method is and ROADMAP.md for what's coming.
"""

import importlib

METHODS = [
    "baseline",      # control: bare model
    "homo_silicus",  # A8/A9: one-sentence preference types, Horton mixture
    "big5",          # A5: numeric Big Five dials from population norms
    "value_anchor",  # A7: Schwartz value anchor
    "gps",           # A6: Falk economic preferences + SVO dials
    "construction",  # A10: GSA-style behavioral trait dials
    "demographic",   # A1/A2: Argyle template from GSS microdata rows
    "anthology",     # A3: narrative backstories
    "twin2k",        # A11: real-person summaries (Twin-2K-500)
]


def sample_personas(method, n, seed=None):
    if method not in METHODS:
        raise ValueError(f"unknown persona method {method!r}; choose from {METHODS}")
    return importlib.import_module(f"personas.{method}").sample(n, seed)
