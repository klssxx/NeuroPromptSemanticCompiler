from __future__ import annotations

import unittest
import tempfile

from version_history import VersionHistory, compute_diff, compute_unified_diff


class VersionHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.hist = VersionHistory(storage_dir=self.tmpdir)

    def test_create_version(self) -> None:
        ver = self.hist.create_version(name="Test", content="Hello world")
        self.assertIsNotNone(ver.id)
        self.assertEqual(ver.name, "Test")
        self.assertEqual(self.hist.count(), 1)

    def test_list_all_sorted(self) -> None:
        for i in range(3):
            self.hist.create_version(name=f"V{i}", content=f"Content {i}")
        versions = self.hist.list_all()
        self.assertEqual(len(versions), 3)

    def test_get_version(self) -> None:
        ver = self.hist.create_version(name="Test", content="Hello")
        retrieved = self.hist.get(ver.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test")

    def test_delete_version(self) -> None:
        ver = self.hist.create_version(name="ToDelete", content="Bye")
        self.assertTrue(self.hist.delete(ver.id))
        self.assertEqual(self.hist.count(), 0)

    def test_persistence(self) -> None:
        """P1 fix item 8: persisted version must survive a new instance.

        Asserts both count and the actual name and content of the
        serialized entry. A serialization bug that zeroes or corrupts
        content would previously pass (only count was checked).
        """
        expected_name = "Persist"
        expected_content = "Serialization regression sentinel content 12345"
        ver = self.hist.create_version(name=expected_name, content=expected_content)
        saved_id = ver.id

        hist2 = VersionHistory(storage_dir=self.tmpdir)
        self.assertEqual(hist2.count(), 1)

        restored = hist2.get(saved_id)
        self.assertIsNotNone(restored, "Version not found after reload")
        self.assertEqual(restored.name, expected_name)
        self.assertEqual(restored.content, expected_content)


class DiffTests(unittest.TestCase):
    def test_compute_diff_additions(self):
        old = "line1\nline2"
        new = "line1\nline2\nline3"
        result = compute_diff(old, new)
        self.assertEqual(result["added"], ["line3"])
        self.assertEqual(result["removed"], [])

    def test_compute_diff_removals(self):
        old = "line1\nline2\nline3"
        new = "line1\nline3"
        result = compute_diff(old, new)
        self.assertEqual(result["removed"], ["line2"])

    def test_compute_diff_modifications(self):
        old = "hello world\nline2"
        new = "hello python\nline2"
        result = compute_diff(old, new)
        self.assertIn("hello world", result["removed"])
        self.assertIn("hello python", result["added"])

    def test_compute_diff_identical(self):
        text = "same content"
        result = compute_diff(text, text)
        self.assertEqual(result["added"], [])
        self.assertEqual(result["removed"], [])

    def test_unified_diff_output(self):
        old = "line1\nline2"
        new = "line1\nline3"
        result = compute_unified_diff(old, new)
        self.assertIn("-line2", result)
        self.assertIn("+line3", result)
