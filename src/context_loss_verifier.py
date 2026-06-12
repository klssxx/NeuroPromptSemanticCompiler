from __future__ import annotations

import re
from typing import Any

from rop_template import validate_rop_text


INTERNAL_TERMS = {
    "extract_semantics",
    "map_seeds",
    "compile_nsl",
    "reconstruct_prompt",
    "verify_context_loss",
    "export_reports",
    "test_pipeline",
    "semantic_extraction",
    "profile_resolution",
    "seed_mapping",
    "nsl_compilation",
    "prompt_reconstruction",
}


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(p.lower() in lowered for p in phrases)


def _word_count(text: str) -> int:
    return len(re.findall(r"\w+", text, flags=re.UNICODE))


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / max(1, denominator), 3)


def _text_tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"\w+", text.lower(), flags=re.UNICODE) if len(t) > 3}


def _unsupported_additions(original: str, output: str, allowed_terms: set[str]) -> list[str]:
    original_tokens = _text_tokens(original)
    output_tokens = _text_tokens(output)
    additions = sorted(token for token in (output_tokens - original_tokens) if token not in allowed_terms)
    return additions[:80]


def verify_context_loss(
    original: str,
    semantics: dict[str, Any],
    reconstructed: str,
    nsl_text: str,
    profile_name: str = "STANDARD",
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fields = {
        "role": semantics.get("role"),
        "goal": semantics.get("goal"),
        "context": semantics.get("context"),
        "tasks": semantics.get("tasks"),
        "constraints": semantics.get("constraints"),
        "priorities": semantics.get("priorities"),
        "tools": semantics.get("tools"),
        "output": semantics.get("output"),
        "style": semantics.get("style"),
        "risks": semantics.get("risks"),
        "target": semantics.get("target"),
        "safety": semantics.get("safety_constraints"),
    }

    critical_losses: list[str] = []
    warnings: list[str] = []
    profile_failures: list[str] = []
    preserved_fields: list[str] = []
    missing_fields: list[str] = []
    score = 100

    nsl_lower = nsl_text.lower()
    rec_lower = reconstructed.lower()
    combined_lower = f"{nsl_lower}\n{rec_lower}"
    profile_upper = profile_name.upper()
    original_words = _word_count(original)
    nsl_words = _word_count(nsl_text)
    reconstructed_words = _word_count(reconstructed)

    if fields["goal"] and str(fields["goal"]).lower()[:20] in rec_lower:
        preserved_fields.append("goal")
        objective_preservation = "preserved"
    else:
        missing_fields.append("goal")
        critical_losses.append("missing_goal")
        score -= 30
        objective_preservation = "missing"

    safety_phrases = {
        "no_sudo": ["no_sudo", "sin sudo", "no sudo"],
        "no_external_api": ["no_external_api", "sin api", "no api", "no external api"],
        "no_destructive_actions": ["no_destructive_actions", "nada destructivo", "no destructive"],
        "stay_inside_project_root": ["stay_inside_project_root", "stay inside", "no tocar fuera"],
    }

    for label, phrases in safety_phrases.items():
        if _contains_any(original, phrases):
            if _contains_any(nsl_lower, [label]) or _contains_any(rec_lower, phrases):
                preserved_fields.append(label)
            else:
                missing_fields.append(label)
                critical_losses.append(f"missing_{label}")
                score -= 25

    for field_name in ["context", "tasks", "constraints", "priorities", "tools", "output", "style", "risks", "target"]:
        value = fields.get(field_name)
        if not value:
            continue
        if isinstance(value, list):
            joined = " ".join(str(v) for v in value)
        else:
            joined = str(value)
        tokens = [t for t in re.split(r"[\s,;:_\-]+", joined.lower()) if len(t) > 3][:8]
        matched = sum(1 for token in tokens if token in nsl_lower or token in rec_lower)
        if tokens and matched >= max(1, len(tokens) // 3):
            preserved_fields.append(field_name)
        elif tokens:
            missing_fields.append(field_name)
            score -= 6
            warnings.append(f"weak_{field_name}_preservation")

    if "output" in missing_fields:
        warnings.append("missing_output_contract")
        score -= 10

    critical_present = [item for item in ["no_sudo", "no_external_api", "no_destructive_actions", "stay_inside_project_root"] if item in preserved_fields]
    role_preservation = "preserved" if fields.get("role") and str(fields.get("role")).lower()[:8] in combined_lower else "weak"
    context_preservation = "preserved" if "context" in preserved_fields else ("not_applicable" if not fields.get("context") else "weak")
    deliverable_preservation = "preserved" if "output" in preserved_fields else ("not_applicable" if not fields.get("output") else "weak")
    output_schema_preservation = "preserved" if ("output_schema" in combined_lower or "expected output" in combined_lower or "output" in preserved_fields) else "weak"
    possible_omissions = [f for f in missing_fields if f not in {"target"}]
    allowed_additions = set()
    for key in ("constraints", "safety_constraints", "style", "priorities", "profile_template_tasks", "profile_template_outputs"):
        allowed_additions.update(str(item).lower() for item in semantics.get(key, []))
    allowed_additions.update({"role", "goal", "context", "tasks", "constraints", "output", "style", "validation", "nsl", "prompt"})
    unsupported = _unsupported_additions(original, reconstructed, allowed_additions)
    internal_contamination = sorted(term for term in INTERNAL_TERMS if term in combined_lower and term not in original.lower())
    unsupported_addition_score = min(100, len(unsupported) * 2 + len(internal_contamination) * 15)
    permitted_profile_expansion = profile_upper in {"ROP", "RESEARCH_MAX"}
    if permitted_profile_expansion:
        unsupported_addition_score = min(35, unsupported_addition_score)
        warnings.append("deliberate_profile_expansion")
    contradiction_markers = [
        ("no_sudo", ["run sudo", "sudo apt", "sudo install"]),
        ("no_external_api", ["call external api", "send to server", "upload prompt"]),
        ("no_destructive_actions", ["delete files", "remove files permanently", "rm -rf"]),
    ]
    contradictions = []
    for constraint, markers in contradiction_markers:
        if constraint in fields.get("constraints", []) and any(marker in rec_lower for marker in markers):
            contradictions.append(f"contradicts_{constraint}")
    contradiction_score = min(100, len(contradictions) * 40)
    user_constraints = set(fields.get("constraints") or [])
    traced_constraints = set(critical_present) | {c for c in user_constraints if c.lower() in combined_lower}
    constraint_traceability_score = int(100 * len(traced_constraints) / max(1, len(user_constraints))) if user_constraints else 100
    retention_score = score
    precision_score = max(0, 100 - unsupported_addition_score - contradiction_score)
    utility_score = max(0, min(100, int((retention_score * 0.5) + (precision_score * 0.3) + (constraint_traceability_score * 0.2))))
    risk_score = min(100, unsupported_addition_score + contradiction_score + max(0, 100 - retention_score))
    compression_ratio_nsl = _ratio(nsl_words, original_words)
    expansion_ratio_execution_prompt = _ratio(reconstructed_words, original_words)
    original_token_estimate = original_words
    nsl_token_estimate = nsl_words
    execution_prompt_token_estimate = reconstructed_words
    nsl_size_ratio = compression_ratio_nsl
    execution_size_ratio = expansion_ratio_execution_prompt
    nsl_token_change_percent = round((nsl_size_ratio - 1.0) * 100, 1)
    execution_token_change_percent = round((execution_size_ratio - 1.0) * 100, 1)

    if internal_contamination:
        warnings.append("internal_pipeline_contamination")
        profile_failures.append("unsupported_internal_terms")
    if unsupported_addition_score >= 35 and not permitted_profile_expansion:
        warnings.append("unsupported_additions_high")
    if contradiction_score:
        warnings.append("contradiction_detected")
        profile_failures.extend(contradictions)
    if profile_upper == "FAST" and expansion_ratio_execution_prompt > 2.0:
        warnings.append(f"fast_execution_prompt_expansion:{expansion_ratio_execution_prompt}")
        profile_failures.append("fast_expanded_too_much")
    if profile_upper == "FAST" and original_words < 10 and nsl_size_ratio > 1.0:
        warnings.append(f"fast_nsl_schema_overhead_for_short_prompt:{nsl_size_ratio}")
    if expansion_ratio_execution_prompt > 4.0 and profile_upper not in {"ROP", "RESEARCH_MAX"}:
        warnings.append(f"execution_prompt_expansion_high:{expansion_ratio_execution_prompt}")
    if score >= 90 and precision_score < 70 and not permitted_profile_expansion:
        warnings.append("high_retention_but_low_precision")

    validation = (profile or {}).get("validation", {})
    min_score = int(validation.get("min_score", 70))
    if profile_upper == "FAST":
        if critical_losses:
            profile_failures.append("fast_critical_loss")
        elif score < min_score:
            warnings.append(f"fast_low_score:{score}<{min_score}")
    elif profile_upper == "STANDARD":
        if critical_losses:
            profile_failures.append("standard_critical_loss")
        if score < min_score:
            warnings.append(f"standard_low_score:{score}<{min_score}")
    elif profile_upper == "ADVANCED":
        required = {"goal", "constraints", "output"}
        for field in sorted(required.intersection(set(missing_fields))):
            profile_failures.append(f"advanced_missing_{field}")
        if critical_losses:
            profile_failures.append("advanced_critical_loss")
        if score < min_score:
            profile_failures.append(f"advanced_score_below_min:{score}<{min_score}")
    elif profile_upper == "ROP":
        for missing in validate_rop_text(reconstructed):
            profile_failures.append(f"rop_missing_{missing.lower()}")
        if critical_losses:
            profile_failures.append("rop_critical_loss")
        if score < min_score:
            profile_failures.append(f"rop_score_below_min:{score}<{min_score}")
    elif profile_upper == "RESEARCH_MAX":
        strict_required = {"goal", "context", "tasks", "constraints", "output", "risks"}
        for field in sorted(strict_required.intersection(set(missing_fields))):
            profile_failures.append(f"research_max_missing_{field}")
        if critical_losses:
            profile_failures.append("research_max_critical_loss")
        blocking_warnings = [warning for warning in warnings if warning != "deliberate_profile_expansion"]
        if blocking_warnings:
            profile_failures.append("research_max_warnings_present")
        if score < min_score:
            profile_failures.append(f"research_max_score_below_min:{score}<{min_score}")

    score = max(0, min(100, int((retention_score * 0.55) + (precision_score * 0.25) + (constraint_traceability_score * 0.20) - (contradiction_score * 0.25))))

    if critical_losses:
        recommendation = "safe"
    elif profile_failures and profile_upper in {"ADVANCED", "ROP", "RESEARCH_MAX"}:
        recommendation = "increase_preservation_or_review"
    elif any("weak_" in warning for warning in warnings):
        recommendation = "balanced"
    else:
        recommendation = "aggressive_not_recommended" if "compression_may_reduce_nuance" in nsl_lower else "balanced"

    return {
        "score": score,
        "aggregate_score_formula": "0.55*retention_score + 0.25*precision_score + 0.20*constraint_traceability_score - 0.25*contradiction_score",
        "critical_losses": sorted(set(critical_losses)),
        "warnings": sorted(set(warnings)),
        "profile": profile_upper,
        "profile_status": "fail" if profile_failures else "pass",
        "profile_failures": sorted(set(profile_failures)),
        "preserved_fields": sorted(set(preserved_fields)),
        "missing_fields": sorted(set(missing_fields)),
        "recommendation": recommendation,
        "objective_preservation": objective_preservation,
        "critical_constraint_preservation": "preserved" if not any(item.startswith("missing_no_") or item.startswith("missing_stay_") for item in critical_losses) else "missing",
        "deliverable_preservation": deliverable_preservation,
        "output_schema_preservation": output_schema_preservation,
        "role_preservation": role_preservation,
        "context_preservation": context_preservation,
        "semantic_retention_score": score,
        "retention_score": retention_score,
        "precision_score": precision_score,
        "unsupported_addition_score": unsupported_addition_score,
        "permitted_profile_expansion": permitted_profile_expansion,
        "unsupported_additions": unsupported,
        "internal_contamination": internal_contamination,
        "contradiction_score": contradiction_score,
        "contradictions": contradictions,
        "constraint_traceability_score": constraint_traceability_score,
        "original_token_estimate": original_token_estimate,
        "nsl_token_estimate": nsl_token_estimate,
        "execution_prompt_token_estimate": execution_prompt_token_estimate,
        "nsl_size_ratio": nsl_size_ratio,
        "execution_size_ratio": execution_size_ratio,
        "nsl_token_change_percent": nsl_token_change_percent,
        "execution_token_change_percent": execution_token_change_percent,
        "metric_notes": {
            "nsl_size_ratio": "Ratio aproximado NSL/original. <1.0 indica reduccion; >1.0 indica expansion.",
            "execution_size_ratio": "Ratio aproximado prompt_de_ejecucion/original. ROP y RESEARCH_MAX pueden expandir de forma deliberada.",
            "legacy_aliases": {
                "compression_ratio_nsl": "nsl_size_ratio",
                "expansion_ratio_execution_prompt": "execution_size_ratio",
            },
        },
        "compression_ratio_nsl": compression_ratio_nsl,
        "expansion_ratio_execution_prompt": expansion_ratio_execution_prompt,
        "utility_score": utility_score,
        "risk_score": risk_score,
        "possible_omissions": sorted(set(possible_omissions)),
        "critical_constraints_preserved": critical_present,
    }
