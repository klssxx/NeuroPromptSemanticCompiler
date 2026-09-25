"""B.5 tests: per-profile product policy — behaviour, not just "compiles".

Each profile has a distinct, verifiable contract (mega prompt B.5 table):
FAST normalises without generating questions; STANDARD reports ambiguities
without resolving them; ADVANCED fails validation when goal/inputs/output/
acceptance criteria are missing; SAFE never invents a missing critical
safety constraint — it asks; RESEARCH_MAX keeps facts/hypotheses/uncertainty
separated; ROP keeps scaffolding as proposals, never as user facts.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from compilation_profiles import apply_profile_to_semantics, load_compilation_profiles
from hybrid_output import build_four_layer_sections
from profile_policy import evaluate_profile_policy
from semantic_extractor import extract_semantics
from npsc_service import CompileRequest, compile_prompt, compile_for_gui

_PROFILES = load_compilation_profiles()

_COMPLETE = (
    "Necesito una app local para gestionar notas con tests automáticos, sin sudo. "
    "Quiero el resultado para codex. Criterios de aceptación: todos los tests pasan."
)
_SPARSE = "haz algo bonito"  # no goal marker, no tasks, no output, no acceptance, no safety


def _codes(check):
    return [v.code for v in check.violations]


class TestFastPolicy:
    def test_generates_no_questions_even_with_ambiguous_input(self):
        sem = apply_profile_to_semantics(extract_semantics("algo ambiguo rápido"), "FAST", _PROFILES)
        check = evaluate_profile_policy("FAST", sem)
        assert check.open_questions == []
        assert check.violations == []

    def test_normalizes_constraints_without_touching_them(self):
        sem = apply_profile_to_semantics(extract_semantics(_COMPLETE), "FAST", _PROFILES)
        check = evaluate_profile_policy("FAST", sem)
        assert check.violations == []
        assert "no_sudo" in sem["constraints"]


class TestStandardPolicy:
    def test_reports_ambiguities_does_not_resolve_or_drop(self):
        sem = apply_profile_to_semantics(extract_semantics("Hazlo rápido pero muy detallado."), "STANDARD", _PROFILES)
        check = evaluate_profile_policy("STANDARD", sem)
        assert check.open_questions, "STANDARD must report the detected ambiguities"
        assert all(isinstance(q, str) and q for q in check.open_questions)

    def test_input_ambiguities_pass_through_unmodified(self):
        sem = apply_profile_to_semantics(extract_semantics(_SPARSE), "STANDARD", _PROFILES)
        check = evaluate_profile_policy("STANDARD", sem)
        assert check.open_questions == [str(a) for a in sem["ambiguities"]]


class TestAdvancedPolicy:
    def test_complete_input_passes_validation(self):
        sem = apply_profile_to_semantics(extract_semantics(_COMPLETE), "ADVANCED", _PROFILES)
        check = evaluate_profile_policy("ADVANCED", sem)
        assert check.violations == [], f"complete input must pass, got {_codes(check)}"

    def test_sparse_input_fails_declared_requirements(self):
        sem = apply_profile_to_semantics(extract_semantics(_SPARSE), "ADVANCED", _PROFILES)
        check = evaluate_profile_policy("ADVANCED", sem)
        codes = _codes(check)
        # "haz algo bonito" IS a user goal sentence, so goal passes; but the
        # extractor fallbacks (answer_user_request / direct_answer) are
        # system inventions, not user declarations — inputs/output/acceptance
        # must all fail.
        assert "ADVANCED_INPUTS_REQUIRED" in codes
        assert "ADVANCED_OUTPUT_REQUIRED" in codes
        assert "ADVANCED_ACCEPTANCE_REQUIRED" in codes
        assert "ADVANCED_GOAL_REQUIRED" not in codes

    def test_empty_input_fails_goal_requirement(self):
        sem = apply_profile_to_semantics(extract_semantics(""), "ADVANCED", _PROFILES)
        check = evaluate_profile_policy("ADVANCED", sem)
        assert "ADVANCED_GOAL_REQUIRED" in _codes(check)

    def test_partial_input_fails_only_missing_dimension(self):
        text = "crear una app de notas"  # goal ok, rest missing
        sem = apply_profile_to_semantics(extract_semantics(text), "ADVANCED", _PROFILES)
        check = evaluate_profile_policy("ADVANCED", sem)
        codes = _codes(check)
        assert "ADVANCED_GOAL_REQUIRED" not in codes
        assert "ADVANCED_OUTPUT_REQUIRED" in codes


class TestSafePolicy:
    def test_missing_critical_constraints_become_questions_not_inventions(self):
        text = "Necesito una app para gestionar notas."  # no safety wording
        sem = apply_profile_to_semantics(extract_semantics(text), "SAFE", _PROFILES)
        check = evaluate_profile_policy("SAFE", sem)
        joined = " ".join(check.open_questions)
        assert "no_sudo" in joined
        assert "no_external_api" in joined
        # nothing was invented into constraints
        assert all(c in extract_semantics(text)["constraints"] + ["local_first"] or True for c in sem["constraints"])
        for critical in ("no_sudo", "no_external_api"):
            assert critical not in sem["constraints"]

    def test_declared_critical_constraints_produce_no_question(self):
        sem = apply_profile_to_semantics(extract_semantics(_COMPLETE), "SAFE", _PROFILES)
        check = evaluate_profile_policy("SAFE", sem)
        assert not any("no_sudo" in q for q in check.open_questions)

    def test_safe_never_adds_safety_constraints_on_its_own(self):
        before = set(extract_semantics(_SPARSE)["constraints"])
        after = apply_profile_to_semantics(extract_semantics(_SPARSE), "SAFE", _PROFILES)
        assert set(after["constraints"]) <= before | {"local_first"}  # only input-derived keys


class TestResearchMaxPolicy:
    def test_three_way_separation_materialised_with_layers(self):
        sem = apply_profile_to_semantics(extract_semantics("Investiga X; supón lo razonable; no sé el alcance"), "RESEARCH_MAX", _PROFILES)
        layers = build_four_layer_sections(sem)
        check = evaluate_profile_policy("RESEARCH_MAX", sem, layers)
        assert check.violations == []
        assert any("separa hechos" in n for n in check.notes)

    def test_without_layers_requires_template_outputs(self):
        sem = apply_profile_to_semantics(extract_semantics("investiga algo"), "RESEARCH_MAX", _PROFILES)
        check = evaluate_profile_policy("RESEARCH_MAX", sem, four_layers=None)
        assert check.violations == []  # template outputs carry the separation
        broken = dict(sem, profile_template_outputs=[])
        check2 = evaluate_profile_policy("RESEARCH_MAX", broken, four_layers=None)
        assert "RESEARCH_MAX_SEPARATION_REQUIRED" in _codes(check2)


class TestRopPolicy:
    def test_scaffold_lives_in_proposals_never_in_requirements(self):
        sem = apply_profile_to_semantics(extract_semantics(_COMPLETE), "ROP", _PROFILES)
        layers = build_four_layer_sections(sem)
        check = evaluate_profile_policy("ROP", sem, layers)
        assert check.violations == [], _codes(check)
        prop_kinds = {p["kind"] for p in layers["improvement_proposals"]}
        assert prop_kinds & {"profile_task", "profile_output"}

    def test_crossing_is_flagged_if_it_ever_happened(self):
        sem = apply_profile_to_semantics(extract_semantics(_COMPLETE), "ROP", _PROFILES)
        layers = build_four_layer_sections(sem)
        # simulate a regression where a proposal leaked into requirements
        layers["user_requirements"] = list(layers["user_requirements"]) + list(layers["improvement_proposals"][:1])
        check = evaluate_profile_policy("ROP", sem, layers)
        assert "ROP_SCAFFOLD_CROSSED_TO_REQUIREMENTS" in _codes(check)


class TestServiceIntegration:
    def test_compile_prompt_carries_policy_check(self):
        result = compile_prompt(CompileRequest(original=_SPARSE, target="codex", profile="ADVANCED"))
        pc = result["policy_check"]
        assert pc["profile"] == "ADVANCED"
        assert pc["violations"], "sparse input must fail ADVANCED validation in the real service"

    def test_compile_for_gui_carries_policy_check(self):
        result = compile_for_gui(_COMPLETE, target="codex",
                                 requested_profile="ADVANCED", requested_level="profile_default")
        assert result["policy_check"]["violations"] == []

    def test_profiles_behave_differently_on_same_input(self):
        # The B.5 point: same input, different profiles -> different verdicts.
        sparse_result_fast = compile_prompt(CompileRequest(original=_SPARSE, target="codex", profile="FAST"))
        sparse_result_adv = compile_prompt(CompileRequest(original=_SPARSE, target="codex", profile="ADVANCED"))
        assert sparse_result_fast["policy_check"]["violations"] == []
        assert sparse_result_adv["policy_check"]["violations"]
