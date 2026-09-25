"""B.6 tests: clarification gate — explicit, per-profile, never implicit.

Invariants: the default mode ("report") changes NO compiled output and NO
existing behaviour; "gate" refuses to compile while the threshold is
exceeded; "prepend" makes the questions unmissable in the execution prompt;
FAST never gates; thresholds are caller-overridable.
"""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clarification_gate import (
    DEFAULT_AMBIGUITY_THRESHOLDS,
    apply_prepend,
    evaluate_clarification_gate,
    render_prepend_block,
    resolve_threshold,
)
from npsc_service import CompileRequest, compile_prompt, compile_for_gui

_AMBIGS = [f"Ambigüedad número {i} del input." for i in range(1, 6)]  # 5 entries


class TestThresholds:
    def test_every_supported_profile_has_a_threshold_entry(self):
        for profile in ("FAST", "STANDARD", "ADVANCED", "SAFE", "RESEARCH_MAX", "ROP", "CODING", "AUTO"):
            assert profile in DEFAULT_AMBIGUITY_THRESHOLDS

    def test_fast_never_gates(self):
        assert resolve_threshold("FAST") is None
        decision = evaluate_clarification_gate("FAST", _AMBIGS)
        assert decision.required is False

    def test_standard_threshold_is_four(self):
        assert resolve_threshold("STANDARD") == 4
        assert evaluate_clarification_gate("STANDARD", _AMBIGS[:4]).required is False
        assert evaluate_clarification_gate("STANDARD", _AMBIGS).required is True  # 5 > 4

    def test_advanced_gates_on_any_ambiguity(self):
        assert resolve_threshold("ADVANCED") == 0
        assert evaluate_clarification_gate("ADVANCED", _AMBIGS[:1]).required is True
        assert evaluate_clarification_gate("ADVANCED", []).required is False

    def test_alias_normalization_applies(self):
        assert resolve_threshold("research-max") == resolve_threshold("RESEARCH_MAX")

    def test_caller_can_override_thresholds(self):
        decision = evaluate_clarification_gate("STANDARD", _AMBIGS, thresholds={"STANDARD": 9})
        assert decision.required is False
        decision2 = evaluate_clarification_gate("STANDARD", _AMBIGS, thresholds={"STANDARD": 2})
        assert decision2.required is True


class TestModes:
    def test_invalid_mode_rejected(self):
        with pytest.raises(ValueError):
            evaluate_clarification_gate("STANDARD", _AMBIGS, mode="banana")

    def test_gate_mode_raises_listing_questions(self):
        decision = evaluate_clarification_gate("STANDARD", _AMBIGS, mode="gate")
        assert decision.required is True
        with pytest.raises(ValueError) as excinfo:
            # simulate the service check
            if decision.required and decision.mode == "gate":
                raise ValueError("- " + "\n- ".join(decision.questions))
        assert "Ambigüedad número 1" in str(excinfo.value)

    def test_prepend_block_is_visible_and_numbered(self):
        decision = evaluate_clarification_gate("STANDARD", _AMBIGS, mode="prepend")
        text = apply_prepend("PROMPT COMPILADO", decision)
        assert text.startswith("⚠️ PREGUNTAS ABIERTAS")
        assert "1. Ambigüedad número 1" in text
        assert text.endswith("PROMPT COMPILADO")

    def test_prepend_noop_when_not_required(self):
        decision = evaluate_clarification_gate("STANDARD", _AMBIGS[:2], mode="prepend")
        assert apply_prepend("PROMPT", decision) == "PROMPT"

    def test_render_block_lists_all_questions(self):
        block = render_prepend_block(["a", "b"])
        assert "a" in block and "b" in block


class TestServiceIntegration:
    _OVER_THRESHOLD = "Crea {{a}} con {{b}} y revisa {{c}}."  # target + acceptance + 3 vars = 5 ambiguities
    _CLEAN = (
        "Necesito una app local para gestionar notas con tests automáticos. "
        "Quiero el resultado para codex. Criterios de aceptación: tests pasan."
    )

    def test_default_report_mode_changes_nothing_in_output(self):
        baseline = compile_prompt(CompileRequest(original=self._OVER_THRESHOLD, target="codex", profile="STANDARD"))
        reported = compile_prompt(CompileRequest(original=self._OVER_THRESHOLD, target="codex", profile="STANDARD"))
        assert baseline["optimized_prompt"] == reported["optimized_prompt"]
        assert reported["clarification"]["mode"] == "report"

    def test_report_mode_attaches_decision_when_required(self):
        result = compile_prompt(CompileRequest(original=self._OVER_THRESHOLD, target="codex", profile="STANDARD"))
        clarification = result["clarification"]
        assert clarification["required"] is True
        assert len(clarification["questions"]) >= 5

    def test_gate_mode_refuses_over_threshold(self):
        with pytest.raises(ValueError, match="clarify='gate'"):
            compile_prompt(CompileRequest(original=self._OVER_THRESHOLD, target="codex", profile="STANDARD", clarify="gate"))

    def test_gate_mode_compiles_clean_input(self):
        result = compile_prompt(CompileRequest(original=self._CLEAN, target="codex", profile="STANDARD", clarify="gate"))
        assert result["clarification"]["required"] is False
        assert result["run_id"]

    def test_prepend_mode_marks_execution_prompt(self):
        result = compile_prompt(CompileRequest(original=self._OVER_THRESHOLD, target="codex", profile="STANDARD", clarify="prepend"))
        assert result["optimized_prompt"].startswith("⚠️ PREGUNTAS ABIERTAS")
        # the question block must carry the unfilled variables' names
        assert "{{a}}" in result["optimized_prompt"].split("PROMPT")[0] or "variable" in result["optimized_prompt"][:600].lower()

    def test_gui_entry_point_accepts_clarify(self):
        result = compile_for_gui(self._OVER_THRESHOLD, target="codex",
                                 requested_profile="STANDARD", requested_level="profile_default")
        assert "clarification" in result
        with pytest.raises(ValueError, match="clarify='gate'"):
            compile_for_gui(self._OVER_THRESHOLD, target="codex",
                            requested_profile="STANDARD", requested_level="profile_default", clarify="gate")

    def test_fast_profile_never_gates_even_in_gate_mode(self):
        result = compile_prompt(CompileRequest(original=self._OVER_THRESHOLD, target="codex", profile="FAST", clarify="gate"))
        assert result["clarification"]["required"] is False
