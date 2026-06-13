from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout

from i18n import get_language, normalize_language, set_language, tr
from npsc_cli import run_cli


class I18nTests(unittest.TestCase):
    def test_language_normalization_and_translation(self):
        self.assertEqual(normalize_language("es_ES"), "es")
        self.assertEqual(normalize_language("en-US"), "en")
        self.assertEqual(normalize_language("unknown"), "es")
        self.assertEqual(set_language("en"), "en")
        self.assertEqual(get_language(), "en")
        self.assertEqual(tr("settings.title"), "Settings")
        self.assertEqual(set_language("es"), "es")
        self.assertEqual(tr("settings.title"), "Configuración")

    def test_cli_explain_profile_language_english(self):
        buffer = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(buffer):
                code = run_cli([
                    "--text", "Test prompt",
                    "--out", tmp,
                    "--target", "codex",
                    "--profile", "standard",
                    "--explain-profile",
                    "--language", "en",
                ])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("Requested profile: STANDARD", output)
        self.assertIn("Explained profile: STANDARD", output)


if __name__ == "__main__":
    unittest.main()
