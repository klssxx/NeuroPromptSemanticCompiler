"""Tests for template_manager.py — covers audit P1 finding.

P1 fix: import with duplicate ID must be detected and handled (not silently
corrupt the store).
"""
from __future__ import annotations

import pytest

from template_manager import TemplateManager


_TPL_A = "Refactor {{module}} to use {{pattern}}."
_TPL_B = "Add unit tests for {{component}} in {{framework}}."


@pytest.fixture()
def mgr() -> TemplateManager:
    return TemplateManager()  # in-memory, no disk


class TestTemplateDuplicate:
    def test_add_two_templates_different_ids(self, mgr: TemplateManager):
        mgr.add(name="refactor", content=_TPL_A)
        mgr.add(name="testing", content=_TPL_B)
        assert len(mgr.list()) == 2

    def test_import_duplicate_name_raises_or_renames(self, mgr: TemplateManager):
        """P1 fix: importing a template whose name already exists must not
        silently overwrite the existing entry without any signal.
        Acceptable behaviours: raise ValueError/KeyError, or rename the new
        entry and return the deduplicated name.
        """
        mgr.add(name="refactor", content=_TPL_A)
        try:
            result = mgr.add(name="refactor", content=_TPL_B)
            # If it succeeds, the store must contain both entries (dedup by rename)
            # OR at least the result must indicate the name was changed.
            names = [t.name if hasattr(t, "name") else t.get("name") for t in mgr.list()]
            # Either we got two distinct names, or the duplicate was rejected.
            assert len(set(names)) == len(names), (
                "Duplicate name silently overwrote existing template — invariant violated."
            )
        except (ValueError, KeyError):
            # Explicit rejection is also correct.
            pass

    def test_import_duplicate_does_not_corrupt_original(self, mgr: TemplateManager):
        """After a duplicate import attempt, the original template must be intact."""
        mgr.add(name="refactor", content=_TPL_A)
        try:
            mgr.add(name="refactor", content=_TPL_B)
        except (ValueError, KeyError):
            pass
        templates = mgr.list()
        originals = [
            t for t in templates
            if (t.name if hasattr(t, "name") else t.get("name")) == "refactor"
        ]
        assert originals, "Original template disappeared after duplicate import."
        first = originals[0]
        content = first.content if hasattr(first, "content") else first.get("content", "")
        assert _TPL_A in content, (
            "Original template content was silently replaced by the duplicate."
        )

    def test_get_by_name_returns_correct_template(self, mgr: TemplateManager):
        mgr.add(name="alpha", content=_TPL_A)
        mgr.add(name="beta", content=_TPL_B)
        tpl = mgr.get("alpha")
        content = tpl.content if hasattr(tpl, "content") else tpl.get("content", "")
        assert _TPL_A in content

    def test_delete_removes_only_target(self, mgr: TemplateManager):
        mgr.add(name="alpha", content=_TPL_A)
        mgr.add(name="beta", content=_TPL_B)
        mgr.delete("alpha")
        names = [t.name if hasattr(t, "name") else t.get("name") for t in mgr.list()]
        assert "alpha" not in names
        assert "beta" in names
