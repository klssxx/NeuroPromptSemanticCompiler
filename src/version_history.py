from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils import ensure_dir


@dataclass
class PromptVersion:
    id: str
    name: str
    content: str                    # The compiled/prompt text at this version
    informal_input: str = ""        # Original informal input
    target: str = "auto"
    profile: str = "AUTO"
    level: str = "profile_default"
    created_at: str = ""
    notes: str = ""
    variables_used: dict[str, str] = field(default_factory=dict)
    template_id: str = ""
    format_exported: str = "none"   # none, markdown, json, txt
    parent_version_id: str = ""     # For version chains

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "PromptVersion":
        valid_fields = set(PromptVersion.__dataclass_fields__)
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return PromptVersion(**filtered)

    @property
    def display_date(self) -> str:
        try:
            dt = datetime.fromisoformat(self.created_at)
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return self.created_at

    @property
    def short_content(self) -> str:
        """First 120 chars for list display."""
        return self.content[:120].replace("\n", " ") + ("..." if len(self.content) > 120 else "")


class VersionHistory:
    """Persistent version history for compiled prompts."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        if storage_dir is None:
            from npsc_gui.settings import data_dir
            storage_dir = data_dir() / "history"
        self._dir = ensure_dir(storage_dir)
        self._versions: dict[str, PromptVersion] = {}
        self._load_all()

    @property
    def storage_dir(self) -> Path:
        return self._dir

    def _index_path(self) -> Path:
        return self._dir / "_index.json"

    def _load_all(self) -> None:
        self._versions = {}
        index = self._index_path()
        if not index.exists():
            return
        try:
            entries = json.loads(index.read_text(encoding="utf-8"))
            if not isinstance(entries, list):
                return
            for entry in entries:
                vid = entry.get("id", "")
                vpath = self._dir / f"{vid}.json"
                if vpath.exists():
                    try:
                        data = json.loads(vpath.read_text(encoding="utf-8"))
                        ver = PromptVersion.from_dict(data)
                        self._versions[ver.id] = ver
                    except Exception:
                        continue
        except Exception:
            return

    def _save_index(self) -> None:
        entries = [v.to_dict() for v in self._versions.values()]
        self._index_path().write_text(
            json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _save_version(self, ver: PromptVersion) -> None:
        path = self._dir / f"{ver.id}.json"
        path.write_text(json.dumps(ver.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _remove_version(self, ver_id: str) -> None:
        path = self._dir / f"{ver_id}.json"
        if path.exists():
            path.unlink()

    # ── CRUD ──

    def list_all(self) -> list[PromptVersion]:
        return sorted(self._versions.values(), key=lambda v: v.created_at, reverse=True)

    def get(self, ver_id: str) -> PromptVersion | None:
        return self._versions.get(ver_id)

    def save(self, ver: PromptVersion) -> PromptVersion:
        self._versions[ver.id] = ver
        self._save_version(ver)
        self._save_index()
        return ver

    def create_version(
        self,
        *,
        name: str,
        content: str,
        informal_input: str = "",
        target: str = "auto",
        profile: str = "AUTO",
        level: str = "profile_default",
        notes: str = "",
        variables_used: dict[str, str] | None = None,
        template_id: str = "",
        parent_version_id: str = "",
    ) -> PromptVersion:
        from utils import now_run_id
        ver = PromptVersion(
            id=now_run_id("ver"),
            name=name,
            content=content,
            informal_input=informal_input,
            target=target,
            profile=profile,
            level=level,
            notes=notes,
            variables_used=variables_used or {},
            template_id=template_id,
            parent_version_id=parent_version_id,
        )
        return self.save(ver)

    def delete(self, ver_id: str) -> bool:
        if ver_id in self._versions:
            del self._versions[ver_id]
            self._remove_version(ver_id)
            self._save_index()
            return True
        return False

    def update_notes(self, ver_id: str, notes: str) -> PromptVersion:
        ver = self._versions.get(ver_id)
        if not ver:
            raise KeyError(f"Version not found: {ver_id}")
        ver.notes = notes
        return self.save(ver)

    def count(self) -> int:
        return len(self._versions)


def compute_diff(old_text: str, new_text: str) -> dict[str, Any]:
    """Compute a readable diff between two texts.
    
    Returns:
        {
            "added": list[str],       # lines added
            "removed": list[str],     # lines removed
            "unchanged": list[str],   # context lines
            "stats": {
                "total_old": int,
                "total_new": int,
                "added_count": int,
                "removed_count": int,
            }
        }
    """
    import difflib

    old_lines = old_text.splitlines(keepends=False)
    new_lines = new_text.splitlines(keepends=False)

    added = []
    removed = []
    unchanged = []

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            for line in new_lines[j1:j2]:
                added.append(line)
        elif tag == "delete":
            for line in old_lines[i1:i2]:
                removed.append(line)
        elif tag == "replace":
            for line in old_lines[i1:i2]:
                removed.append(line)
            for line in new_lines[j1:j2]:
                added.append(line)
        else:  # equal
            for line in old_lines[i1:i2]:
                unchanged.append(line)

    return {
        "added": added,
        "removed": removed,
        "unchanged": unchanged,
        "stats": {
            "total_old": len(old_lines),
            "total_new": len(new_lines),
            "added_count": len(added),
            "removed_count": len(removed),
        },
    }


def compute_unified_diff(old_text: str, new_text: str, old_label: str = "version_a", new_label: str = "version_b") -> str:
    """Return a unified diff string between two texts."""
    import difflib
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=old_label, tofile=new_label,
        lineterm="",
    )
    return "\n".join(diff)
