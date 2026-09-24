"""B.2 mutation tests for the extended semantic IR.

Contract under test (mega prompt B.2): extract_semantics() additionally
returns ambiguities / contradictions / assumptions / confidence — additive,
no previously verified field removed — where:

- every ambiguity is a readable sentence explaining WHY it matters (never a
  bare code);
- assumptions clearly separate system inferences/fallbacks from user data
  (origin field);
- mutation battery: empty text, contradictory text, unfilled variables, and
  an already-complete prompt (which must yield ambiguities == []).
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from semantic_extractor import extract_semantics
from semantic_ir import build_semantic_ir


def _all_readable_sentences(items: list[str]) -> bool:
    return all(isinstance(i, str) and len(i) >= 40 and i.endswith(".") for i in items)


class TestMutationEmpty:
    def test_empty_text_reports_ambiguities_not_silence(self):
        result = extract_semantics("")
        assert result["ambiguities"], "empty input must surface ambiguities, not stay silent"
        assert _all_readable_sentences(result["ambiguities"])
        assert any("objetivo" in a.lower() for a in result["ambiguities"])

    def test_whitespace_only_text_behaves_like_empty(self):
        result = extract_semantics("   \n\t  ")
        assert result["ambiguities"]
        assert result["contradictions"] == []

    def test_empty_text_confidence_low_for_goal(self):
        result = extract_semantics("")
        assert result["confidence"]["goal"] <= 0.3


class TestMutationContradictory:
    def test_fast_vs_detailed_is_detected(self):
        text = "Hazme un informe rápido pero muy detallado y sin errores."
        result = extract_semantics(text)
        assert result["contradictions"], "'rápido' + 'muy detallado' must be flagged"
        joined = " ".join(result["contradictions"]).lower()
        assert "rápido" in joined and "detallado" in joined
        assert _all_readable_sentences(result["contradictions"])

    def test_short_vs_detailed_is_detected(self):
        result = extract_semantics("Un resumen corto y exhaustivo del tema.")
        assert result["contradictions"]

    def test_non_contradictory_text_yields_none(self):
        result = extract_semantics("Necesito una app local para gestionar notas con tests.")
        assert result["contradictions"] == []


class TestMutationUnfilledVariables:
    def test_placeholder_surfaces_as_ambiguity(self):
        result = extract_semantics("Crea un informe de {{proyecto}} con tests para {{modulo}}.")
        joined = " ".join(result["ambiguities"])
        assert "{{proyecto}}" in joined
        assert "{{modulo}}" in joined


class TestMutationCompletePrompt:
    # Satisfies every gap check: explicit goal sentence, concrete tasks,
    # declared output, declared target, acceptance criteria, no placeholders,
    # no contradiction pair.
    _COMPLETE = (
        "Necesito una app local para gestionar notas con tests automáticos. "
        "Quiero el resultado para codex. "
        "Criterios de aceptación: todos los tests pasan y la app funciona sin conexión."
    )

    def test_complete_prompt_has_no_ambiguities(self):
        result = extract_semantics(self._COMPLETE)
        assert result["ambiguities"] == [], (
            f"a fully specified prompt must not accumulate filler ambiguities, got: {result['ambiguities']}"
        )

    def test_complete_prompt_still_extracted_correctly(self):
        result = extract_semantics(self._COMPLETE)
        assert result["target"] != "generic"
        assert result["tasks"]
        assert result["confidence"]["goal"] >= 0.9


class TestAssumptionsProvenance:
    def test_fallback_target_is_marked_as_system_fallback(self):
        result = extract_semantics("Hazme algo bonito.")  # no target marker
        target_assumptions = [a for a in result["assumptions"] if a["field"] == "target"]
        assert target_assumptions, "fallback target must be an explicit assumption"
        entry = target_assumptions[0]
        assert entry["origin"] == "system_fallback"
        assert 0.0 < entry["confidence"] < 1.0
        assert entry["reason"]

    def test_explicit_target_is_not_a_fallback_assumption(self):
        result = extract_semantics("Compila este prompt para codex con tests.")
        target_assumptions = [a for a in result["assumptions"] if a["field"] == "target"]
        assert target_assumptions == []

    def test_every_assumption_has_required_shape(self):
        result = extract_semantics("texto ambiguo cualquiera")
        for a in result["assumptions"]:
            assert set(a) >= {"field", "value", "confidence"}
            assert 0.0 <= a["confidence"] <= 1.0
            assert isinstance(a["reason"], str) and a["reason"]


class TestConfidenceContract:
    def test_all_values_in_unit_interval(self):
        result = extract_semantics("Cualquier texto de prueba con tests.")
        assert result["confidence"]
        for field, value in result["confidence"].items():
            assert isinstance(field, str)
            assert 0.0 <= value <= 1.0, f"confidence[{field}]={value} out of [0,1]"

    def test_confidence_reflects_extraction_strength(self):
        strong = extract_semantics("Necesito una app local con tests, target codex.")
        weak = extract_semantics("mm")
        assert strong["confidence"]["target"] > weak["confidence"]["target"]


class TestAdditiveContract:
    def test_no_a6_verified_field_was_removed(self):
        result = extract_semantics("Quiero una app local sin sudo y con tests para codex.")
        for field in (
            "language", "target", "role", "goal", "tasks", "constraints", "priorities",
            "tools", "output", "style", "risks", "context", "safety_constraints",
        ):
            assert field in result, f"pre-existing IR field '{field}' disappeared"

    def test_semantic_ir_layer_propagates_gap_fields(self):
        semantics = extract_semantics("Hazlo rápido pero muy detallado.")
        ir = build_semantic_ir(
            raw_prompt="Hazlo rápido pero muy detallado.",
            sha256="0" * 64,
            semantics=semantics,
            requested_profile="STANDARD",
            applied_profile="STANDARD",
            auto_info={"features": {}, "scores": {}},
            canonical_nsl="NSL/0.1",
            optimized_prompt="optimized",
            validation={},
        )
        layer = ir["semantic_ir"]
        assert layer["contradictions"], "contradiction lost in semantic_ir layer"
        assert layer["ambiguities"]
        assert isinstance(layer["confidence"], dict) and layer["confidence"]

    def test_semantic_ir_tolerates_legacy_semantics_without_gap_fields(self):
        legacy = {"role": "senior", "goal": "crear app", "context": None,
                  "tasks": [], "constraints": [], "priorities": [], "output": []}
        ir = build_semantic_ir(
            raw_prompt="x", sha256="0" * 64, semantics=legacy,
            requested_profile="FAST", applied_profile="FAST",
            auto_info={}, canonical_nsl="", optimized_prompt="", validation={},
        )
        layer = ir["semantic_ir"]
        assert layer["ambiguities"] == [] and layer["contradictions"] == []
        assert layer["confidence"] == {}
