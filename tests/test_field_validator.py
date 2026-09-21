from __future__ import annotations

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from field_validator import (
    FieldValidationResult,
    validate_compile_form,
    validate_export_form,
    validate_template_form,
    assert_prompt_not_empty,
)


class AssertPromptNotEmptyTests(unittest.TestCase):
    """P2 fix item 14: service-level guardrail."""

    def test_raises_on_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            assert_prompt_not_empty("")

    def test_raises_on_whitespace_only(self) -> None:
        with self.assertRaises(ValueError):
            assert_prompt_not_empty("   \n\t  ")

    def test_passes_for_non_empty(self) -> None:
        assert_prompt_not_empty("Write a poem about autumn.")  # must not raise


class ValidateCompileFormTargetTests(unittest.TestCase):
    """P1 fix item 5: target validation in validate_compile_form."""

    KNOWN = ["gpt4", "codex", "claude"]
    PROMPT = "Summarize the following text in three sentences."

    def test_unknown_target_non_strict_emits_warning(self) -> None:
        result = validate_compile_form(
            self.PROMPT,
            target="unknown-model-xyz",
            known_targets=self.KNOWN,
            strict=False,
        )
        self.assertTrue(result.valid)
        self.assertIn("target", [w["field"] for w in result.warnings])

    def test_unknown_target_strict_emits_error(self) -> None:
        result = validate_compile_form(
            self.PROMPT,
            target="unknown-model-xyz",
            known_targets=self.KNOWN,
            strict=True,
        )
        self.assertFalse(result.valid)
        self.assertIn("target", [e["field"] for e in result.errors])

    def test_known_target_no_warning(self) -> None:
        result = validate_compile_form(
            self.PROMPT,
            target="gpt4",
            known_targets=self.KNOWN,
        )
        self.assertTrue(result.valid)
        self.assertEqual([w for w in result.warnings if w["field"] == "target"], [])

    def test_no_target_param_skips_validation(self) -> None:
        """Backward compat: omitting target must not add any target warning."""
        result = validate_compile_form(self.PROMPT)
        self.assertEqual([w for w in result.warnings if w["field"] == "target"], [])


class ValidateCompileFormTests(unittest.TestCase):
    def test_empty_prompt_returns_error(self) -> None:
        result = validate_compile_form("")
        self.assertFalse(result.valid)
        self.assertEqual(result.errors[0]["field"], "prompt")

    def test_whitespace_prompt_returns_error(self) -> None:
        result = validate_compile_form("   ")
        self.assertFalse(result.valid)

    def test_valid_prompt_returns_valid(self) -> None:
        result = validate_compile_form("Write a poem about spring.")
        self.assertTrue(result.valid)


class ValidateExportFormTests(unittest.TestCase):
    def test_empty_result_data_returns_error(self) -> None:
        result = validate_export_form({})
        self.assertFalse(result.valid)

    def test_result_with_optimized_prompt_valid(self) -> None:
        result = validate_export_form({"optimized_prompt": "Hello"})
        self.assertTrue(result.valid)
        self.assertEqual(result.warnings, [])

    def test_result_with_chosen_nsl_only_no_warning(self) -> None:
        """NOR: chosen_nsl alone is sufficient — no warning."""
        result = validate_export_form({"chosen_nsl": "NSL content"})
        self.assertTrue(result.valid)
        self.assertEqual(
            [w for w in result.warnings if w["message"] == "no_compiled_output"], []
        )

    def test_result_missing_both_fields_warns(self) -> None:
        """NOR: warning fires only when BOTH keys are absent."""
        result = validate_export_form({"some_other_key": "value"})
        self.assertIn("no_compiled_output", [w["message"] for w in result.warnings])

    def test_unsupported_format_warns(self) -> None:
        result = validate_export_form(
            {"optimized_prompt": "hello"},
            export_formats=["pdf"],
        )
        self.assertTrue(result.valid)
        self.assertTrue(len([w for w in result.warnings if w["field"] == "formats"]) > 0)
