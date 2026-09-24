"""Tests for safety_vocabulary.py — P0 fix coverage.

Covers:
1. Every phrase in PHRASES is detectable by canonical_constraints().
2. contains_constraint() works per key.
3. phrases_for() returns empty list for unknown keys.
4. context_loss_verifier no longer contains a hardcoded safety_phrases dict.
5. Both context_loss_verifier and semantic_extractor are importable
   (smoke test — ImportError would fail the test).
"""
from __future__ import annotations

import inspect
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from safety_vocabulary import PHRASES, canonical_constraints, contains_constraint, phrases_for


# ---------------------------------------------------------------------------
# 1. Parametrized phrase coverage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key,phrase", [
    (key, phrase)
    for key, phrases in PHRASES.items()
    for phrase in phrases
])
def test_every_phrase_activates_its_key(key: str, phrase: str) -> None:
    """Each listed phrase must activate its canonical key."""
    text = f"Make sure to follow this rule: {phrase}."
    result = canonical_constraints(text)
    assert key in result, (
        f"Phrase '{phrase}' should activate key '{key}'; got keys: {result}"
    )


# ---------------------------------------------------------------------------
# 2. Neutral text produces no constraints
# ---------------------------------------------------------------------------

def test_neutral_text_returns_empty() -> None:
    assert canonical_constraints("write a haiku about autumn leaves") == []


# ---------------------------------------------------------------------------
# 3. contains_constraint helper
# ---------------------------------------------------------------------------

def test_contains_constraint_true() -> None:
    first_key = next(iter(PHRASES))
    first_phrase = PHRASES[first_key][0]
    assert contains_constraint(f"remember: {first_phrase} always", first_key)


def test_contains_constraint_false() -> None:
    first_key = next(iter(PHRASES))
    assert not contains_constraint("do whatever feels right", first_key)


# ---------------------------------------------------------------------------
# 4. phrases_for unknown key
# ---------------------------------------------------------------------------

def test_phrases_for_unknown_key_returns_empty() -> None:
    assert phrases_for("this_key_does_not_exist_xyz") == []


# ---------------------------------------------------------------------------
# 5. Verifier no longer contains hardcoded safety_phrases dict
# ---------------------------------------------------------------------------

def test_verifier_no_hardcoded_safety_dict() -> None:
    import context_loss_verifier
    source = inspect.getsource(context_loss_verifier)
    assert "safety_phrases = {" not in source, (
        "context_loss_verifier still contains a hardcoded 'safety_phrases' dict. "
        "It must import from safety_vocabulary instead."
    )


# ---------------------------------------------------------------------------
# 6. Import smoke tests
# ---------------------------------------------------------------------------

def test_context_loss_verifier_importable() -> None:
    import context_loss_verifier  # noqa: F401 — ImportError = test failure
    assert callable(context_loss_verifier.verify_context_loss)


def test_semantic_extractor_importable() -> None:
    import semantic_extractor  # noqa: F401 — ImportError = test failure
    # Just importing is enough; the parametrized suite above validates behaviour
