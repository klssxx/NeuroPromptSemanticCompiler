from __future__ import annotations

import re
from typing import Any


TECHNICAL_SIGNALS = [
    "code", "codigo", "código", "arquitectura", "architecture", "documentacion",
    "documentación", "app", "sistema", "system", "error", "debug", "tests",
    "cli", "api", "modulo", "módulo", "repositorio", "repo", "implementa",
]
CODE_SIGNALS = [
    "python", "javascript", "typescript", "tkinter", "qt", "cli", "tests",
    "pytest", "unittest", "bug", "error", "traceback", "refactor", "api",
    "modulo", "módulo", "funcion", "función", "clase", "repositorio",
]
HIGH_STAKES_SIGNALS = [
    "dinero", "money", "inversion", "inversión", "legal", "salud", "health",
    "seguridad", "security", "empresa", "company", "contrato", "risk",
    "riesgo", "produccion", "producción", "critical", "critico", "crítico",
]
AMBIGUITY_SIGNALS = [
    "algo", "cosa", "mejorar", "optimizar", "no se", "no sé", "quizas",
    "quizás", "maybe", "whatever", "ambiguo", "ambiguous",
]
MULTI_AGENT_SIGNALS = ["multiagente", "multi-agent", "agentes", "agents", "orquestacion", "orquestación"]
STRATEGIC_SIGNALS = [
    "decision", "decisión", "dinero", "money", "negocio", "business", "estrategia",
    "strategy", "comparativa", "comparar", "future", "futuro", "riesgo", "riesgos",
    "risk", "probabilidad", "probability", "optimizar", "optimization", "inversion",
    "inversión", "mercado", "market",
]
RESEARCH_SIGNALS = [
    "investigacion", "investigación", "research", "evidencia", "evidence",
    "analisis profundo", "análisis profundo", "planificacion compleja",
    "planificación compleja", "multiagente", "multi-agent", "sistemas avanzados",
    "advanced systems", "hipotesis", "hipótesis", "paper", "bibliografia",
    "bibliografía", "riesgos importantes", "decisiones importantes",
]
SIMPLE_SIGNALS = [
    "resume", "resumir", "rewrite", "reescribe", "corrige", "mejora este texto",
    "traduce", "translate", "simple", "rapido", "rápido",
]
EVIDENCE_SIGNALS = ["evidencia", "evidence", "fuentes", "sources", "datos", "data", "validar", "validate"]


def _contains_any(text: str, signals: list[str]) -> bool:
    return any(signal in text for signal in signals)


def _count_constraints(semantics: dict[str, Any]) -> int:
    return len(list(semantics.get("constraints", [])))


def _word_count(text: str) -> int:
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


def _score(text: str, signals: list[str]) -> int:
    return sum(1 for signal in signals if signal in text)


