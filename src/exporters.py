from __future__ import annotations

from pathlib import Path
import json

from utils import ensure_dir


def export_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def export_json(path: str | Path, content: dict | list) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare_output_dir(path: str | Path) -> Path:
    return ensure_dir(path)
