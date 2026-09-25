"""Per-profile product policy (Eje B, item B.5).

Each profile is not just a formatting choice: it carries a verifiable
contract. evaluate_profile_policy() checks that contract against the
profiled semantics and the B.4 four-layer separation, and returns
violations (contract failures) and open_questions (things the USER must
resolve — never invented facts).

Deterministic and local; no model calls, no network.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from compilation_profiles import normalize_profile_name
from constraint_normalizer import CRITICAL_CONSTRAINTS

_ACCEPTANCE_AMBIGUITY_TOKEN = "criterios de aceptación"

# Canonical extractor fallbacks (semantic_extractor fills these in when
# nothing is detected). They are SYSTEM inventions, not user declarations,
# so ADVANCED validation must not accept them as real inputs/outputs.
_EXTRACTOR_FALLBACK_TASKS = frozenset({"answer_user_request"})
_EXTRACTOR_FALLBACK_OUTPUTS = frozenset({"direct_answer"})

# ROP/CODING scaffolding that must exist as PROPOSALS, never as user facts.
ROP_SCAFFOLD_KINDS = ("profile_task", "profile_output")


@dataclass
class PolicyViolation:
    code: str
    message: str


@dataclass
class PolicyCheck:
    profile: str
    violations: list[PolicyViolation] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _has_acceptance_criteria(semantics: dict[str, Any]) -> bool:
    """Acceptance criteria are OK when no B.2 ambiguity reports them missing."""
    for entry in semantics.get("ambiguities") or []:
        if _ACCEPTANCE_AMBIGUITY_TOKEN in str(entry).lower():
            return False
    return True


def evaluate_profile_policy(
    profile_name: str,
    semantics: dict[str, Any],
    four_layers: dict[str, Any] | None = None,
) -> PolicyCheck:
    profile = normalize_profile_name(profile_name)
    check = PolicyCheck(profile=profile)
    constraints = [str(c) for c in (semantics.get("constraints") or [])]
    ambiguities = [str(a) for a in (semantics.get("ambiguities") or [])]

    if profile == "FAST":
        # Policy: normalise constraints, never generate NEW questions.
        # open_questions stays empty by definition — the profile answers
        # nothing and asks nothing; it only normalises.
        check.notes.append(
            "FAST normaliza restricciones y no genera preguntas; las "
            "ambigüedades del input viajan en el IR, no como preguntas nuevas."
        )

    elif profile == "STANDARD":
        # Policy: report ambiguities, never resolve them silently.
        check.open_questions.extend(ambiguities)
        if not ambiguities:
            check.notes.append("STANDARD: sin ambigüedades detectadas que reportar.")

    elif profile == "ADVANCED":
        # Policy: goal + inputs + output + acceptance criteria are REQUIRED;
        # missing ones fail validation (violations), they are not invented.
        # Extractor fallbacks (answer_user_request / direct_answer) do not
        # count as user declarations.
        goal = str(semantics.get("goal") or "").strip()
        if not goal or goal == "compile semantic instruction from prompt":
            check.violations.append(PolicyViolation(
                "ADVANCED_GOAL_REQUIRED",
                "El perfil ADVANCED exige un objetivo explícito y el input no lo declara.",
            ))
        effective_tasks = [
            t for t in (semantics.get("tasks") or [])
            if str(t) not in _EXTRACTOR_FALLBACK_TASKS
        ]
        if not effective_tasks:
            check.violations.append(PolicyViolation(
                "ADVANCED_INPUTS_REQUIRED",
                "El perfil ADVANCED exige entradas/tareas concretas y el input no las declara.",
            ))
        effective_outputs = [
            o for o in (semantics.get("output") or [])
            if str(o) not in _EXTRACTOR_FALLBACK_OUTPUTS
        ]
        if not effective_outputs:
            check.violations.append(PolicyViolation(
                "ADVANCED_OUTPUT_REQUIRED",
                "El perfil ADVANCED exige un contrato de salida y el input no lo declara.",
            ))
        if not _has_acceptance_criteria(semantics):
            check.violations.append(PolicyViolation(
                "ADVANCED_ACCEPTANCE_REQUIRED",
                "El perfil ADVANCED exige criterios de aceptación y el input no los declara.",
            ))

    elif profile == "SAFE":
        # Policy: never assume a missing critical safety constraint. Every
        # missing one becomes an open question for the user — nothing is
        # invented into constraints.
        for critical in CRITICAL_CONSTRAINTS:
            if critical not in constraints:
                check.open_questions.append(
                    f"¿Debe aplicarse la restricción crítica '{critical}'? El input no la "
                    "declara y el perfil SAFE no la asume por su cuenta."
                )
        check.notes.append(
            "SAFE no inventa restricciones: las críticas ausentes quedan como "
            "preguntas abiertas para el usuario."
        )

    elif profile == "RESEARCH_MAX":
        # Policy: facts / hypotheses / uncertainty must be explicitly
        # separated. With B.4 layers present, verify the three-way split is
        # materialised; without layers, require the template outputs that
        # carry the separation.
        if four_layers is not None:
            facts = four_layers.get("user_requirements") or []
            hypotheses = four_layers.get("system_assumptions") or []
            uncertainty = four_layers.get("open_questions") or []
            check.notes.append(
                f"RESEARCH_MAX separa hechos ({len(facts)}), hipótesis/supuestos "
                f"({len(hypotheses)}) e incertidumbre ({len(uncertainty)})."
            )
            if not uncertainty and not ambiguities:
                check.notes.append("Sin incertidumbres detectadas; la separación sigue siendo explícita.")
        else:
            template_outputs = [str(o) for o in (semantics.get("profile_template_outputs") or [])]
            if "structured_analysis" not in template_outputs:
                check.violations.append(PolicyViolation(
                    "RESEARCH_MAX_SEPARATION_REQUIRED",
                    "El perfil RESEARCH_MAX exige separar hechos, hipótesis e incertidumbre.",
                ))

    elif profile in ("ROP", "CODING"):
        # Policy: environment / affected files / test plan / rollback must
        # appear as PROPOSED structure, never as user-given facts.
        proposals = [str(p.get("value", "")) for p in ((four_layers or {}).get("improvement_proposals") or [])]
        requirements = [str(r.get("value", "")) for r in ((four_layers or {}).get("user_requirements") or [])]
        if not proposals:
            check.violations.append(PolicyViolation(
                "ROP_SCAFFOLD_REQUIRED",
                "El perfil ROP exige estructura propuesta (entorno, archivos, plan de pruebas, rollback) "
                "y el resultado no contiene ninguna propuesta.",
            ))
        crossing = [p for p in proposals if p in requirements]
        if crossing:
            check.violations.append(PolicyViolation(
                "ROP_SCAFFOLD_CROSSED_TO_REQUIREMENTS",
                f"Contenido propuesto apareció como requisito del usuario: {', '.join(crossing)}.",
            ))

    return check
