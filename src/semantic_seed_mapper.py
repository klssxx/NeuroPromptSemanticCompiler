from __future__ import annotations

from typing import Any

from utils import unique_preserve


def _score_seed(seed: dict[str, Any], semantics: dict[str, Any], target: str, level: str) -> int:
    score = int(seed.get("priority", 50))
    categories = set(seed.get("categories", []))
    name = str(seed.get("name", ""))

    if semantics.get("safety_constraints") and "safety" in categories:
        score += 30
    if target in seed.get("target_models", []):
        score += 20
    if level == "aggressive" and "compression" in categories:
        score += 20
    if level == "safe" and "safety" in categories:
        score += 15
    if level == "balanced" and "semantic" in categories:
        score += 10

    goal = str(semantics.get("goal", "")).lower()
    if any(token in goal for token in ["compile", "compil", "semantic", "prompt"]):
        if any(token in name for token in ["semantic", "compiler", "prompt", "intent", "extract"]):
            score += 10

    constraints = set(semantics.get("constraints", []))
    constraint_map = {
        "no_sudo": "no_sudo",
        "no_external_api": "no_external_api",
        "no_destructive_actions": "no_destructive",
        "stay_inside_project_root": "stay_inside_root",
    }
    for c, needle in constraint_map.items():
        if c in constraints and needle in name:
            score += 40

    return score


def suggest_seeds(semantics: dict, dictionary: list, target: str, level: str, limit: int | None = None) -> list[dict]:
    scored = sorted(
        ((seed, _score_seed(seed, semantics, target, level)) for seed in dictionary),
        key=lambda item: item[1],
        reverse=True,
    )

    limits = {"safe": 16, "balanced": 22, "aggressive": 30, "all": 22}
    seed_limit = limit if limit is not None else limits.get(level, 22)

    selected: list[dict] = []
    selected_ids: set[str] = set()

    # Hard include critical safety seeds.
    hard_map = {
        "no_sudo": "no_sudo",
        "no_external_api": "no_external_api",
        "no_destructive_actions": "no_destructive_actions",
        "stay_inside_project_root": "stay_inside_root",
    }
    present_constraints = set(semantics.get("constraints", []))
    for constraint, seed_hint in hard_map.items():
        if constraint in present_constraints:
            for seed in dictionary:
                if seed_hint in seed.get("name", ""):
                    sid = seed.get("id")
                    if sid not in selected_ids:
                        tagged = dict(seed)
                        tagged["selection_origin"] = "user_constraint"
                        selected.append(tagged)
                        selected_ids.add(sid)
                        break

    # Include target compatibility seed where possible.
    target_alias = f"{target}_compatibility"
    for seed in dictionary:
        if seed.get("name") == target_alias and seed.get("id") not in selected_ids:
            tagged = dict(seed)
            tagged["selection_origin"] = "target_adapter"
            selected.append(tagged)
            selected_ids.add(seed["id"])
            break

    # Fill from score order.
    for seed, _score in scored:
        sid = seed.get("id")
        if sid in selected_ids:
            continue
        categories = set(seed.get("categories", []))
        if "safety" in categories and not present_constraints:
            continue
        tagged = dict(seed)
        tagged["selection_origin"] = "user_intent" if categories else "semantic_match"
        selected.append(tagged)
        selected_ids.add(sid)
        if len(selected) >= seed_limit:
            break

    ordered_ids = unique_preserve([s["id"] for s in selected])
    final = [next(seed for seed in selected if seed["id"] == sid) for sid in ordered_ids]
    return final
