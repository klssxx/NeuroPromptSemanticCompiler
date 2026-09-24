"""Tests for template_manager.py.

P1-5 addition: duplicate-ID import rejection test.
Verifies that importing a template whose ID already exists in the store
either raises an appropriate error or returns a failure indicator — it must
never silently overwrite an existing template.
"""
from __future__ import annotations

import copy
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from template_manager import TemplateManager


@pytest.fixture()
def manager(tmp_path):
    return TemplateManager(storage_dir=tmp_path)


def _make_template(name: str = "Test template", body: str = "Do {{task}} carefully.") -> dict:
    return {"name": name, "body": body, "tags": ["test"]}


class TestTemplateManagerCRUD:
    def test_add_and_list(self, manager):
        manager.add_template(_make_template())
        templates = manager.list_templates()
        assert len(templates) == 1

    def test_get_by_id(self, manager):
        tid = manager.add_template(_make_template())
        t = manager.get_template(tid)
        assert t is not None
        assert t["name"] == "Test template"

    def test_delete(self, manager):
        tid = manager.add_template(_make_template())
        manager.delete_template(tid)
        assert manager.get_template(tid) is None

    def test_search_by_name(self, manager):
        manager.add_template(_make_template(name="Alpha template"))
        manager.add_template(_make_template(name="Beta template"))
        results = manager.search_templates("Alpha")
        assert len(results) == 1
        assert results[0]["name"] == "Alpha template"

    def test_update_template(self, manager):
        tid = manager.add_template(_make_template())
        manager.update_template(tid, {"name": "Updated name"})
        t = manager.get_template(tid)
        assert t["name"] == "Updated name"


class TestTemplateManagerImport:
    """P1-5: duplicate-ID import rejection.

    Rationale: if import_template does not check for ID collisions, a second
    import of the same template silently overwrites the first.  This is a data
    integrity bug — the store would lose the original (possibly edited) template
    without any indication to the user.
    """

    def test_import_new_template_succeeds(self, manager):
        template = _make_template(name="Imported template")
        manager.import_template(template)
        # import_template may return the assigned id or a bool/dict.
        # Either way, the template must be retrievable afterwards.
        templates = manager.list_templates()
        assert any(t["name"] == "Imported template" for t in templates)

    def test_duplicate_id_import_is_rejected(self, manager):
        """Importing a template with an ID that already exists must not silently overwrite."""
        # Step 1: add a template and capture its assigned id.
        tid = manager.add_template(_make_template(name="Original"))
        original = manager.get_template(tid)

        # Step 2: construct an import payload that carries the same id.
        duplicate = copy.deepcopy(original)
        duplicate["name"] = "Overwrite attempt"

        # Step 3: attempt to import — must raise or signal failure.
        try:
            manager.import_template(duplicate)
            # If no exception: the method must signal rejection, not silently accept.
            # We check that the original template is still intact.
            after = manager.get_template(tid)
            assert after is not None, "Template was deleted on duplicate import."
            assert after["name"] == "Original", (
                f"Template was silently overwritten. name is now '{after['name']}' "
                "but should still be 'Original'."
            )
        except (ValueError, KeyError, RuntimeError) as exc:
            # Explicit rejection via exception is the preferred behaviour.
            assert str(exc), "Exception raised but has no message."
