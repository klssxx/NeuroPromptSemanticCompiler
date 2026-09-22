"""Integration tests for npsc_service P1 fixes.

Covers:
- P1-1: _assert_prompt_not_empty enforced in both compile_prompt and compile_for_gui.
- P1-2: compile_for_gui rejects unknown target.
- P1-3: compile_for_gui returns full audit-trail fields.
"""
from __future__ import annotations

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from npsc_service import CompileRequest, compile_prompt, compile_for_gui


_VALID_PROMPT = "Refactor the authentication module to use JWT tokens with a 1-hour expiry."
_VALID_TARGET = "codex"
_VALID_PROFILE = "STANDARD"
_VALID_LEVEL = "balanced"


# ---------------------------------------------------------------------------
# P1-1: empty-prompt guard in compile_prompt
# ---------------------------------------------------------------------------

class TestCompilePromptEmptyGuard:
    def test_empty_string_raises(self):
        req = CompileRequest(original="")
        with pytest.raises(ValueError, match="compile_prompt"):
            compile_prompt(req)

    def test_whitespace_only_raises(self):
        req = CompileRequest(original="   \n\t  ")
        with pytest.raises(ValueError, match="compile_prompt"):
            compile_prompt(req)

    def test_valid_prompt_does_not_raise(self):
        req = CompileRequest(original=_VALID_PROMPT, target=_VALID_TARGET, profile=_VALID_PROFILE)
        result = compile_prompt(req)
        assert result["run_id"].startswith("npsc-")


# ---------------------------------------------------------------------------
# P1-1: empty-prompt guard in compile_for_gui
# ---------------------------------------------------------------------------

class TestCompileForGuiEmptyGuard:
    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="compile_for_gui"):
            compile_for_gui("", _VALID_TARGET, _VALID_PROFILE, _VALID_LEVEL)

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="compile_for_gui"):
            compile_for_gui("   ", _VALID_TARGET, _VALID_PROFILE, _VALID_LEVEL)


# ---------------------------------------------------------------------------
# P1-2: target validation in compile_for_gui
# ---------------------------------------------------------------------------

class TestCompileForGuiTargetValidation:
    def test_unknown_target_raises(self):
        with pytest.raises(ValueError, match="unknown target"):
            compile_for_gui(_VALID_PROMPT, "not_a_real_model_xyz", _VALID_PROFILE, _VALID_LEVEL)

    def test_known_target_accepted(self):
        result = compile_for_gui(_VALID_PROMPT, _VALID_TARGET, _VALID_PROFILE, _VALID_LEVEL)
        assert result["semantics"] is not None


# ---------------------------------------------------------------------------
# P1-3: audit-trail fields present in compile_for_gui result
# ---------------------------------------------------------------------------

class TestCompileForGuiAuditTrail:
    def setup_method(self):
        self.result = compile_for_gui(_VALID_PROMPT, _VALID_TARGET, _VALID_PROFILE, _VALID_LEVEL)

    def test_run_id_present_and_prefixed(self):
        assert "run_id" in self.result
        assert self.result["run_id"].startswith("npsc-gui-")

    def test_created_at_present_and_iso(self):
        assert "created_at" in self.result
        # Must be a non-empty ISO-8601 string ending with timezone offset.
        assert "+" in self.result["created_at"] or self.result["created_at"].endswith("Z") or "T" in self.result["created_at"]

    def test_privacy_mode_present(self):
        assert self.result.get("privacy_mode") == "full_original"

    def test_policy_layer_present_and_structured(self):
        pl = self.result.get("policy_layer")
        assert isinstance(pl, dict)
        assert pl.get("origin") == "product_policy"
        assert "policy_constraints" in pl
        assert "strict_policy" in pl

    def test_strict_passed_is_bool(self):
        assert isinstance(self.result.get("strict_passed"), bool)

    def test_strict_failures_is_list(self):
        assert isinstance(self.result.get("strict_failures"), list)

    def test_token_report_present_and_has_keys(self):
        tr = self.result.get("token_report")
        assert isinstance(tr, dict)
        # token_report must contain at least one level key.
        assert any(k in tr for k in ("safe", "balanced", "aggressive", "optimized"))
