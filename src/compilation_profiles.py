from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from constraint_normalizer import CRITICAL_CONSTRAINTS, normalize_constraints
from rop_template import render_rop
from resource_paths import resource_path


PROFILES_PATH = resource_path("configs/compilation_profiles.json")
_cached_compilation_profiles: dict[str, Any] | None = None

PROFILE_ALIASES = {
    "FAST": "FAST",
    "STANDARD": "STANDARD",
    "ADVANCED": "ADVANCED",
    "ROP": "ROP",
    "RESEARCH_MAX": "RESEARCH_MAX",
    "RESEARCH-MAX": "RESEARCH_MAX",
    "RESEARCHMAX": "RESEARCH_MAX",
    "AUTO": "AUTO",
}


def load_compilation_profiles(path: str | Path | None = None) -> dict[str, Any]:
    global _cached_compilation_profiles
    if _cached_compilation_profiles is not None and path is None:
        return _cached_compilation_profiles
    source = Path(path) if path else PROFILES_PATH
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(f"Cannot load compilation profiles from {source}: {exc}") from exc
    if path is None:
        _cached_compilation_profiles = data
    return data


def normalize_profile_name(value: str | None) -> str:
    if not value:
        return "STANDARD"
    key = value.strip().upper().replace(" ", "_")
    key = key.replace("-", "_")
    return PROFILE_ALIASES.get(key, key)


def supported_profile_names(config: dict[str, Any] | None = None) -> list[str]:
    data = config or load_compilation_profiles()
    return list(data.get("supported_profiles", []))


def validate_profile_name(value: str | None, config: dict[str, Any] | None = None) -> str:
    data = config or load_compilation_profiles()
    profile_name = normalize_profile_name(value or data.get("default_profile", "STANDARD"))
    if profile_name not in data.get("profiles", {}):
        supported = ", ".join(supported_profile_names(data))
        raise ValueError(f"Unsupported compilation profile '{value}'. Supported profiles: {supported}")
    return profile_name


def get_profile(profile_name: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    data = config or load_compilation_profiles()
    normalized = validate_profile_name(profile_name, data)
    return deepcopy(data["profiles"][normalized])


def profile_default_level(profile_name: str, profile: dict[str, Any] | None = None) -> str:
    data = profile or get_profile(profile_name)
    return str(data.get("technical_level", "balanced"))


def profile_seed_limit(profile_name: str, profile: dict[str, Any] | None = None) -> int:
    data = profile or get_profile(profile_name)
    return int(data.get("seed_limit", 22))


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def _merge_list(semantics: dict[str, Any], key: str, values: list[str]) -> None:
    semantics[key] = _unique(list(semantics.get(key, [])) + values)


def apply_profile_to_semantics(semantics: dict[str, Any], profile_name: str, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    selected = normalize_profile_name(profile_name)
    adjusted = deepcopy(semantics)
    constraints = normalize_constraints(list(adjusted.get("constraints", [])))
    for item in CRITICAL_CONSTRAINTS:
        if item in semantics.get("constraints", []) and item not in constraints:
            constraints.append(item)
    adjusted["constraints"] = _unique(constraints)
    adjusted["semantic_compilation_profile"] = selected
    adjusted["profile_template_tasks"] = []
    adjusted["profile_template_outputs"] = []
    adjusted["profile_template_constraints"] = []

    if selected == "FAST":
        _merge_list(adjusted, "style", ["compact", "low_verbosity"])
        _merge_list(adjusted, "risks", ["profile_fast_possible_context_loss"])
        _merge_list(adjusted, "priorities", ["speed", "compression"])
    elif selected == "STANDARD":
        _merge_list(adjusted, "style", ["balanced_density", "model_readable"])
        _merge_list(adjusted, "priorities", ["semantic_preservation", "clarity"])
    elif selected == "ADVANCED":
        _merge_list(adjusted, "profile_template_tasks", ["preserve_structure", "validate_outputs", "surface_risks"])
        _merge_list(adjusted, "profile_template_outputs", ["structured_contract", "verification_report"])
        _merge_list(adjusted, "style", ["expanded_structure", "strong_validation"])
        _merge_list(adjusted, "priorities", ["semantic_preservation", "context_integrity", "verification"])
    elif selected == "ROP":
        _merge_list(adjusted, "profile_template_tasks", ["generate_alternatives", "falsify_conclusions", "scenario_analysis", "self_audit"])
        _merge_list(adjusted, "profile_template_outputs", ["conclusion", "reality_model", "scenario_matrix", "option_ranking", "confidence_score"])
        _merge_list(adjusted, "style", ["reality_oriented", "adversarial_review", "evidence_levels", "convergence"])
        _merge_list(adjusted, "priorities", ["truth_approximation", "predictive_power", "practical_utility", "robustness"])
        _merge_list(adjusted, "risks", ["bias", "overconfidence", "missing_variables"])
    elif selected == "RESEARCH_MAX":
        _merge_list(adjusted, "profile_template_tasks", ["preserve_all_context", "rank_uncertainties", "validate_evidence", "audit_context_loss"])
        _merge_list(adjusted, "profile_template_outputs", ["original_context_preserved", "structured_analysis", "evidence_notes", "strict_validation_report"])
        _merge_list(adjusted, "style", ["maximum_preservation", "extensive_structured", "strict_validation"])
        _merge_list(adjusted, "priorities", ["semantic_preservation", "evidence_quality", "risk_visibility", "context_integrity"])
        _merge_list(adjusted, "risks", ["semantic_loss", "missing_evidence", "important_decision"])

    return adjusted


def render_rop_template(original_prompt: str, profile: dict[str, Any] | None = None) -> str:
    return render_rop(original_prompt)


def build_profile_status(
    requested_profile: str,
    applied_profile: str,
    profile: dict[str, Any],
    requested_level: str | None,
    chosen_level: str,
    auto_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    default_level = profile_default_level(applied_profile, profile)
    conflict = None
    if requested_level and requested_level != "all" and requested_level != default_level:
        conflict = (
            f"profile {applied_profile} recommends technical level '{default_level}', "
            f"but --level requested '{requested_level}'. --profile controls semantic intent; --level controls technical compression."
        )
    elif requested_level == "all":
        conflict = "--level all delegates technical compression to model/profile selection."

    return {
        "requested_profile": normalize_profile_name(requested_profile),
        "applied_profile": applied_profile,
        "profile_label": profile.get("label", applied_profile),
        "semantic_purpose": profile.get("purpose", ""),
        "compression": profile.get("compression", ""),
        "verbosity": profile.get("verbosity", ""),
        "output_length": profile.get("output_length", ""),
        "profile_default_level": default_level,
        "requested_level": requested_level,
        "chosen_level": chosen_level,
        "level_conflict": conflict,
        "auto": auto_info or {},
    }
