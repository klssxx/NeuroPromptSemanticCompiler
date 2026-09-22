"""Tests for npsc_service.py — covers audit findings P1/P2.

Findings covered:
  P1 — compile_prompt raises on empty/whitespace prompt.
  P1 — compile_for_gui raises on empty/whitespace prompt.
  P1 — compile_for_gui now includes privacy_mode, policy_layer, run_id, strict.
  P1 — compile_for_gui returns consistent keys expected by GUI layer.
  P2 — _resolve_target falls back to 'codex' for unknown targets.
  P2 — compile_for_gui validates target via _resolve_target.
"""
from __future__ import annotations

import pytest

from npsc_service import (
    CompileRequest,
    _resolve_target,
    compile_for_gui,
    compile_prompt,
)


_VALID_PROMPT = (
    "Refactor the authentication module to use JWT tokens "
    "instead of session cookies, keeping all existing tests green."
)


# ---------------------------------------------------------------------------
# _resolve_target (unit — no I/O)
# ---------------------------------------------------------------------------

class TestResolveTarget:
    _PROFILES = {"codex": {}, "gpt4": {}, "claude": {}}

    def test_known_target_returned_as_is(self):
        assert _resolve_target("gpt4", {}, self._PROFILES) == "gpt4"

    def test_unknown_target_falls_back_to_codex(self):
        """P2 fix: unknown target must not reach downstream adapters."""
        result = _resolve_target("nonexistent_xyz", {}, self._PROFILES)
        assert result == "codex"

    def test_auto_resolves_from_semantics_when_known(self):
        semantics = {"target": "claude"}
        assert _resolve_target("auto", semantics, self._PROFILES) == "claude"

    def test_auto_falls_back_when_detected_unknown(self):
        semantics = {"target": "mystery_model"}
        assert _resolve_target("auto", semantics, self._PROFILES) == "codex"

    def test_auto_falls_back_when_target_is_auto(self):
        """'auto' must not be accepted as a resolved target."""
        semantics = {"target": "auto"}
        assert _resolve_target("auto", semantics, self._PROFILES) == "codex"

    def test_auto_falls_back_when_target_is_generic(self):
        semantics = {"target": "generic"}
        assert _resolve_target("auto", semantics, self._PROFILES) == "codex"


# ---------------------------------------------------------------------------
# compile_prompt guardrail (integration — requires full environment)
# ---------------------------------------------------------------------------

class TestCompilePromptGuardrail:
    def test_empty_string_raises(self):
        """P1 fix: compile_prompt must reject empty prompt at service layer."""
        with pytest.raises(ValueError, match="non-empty"):
            compile_prompt(CompileRequest(original=""))

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            compile_prompt(CompileRequest(original="   \n  "))

    def test_valid_prompt_returns_dict(self):
        result = compile_prompt(CompileRequest(original=_VALID_PROMPT))
        assert isinstance(result, dict)
        assert "run_id" in result
        assert "chosen_nsl" in result
        assert "optimized_prompt" in result


# ---------------------------------------------------------------------------
# compile_for_gui guardrails and parity (integration)
# ---------------------------------------------------------------------------

class TestCompileForGuiGuardrail:
    def test_empty_string_raises(self):
        """P1 fix: compile_for_gui must also reject empty prompt."""
        with pytest.raises(ValueError, match="non-empty"):
            compile_for_gui("", "codex", "standard", "profile_default")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            compile_for_gui("  ", "codex", "standard", "profile_default")

    def test_valid_call_returns_expected_keys(self):
        result = compile_for_gui(_VALID_PROMPT, "codex", "standard", "profile_default")
        assert isinstance(result, dict)
        for key in ("run_id", "created_at", "chosen_nsl", "optimized_prompt",
                    "policy_layer", "privacy_mode", "context_loss_report"):
            assert key in result, f"Missing key: {key}"

    def test_run_id_is_non_empty_string(self):
        """P1 fix: GUI path now returns audit trail (run_id)."""
        result = compile_for_gui(_VALID_PROMPT, "codex", "standard", "profile_default")
        assert isinstance(result["run_id"], str) and result["run_id"]

    def test_policy_layer_present(self):
        """P1 fix: policy_layer must appear in GUI result."""
        result = compile_for_gui(_VALID_PROMPT, "codex", "standard", "profile_default")
        pl = result["policy_layer"]
        assert isinstance(pl, dict)
        assert pl.get("origin") == "product_policy"

    def test_privacy_mode_default_is_full_original(self):
        result = compile_for_gui(_VALID_PROMPT, "codex", "standard", "profile_default")
        assert result["privacy_mode"] == "full_original"

    def test_privacy_mode_hash_only_scrubs_output(self):
        """P1 fix: GUI path now honours privacy_mode=hash_only."""
        result = compile_for_gui(
            _VALID_PROMPT, "codex", "standard", "profile_default",
            privacy_mode="hash_only",
        )
        assert result["privacy_mode"] == "hash_only"
        # The optimized prompt must NOT contain raw prompt fragments.
        assert _VALID_PROMPT[:20] not in result["optimized_prompt"]

    def test_unknown_target_falls_back_gracefully(self):
        """P2 fix: compile_for_gui must not crash on unknown target."""
        result = compile_for_gui(
            _VALID_PROMPT, "totally_unknown_model_xyz", "standard", "profile_default"
        )
        # Should complete without exception and resolve to a known target.
        assert result["target"] != "totally_unknown_model_xyz"
        assert isinstance(result["chosen_nsl"], str)

    def test_strict_mode_propagated(self):
        result = compile_for_gui(
            _VALID_PROMPT, "codex", "standard", "profile_default", strict=True
        )
        assert "strict_passed" in result
        assert "strict_failures" in result