def auto_select_profile(original: str, semantics: dict[str, Any]) -> dict[str, Any]:
    lowered = original.lower()
    words = _word_count(original)
    constraints = _count_constraints(semantics)
    tasks = len(list(semantics.get("tasks", [])))
    output_items = len(list(semantics.get("output", [])))

    technical_signal_score = _score(lowered, TECHNICAL_SIGNALS)
    code_signal_score = _score(lowered, CODE_SIGNALS)
    research_signal_score = _score(lowered, RESEARCH_SIGNALS)
    strategy_signal_score = _score(lowered, STRATEGIC_SIGNALS)
    high_stakes_signal_score = _score(lowered, HIGH_STAKES_SIGNALS)
    evidence_requirement_score = _score(lowered, EVIDENCE_SIGNALS)
    ambiguity_score = _score(lowered, AMBIGUITY_SIGNALS)
    multi_agent_signal_score = _score(lowered, MULTI_AGENT_SIGNALS)
    critical_constraints = len([c for c in semantics.get("constraints", []) if c in {"no_sudo", "no_external_api", "no_destructive_actions", "stay_inside_project_root"}])
    context_loss_risk_score = 0
    context_loss_risk_score += 2 if words > 180 else 0
    context_loss_risk_score += 2 if constraints >= 4 else 0
    context_loss_risk_score += 2 if research_signal_score else 0
    context_loss_risk_score += 1 if ambiguity_score else 0

    scores = {
        "FAST": 0,
        "STANDARD": 3,
        "ADVANCED": 0,
        "ROP": 0,
        "RESEARCH_MAX": 0,
    }
    risk_flags: list[str] = []
    reasons: list[str] = []

    if words <= 35 and constraints <= 1 and not _contains_any(lowered, RESEARCH_SIGNALS + STRATEGIC_SIGNALS):
        scores["FAST"] += 8
        reasons.append("short_simple_prompt")
    if _contains_any(lowered, SIMPLE_SIGNALS) and words <= 80:
        scores["FAST"] += 4
        reasons.append("simple_task_signal")

    if 35 < words <= 180:
        scores["STANDARD"] += 3
        reasons.append("medium_prompt")

    if technical_signal_score or code_signal_score:
        scores["ADVANCED"] += 8 + min(4, code_signal_score)
        reasons.append("technical_or_system_task")
    if tasks >= 6 or output_items >= 5:
        scores["ADVANCED"] += 3
        reasons.append("multi_step_structure")

    if strategy_signal_score:
        scores["ROP"] += 9 + min(4, high_stakes_signal_score)
        reasons.append("strategic_decision_or_risk_signal")
        risk_flags.append("decision_risk")
    if "probabilidad" in lowered or "probability" in lowered:
        scores["ROP"] += 2
        risk_flags.append("probabilistic_reasoning")

    if research_signal_score:
        scores["RESEARCH_MAX"] += 10 + min(5, evidence_requirement_score + multi_agent_signal_score)
        reasons.append("research_or_deep_analysis_signal")
        risk_flags.append("high_context_loss_risk")
    if words > 260:
        scores["RESEARCH_MAX"] += 4
        reasons.append("long_prompt")
        risk_flags.append("long_prompt")
    if constraints >= 5:
        scores["RESEARCH_MAX"] += 4
        reasons.append("many_critical_restrictions")
        risk_flags.append("many_constraints")
    if evidence_requirement_score:
        scores["RESEARCH_MAX"] += 3
        reasons.append("evidence_needed")
        risk_flags.append("evidence_needed")
    if context_loss_risk_score >= 4:
        scores["RESEARCH_MAX"] += 2
        risk_flags.append("context_loss_risk")

    tie_priority = {"RESEARCH_MAX": 5, "ROP": 4, "ADVANCED": 3, "STANDARD": 2, "FAST": 1}
    selected = max(scores.items(), key=lambda item: (item[1], tie_priority[item[0]]))[0]
    fallback = "STANDARD"
    if selected == "FAST" and (constraints >= 2 or words > 90):
        selected = "STANDARD"
        fallback = "FAST"
        reasons.append("fast_fallback_due_to_constraints_or_length")
    if selected == "ROP" and scores["RESEARCH_MAX"] >= scores["ROP"] + 3:
        selected = "RESEARCH_MAX"
        fallback = "ROP"
    if selected == "STANDARD" and (scores["ADVANCED"] >= 8):
        selected = "ADVANCED"
        fallback = "STANDARD"

    return {
        "auto_selected_profile": selected,
        "selection_reason": ", ".join(reasons) or "general_default",
        "risk_flags": sorted(set(risk_flags)),
        "fallback_profile": fallback,
        "confidence": min(100, max(35, 50 + max(scores.values()) * 4 - sorted(scores.values())[-2] * 2)),
        "scores": scores,
        "features": {
            "prompt_length": words,
            "constraint_count": constraints,
            "critical_constraint_count": critical_constraints,
            "technical_signal_score": technical_signal_score,
            "code_signal_score": code_signal_score,
            "research_signal_score": research_signal_score,
            "strategy_signal_score": strategy_signal_score,
            "high_stakes_signal_score": high_stakes_signal_score,
            "evidence_requirement_score": evidence_requirement_score,
            "ambiguity_score": ambiguity_score,
            "context_loss_risk_score": context_loss_risk_score,
            "multi_agent_signal_score": multi_agent_signal_score,
            "task_count": tasks,
            "output_count": output_items,
        },
    }
