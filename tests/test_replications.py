"""Paper-replication assertions — read saved artifacts, never call the API.

Each persona method's replication.py (run manually, costs money) writes
personas/<method>/replication.json:
    {"method", "model", "experiment", "paper_targets": {...},
     "results": {...}, "pass": bool, "criteria": "...", "n_calls",
     "cost_estimate_usd", "timestamp"}

These tests assert pass==true per artifact; missing artifact = SKIP (the
replication simply hasn't been run yet), a failed replication = FAIL.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import Skip

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPLICATED = ["homo_silicus", "big5", "value_anchor", "gps", "construction",
              "demographic", "anthology", "twin2k"]


def _artifact(method):
    path = os.path.join(REPO, "personas", method, "replication.json")
    if not os.path.exists(path):
        raise Skip(f"{method}/replication.json not generated yet")
    with open(path) as f:
        return json.load(f)


def _check(method):
    art = _artifact(method)
    for key in ("paper_targets", "results", "criteria", "model"):
        assert key in art, f"{method}: artifact missing {key}"
    assert art["pass"] is True, (
        f"{method}: replication FAILED criteria '{art['criteria']}' — "
        f"targets {art['paper_targets']} vs results {art['results']}")


def test_replication_homo_silicus():
    _check("homo_silicus")


def test_replication_big5():
    _check("big5")


def test_replication_value_anchor():
    _check("value_anchor")


def test_replication_gps():
    _check("gps")


def test_replication_construction():
    _check("construction")


def test_replication_demographic():
    _check("demographic")


def test_replication_anthology():
    _check("anthology")


def test_replication_twin2k():
    _check("twin2k")
