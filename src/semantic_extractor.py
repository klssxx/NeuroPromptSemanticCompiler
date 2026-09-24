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
    }
