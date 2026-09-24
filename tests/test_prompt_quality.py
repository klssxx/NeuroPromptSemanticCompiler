"""B.3 tests for prompt_quality.evaluate_quality — one test per scoring rule.

Hard invariants under mutation:
- padding the compiled output with filler text must NOT raise the score
  (length is never rewarded);
- adding empty section headings must NOT raise the score ("more sections"
  is never "more quality").
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prompt_quality import evaluate_quality
from semantic_extractor import extract_semantics
from compilation_profiles import apply_profile_to_semantics, load_compilation_profiles
from npsc_service import CompileRequest, compile_prompt, compile_for_gui
from export_manager import export_json_result, export_markdown_result


def _codes(report):
    return [i.code for i in report.issues]


_BASE_SEMANTICS = {
    "goal": "crear app",
    "tasks": ["build_application"],
    "constraints": ["no_sudo"],
    "output": ["cli"],
    "ambiguities": [],
    "contradictions": [],
}


class TestOutputContractRule:
    def test_missing_output_contract_is_penalized(self):
        semantics = dict(_BASE_SEMANTICS, output=[])
        report = evaluate_quality("x", semantics, "output")
        assert report.has_output_contract is False
        assert "MISSING_OUTPUT_CONTRACT" in _codes(report)
        assert report.score < 100

    def test_present_output_contract_avoids_penalty(self):
        report = evaluate_quality("x", _BASE_SEMANTICS, "output")
        assert report.has_output_contract is True
        assert "MISSING_OUTPUT_CONTRACT" not in _codes(report)


class TestUnfilledVariablesRule:
    def test_each_unfilled_variable_penalized(self):
        report = evaluate_quality("x", _BASE_SEMANTICS, "Haz {{a}} y {{b}}.")
        assert report.unfilled_variables == 2
        assert "UNFILLED_VARIABLES" in _codes(report)

    def test_penalty_capped(self):
        many = " ".join(f"{{{{v{i}}}}}" for i in range(10))
        report = evaluate_quality("x", _BASE_SEMANTICS, many)
        assert report.unfilled_variables == 10
        one = evaluate_quality("x", _BASE_SEMANTICS, "{{only}}")
        # 10 vars deduct the cap (30), not 100; more than 1 var deducts more.
        assert report.score <= one.score - 20

    def test_no_placeholders_no_penalty(self):
        report = evaluate_quality("x", _BASE_SEMANTICS, "limpio")
        assert report.unfilled_variables == 0
        assert "UNFILLED_VARIABLES" not in _codes(report)


class TestAmbiguityRule:
    def test_variable_ambiguity_filled_in_output_counts_resolved(self):
        semantics = dict(_BASE_SEMANTICS, ambiguities=[
            "La variable '{{modulo}}' queda sin rellenar: hueco en el prompt.",
        ])
        filled = evaluate_quality("x", semantics, "modulo listo")
        assert filled.ambiguities_resolved == 1
        assert filled.ambiguities_remaining == 0

    def test_variable_ambiguity_still_unfilled_counts_remaining(self):
        semantics = dict(_BASE_SEMANTICS, ambiguities=[
            "La variable '{{modulo}}' queda sin rellenar: hueco en el prompt.",
        ])
        report = evaluate_quality("x", semantics, "sigue {{modulo}}")
        assert report.ambiguities_remaining == 1
        assert report.ambiguities_resolved == 0
        assert "AMBIGUITIES_UNRESOLVED" in _codes(report)

    def test_structural_ambiguities_remain(self):
        semantics = dict(_BASE_SEMANTICS, ambiguities=[
            "No se declara el modelo objetivo: se aplicará un target genérico.",
        ])
        report = evaluate_quality("x", semantics, "output")
        assert report.ambiguities_remaining == 1


class TestContradictionRule:
    def test_contradictions_from_ir_penalized(self):
        semantics = dict(_BASE_SEMANTICS, contradictions=[
            "Contradicción interna: el texto pide 'rápido' y a la vez 'detallado'.",
        ])
        report = evaluate_quality("x", semantics, "output")
        assert "CONTRADICTIONS_IN_INPUT" in _codes(report)
        clean = evaluate_quality("x", _BASE_SEMANTICS, "output")
        assert report.score < clean.score


class TestConstraintTraceabilityRule:
    def test_preserved_critical_constraint_rewarded(self):
        # Both scenarios carry a missing-output-contract penalty (-15) so the
        # scores stay under the 100 cap and the +3 bonus is observable.
        with_constraint = evaluate_quality(
            "x", dict(_BASE_SEMANTICS, output=[]), "respeta no_sudo siempre"
        )
        without = evaluate_quality("x", dict(_BASE_SEMANTICS, output=[], constraints=[]), "sin menciones")
        assert with_constraint.score == without.score + 3

    def test_dropped_critical_constraint_penalized(self):
        report = evaluate_quality("x", _BASE_SEMANTICS, "aquí no se menciona nada")
        assert "CRITICAL_CONSTRAINT_DROPPED" in _codes(report)

    def test_dash_normalized_trace_counts(self):
        report = evaluate_quality("x", _BASE_SEMANTICS, "regla no-sudo activa")
        assert "CRITICAL_CONSTRAINT_DROPPED" not in _codes(report)


class TestAcceptanceCriteriaRule:
    def test_required_profile_missing_acceptance_penalized(self):
        semantics = dict(_BASE_SEMANTICS, semantic_compilation_profile="ADVANCED")
        report = evaluate_quality("x", semantics, "sin criterios")
        assert "ACCEPTANCE_CRITERIA_MISSING" in _codes(report)

    def test_required_profile_with_acceptance_rewarded(self):
        semantics = dict(_BASE_SEMANTICS, semantic_compilation_profile="ADVANCED")
        with_acc = evaluate_quality("x", semantics, "criterios de aceptación: tests ok")
        without = evaluate_quality("x", semantics, "nada")
        assert with_acc.score > without.score
        assert with_acc.has_acceptance_criteria is True

    def test_optional_profile_absence_is_info_only(self):
        semantics = dict(_BASE_SEMANTICS, semantic_compilation_profile="FAST")
        report = evaluate_quality("x", semantics, "nada")
        assert "ACCEPTANCE_CRITERIA_MISSING" not in _codes(report)
        assert "ACCEPTANCE_CRITERIA_INFO" in _codes(report)
        info_only = evaluate_quality("x", _BASE_SEMANTICS, "nada")  # no profile key
        assert "ACCEPTANCE_CRITERIA_MISSING" not in _codes(info_only)


class TestAntiInflationMutations:
    """Length and section count must never raise the score."""

    _SEMANTICS = dict(_BASE_SEMANTICS, semantic_compilation_profile="ADVANCED")

    def test_length_padding_never_raises_score(self):
        base = evaluate_quality("x", self._SEMANTICS, "ejecuta y verifica no_sudo")
        padded = evaluate_quality(
            "x", self._SEMANTICS,
            "ejecuta y verifica no_sudo" + (" relleno inofensivo" * 800),
        )
        assert padded.score == base.score

    def test_section_stuffing_never_raises_score(self):
        base = evaluate_quality("x", self._SEMANTICS, "ejecuta y verifica no_sudo")
        stuffed = evaluate_quality(
            "x", self._SEMANTICS,
            "ejecuta y verifica no_sudo\n## Contexto\n## Tono\n## Público\n## Extras",
        )
        assert stuffed.score == base.score

    def test_score_stays_in_bounds(self):
        terrible = dict(
            _BASE_SEMANTICS, output=[], constraints=["no_sudo"],
            ambiguities=["sin target"] * 6, contradictions=["choque"] * 3,
        )
        low = evaluate_quality("x", terrible, "{{a}} {{b}} {{c}} sin nada")
        assert 0 <= low.score <= 100
        perfect = evaluate_quality(
            "x",
            dict(_BASE_SEMANTICS, semantic_compilation_profile="ADVANCED"),
            "entrega cli; no_sudo activo; criterios de aceptación: tests pasan",
        )
        assert 0 <= perfect.score <= 100


class TestServiceIntegration:
    """compile_prompt / compile_for_gui expose quality_report additively."""

    _PROMPT = (
        "Necesito una app local para gestionar notas con tests automáticos. "
        "Quiero el resultado para codex. "
        "Criterios de aceptación: todos los tests pasan y funciona sin conexión."
    )

    def test_compile_prompt_result_carries_quality_report(self):
        result = compile_prompt(CompileRequest(original=self._PROMPT, target="codex", profile="STANDARD"))
        qr = result["quality_report"]
        for key in ("score", "issues", "ambiguities_resolved", "ambiguities_remaining",
                    "unfilled_variables", "has_output_contract", "has_acceptance_criteria"):
            assert key in qr, f"quality_report missing '{key}'"
        assert 0 <= qr["score"] <= 100
        assert all(i["severity"] in ("info", "warning", "error") for i in qr["issues"])

    def test_compile_for_gui_result_carries_quality_report(self):
        result = compile_for_gui(self._PROMPT, target="codex",
                                 requested_profile="STANDARD", requested_level="profile_default")
        assert "quality_report" in result
        assert result["quality_report"]["score"] >= 0

    def test_service_and_evaluator_agree_on_score(self):
        result = compile_prompt(CompileRequest(original=self._PROMPT, target="codex", profile="STANDARD"))
        direct = evaluate_quality(self._PROMPT, result["semantics"], result["optimized_prompt"])
        assert result["quality_report"]["score"] == direct.score

    def test_exports_still_work_with_enriched_result(self):
        result = compile_prompt(CompileRequest(original=self._PROMPT, target="codex", profile="STANDARD"))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            export_json_result(result, out)
            export_markdown_result(result, out)
            assert (out / "result.json").exists()
            assert (out / "result.md").exists()


class TestRealPipelineQualitySignal:
    def test_messy_prompt_scores_lower_than_complete_one(self):
        profiles = load_compilation_profiles()
        messy = extract_semantics("haz algo rápido y muy detallado con {{hueco}}")
        complete = extract_semantics(
            "Necesito una app local para gestionar notas con tests automáticos. "
            "Quiero el resultado para codex. Criterios de aceptación: tests pasan."
        )
        messy_profiled = apply_profile_to_semantics(messy, "STANDARD", profiles)
        complete_profiled = apply_profile_to_semantics(complete, "STANDARD", profiles)
        low = evaluate_quality("t", messy_profiled, "output rápido y muy detallado {{hueco}}")
        high = evaluate_quality("t", complete_profiled, "app local con tests; no_sudo; criterios de aceptación: ok")
        assert low.score < high.score
