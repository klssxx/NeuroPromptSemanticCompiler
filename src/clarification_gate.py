"""Clarification gate (Eje B, item B.6).

When the input's ambiguities exceed a per-profile threshold, NPSC makes
the situation EXPLICIT instead of silently compiling a weak prompt.
Three caller-chosen modes — never implicit:

- "report"  (default): compile as usual, attach the decision to the
  result. Zero behaviour change for existing callers.
- "gate":   refuse to compile (ValueError listing the questions) while
  the threshold is exceeded.
- "prepend": compile, but prepend a highly visible
  "PREGUNTAS ABIERTAS" block to the execution prompt.

Deterministic and local; thresholds are code defaults overridable via
the ``thresholds`` argument (and optionally via
compiler_defaults["clarification_thresholds"]).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from compilation_profiles import normalize_profile_name

# None = the profile never gates (FAST answers without asking; SAFE always
# surfaces its questions via the B.5 policy regardless).
DEFAULT_AMBIGUITY_THRESHOLDS: dict[str, int | None] = {
    "FAST": None,
    "STANDARD": 4,
    "ADVANCED": 0,
    "SAFE": None,
    "RESEARCH_MAX": 6,
    "ROP": 6,
    "CODING": 6,
    "AUTO": 4,
}

_PREPEND_HEADER = "⚠️ PREGUNTAS ABIERTAS — responde antes de ejecutar para un resultado fiable:"


@dataclass
class ClarificationDecision:
    required: bool
    mode: str
    threshold: int | None
    questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_threshold(profile_name: str, thresholds: dict[str, int | None] | None = None) -> int | None:
    profile = normalize_profile_name(profile_name)
    source = thresholds if thresholds is not None else DEFAULT_AMBIGUITY_THRESHOLDS
    if profile in source:
        return source[profile]
    return DEFAULT_AMBIGUITY_THRESHOLDS.get("STANDARD", 4)


def evaluate_clarification_gate(
    profile_name: str,
    ambiguities: list[str],
    mode: str = "report",
    thresholds: dict[str, int | None] | None = None,
) -> ClarificationDecision:
    """Decide whether the input needs user clarification before compiling."""
    if mode not in ("report", "gate", "prepend"):
        raise ValueError(f"clarify mode inválido: {mode!r} (usar 'report' | 'gate' | 'prepend')")
    profile = normalize_profile_name(profile_name)
    threshold = resolve_threshold(profile, thresholds)
    questions = [str(q) for q in (ambiguities or [])]
    required = threshold is not None and len(questions) > threshold
    return ClarificationDecision(
        required=required,
        mode=mode,
        threshold=threshold,
        questions=questions,
    )


def render_prepend_block(questions: list[str]) -> str:
    lines = [_PREPEND_HEADER]
    lines.extend(f"{i}. {q}" for i, q in enumerate(questions, start=1))
    return "\n".join(lines)


def apply_prepend(optimized_prompt: str, decision: ClarificationDecision) -> str:
    """Prepend the open-questions block to a compiled prompt (mode 'prepend')."""
    if not decision.required or not decision.questions:
        return optimized_prompt
    block = render_prepend_block(decision.questions)
    return f"{block}\n\n{optimized_prompt}"
