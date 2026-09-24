"""Semantic extractor for the NeuroPromptSemanticCompiler pipeline.

Changes vs previous version
---------------------------
* P0 fix: safety constraint detection now delegates to ``safety_vocabulary``
  (``canonical_constraints``) instead of duplicating phrase lists.
* P1 fix: corrected three dead-code regexes in ``_extract_constraints`` that
  used double-escaped ``\\\\s+`` (raw-string error).  The equivalent coverage
  is now provided by the unified vocabulary, so the dead branches are removed.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any

from utils import unique_preserve
from constraint_normalizer import normalize_constraints
from resource_paths import resource_path
from safety_vocabulary import canonical_constraints as _safety_canonical


PATTERN_PATH = resource_path("configs/extraction_patterns.json")

_cached_patterns: dict[str, Any] | None = None


def _load_patterns(path: str | Path | None = None) -> dict[str, Any]:
    global _cached_patterns
    if _cached_patterns is not None and path is None:
        return _cached_patterns
    source = Path(path) if path else PATTERN_PATH
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(f"Cannot load patterns from {source}: {exc}") from exc
    if path is None:
        _cached_patterns = data
    return data


def _detect_language(text: str) -> str:
    lowered = text.lower()
    spanish_markers = ["quiero", "necesito", "sin", "con", "para", "hacer", "restricciones", "seguridad"]
    english_markers = ["build", "need", "without", "with", "for", "create", "constraints", "safety"]
    s_score = sum(1 for token in spanish_markers if token in lowered)
    e_score = sum(1 for token in english_markers if token in lowered)
    if s_score > e_score:
        return "es"
    if e_score > s_score:
        return "en"
    return "mixed"


def _sentence_candidates(text: str) -> list[str]:
    parts = re.split(r"[\n\.\!\?]+", text)
    return [p.strip() for p in parts if p.strip()]


def _find_target(text: str, patterns: dict[str, Any]) -> str:
    lowered = text.lower()
    mapping = patterns.get("target_markers", {})
    for target, markers in mapping.items():
        if any(m.lower() in lowered for m in markers):
            return target
    return "generic"


def _find_role(text: str, patterns: dict[str, Any]) -> str:
    lowered = text.lower()
    role_keywords = patterns.get("roles", [])
    if "architect" in lowered or "arquitecto" in lowered:
        return "principal_ai_system_architect"
    if "codex" in lowered:
        return "codex_engineer"
    if "hermes" in lowered:
        return "hermes_agent_operator"
    if "prompt" in lowered:
        return "prompt_language_designer"
    if "research" in lowered or "investig" in lowered:
        return "semantic_compression_researcher"
    if any(k in lowered for k in role_keywords):
        return "senior_expert"
    return "semantic_compiler_operator"


def _extract_goal(text: str, patterns: dict[str, Any]) -> str:
    sentences = _sentence_candidates(text)
    lowered_markers = [m.lower() for m in patterns.get("goal_markers", [])]
    for sentence in sentences:
        if any(marker in sentence.lower() for marker in lowered_markers):
            return sentence
    return sentences[0] if sentences else "compile semantic instruction from prompt"


def _extract_tasks(text: str, patterns: dict[str, Any]) -> list[str]:
    lowered = text.lower()
    tasks: list[str] = []
    task_patterns = [
        ("correct_spelling", [r"\bcorrige\b", r"\bcorregir\b", r"\borthography\b", r"\bortograf"]),
        ("translate_text", [r"\btraduce\b", r"\btraducir\b", r"\btranslate\b"]),
        ("write_email", [r"\bcorreo\b", r"\bemail\b", r"\be-mail\b"]),
        ("summarize_text", [r"\bresume\b", r"\bresumir\b", r"\bsummarize\b"]),
        ("analyze_code", [r"\bc[o\u00f3]digo\b", r"\bcode\b", r"\bdebug\b", r"\berror\b"]),
        ("design_architecture", [r"\barquitectura\b", r"\barchitecture\b"]),
        ("build_application", [r"\bapp\b", r"\baplicaci[o\u00f3]n\b", r"\btool\b", r"\bherramienta\b"]),
        ("create_tests", [r"\btests?\b", r"\bpruebas?\b", r"\bunittest\b", r"\bpytest\b"]),
        ("evaluate_strategy", [r"\bestrategia\b", r"\bstrategy\b", r"\bmonetiz", r"\bcompar"]),
        ("research_topic", [r"\binvestiga", r"\binvestigaci[o\u00f3]n\b", r"\bresearch\b"]),
        ("optimize_prompt", [r"\bprompt\b", r"\boptimiza\b", r"\boptimizar\b"]),
    ]
    for label, regexes in task_patterns:
        if any(re.search(regex, lowered) for regex in regexes):
            tasks.append(label)

    explicit_internal = {
        "extract_semantics": ["extract_semantics", "extrae semantica", "extrae sem\u00e1ntica"],
        "map_seeds": ["map_seeds", "mapear seeds", "semantic seeds"],
        "compile_nsl": ["compile_nsl", "compilar nsl", "nsl"],
        "reconstruct_prompt": ["reconstruct_prompt", "reconstruir prompt"],
        "verify_context_loss": ["verify_context_loss", "p\u00e9rdida de contexto", "perdida de contexto"],
        "export_reports": ["export_reports", "exportar reportes", "exportar informes"],
    }
    for label, markers in explicit_internal.items():
        if any(marker in lowered for marker in markers):
            tasks.append(label)

    if not tasks:
        tasks.append("answer_user_request")
    return unique_preserve(tasks)


def _extract_constraints(text: str, patterns: dict[str, Any]) -> list[str]:
    """Detect safety/operational constraints in *text*.

    Primary detection is now delegated to ``safety_vocabulary.canonical_constraints``
    which uses the unified PHRASES dict as a single source of truth.

    The ``safety_map`` in *patterns* is kept as a supplementary path for any
    project-specific markers not yet in the central vocabulary.
    Additional implicit pairs are preserved for non-safety operational
    constraints (ubuntu, local, offline aliases).
    """
    lowered = text.lower()
    detected: list[str] = []

    # --- Primary: unified vocabulary (P0 fix) ---
    detected.extend(_safety_canonical(text))

    # --- Supplementary: project-specific safety_map from patterns JSON ---
    safety_map = patterns.get("safety_map", {})
    for label, markers in safety_map.items():
        if label not in detected and any(marker.lower() in lowered for marker in markers):
            detected.append(label)

    # --- Implicit operational constraints (non-safety) ---
    implicit_pairs = {
        "ubuntu": "ubuntu_environment",
        "local": "local_first",
    }
    for needle, label in implicit_pairs.items():
        if needle in lowered and label not in detected:
            detected.append(label)

    return unique_preserve(normalize_constraints(detected))


def _extract_priorities(text: str) -> list[str]:
    lowered = text.lower()
    candidates = [
        ("safety", ["safety", "seguridad", "safe"]),
        ("semantic_preservation", ["preserve", "preserv", "intenci\u00f3n", "meaning"]),
        ("clarity", ["clarity", "claro", "readable"]),
        ("compression", ["compact", "compression", "comprimir"]),
        ("extensibility", ["extensible", "extensibility", "future"]),
        ("speed", ["fast", "speed", "r\u00e1pido"]),
    ]
    ranked = [name for name, needles in candidates if any(n in lowered for n in needles)]
    if not ranked:
        ranked = ["clarity"]
    return unique_preserve(ranked)


def _extract_tools(text: str) -> list[str]:
    lowered = text.lower()
    known = {
        "python": "python",
        "argparse": "argparse",
        "json": "json",
        "pathlib": "pathlib",
        "unittest": "unittest",
        "bash": "bash",
        "ubuntu": "ubuntu",
        "cli": "cli",
        "codex": "codex",
        "hermes": "hermes",
        "gpt": "gpt",
    }
    tools = [mapped for key, mapped in known.items() if key in lowered]
    return unique_preserve(tools)


def _extract_output(text: str) -> list[str]:
    lowered = text.lower()
    mapping = [
        ("corrected_text", [r"\bcorrige\b", r"\bcorregir\b", r"\bortograf"]),
        ("translated_text", [r"\btraduce\b", r"\btranslate\b"]),
        ("email_draft", [r"\bcorreo\b", r"\bemail\b"]),
        ("summary", [r"\bresumen\b", r"\bresume\b", r"\bsummar"]),
        ("code_review", [r"\bc[o\u00f3]digo\b", r"\bcode\b", r"\berror\b"]),
        ("architecture_proposal", [r"\barquitectura\b", r"\barchitecture\b"]),
        ("tests", [r"\btests?\b", r"\bpruebas?\b"]),
        ("risk_analysis", [r"\briesgos?\b", r"\brisks?\b"]),
        ("scenario_matrix", [r"\bescenarios?\b", r"\bscenarios?\b"]),
        ("research_plan", [r"\binvestig", r"\bresearch\b"]),
        ("json", [r"\bjson\b"]),
        ("nsl", [r"\bnsl\b"]),
        ("files", [r"\barchivos?\b", r"\bfiles?\b"]),
        ("docs", [r"\bdocs?\b", r"\bdocumentaci[o\u00f3]n\b"]),
    ]
    outputs = [label for label, regexes in mapping if any(re.search(regex, lowered) for regex in regexes)]
    if not outputs:
        outputs.append("direct_answer")
    return unique_preserve(outputs)


def _extract_style(text: str) -> list[str]:
    lowered = text.lower()
    mapping = [
        ("precise", ["precise", "preciso"]),
        ("operational", ["operational", "operativo"]),
        ("compact", ["compact", "compacto"]),
        ("model_readable", ["readable", "legible", "model-readable"]),
        ("concise", ["concise", "concreto"]),
    ]
    styles = [name for name, needles in mapping if any(n in lowered for n in needles)]
    if not styles:
        styles = ["precise", "operational", "model_readable"]
    return unique_preserve(styles)


def _extract_risks(text: str) -> list[str]:
    lowered = text.lower()
    risks = []
    if "aggressive" in lowered or "agresivo" in lowered:
        risks.append("overcompression")
    if "ambigu" in lowered or "vague" in lowered:
        risks.append("ambiguous_goal")
    if "token" in lowered:
        risks.append("false_token_estimate")
    return unique_preserve(risks)


# ─── B.2: semantic gap analysis (ambiguities / contradictions / assumptions) ───
# All deterministic and local: no model calls, no network. Every message is a
# full readable sentence (why it matters), never a bare code.

_DEFAULT_GOAL = "compile semantic instruction from prompt"
_DEFAULT_ROLE = "semantic_compiler_operator"
_FALLBACK_TARGET = "generic"
_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")

_CONTRACTION_PAIRS: list[tuple[tuple[str, ...], tuple[str, ...], str]] = [
    (
        ("rápido", "rapido", "fast", "quick", "lo antes posible", "ya mismo"),
        ("detallado", "exhaustivo", "detailed", "exhaustive", "thorough", "muy completo"),
        "generar detalle cuesta tiempo; el texto no declara cuál de los dos manda",
    ),
    (
        ("corto", "breve", "conciso", "short", "resumido"),
        ("detallado", "exhaustivo", "extenso", "largo", "detailed", "exhaustive"),
        "la extensión pedida choca con el nivel de detalle pedido",
    ),
    (
        ("simple", "sencillo", "minimalista", "simple", "minimal"),
        ("complejo", "avanzado", "complex", "con todas las funciones", "completo"),
        "una solución no puede ser minimalista y tener todas las funciones a la vez",
    ),
    (
        ("gratis", "sin coste", "free of charge",),
        ("de pago", "premium", "suscripción", "paid", "subscription"),
        "el modelo de coste declarado se contradice",
    ),
    (
        ("local", "offline", "sin nube", "air-gapped"),
        ("en la nube", "cloud", "online", "sincroniza con"),
        "el despliegue local-first excluye el despliegue en nube declarado",
    ),
]

# Public: prompt_quality (B.3) reuses the same acceptance-criteria vocabulary
# so extraction and evaluation can never drift apart.
ACCEPTANCE_MARKERS = (
    "criterios de aceptación", "criterio de aceptación", "acceptance criteria",
    "definition of done", "se considera exitoso", "se considera correcto",
    "se considera listo", "como validar", "cómo validar", "cómo verificar",
    "checklist", "verifica que", "valida que", "test de aceptación",
)


def _detect_contradictions(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for side_a, side_b, why in _CONTRACTION_PAIRS:
        hit_a = next((p for p in side_a if p in lowered), None)
        hit_b = next((p for p in side_b if p in lowered), None)
        if hit_a and hit_b:
            found.append(
                f"Contradicción interna: el texto pide '{hit_a}' y a la vez '{hit_b}' — {why}."
            )
    return found


def _detect_ambiguities(
    text: str,
    *,
    goal: str,
    target: str,
    tasks: list[str],
    output: list[str],
) -> list[str]:
    ambiguities: list[str] = []
    if not text.strip():
        ambiguities.append(
            "No hay objetivo: el texto de entrada está vacío, así que no existe intención "
            "que conservar y el compilador no puede decidir qué preservar."
        )
        return ambiguities

    if goal == _DEFAULT_GOAL:
        ambiguities.append(
            "No hay objetivo utilizable: ninguna frase del texto sirve como goal, "
            "por lo que la compilación trabajaría sobre una intención inventada."
        )
    if not tasks:
        ambiguities.append(
            "No se identifican tareas concretas: la especificación no dice qué hay que "
            "hacer y el resultado no será accionable."
        )
    if not output:
        ambiguities.append(
            "No se especifica la salida esperada: sin contrato de salida (formato o "
            "entregable) no habrá forma de verificar lo producido."
        )
    if target == _FALLBACK_TARGET:
        ambiguities.append(
            "No se declara el modelo objetivo: el prompt se compilará para un target "
            "genérico en lugar de adaptarse a un modelo concreto."
        )
    lowered = text.lower()
    if not any(marker in lowered for marker in ACCEPTANCE_MARKERS):
        ambiguities.append(
            "No hay criterios de aceptación: nada en el texto define cómo validar que "
            "el resultado es correcto, así que el éxito quedaría sin verificar."
        )
    for name in _PLACEHOLDER_RE.findall(text):
        ambiguities.append(
            f"La variable '{{{{{name}}}}}' queda sin rellenar: el prompt contiene un hueco "
            "que podría colarse hasta la salida final sin que nadie lo note."
        )
    return ambiguities


def _build_assumptions(text: str, *, language: str, target: str, role: str) -> list[dict[str, Any]]:
    """System inferences, explicitly separated from user-provided data."""
    lowered = text.lower()
    assumptions: list[dict[str, Any]] = []

    if language != "mixed" and not any(
        marker in lowered for marker in ("español", "spanish", "inglés", "english", "idioma")
    ):
        assumptions.append({
            "field": "language",
            "value": language,
            "confidence": 0.8,
            "origin": "system_inferred",
            "reason": "Idioma inferido del vocabulario del texto; el usuario no lo declaró.",
        })

    if target == _FALLBACK_TARGET:
        assumptions.append({
            "field": "target",
            "value": _FALLBACK_TARGET,
            "confidence": 0.4,
            "origin": "system_fallback",
            "reason": "Ningún marcador de modelo objetivo en el texto; se aplica el fallback genérico.",
        })

    if role == _DEFAULT_ROLE:
        assumptions.append({
            "field": "role",
            "value": _DEFAULT_ROLE,
            "confidence": 0.5,
            "origin": "system_fallback",
            "reason": "Sin pistas de rol en el texto; se asume el rol operador por defecto.",
        })
    else:
        assumptions.append({
            "field": "role",
            "value": role,
            "confidence": 0.7,
            "origin": "system_inferred",
            "reason": "Rol deducido de palabras clave del texto, no declarado explícitamente.",
        })
    return assumptions


def _field_confidence(
    text: str, *, language: str, target: str, role: str, goal: str,
    tasks: list[str], constraints: list[str], priorities: list[str],
    tools: list[str], output: list[str], style: list[str], risks: list[str],
) -> dict[str, float]:
    def list_conf(values: list[str]) -> float:
        return 0.8 if values else 0.2

    return {
        "goal": 0.9 if (text.strip() and goal != _DEFAULT_GOAL) else 0.2,
        "target": 0.9 if target != _FALLBACK_TARGET else 0.4,
        "role": 0.7 if role != _DEFAULT_ROLE else 0.5,
        "language": 0.9 if language in ("es", "en") and text.strip() else 0.4,
        "tasks": list_conf(tasks),
        "constraints": list_conf(constraints),
        "priorities": list_conf(priorities),
        "tools": list_conf(tools),
        "output": list_conf(output),
        "style": list_conf(style),
        "risks": list_conf(risks),
    }


def extract_semantics(text: str) -> dict[str, Any]:
    patterns = _load_patterns()
    language = _detect_language(text)
    target = _find_target(text, patterns)
    role = _find_role(text, patterns)
    goal = _extract_goal(text, patterns)
    tasks = _extract_tasks(text, patterns)
    constraints = _extract_constraints(text, patterns)
    priorities = _extract_priorities(text)
    tools = _extract_tools(text)
    output = _extract_output(text)
    style = _extract_style(text)
    risks = _extract_risks(text)
    contradictions = _detect_contradictions(text)
    ambiguities = _detect_ambiguities(
        text, goal=goal, target=target, tasks=tasks, output=output
    )
    assumptions = _build_assumptions(text, language=language, target=target, role=role)
    confidence = _field_confidence(
        text, language=language, target=target, role=role, goal=goal,
        tasks=tasks, constraints=constraints, priorities=priorities,
        tools=tools, output=output, style=style, risks=risks,
    )
    return {
        "language": language,
        "target": target,
        "role": role,
        "goal": goal,
        "tasks": tasks,
        "constraints": constraints,
        "priorities": priorities,
        "tools": tools,
        "output": output,
        "style": style,
        "risks": risks,
        "context": None,
        "safety_constraints": [c for c in constraints if c in [
            "no_sudo", "no_external_api", "no_destructive_actions",
            "stay_inside_project_root", "offline_only",
        ]],
        # B.2 — semantic gap analysis (additive; no A.6-verified field removed)
        "ambiguities": ambiguities,
        "contradictions": contradictions,
        "assumptions": assumptions,
        "confidence": confidence,
    }
