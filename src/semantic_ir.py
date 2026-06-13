from __future__ import annotations

from typing import Any

from constraint_normalizer import critical_constraints


SCHEMA_VERSION = "NPSC-HYBRID/1.0"


def origin_items(values: list[str], origin: str, layer: str) -> list[dict[str, str]]:
    return [{"value": str(value), "origin": origin, "layer": layer} for value in values]


def privacy_source(raw_prompt: str, sha256: str, language: str, privacy_mode: str) -> dict[str, Any]:
    if privacy_mode == "hash_only":
        return {"sha256": sha256, "language": language, "privacy_mode": privacy_mode}
    if privacy_mode == "redacted_preview":
        preview = raw_prompt[:80] + ("..." if len(raw_prompt) > 80 else "")
        return {"raw_prompt_preview": preview, "sha256": sha256, "language": language, "privacy_mode": privacy_mode}
    return {"raw_prompt": raw_prompt, "sha256": sha256, "language": language, "privacy_mode": "full_original"}


def build_semantic_ir(
    *,
    raw_prompt: str,
    sha256: str,
    semantics: dict[str, Any],
    requested_profile: str,
    applied_profile: str,
    auto_info: dict[str, Any],
    canonical_nsl: str,
    optimized_prompt: str,
    validation: dict[str, Any],
    profile_payload: dict[str, Any] | None = None,
    compiler_trace: dict[str, Any] | None = None,
    policy_layer: dict[str, Any] | None = None,
    target_adapter_layer: dict[str, Any] | None = None,
    privacy_mode: str = "full_original",
) -> dict[str, Any]:
    constraints = list(semantics.get("constraints", []))
    policy_constraints = list((policy_layer or {}).get("policy_constraints", []))
    adapter_constraints = list((target_adapter_layer or {}).get("adapter_constraints", []))
    profile_constraints = list(semantics.get("profile_template_constraints", []))
    effective_constraints = list(dict.fromkeys(constraints + policy_constraints + adapter_constraints + profile_constraints))
    selection_reason = auto_info.get("selection_reason", "")
    if isinstance(selection_reason, str):
        selection_reason_items = [item.strip() for item in selection_reason.split(",") if item.strip()]
    else:
        selection_reason_items = list(selection_reason or [])

    return {
        "schema_version": SCHEMA_VERSION,
        "source": privacy_source(raw_prompt, sha256, semantics.get("language", "unknown"), privacy_mode),
        "selection": {
            "requested_profile": requested_profile,
            "applied_profile": applied_profile,
            "selection_reason": selection_reason_items,
            "risk_flags": list(auto_info.get("risk_flags", [])),
            "fallback_profile": auto_info.get("fallback_profile", ""),
            "confidence": auto_info.get("confidence"),
            "features": auto_info.get("features", {}),
            "scores": auto_info.get("scores", {}),
        },
        "semantic_ir": {
            "role": semantics.get("role", ""),
            "objectives": [semantics.get("goal", "")] if semantics.get("goal") else [],
            "context": list(semantics.get("context", [])),
            "constraints": constraints,
            "critical_constraints": critical_constraints(constraints),
            "deliverables": list(semantics.get("output", [])),
            "quality_criteria": list(semantics.get("priorities", [])),
            "verification_requirements": ["context_loss", "critical_constraints", "run_summary"],
            "unknowns": list(semantics.get("unknowns", [])),
            "tasks": list(semantics.get("tasks", [])),
            "risks": list(semantics.get("risks", [])),
            "target": semantics.get("target", ""),
        },
        "user_intent_ir": {
            "role": {"value": semantics.get("role", ""), "origin": "user_inferred", "layer": "USER_INTENT_IR"},
            "goal": {"value": semantics.get("goal", ""), "origin": "user_inferred", "layer": "USER_INTENT_IR"},
            "tasks": origin_items(list(semantics.get("tasks", [])), "user_inferred", "USER_INTENT_IR"),
            "deliverables": origin_items(list(semantics.get("output", [])), "user_inferred", "USER_INTENT_IR"),
            "user_constraints": origin_items(constraints, "user_explicit", "USER_INTENT_IR"),
            "context": origin_items(list(semantics.get("context", [])), "user_inferred", "USER_INTENT_IR"),
        },
        "compiler_trace": compiler_trace or {},
        "policy_layer": policy_layer or {"policy_constraints": [], "origin": "product_policy"},
        "target_adapter_layer": target_adapter_layer or {"adapter_constraints": [], "origin": "target_adapter"},
        "effective_prompt_ir": {
            "effective_constraints": (
                origin_items(constraints, "user_explicit", "EFFECTIVE_PROMPT_IR")
                + origin_items(policy_constraints, "product_policy", "EFFECTIVE_PROMPT_IR")
                + origin_items(adapter_constraints, "target_adapter", "EFFECTIVE_PROMPT_IR")
                + origin_items(profile_constraints, "profile_template", "EFFECTIVE_PROMPT_IR")
            ),
            "constraint_values": effective_constraints,
            "profile_template_tasks": origin_items(list(semantics.get("profile_template_tasks", [])), "profile_template", "EFFECTIVE_PROMPT_IR"),
            "profile_template_outputs": origin_items(list(semantics.get("profile_template_outputs", [])), "profile_template", "EFFECTIVE_PROMPT_IR"),
        },
        "canonical_nsl": canonical_nsl,
        "optimized_prompt": optimized_prompt,
        "profile_payload": profile_payload or {},
        "validation": {
            "semantic_retention_score": validation.get("semantic_retention_score", validation.get("score", 0)),
            "critical_constraints_preserved": validation.get("critical_constraint_preservation") == "preserved",
            "warnings": list(validation.get("warnings", [])),
            "possible_omissions": list(validation.get("possible_omissions", [])),
            "profile_status": validation.get("profile_status", "unknown"),
            "profile_failures": list(validation.get("profile_failures", [])),
        },
    }
