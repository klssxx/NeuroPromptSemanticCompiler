from __future__ import annotations

import unittest
from field_validator import validate_compile_form, validate_template_form, validate_export_form


class CompileFormValidationTests(unittest.TestCase):
    def test_empty_prompt_error(self) -> None:
        result = validate_compile_form("")
        self.assertFalse(result.valid)
        self.assertTrue(any(e["field"] == "prompt" for e in result.errors))

    def test_valid_prompt(self) -> None:
        result = validate_compile_form("Write a Python function to sort a list")
        self.assertTrue(result.valid)

    def test_unfilled_variables_warning(self) -> None:
        result = validate_compile_form("Create {{project}} using {{language}}")
        self.assertTrue(result.valid)  # Not an error, just warning
        self.assertTrue(any(w["field"] == "variables" for w in result.warnings))

    def test_unfilled_variables_strict_error(self) -> None:
        result = validate_compile_form("Create {{project}}", strict=True)
        self.assertFalse(result.valid)

    def test_short_prompt_warning(self) -> None:
        result = validate_compile_form("Hi")
        self.assertTrue(result.valid)
        self.assertTrue(any("short" in w["message"] for w in result.warnings))


class TemplateFormValidationTests(unittest.TestCase):
    def test_empty_name_error(self) -> None:
        result = validate_template_form("", "content")
        self.assertFalse(result.valid)

    def test_empty_content_error(self) -> None:
        result = validate_template_form("name", "")
        self.assertFalse(result.valid)

    def test_valid_template(self) -> None:
        result = validate_template_form("My Template", "Hello {{name}}")
        self.assertTrue(result.valid)


class ExportFormValidationTests(unittest.TestCase):
    def test_no_result_error(self) -> None:
        result = validate_export_form({})
        self.assertFalse(result.valid)

    def test_valid_result(self) -> None:
        result = validate_export_form({"optimized_prompt": "test"})
        self.assertTrue(result.valid)
