from __future__ import annotations

from typing import Iterable


CONSTRAINT_ALIASES = {
    "no_api": "no_external_api",
    "no_external_api": "no_external_api",
    "sin_api": "no_external_api",
    "no_sudo": "no_sudo",
    "sin_sudo": "no_sudo",
    "no_destructive": "no_destructive_actions",
    "no_destructive_actions": "no_destructive_actions",
    "stay_inside_root": "stay_inside_project_root",
    "stay_inside_project_root": "stay_inside_project_root",
    "do_not_modify_outside_project": "stay_inside_project_root",
}

CRITICAL_CONSTRAINTS = [
    "no_sudo",
    "no_external_api",
    "no_destructive_actions",
    "stay_inside_project_root",
]


def normalize_constraint(value: str) -> str:
    key = value.strip().lower().replace("-", "_").replace(" ", "_")
    return CONSTRAINT_ALIASES.get(key, key)


def normalize_constraints(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = normalize_constraint(str(value))
        if normalized and normalized not in seen:
            out.append(normalized)
            seen.add(normalized)
    return out


def critical_constraints(values: Iterable[str]) -> list[str]:
    normalized = set(normalize_constraints(values))
    return [item for item in CRITICAL_CONSTRAINTS if item in normalized]
