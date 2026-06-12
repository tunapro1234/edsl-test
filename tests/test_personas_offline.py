"""Offline contract tests for every persona method — no network, no billing.

pytest-compatible; run free with `.venv/bin/python -m tests.run offline`.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from personas import METHODS, sample_personas

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_registry_complete():
    assert len(METHODS) == 9
    for m in METHODS:
        assert os.path.isdir(os.path.join(REPO, "personas", m)), m


def test_deterministic_given_seed():
    for m in METHODS:
        assert sample_personas(m, 4, seed=7) == sample_personas(m, 4, seed=7), m


def test_seed_changes_samples():
    for m in METHODS:
        if m in ("baseline", "homo_silicus", "construction"):
            continue  # seed-invariant by design (empty / quota / balanced)
        assert sample_personas(m, 8, seed=1) != sample_personas(m, 8, seed=2), m


def test_returns_n_strings():
    for m in METHODS:
        ps = sample_personas(m, 5, seed=3)
        assert len(ps) == 5 and all(isinstance(p, str) for p in ps), m


def test_baseline_is_empty():
    assert sample_personas("baseline", 3, seed=1) == ["", "", ""]


def test_persona_lengths_sane():
    # non-baseline personas are non-empty and below ~20k chars (prompt budget)
    for m in METHODS:
        if m == "baseline":
            continue
        for p in sample_personas(m, 4, seed=5):
            assert 20 < len(p) < 20_000, (m, len(p))


def test_no_jinja_collisions():
    # persona text is injected into jinja templates; literal {{ }} would break them
    for m in METHODS:
        for p in sample_personas(m, 6, seed=11):
            assert "{{" not in p and "}}" not in p, m


def test_value_anchor_opposites_pinned():
    # Pins the circle geometry the value_anchor replication gate depends on.
    # The gate (own > mean of 3 "opposite" ratings) cannot itself detect a
    # shuffled circle order — if anchoring works, own is the top score and
    # beats the mean of ANY 3 values — so the opposite sets are asserted here.
    from personas.value_anchor.replication import TEST_ANCHORS, opposites
    expected = {
        "stimulation": [
            "conformity-rules", "conformity-interpersonal", "humility"],
        "power-resources": [
            "benevolence-dependability", "benevolence-caring",
            "universalism-concern"],
        "security-personal": [
            "universalism-nature", "universalism-tolerance",
            "self-direction-thought"],
        "benevolence-caring": [
            "power-resources", "power-dominance", "face"],
    }
    assert TEST_ANCHORS == list(expected)
    for anchor, opp in expected.items():
        assert opposites(anchor) == opp, anchor


def test_agent_banks_stable():
    # frozen econgamebench banks must match what sample_personas regenerates today
    bank_dir = os.path.join(REPO, "benchmark", "econgamebench", "b01", "agents_bank")
    for m in METHODS:
        path = os.path.join(bank_dir, f"{m}.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            bank = json.load(f)
        regen = sample_personas(m, len(bank), seed=1000)
        assert list(bank.values()) == regen, f"{m}: bank drifted from sampler"
