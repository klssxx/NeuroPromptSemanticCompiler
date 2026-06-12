from __future__ import annotations

from pathlib import Path
import json

from resource_paths import resource_path

DEFAULT_DICTIONARY = resource_path("configs/semantic_dictionary.json")
_cached_semantic_dictionary: list[dict] | None = None

REQUIRED_SEED_FIELDS = {"id", "name", "meaning", "compact", "expansion", "categories", "target_models", "priority"}
VALID_TARGETS = {"gpt", "codex", "hermes", "claude", "gemini", "qwen", "deepseek", "llama", "mistral", "generic", "custom", "gpt55_codex"}


def load_semantic_dictionary(path: str | Path | None = None) -> list[dict]:
    global _cached_semantic_dictionary
    if _cached_semantic_dictionary is not None and path is None:
        return _cached_semantic_dictionary
    source = Path(path) if path else DEFAULT_DICTIONARY
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(f"Cannot load semantic dictionary from {source}: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("semantic_dictionary.json must be a list")
    if path is None:
        _cached_semantic_dictionary = data
    return data


def validate_semantic_dictionary(seeds: list[dict] | None = None, minimum: int = 150) -> dict:
    selected = seeds or load_semantic_dictionary()
    errors: list[str] = []
    ids: list[str] = []
    names: list[str] = []
    meanings: list[str] = []
    for index, seed in enumerate(selected):
        missing = REQUIRED_SEED_FIELDS - set(seed)
        if missing:
            errors.append(f"seed_{index}_missing:{','.join(sorted(missing))}")
        sid = str(seed.get("id", ""))
        name = str(seed.get("name", ""))
        meaning = str(seed.get("meaning", "")).strip().lower()
        ids.append(sid)
        names.append(name)
        meanings.append(meaning)
        priority = seed.get("priority", -1)
        if not isinstance(priority, int) or not 0 <= priority <= 100:
            errors.append(f"{sid}_priority_out_of_range")
        if not isinstance(seed.get("categories", []), list) or not seed.get("categories"):
            errors.append(f"{sid}_missing_categories")
        targets = set(seed.get("target_models", []))
        invalid_targets = sorted(targets - VALID_TARGETS)
        if invalid_targets:
            errors.append(f"{sid}_invalid_targets:{','.join(invalid_targets)}")
    if len(selected) < minimum:
        errors.append(f"minimum_not_met:{len(selected)}<{minimum}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate_ids")
    if len(names) != len(set(names)):
        errors.append("duplicate_names")
    duplicate_meanings = {m for m in meanings if meanings.count(m) > 1 and m}
    if duplicate_meanings:
        errors.append("duplicate_meanings")
    return {
        "count": len(selected),
        "minimum": minimum,
        "valid": not errors,
        "errors": errors,
    }
