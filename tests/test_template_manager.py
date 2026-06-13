from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from template_manager import TemplateManager, PromptTemplate


class TemplateManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = TemplateManager(storage_dir=self.tmpdir)

    def test_create_template(self) -> None:
        tpl = PromptTemplate(id="tpl-1", name="Test", content="Hello {{name}}")
        self.mgr.create(tpl)
        self.assertEqual(self.mgr.count(), 1)

    def test_create_duplicate_raises(self) -> None:
        tpl = PromptTemplate(id="tpl-1", name="Test", content="Hello")
        self.mgr.create(tpl)
        with self.assertRaises(ValueError):
            self.mgr.create(tpl)

    def test_get_template(self) -> None:
        tpl = PromptTemplate(id="tpl-1", name="Test", content="Hello")
        self.mgr.create(tpl)
        retrieved = self.mgr.get("tpl-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test")

    def test_update_template(self) -> None:
        tpl = PromptTemplate(id="tpl-1", name="Test", content="Hello")
        self.mgr.create(tpl)
        tpl.name = "Updated"
        self.mgr.update(tpl)
        self.assertEqual(self.mgr.get("tpl-1").name, "Updated")

    def test_delete_template(self) -> None:
        tpl = PromptTemplate(id="tpl-1", name="Test", content="Hello")
        self.mgr.create(tpl)
        self.assertTrue(self.mgr.delete("tpl-1"))
        self.assertEqual(self.mgr.count(), 0)

    def test_duplicate_template(self) -> None:
        tpl = PromptTemplate(id="tpl-1", name="Test", content="Hello {{x}}")
        self.mgr.create(tpl)
        new_tpl = self.mgr.duplicate("tpl-1")
        self.assertNotEqual(new_tpl.id, "tpl-1")
        self.assertIn("copia", new_tpl.name)
        self.assertEqual(self.mgr.count(), 2)

    def test_list_all_sorted(self) -> None:
        for i in range(3):
            tpl = PromptTemplate(id=f"tpl-{i}", name=f"T{i}", content="C")
            self.mgr.create(tpl)
        all_tpls = self.mgr.list_all()
        self.assertEqual(len(all_tpls), 3)

    def test_categories(self) -> None:
        tpl1 = PromptTemplate(id="t1", name="A", content="C", category="Dev")
        tpl2 = PromptTemplate(id="t2", name="B", content="C", category="Docs")
        self.mgr.create(tpl1)
        self.mgr.create(tpl2)
        cats = self.mgr.categories()
        self.assertIn("Dev", cats)
        self.assertIn("Docs", cats)

    def test_export_import_roundtrip(self) -> None:
        tpl = PromptTemplate(id="exp-1", name="Export Test", content="Hello {{x}}", category="Test")
        self.mgr.create(tpl)
        export_path = self.mgr.export_template("exp-1", Path(self.tmpdir) / "exported.json")
        self.assertTrue(export_path.exists())
        imported = self.mgr.import_template(export_path)
        self.assertEqual(imported.content, "Hello {{x}}")
        self.assertEqual(imported.category, "Test")
