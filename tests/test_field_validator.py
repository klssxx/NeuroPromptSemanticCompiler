"""Tests for field_validator.py — covers audit findings P1/P2.

Fixes covered:
  P1 — validate_export_form AND→OR bug: warn when *either* key is missing.
  P1 — required_fields: empty string treated as missing.
  P1 — target validation placeholder is now implemented.
"""
from __future__ import annotations

import pytest

from field_validator import (
    FieldValidationResult,
    validate_compile_form,
    validate_export_form,
    validate_template_form,
)


# ---------------------------------------------------------------------------
# validate_compile_form
# ---------------------------------------------------------------------------

class TestValidateCompileForm:
    def test_empty_prompt_returns_error(self):
        result = validate_compile_form("")
        assert not result.valid
        assert any(e["message"] == "empty_prompt" for e in result.errors)

    def test_whitespace_only_prompt_returns_error(self):
        result = validate_compile_form("   \n  ")
        assert not result.valid
        assert any(e["message"] == "empty_prompt" for e in result.errors)

    def test_valid_prompt_passes(self):
        result = validate_compile_form("Refactor the login module to use JWT.")
        assert result.valid
        assert result.errors == []

    def test_required_field_empty_string_is_missing(self):
        """P1 fix: empty string must be treated as an unfilled required field."""
        result = validate_compile_form(
            "Do something with {{name}}",
            variables={"name": ""},
            required_fields=["name"],
        )
        # Not strict → warning, not error, but the warning must be present.
        assert any(
            "name" in w["field"] or "name" in w["message"]
            for w in result.warnings
        )

    def test_required_field_empty_string_strict_is_error(self):
        result = validate_compile_form(
            "Do something with {{name}}",
            variables={"name": ""},
            required_fields=["name"],
            strict=True,
        )
        assert not result.valid
        assert any("name" in e["field"] or "name" in e["message"] for e in result.errors)

    def test_required_field_whitespace_only_strict_is_error(self):
        result = validate_compile_form(
            "Do something with {{name}}",
            variables={"name": "   "},
            required_fields=["name"],
            strict=True,
        )
        assert not result.valid

    def test_unknown_target_warning(self):
        """P1 fix: implemented target validation (was a placeholder)."""
        result = validate_compile_form(
            "Rewrite the cache layer.",
            target="nonexistent_model",
            known_targets={"codex", "gpt4", "claude"},
        )
        assert any("unknown_target" in w["message"] for w in result.warnings)
        assert result.valid  # warning, not error

    def test_unknown_target_strict_is_error(self):
        result = validate_compile_form(
            "Rewrite the cache layer.",
            target="nonexistent_model",
            known_targets={"codex", "gpt4"},
            strict=True,
        )
        assert not result.valid
        assert any("unknown_target" in e["message"] for e in result.errors)

    def test_known_target_no_warning(self):
        result = validate_compile_form(
            "Rewrite the cache layer.",
            target="codex",
            known_targets={"codex", "gpt4"},
        )
        assert result.valid
        assert not any("unknown_target" in w["message"] for w in result.warnings)

    def test_no_target_check_when_known_targets_none(self):
        """Passing known_targets=None skips target validation entirely."""
        result = validate_compile_form(
            "Rewrite the cache layer.",
            target="whatever",
            known_targets=None,
        )
        assert result.valid
        assert not any("unknown_target" in w["message"] for w in result.warnings)

    def test_short_prompt_warning(self):
        result = validate_compile_form("short")
        assert any(w["message"] == "prompt_too_short" for w in result.warnings)


# ---------------------------------------------------------------------------
# validate_export_form  —  P1 AND→OR fix
# ---------------------------------------------------------------------------

class TestValidateExportForm:
    def test_missing_both_keys_warns(self):
        """Original AND bug: both absent → warning. Still works after fix."""
        result = validate_export_form({"run_id": "x"})
        assert any("no_compiled_output" in w["message"] for w in result.warnings)

    def test_missing_only_optimized_prompt_warns(self):
        """P1 fix: missing *either* key must warn. Was silently ignored before."""
        result = validate_export_form({"chosen_nsl": "GOAL[refactor]"})
        assert any("no_compiled_output" in w["message"] for w in result.warnings)

    def test_missing_only_chosen_nsl_warns(self):
        """P1 fix: missing *either* key must warn."""
        result = validate_export_form({"optimized_prompt": "Refactor the cache."})
        assert any("no_compiled_output" in w["message"] for w in result.warnings)

    def test_both_keys_present_no_warning(self):
        result = validate_export_form(
            {"optimized_prompt": "Refactor.", "chosen_nsl": "GOAL[refactor]"}
        )
        assert not any("no_compiled_output" in w["message"] for w in result.warnings)
        assert result.valid

    def test_empty_result_data_error(self):
        result = validate_export_form({})
        assert not result.valid
        assert any(e["message"] == "no_result_to_export" for e in result.errors)

    def test_unsupported_format_warning(self):
        result = validate_export_form(
            {"optimized_prompt": "x", "chosen_nsl": "y"},
            export_formats=["pdf"],
        )
        assert any("unsupported_formats" in w["message"] for w in result.warnings)


# ---------------------------------------------------------------------------
# validate_template_form
# ---------------------------------------------------------------------------

class TestValidateTemplateForm:
    def test_empty_name_error(self):
        result = validate_template_form("", "Some content")
        assert not result.valid
        assert any(e["message"] == "template_name_required" for e in result.errors)

    def test_empty_content_error(self):
        result = validate_template_form("my_tpl", "")
        assert not result.valid
        assert any(e["message"] == "template_content_required" for e in result.errors)

    def test_valid_template_passes(self):
        result = validate_template_form("refactor", "Refactor the {{module}} using {{pattern}}.")
        assert result.valid or result.warnings  # may warn about unfilled vars but not error
        assert result.errors == []
