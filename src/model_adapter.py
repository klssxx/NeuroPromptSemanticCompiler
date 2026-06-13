from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from resource_paths import resource_path

PROFILES_PATH = resource_path("configs/model_profiles.json")

_cached_model_profiles: dict[str, Any] | None = None


def load_model_profiles(path: str | Path | None = None) -> dict[str, Any]:
    global _cached_model_profiles
    if _cached_model_profiles is not None and path is None:
        return _cached_model_profiles
    source = Path(path) if path else PROFILES_PATH
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(f"Cannot load model profiles from {source}: {exc}") from exc
    if path is None:
        _cached_model_profiles = data
    return data


def get_model_profile(target: str, profiles: dict[str, Any] | None = None) -> dict[str, Any]:
    data = profiles or load_model_profiles()
    return data.get(target, data["generic"])


def select_level(requested_level: str, target: str, profiles: dict[str, Any] | None = None) -> str:
    if requested_level != "all":
        return requested_level
    profile = get_model_profile(target, profiles)
    recommended = profile.get("best_level", "balanced")
    return "safe" if recommended == "safe" else "balanced"


def adapter_layer(target: str, profiles: dict[str, Any] | None = None, custom_model_name: str | None = None) -> dict[str, Any]:
    profile = get_model_profile(target, profiles)
    resolved_name = custom_model_name.strip() if custom_model_name and target == "custom" else profile.get("label", target)
    constraints = list(profile.get("constraints", []))
    raw_notes = profile.get("notes", [])
    notes = [raw_notes] if isinstance(raw_notes, str) and raw_notes else list(raw_notes)
    if target == "custom" and resolved_name:
        notes.append(f"custom_model_name:{resolved_name}")
    return {
        "target": target,
        "model_name": resolved_name or target,
        "origin": "target_adapter",
        "adapter_constraints": constraints,
        "adapter_notes": notes,
        "best_level": profile.get("best_level", "balanced"),
    }
