from __future__ import annotations

import unittest
from export_manager import export_markdown_result, export_json_result, export_txt_result, export_all_formats


class ExportManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile
        self.tmpdir = tempfile.mkdtemp()

    def _sample_result(self) -> dict:
        return {
            "optimized_prompt": "Compiled prompt text",
            "chosen_nsl": "NSL compact version",
            "target": "codex",
            "applied_profile": "ADVANCED",
            "original": "Original messy prompt",
            "score": 85,
        }

    def test_export_markdown(self) -> None:
        result = self._sample_result()
        path = export_markdown_result(result, self.tmpdir, "test")
        self.assertTrue(path.exists())
        content = path.read_text(encoding="utf-8")
        self.assertIn("Compiled prompt text", content)
        self.assertIn("NSL", content)

    def test_export_json(self) -> None:
        result = self._sample_result()
        path = export_json_result(result, self.tmpdir, "test")
        self.assertTrue(path.exists())
        import json
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("result", data)
        self.assertIn("$schema", data)

    def test_export_txt(self) -> None:
        result = self._sample_result()
        path = export_txt_result(result, self.tmpdir, "test")
        self.assertTrue(path.exists())
        content = path.read_text(encoding="utf-8")
        self.assertEqual(content, "Compiled prompt text")

    def test_export_all_formats(self) -> None:
        result = self._sample_result()
        paths = export_all_formats(result, self.tmpdir, "all")
        self.assertIn("markdown", paths)
        self.assertIn("json", paths)
        self.assertIn("txt", paths)
        for path in paths.values():
            self.assertTrue(path.exists())
