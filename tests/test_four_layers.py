"""B.4 tests: four-layer content separation (requirements / assumptions /
proposals / open questions) and the non-crossing invariant.

Hard rule under mutation: NOTHING may cross from proposals or assumptions
into user_requirements without user confirmation — profile-injected template
content and seed suggestions must never appear as user requirements, even
when their names overlap with real user content.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hybrid_output import (
    append_four_layers_section,
    build_four_layer_sections,
    build_hybrid_output,
    render_four_layers,
)
from npsc_service import CompileRequest, compile_prompt, compile_for_gui

_PROFILED_ADVANCED = {
    "goal": "crear app de notas",
    "tasks": ["build_application", "create_tests"],
    "constraints": ["no_sudo"],
    "output": ["cli"],
    "profile_template_tasks": ["preserve_structure", "validate_outputs"],
    "profile_template_outputs": ["structured_contract"],
    "profile_template_constraints": ["strong_validation"],
    "assumptions": [
        {"field": "target", "value": "generic", "confidence": 0.4,
         "origin": "system_fallback", "reason": "sin marcador de target"},
    ],
    "ambiguities": [
        "No se declara el modelo objetivo: el prompt se compilará para un target genérico.",
    ],
}


class TestLayerAssignment:
    def test_user_requirements_hold_only_user_content(self):
        layers = build_four_layer_sections(_PROFILED_ADVANCED)
        values = [r["value"] for r in layers["user_requirements"]]
        assert "crear app de notas" in values
        assert "build_application" in values
        assert "no_sudo" in values
        # profile-template content is never a user requirement
        assert "preserve_structure" not in values
        assert not any("validate_outputs" in v for v in values)

    def test_profile_template_content_lives_in_proposals(self):
        layers = build_four_layer_sections(_PROFILED_ADVANCED)
        props = [p["value"] for p in layers["improvement_proposals"]]
        assert "validate_outputs" in props
        assert "structured_contract" in props
        assert "strong_validation" in props

    def test_overlap_attack_profile_task_named_like_user_task_stays_out_of_requirements(self):
        semantics = dict(_PROFILED_ADVANCED,
                         profile_template_tasks=["build_application_automated"])
        layers = build_four_layer_sections(semantics)
        req_values = [r["value"] for r in layers["user_requirements"]]
        prop_values = [p["value"] for p in layers["improvement_proposals"]]
        assert "build_application_automated" not in req_values
        assert "build_application_automated" in prop_values

    def test_seeds_are_proposals_never_requirements(self):
        layers = build_four_layer_sections(_PROFILED_ADVANCED, seeds=[
            {"id": "S001", "name": "no-sudo"}, {"id": "S002", "name": "test-first"},
        ])
        prop_kinds = {p["kind"] for p in layers["improvement_proposals"]}
        assert "seed" in prop_kinds
        assert not any("S001" in r["value"] for r in layers["user_requirements"])

    def test_assumptions_mirror_ir_with_origin(self):
        layers = build_four_layer_sections(_PROFILED_ADVANCED)
        assert len(layers["system_assumptions"]) == 1
        a = layers["system_assumptions"][0]
        assert a["origin"] == "system_fallback"
        assert a["confidence"] == 0.4

    def test_ambiguities_become_open_questions(self):
        layers = build_four_layer_sections(_PROFILED_ADVANCED)
        assert layers["open_questions"] == _PROFILED_ADVANCED["ambiguities"]

    def test_fast_profile_without_template_content_has_empty_proposals(self):
        layers = build_four_layer_sections({
            "goal": "hacer algo", "tasks": [], "constraints": [], "output": [],
        })
        assert layers["improvement_proposals"] == []


class TestRendering:
    def test_render_contains_four_section_titles(self):
        text = render_four_layers(build_four_layer_sections(_PROFILED_ADVANCED))
        for title in ("REQUISITOS DEL USUARIO", "SUPUESTOS DEL SISTEMA",
                      "PROPUESTAS DE MEJORA", "PREGUNTAS ABIERTAS"):
            assert title in text

    def test_render_marks_assumptions_with_confidence(self):
        text = render_four_layers(build_four_layer_sections(_PROFILED_ADVANCED))
        assert "40%" in text and "system_fallback" in text

    def test_append_section_adds_block_to_hybrid_markdown(self):
        base = build_hybrid_output(
            "prompt original", {"applied_profile": "ADVANCED"}, "NSL/0.1",
            "prompt optimizado", [], _PROFILED_ADVANCED, {"score": 90},
        )
        combined = append_four_layers_section(base, build_four_layer_sections(_PROFILED_ADVANCED))
        assert combined.startswith(base.rstrip())
        assert "## Capas de contenido" in combined
        assert "PROPUESTAS DE MEJORA" in combined


class TestServiceIntegration:
    _PROMPT = (
        "Necesito una app local para gestionar notas con tests automáticos, sin sudo. "
        "Quiero el resultado para codex. Criterios de aceptación: tests pasan."
    )

    def test_compile_prompt_carries_four_layers(self):
        result = compile_prompt(CompileRequest(original=self._PROMPT, target="codex", profile="ADVANCED"))
        fl = result["four_layers"]
        assert {"user_requirements", "system_assumptions", "improvement_proposals", "open_questions"} == set(fl)
        req_values = [r["value"] for r in fl["user_requirements"]]
        assert any("notas" in v for v in req_values)
        assert "no_sudo" in req_values

    def test_compile_for_gui_carries_four_layers(self):
        result = compile_for_gui(self._PROMPT, target="codex",
                                 requested_profile="ADVANCED", requested_level="profile_default")
        assert "four_layers" in result
        assert result["four_layers"]["user_requirements"]

    def test_hybrid_markdown_contains_layer_block(self):
        result = compile_prompt(CompileRequest(original=self._PROMPT, target="codex", profile="ADVANCED"))
        assert "## Capas de contenido" in result["hybrid_markdown"]

    def test_hash_only_privacy_never_leaks_user_sentences_into_layers(self):
        result = compile_prompt(CompileRequest(
            original=self._PROMPT, target="codex", profile="ADVANCED", privacy_mode="hash_only",
        ))
        fl = result["four_layers"]
        serialized = str(fl)
        assert "gestionar notas" not in serialized, "raw user sentence leaked in hash_only mode"
        assert "## Capas de contenido" in result["hybrid_markdown"]
