from __future__ import annotations

import itertools

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


_last_run_id_ts = ""
_run_id_collision_seq = itertools.count(1)


def now_run_id(prefix: str = "run") -> str:
    """Timestamped id: ``{prefix}_YYYYmmdd_HHMMSS_microseconds``.

    datetime.now() can have coarse resolution on some platforms (notably
    Windows, ~1 ms), so consecutive calls can land on the exact same
    timestamp. Callers use these ids as dict keys and file names, so a
    collision silently OVERWRITES data (e.g. two version saves -> one
    lost). Same-timestamp calls therefore get a '-n' discriminator.
    """
    global _last_run_id_ts
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    if ts == _last_run_id_ts:
        return f"{prefix}_{ts}-{next(_run_id_collision_seq)}"
    _last_run_id_ts = ts
    return f"{prefix}_{ts}"


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
