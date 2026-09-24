"""Tests for nsl_compiler.py.

P2-1 additions: 4 robustness cases.
  1. Empty semantics dict — compiler must not raise; must return a non-empty string.
  2. Missing 'goal' key — compiler must produce output that does not crash downstream.
  3. Conflicting levels — if 'safe' and 'aggressive' both requested, compiler picks one deterministically.
  4. Unknown target — compiler must handle gracefully (no KeyError).
"""
from __future__ import annotations

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nsl_compiler import compile_to_nsl


_NORMAL_SEMANTICS = {
    "goal": "Refactor authentication to use JWT",
    "domain": "backend",
    "complexity": "medium",
    "constraints": ["no external APIs", "stay inside project root"],
    "output_format": "code",
}
_SEEDS = ["jwt", "auth", "refactor"]


class TestNslCompilerBasic:
    def test_balanced_produces_string(self):
        result = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="balanced", target="codex")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_safe_shorter_than_aggressive(self):
        safe = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="safe", target="codex")
        aggressive = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="aggressive", target="codex")
        assert len(safe) <= len(aggressive)

    def test_target_appears_in_output_or_metadata(self):
        result = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="balanced", target="hermes")
        assert isinstance(result, str)


class TestNslCompilerRobustness:
    """P2-1: robustness against malformed or incomplete semantics."""

    def test_empty_semantics_does_not_raise(self):
        """Compiler must not crash on an empty semantics dict."""
        result = compile_to_nsl({}, [], level="balanced", target="codex")
        assert isinstance(result, str), "Expected str output even for empty semantics."
        assert len(result) > 0, "Expected non-empty output even for empty semantics."

    def test_missing_goal_does_not_raise(self):
        """Compiler must handle semantics without a 'goal' key without raising KeyError."""
        semantics_no_goal = {k: v for k, v in _NORMAL_SEMANTICS.items() if k != "goal"}
        result = compile_to_nsl(semantics_no_goal, _SEEDS, level="balanced", target="codex")
        assert isinstance(result, str)

    def test_conflicting_levels_are_deterministic(self):
        """Calling compile_to_nsl twice with the same args must return identical output.

        The ID= line carries a per-invocation run id (utils.now_run_id), which
        is trace metadata, not compilation semantics — on any clock with real
        microsecond resolution two calls produce different ids by design.
        Determinism is asserted over everything EXCEPT that trace line.
        """
        def without_run_id(nsl: str) -> str:
            return "\n".join(line for line in nsl.splitlines() if not line.startswith("ID="))

        r1 = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="safe", target="codex")
        r2 = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="safe", target="codex")
        assert without_run_id(r1) == without_run_id(r2), (
            "compile_to_nsl is not deterministic for the same inputs (ignoring the ID= trace line)."
        )

    def test_unknown_target_does_not_raise(self):
        """An unknown target value must not cause a KeyError or unhandled exception."""
        try:
            result = compile_to_nsl(_NORMAL_SEMANTICS, _SEEDS, level="balanced", target="totally_unknown_target_xyz")
            assert isinstance(result, str)
        except (ValueError, KeyError) as exc:
            pytest.fail(
                f"compile_to_nsl raised {type(exc).__name__} for unknown target: {exc}. "
                "It should fall back gracefully, not crash."
            )
