"""Tests for variables.py.

P2-2 addition: empty-string fill counts as unfilled.
Verifies that a {{variable}} whose fill value is "" (empty string) is treated
as unfilled — the same invariant that applies to None or whitespace-only.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from variables import extract_variables, fill_variables, has_unfilled_variables


class TestExtractVariables:
    def test_no_variables(self):
        assert extract_variables("Hello world") == []

    def test_single_variable(self):
        result = extract_variables("Hello {{name}}")
        assert result == ["name"]

    def test_multiple_variables(self):
        result = extract_variables("{{greeting}} {{name}}, do {{task}}")
        assert set(result) == {"greeting", "name", "task"}

    def test_duplicate_variable_reported_once(self):
        result = extract_variables("{{x}} and {{x}} again")
        assert result.count("x") == 1

    def test_nested_braces_ignored(self):
        result = extract_variables("{not_a_var} and {{real_var}}")
        assert result == ["real_var"]


class TestFillVariables:
    def test_fill_single(self):
        text, unfilled = fill_variables("Hello {{name}}", {"name": "Alice"})
        assert "Alice" in text
        assert unfilled == []

    def test_fill_partial_leaves_unfilled(self):
        text, unfilled = fill_variables("{{a}} and {{b}}", {"a": "yes"})
        assert "yes" in text
        assert "b" in unfilled

    def test_fill_all_variables(self):
        text, unfilled = fill_variables("{{x}} + {{y}}", {"x": "1", "y": "2"})
        assert unfilled == []
        assert "1" in text and "2" in text


class TestHasUnfilledVariables:
    def test_no_variables_returns_false(self):
        assert has_unfilled_variables("plain text") is False

    def test_unfilled_variable_returns_true(self):
        assert has_unfilled_variables("Do {{task}} now") is True

    def test_filled_text_returns_false(self):
        text, _ = fill_variables("Do {{task}} now", {"task": "something"})
        assert has_unfilled_variables(text) is False


class TestEmptyStringFillIsUnfilled:
    """P2-2: empty-string fill must be treated as unfilled.

    Rationale: a caller that sets variables={"task": ""} has not meaningfully
    filled the placeholder.  Treating it as filled would silently produce a
    prompt with an invisible hole, which is worse than leaving the placeholder
    visible.  The invariant is: fill value must be a non-empty, non-whitespace
    string to count as a completed fill.
    """

    def test_empty_string_value_leaves_variable_unfilled(self):
        _text, unfilled = fill_variables("Do {{task}} carefully.", {"task": ""})
        assert "task" in unfilled, (
            "Expected 'task' to appear in unfilled when fill value is empty string, "
            f"but unfilled={unfilled!r}"
        )

    def test_whitespace_only_value_leaves_variable_unfilled(self):
        _text, unfilled = fill_variables("Result: {{output}}", {"output": "   "})
        assert "output" in unfilled, (
            "Expected 'output' to appear in unfilled when fill value is whitespace-only, "
            f"but unfilled={unfilled!r}"
        )

    def test_none_value_leaves_variable_unfilled(self):
        _text, unfilled = fill_variables("Target: {{model}}", {"model": None})
        assert "model" in unfilled, (
            "Expected 'model' to appear in unfilled when fill value is None, "
            f"but unfilled={unfilled!r}"
        )

    def test_valid_fill_is_still_accepted(self):
        _text, unfilled = fill_variables("Do {{task}} carefully.", {"task": "refactor auth"})
        assert "task" not in unfilled, (
            "A non-empty fill value must not appear in unfilled."
        )
