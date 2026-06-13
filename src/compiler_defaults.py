from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from resource_paths import resource_path


DEFAULTS_PATH = resource_path("configs/compiler_defaults.json")
_cached_compiler_defaults: dict[str, Any] | None = None


def load_compiler_defaults(path: str | Path | None = None) -> dict[str, Any]:
    global _cached_compiler_defaults
    if _cached_compiler_defaults is not None and path is None:
        return _cached_compiler_defaults
    source = Path(path) if path else DEFAULTS_PATH
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FileNotFoundError(f"Cannot load compiler defaults from {source}: {exc}") from exc
    if path is None:
        _cached_compiler_defaults = data
    return data


def strict_policy(path: str | Path | None = None) -> dict[str, Any]:
    return dict(load_compiler_defaults(path).get("strict_policy", {}))
