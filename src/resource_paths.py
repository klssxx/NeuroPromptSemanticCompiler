from __future__ import annotations

from importlib import resources
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def resource_path(relative_path: str) -> Path:
    """Return a source-tree resource path or an installed package resource path."""
    source = ROOT / relative_path
    if source.exists():
        return source

    parts = relative_path.split("/")
    if not parts:
        raise FileNotFoundError(relative_path)
    package = "npsc_resources." + ".".join(parts[:-1]) if len(parts) > 1 else "npsc_resources"
    try:
        return Path(str(resources.files(package).joinpath(parts[-1])))
    except ModuleNotFoundError as exc:
        raise FileNotFoundError(relative_path) from exc
