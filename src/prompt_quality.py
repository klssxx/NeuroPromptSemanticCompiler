"""Deterministic prompt-quality evaluator (Eje B, item B.3).

Scores a compiled prompt against verifiable contract properties of the
extended semantic IR (B.2). 100% local and deterministic: rule tables only,
no model calls, no network.

Scoring philosophy (hard invariants, each pinned by a unit test):
- NEVER rewards length per se: no rule reads the size of the compiled output.
- NEVER rewards "more sections": adding empty headings changes nothing.
- Only rewards traceable properties: critical constraints preserved in the
  output, acceptance criteria present when the active profile requires them.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from constraint_normalizer import critical_constraints
from semantic_extractor import ACCEPTANCE_MARKERS

_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")

# Profiles whose product contract requires acceptance criteria. B.5 will
# formalize the full per-profile policy table; this set is the minimum B.3
# needs to score profile-dependent requirements.
PROFILE_REQUIRES_ACCEPTANCE = frozenset({"ADVANCED", "RESEARCH_MAX", "ROP", "CODING"})

_MAX_UNFILLED_DEDUCTION = 30
_MAX_AMBIGUITY_DEDUCTION = 25
_MAX_CONTRADICTION_DEDUCTION = 20
_MAX_TRACEABILITY_BONUS = 9


@dataclass
class QualityIssue:
    code: str
    severity: str  # "info" | "warning" | "error"
    message: str


@dataclass
class QualityReport:
    score: int  # 0-100
    issues: list[QualityIssue] = field(default_factory=list)
    ambiguities_resolved: int = 0
    ambiguities_remaining: int = 0
    unfilled_variables: int = 0
    has_output_contract: bool = False
    has_acceptance_criteria: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ambiguity_variable(entry: str) -> str | None:
    match = _PLACEHOLDER_RE.search(entry)
    return match.group(1) if match else None


def evaluate_quality(original: str, semantics: dict[str, Any], compiled_output: str) -> QualityReport:
    """Evaluate the compiled output against the IR's contract properties.

    ``original`` is kept in the signature as the canonical entry point (B.3
    spec); the current rules derive everything from the IR and the compiled
    output — ambiguity deltas are computed against the IR that B.2 extracted
    from ``original``, so re-extracting here would be redundant.
    """
    del original  # explicit: not used by the current rule set (see docstring)

    issues: list[QualityIssue] = []
    deductions = 0
    bonuses = 0
    compiled = compiled_output or ""
    lowered = compiled.lower()

    # ── Rule 1: output contract ─────────────────────────────────────────
    outputs = semantics.get("output") or []
    has_output_contract = bool(outputs)
    if not has_output_contract:
        issues.append(QualityIssue(
            "MISSING_OUTPUT_CONTRACT", "warning",
            "El prompt no declara contrato de salida: sin entregable o formato "
            "explícito, el resultado no es directamente verificable.",
        ))
        deductions += 15

    # ── Rule 2: unfilled variables in the COMPILED output ──────────────
    unfilled = sorted(set(_PLACEHOLDER_RE.findall(compiled)))
    unfilled_variables = len(unfilled)
    if unfilled:
        issues.append(QualityIssue(
            "UNFILLED_VARIABLES", "error",
            f"El output compilado conserva {unfilled_variables} variable(s) sin "
            f"rellenar: {', '.join(f'{{{{{v}}}}}' for v in unfilled)}.",
        ))
        deductions += min(_MAX_UNFILLED_DEDUCTION, 10 * unfilled_variables)

    # ── Rule 3: ambiguities resolved vs. still applying ─────────────────
    ir_ambiguities = list(semantics.get("ambiguities") or [])
    still_unfilled = set(unfilled)
    variable_ambigs: list[str] = []
    other_ambigs: list[str] = []
    for entry in ir_ambiguities:
        var = _ambiguity_variable(entry)
        if var is not None:
            variable_ambigs.append(var)
        else:
            other_ambigs.append(entry)
    remaining_variables = sum(1 for v in variable_ambigs if v in still_unfilled)
    ambiguities_resolved = len(variable_ambigs) - remaining_variables
    ambiguities_remaining = len(other_ambigs) + remaining_variables
    if ambiguities_remaining:
        issues.append(QualityIssue(
            "AMBIGUITIES_UNRESOLVED", "warning",
            f"{ambiguities_remaining} ambigüedad(es) del input siguen aplicando "
            "al output compilado (contrato de salida, criterios, target, huecos).",
        ))
        deductions += min(_MAX_AMBIGUITY_DEDUCTION, 5 * ambiguities_remaining)

    # ── Rule 4: contradictions carried over from the input ─────────────
    contradictions = list(semantics.get("contradictions") or [])
    if contradictions:
        issues.append(QualityIssue(
            "CONTRADICTIONS_IN_INPUT", "error",
            f"El input contiene {len(contradictions)} contradicción(es) internas "
            "que la compilación no puede resolver por sí sola.",
        ))
        deductions += min(_MAX_CONTRADICTION_DEDUCTION, 10 * len(contradictions))

    # ── Rule 5: critical-constraint traceability (reward / penalty) ────
    critical = critical_constraints(list(semantics.get("constraints") or []))
    normalized_output = lowered.replace("-", "_")
    preserved = [c for c in critical if c.lower() in normalized_output]
    dropped = [c for c in critical if c not in preserved]
    if preserved:
        bonuses += min(_MAX_TRACEABILITY_BONUS, 3 * len(preserved))
    if dropped:
        issues.append(QualityIssue(
            "CRITICAL_CONSTRAINT_DROPPED", "error",
            f"Restricción(es) crítica(s) ausentes en el output compilado: "
            f"{', '.join(dropped)}.",
        ))
        deductions += 15

    # ── Rule 6: acceptance criteria (profile-dependent) ─────────────────
    has_acceptance = any(marker in lowered for marker in ACCEPTANCE_MARKERS)
    profile_name = str(semantics.get("semantic_compilation_profile") or "").upper()
    requires_acceptance = profile_name in PROFILE_REQUIRES_ACCEPTANCE
    if has_acceptance and requires_acceptance:
        bonuses += 5
    elif requires_acceptance and not has_acceptance:
        issues.append(QualityIssue(
            "ACCEPTANCE_CRITERIA_MISSING", "error",
            f"El perfil activo ({profile_name}) exige criterios de aceptación y "
            "el output compilado no los contiene.",
        ))
        deductions += 10
    elif not has_acceptance:
        issues.append(QualityIssue(
            "ACCEPTANCE_CRITERIA_INFO", "info",
            "El output no declara criterios de aceptación; para este perfil es "
            "opcional, pero declararlos mejoraría la verificabilidad.",
        ))

    score = max(0, min(100, 100 - deductions + bonuses))
    return QualityReport(
        score=score,
        issues=issues,
        ambiguities_resolved=max(0, ambiguities_resolved),
        ambiguities_remaining=ambiguities_remaining,
        unfilled_variables=unfilled_variables,
        has_output_contract=has_output_contract,
        has_acceptance_criteria=has_acceptance,
    )
