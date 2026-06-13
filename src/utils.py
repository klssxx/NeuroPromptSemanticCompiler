from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Iterable


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def now_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"


def normalize_token(text: str) -> str:
    token = text.strip().lower()
    token = re.sub(r"\s+", "_", token)
    token = re.sub(r"[^a-z0-9_\-]", "", token)
    return token


def split_items(value: str, separators: str = ",;") -> list[str]:
    if not value:
        return []
    pattern = "[" + re.escape(separators) + "]"
    items = [v.strip() for v in re.split(pattern, value) if v.strip()]
    return items


def unique_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def compact_join(items: Iterable[str], sep: str = ";") -> str:
    filtered = [i.strip() for i in items if i and i.strip()]
    return sep.join(unique_preserve(filtered))


def safe_slug(text: str, fallback: str = "item") -> str:
    slug = normalize_token(text).replace("_", "-")
    return slug or fallback
