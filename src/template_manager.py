from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils import ensure_dir


@dataclass
class PromptTemplate:
    id: str
    name: str
    content: str
    category: str = "General"
    description: str = ""
    variables: list[str] = field(default_factory=list)
    target: str = "auto"
    profile: str = "AUTO"
    created_at: str = ""
    updated_at: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> PromptTemplate:
        return PromptTemplate(**{k: v for k, v in data.items() if k in PromptTemplate.__dataclass_fields__})


class TemplateManager:
    """CRUD manager for reusable prompt templates stored as JSON files."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        if storage_dir is None:
            from npsc_gui.settings import data_dir
            storage_dir = data_dir() / "templates"
        self._dir = ensure_dir(storage_dir)
        self._templates: dict[str, PromptTemplate] = {}
        self._load_all()

    @property
    def storage_dir(self) -> Path:
        return self._dir

    def _load_all(self) -> None:
        self._templates = {}
        for path in sorted(self._dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                tpl = PromptTemplate.from_dict(data)
                self._templates[tpl.id] = tpl
            except Exception:
                continue  # skip corrupt files

    def _save_file(self, tpl: PromptTemplate) -> None:
        path = self._dir / f"{tpl.id}.json"
        path.write_text(json.dumps(tpl.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _remove_file(self, tpl_id: str) -> None:
        path = self._dir / f"{tpl_id}.json"
        if path.exists():
            path.unlink()

    # ── CRUD ──

    def list_all(self) -> list[PromptTemplate]:
        return sorted(self._templates.values(), key=lambda t: t.updated_at, reverse=True)

    def get(self, tpl_id: str) -> PromptTemplate | None:
        return self._templates.get(tpl_id)

    def create(self, tpl: PromptTemplate) -> PromptTemplate:
        if tpl.id in self._templates:
            raise ValueError(f"Template id already exists: {tpl.id}")
        tpl.updated_at = datetime.now(timezone.utc).isoformat()
        self._templates[tpl.id] = tpl
        self._save_file(tpl)
        return tpl

    def update(self, tpl: PromptTemplate) -> PromptTemplate:
        if tpl.id not in self._templates:
            raise KeyError(f"Template not found: {tpl.id}")
        tpl.updated_at = datetime.now(timezone.utc).isoformat()
        self._templates[tpl.id] = tpl
        self._save_file(tpl)
        return tpl

    def delete(self, tpl_id: str) -> bool:
        if tpl_id in self._templates:
            del self._templates[tpl_id]
            self._remove_file(tpl_id)
            return True
        return False

    def duplicate(self, tpl_id: str, new_name: str | None = None) -> PromptTemplate:
        original = self._templates.get(tpl_id)
        if not original:
            raise KeyError(f"Template not found: {tpl_id}")
        from utils import now_run_id
        new_id = now_run_id("tpl")
        data = original.to_dict()
        data["id"] = new_id
        data["name"] = new_name or f"{original.name} (copia)"
        data["created_at"] = ""
        data["updated_at"] = ""
        new_tpl = PromptTemplate.from_dict(data)
        return self.create(new_tpl)

    # ── Categories ──

    def categories(self) -> list[str]:
        cats = sorted(set(t.category for t in self._templates.values()))
        return cats

    def by_category(self, category: str) -> list[PromptTemplate]:
        return [t for t in self._templates.values() if t.category == category]

    # ── Import / Export ──

    def export_template(self, tpl_id: str, dest: str | Path) -> Path:
        tpl = self._templates.get(tpl_id)
        if not tpl:
            raise KeyError(f"Template not found: {tpl_id}")
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(json.dumps(tpl.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return dest_path

    def import_template(self, src: str | Path) -> PromptTemplate:
        src_path = Path(src)
        data = json.loads(src_path.read_text(encoding="utf-8"))
        # Ensure unique ID on import
        if "id" not in data:
            from utils import now_run_id
            data["id"] = now_run_id("tpl")
        tpl = PromptTemplate.from_dict(data)
        if tpl.id in self._templates:
            from utils import now_run_id
            tpl.id = now_run_id("tpl")
        return self.create(tpl)

    def export_all(self, dest_dir: str | Path) -> list[Path]:
        dest = ensure_dir(dest_dir)
        written = []
        for tpl in self._templates.values():
            path = dest / f"{tpl.id}.json"
            path.write_text(json.dumps(tpl.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            written.append(path)
        return written

    def count(self) -> int:
        return len(self._templates)
