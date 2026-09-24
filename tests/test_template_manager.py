"""Tests for template_manager.py.

Coverage lineage (A.6 integrity audit):
- Restored: the real-API CRUD/duplicate/categories/export-import coverage
  that the historical test file asserted (create, duplicate-id create raise,
  get, update, delete, duplicate, list_all, categories, export/import
  round-trip). The PR had replaced it with tests for a dict-based API
  (add_template/list_templates/...) that no implementation ever provided —
  those phantom-API tests failed at collection-behind-ruff and are superseded
  by this file.
- Kept from the PR (P1-5 intent, adapted to the real file-based
  import_template(src: Path) API): importing a template whose id collides
  with an existing one must NEVER silently overwrite the original. The
  implementation regenerates a fresh id in that case, which satisfies the
  data-integrity invariant; these tests pin that invariant so a future
  refactor cannot silently drop it.
"""
from __future__ import annotations

import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from template_manager import PromptTemplate, TemplateManager


@pytest.fixture()
def manager(tmp_path):
    return TemplateManager(storage_dir=tmp_path)


def _tpl(tid: str, name: str = "Test", content: str = "Hello {{x}}", **kwargs) -> PromptTemplate:
    return PromptTemplate(id=tid, name=name, content=content, **kwargs)


class TestTemplateManagerCRUD:
    def test_create_template(self, manager):
        manager.create(_tpl("tpl-1"))
        assert manager.count() == 1

    def test_create_duplicate_id_raises(self, manager):
        manager.create(_tpl("tpl-1"))
        with pytest.raises(ValueError):
            manager.create(_tpl("tpl-1"))

    def test_get_template(self, manager):
        manager.create(_tpl("tpl-1", name="Test"))
        retrieved = manager.get("tpl-1")
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_update_template(self, manager):
        tpl = _tpl("tpl-1")
        manager.create(tpl)
        tpl.name = "Updated"
        manager.update(tpl)
        assert manager.get("tpl-1").name == "Updated"

    def test_delete_template(self, manager):
        manager.create(_tpl("tpl-1"))
        assert manager.delete("tpl-1") is True
        assert manager.count() == 0

    def test_duplicate_template_gets_new_id(self, manager):
        manager.create(_tpl("tpl-1"))
        new_tpl = manager.duplicate("tpl-1")
        assert new_tpl.id != "tpl-1"
        assert "copia" in new_tpl.name
        assert manager.count() == 2

    def test_list_all(self, manager):
        for i in range(3):
            manager.create(_tpl(f"tpl-{i}", name=f"T{i}"))
        assert len(manager.list_all()) == 3

    def test_categories(self, manager):
        manager.create(_tpl("t1", category="Dev"))
        manager.create(_tpl("t2", category="Docs"))
        cats = manager.categories()
        assert "Dev" in cats and "Docs" in cats

    def test_by_category(self, manager):
        manager.create(_tpl("t1", category="Dev"))
        manager.create(_tpl("t2", category="Docs"))
        assert [t.id for t in manager.by_category("Dev")] == ["t1"]


class TestTemplateManagerImport:
    """P1-5: duplicate-ID import must never overwrite the original template."""

    def test_import_new_template_succeeds(self, manager, tmp_path):
        payload = {
            "id": "fresh-import",
            "name": "Imported template",
            "content": "Do {{task}} carefully.",
        }
        src = tmp_path / "fresh_import.json"
        src.write_text(json.dumps(payload), encoding="utf-8")

        imported = manager.import_template(src)

        assert any(t.name == "Imported template" for t in manager.list_all())
        assert imported.content == "Do {{task}} carefully."

    def test_duplicate_id_import_never_overwrites_original(self, manager, tmp_path):
        """Importing an id that already exists must not clobber the stored template.

        The implementation may reject (raise) or import-as-copy (regenerate the
        id); the invariant under test is that the ORIGINAL stays intact.
        """
        # Step 1: store the original and capture its id.
        original = _tpl("dup-1", name="Original")
        manager.create(original)

        # Step 2: build an import payload carrying the same id but tampered data.
        src = tmp_path / "duplicate.json"
        payload = original.to_dict()
        payload["name"] = "Overwrite attempt"
        src.write_text(json.dumps(payload), encoding="utf-8")

        # Step 3: import — must not overwrite.
        try:
            imported = manager.import_template(src)
            after = manager.get("dup-1")
            assert after is not None, "Template was deleted on duplicate import."
            assert after.name == "Original", (
                f"Template was silently overwritten: name is now {after.name!r} "
                "but should still be 'Original'."
            )
            # Import-as-copy must assign a distinct id, not reuse the colliding one.
            assert imported.id != "dup-1"
            assert manager.count() == 2
        except (ValueError, KeyError, RuntimeError) as exc:
            # Explicit rejection is the preferred behaviour; original must remain.
            assert str(exc), "Exception raised but has no message."
            assert manager.get("dup-1").name == "Original"

    def test_export_import_roundtrip_preserves_content(self, manager, tmp_path):
        manager.create(_tpl("exp-1", name="Export Test", content="Hello {{x}}", category="Test"))
        export_path = manager.export_template("exp-1", tmp_path / "exported.json")
        assert export_path.exists()

        imported = manager.import_template(export_path)
        assert imported.content == "Hello {{x}}"
        assert imported.category == "Test"
        # Re-importing a live id must import-as-copy, never overwrite.
        assert imported.id != "exp-1"
        assert manager.get("exp-1").name == "Export Test"
