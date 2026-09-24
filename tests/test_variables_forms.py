"""Tests for variables.py form and template-validation contracts.

Restored historical coverage (A.6 integrity audit): the PR that rewrote
``test_variables.py`` for the renamed detection API dropped the tests for
``build_fill_form`` / ``VariableFillForm`` / ``validate_template`` / strict
fills. Those behaviours are still part of the shipped contract (consumed by
``field_validator`` and the GUI), so they are re-asserted here.

The only historical expectation intentionally NOT restored verbatim is the
old "empty string replaces the variable" fill behaviour: the fill contract
changed (P2-2) so that empty/whitespace/None values count as unfilled and the
placeholder stays visible. That change is covered in ``test_variables.py``.
"""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from variables import (
    VariableDefinition,
    build_fill_form,
    extract_variables,
    fill_variables,
    validate_template,
)


class VariableDetectionAliasTests:
    """extract_variables keeps the semantics of the old detect_variables."""

    def test_detect_single_variable(self):
        assert extract_variables("Hola {{nombre}}, bienvenido") == ["nombre"]

    def test_detect_multiple_variables_sorted_unique(self):
        result = extract_variables("{{proyecto}} usa {{lenguaje}} en {{sistema}}")
        assert result == ["lenguaje", "proyecto", "sistema"]

    def test_duplicate_variables_reported_once(self):
        assert extract_variables("{{nombre}} y {{nombre}} otra vez") == ["nombre"]

    def test_empty_text(self):
        assert extract_variables("") == []


class VariableFillTests:
    def test_fill_multiple_variables(self):
        text, unfilled = fill_variables(
            "{{proyecto}} usa {{lenguaje}}",
            {"proyecto": "MiApp", "lenguaje": "Python"},
        )
        assert text == "MiApp usa Python"
        assert unfilled == []

    def test_fill_missing_variable_non_strict_keeps_placeholder(self):
        text, unfilled = fill_variables(
            "Hola {{nombre}}, bienvenido a {{lugar}}", {"nombre": "Ana"}
        )
        assert text == "Hola Ana, bienvenido a {{lugar}}"
        assert unfilled == ["lugar"]

    def test_fill_missing_variable_strict_raises(self):
        with pytest.raises(ValueError):
            fill_variables("Hola {{nombre}}", {}, strict=True)

    def test_fill_empty_string_strict_raises(self):
        # P2-2: empty string is NOT a valid fill, so strict mode must reject it.
        with pytest.raises(ValueError):
            fill_variables("Hola {{nombre}}", {"nombre": ""}, strict=True)


class VariableFormTests:
    def test_build_form_detects_variables(self):
        text = "Proyecto: {{nombre}}, Lenguaje: {{lang}}"
        form = build_fill_form(text)
        assert "nombre" in form.variables
        assert "lang" in form.variables

    def test_form_complete_when_all_filled(self):
        form = build_fill_form("{{a}} y {{b}}")
        form.set_value("a", "1")
        form.set_value("b", "2")
        assert form.is_complete() is True

    def test_form_incomplete_when_required_missing(self):
        text = "{{a}} y {{b}}"
        form = build_fill_form(text, overrides={"a": VariableDefinition(name="a", required=True)})
        assert form.is_complete() is False
        assert form.missing_required() == ["a"]

    def test_form_unfilled_list(self):
        form = build_fill_form("{{a}} y {{b}}")
        form.set_value("a", "1")
        assert form.unfilled() == ["b"]


class TemplateValidationTests:
    def test_valid_template(self):
        result = validate_template("Hola {{nombre}}")
        assert result["valid"] is True
        assert result["variables"] == ["nombre"]

    def test_empty_template(self):
        result = validate_template("")
        assert result["valid"] is False
        assert "empty_template" in result["errors"]

    def test_no_variables_template(self):
        result = validate_template("Texto sin variables")
        assert result["valid"] is True
        assert result["variables"] == []
