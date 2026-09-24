"""Tests for field_validator module.

Extended coverage
-----------------
- assert_prompt_not_empty: raises ValueError for empty / whitespace (P2-14).
- validate_compile_form target/known_targets params (P1 item 5).
- validate_export_form NOR-condition (P1 item 4).
"""
from __future__ import annotations

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from field_validator import (
    validate_compile_form,
    validate_export_form,
    assert_prompt_not_empty,
)


class AssertPromptNotEmptyTests(unittest.TestCase):
    """P2 fix item 14: service-level guardrail in compile_prompt."""

    def test_raises_on_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            assert_prompt_not_empty("")

    def test_raises_on_whitespace_only(self) -> None:
        with self.assertRaises(ValueError):
            assert_prompt_not_empty("   \n\t  ")

    def test_passes_for_non_empty(self) -> None:
        assert_prompt_not_empty("Write a poem about autumn.")  # must not raise


class ValidateCompileFormTargetTests(unittest.TestCase):
    """P1 fix item 5: target validation added to validate_compile_form."""

    KNOWN = ["gpt4", "codex", "claude"]
    PROMPT = "Summarize the following text in three sentences."

    def test_unknown_target_non_strict_warns(self) -> None:
        result = validate_compile_form(
            self.PROMPT, target="unknown-xyz", known_targets=self.KNOWN, strict=False
        )
        self.assertTrue(result.valid)
        self.assertIn("target", [w["field"] for w in result.warnings])

    def test_unknown_target_strict_errors(self) -> None:
        result = validate_compile_form(
            self.PROMPT, target="unknown-xyz", known_targets=self.KNOWN, strict=True
        )
        self.assertFalse(result.valid)
        self.assertIn("target", [e["field"] for e in result.errors])

    def test_known_target_no_warning(self) -> None:
        result = validate_compile_form(
            self.PROMPT, target="gpt4", known_targets=self.KNOWN
        )
        self.assertTrue(result.valid)
        self.assertEqual(
            [w for w in result.warnings if w["field"] == "target"], []
        )

    def test_no_target_param_is_backward_compatible(self) -> None:
        """Omitting target must not produce any target warning (backward compat)."""
        result = validate_compile_form(self.PROMPT)
        self.assertEqual(
            [w for w in result.warnings if w["field"] == "target"], []
        )


class ValidateCompileFormTests(unittest.TestCase):
    def test_empty_prompt_invalid(self) -> None:
        result = validate_compile_form("")
        self.assertFalse(result.valid)
        self.assertEqual(result.errors[0]["field"], "prompt")

    def test_whitespace_prompt_invalid(self) -> None:
        self.assertFalse(validate_compile_form("   ").valid)

    def test_valid_prompt(self) -> None:
        self.assertTrue(validate_compile_form("Write a poem about spring.").valid)


class ValidateExportFormTests(unittest.TestCase):
    """P1 fix item 4: NOR condition — warn only when BOTH fields are absent."""

    def test_empty_data_errors(self) -> None:
        self.assertFalse(validate_export_form({}).valid)

    def test_optimized_prompt_sufficient(self) -> None:
        result = validate_export_form({"optimized_prompt": "Hello"})
        self.assertTrue(result.valid)
        self.assertEqual(result.warnings, [])

    def test_chosen_nsl_alone_sufficient(self) -> None:
        """chosen_nsl alone must NOT trigger the no_compiled_output warning."""
        result = validate_export_form({"chosen_nsl": "NSL data"})
        self.assertEqual(
            [w for w in result.warnings if w["message"] == "no_compiled_output"], []
        )

    def test_both_absent_warns(self) -> None:
        result = validate_export_form({"other_key": "value"})
        self.assertIn(
            "no_compiled_output", [w["message"] for w in result.warnings]
        )

    def test_unsupported_format_warns(self) -> None:
        result = validate_export_form(
            {"optimized_prompt": "x"}, export_formats=["pdf"]
        )
        self.assertTrue(result.valid)
        self.assertTrue(any(w["field"] == "formats" for w in result.warnings))
