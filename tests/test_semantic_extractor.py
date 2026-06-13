from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from semantic_extractor import extract_semantics


class SemanticExtractorTests(unittest.TestCase):
    def test_extracts_goal_tasks_constraints_from_spanish_messy_prompt(self):
        text = (
            "Quiero una app local que detecte intención y restricciones, "
            "sin sudo, sin APIs externas, no tocar fuera del proyecto, "
            "nada destructivo, con tests y reportes para Codex y Hermes en Ubuntu."
        )
        data = extract_semantics(text)
        self.assertIn("quiero", data["goal"].lower())
        self.assertIn("build_application", data["tasks"])
        self.assertIn("create_tests", data["tasks"])
        self.assertNotIn("extract_semantics", data["tasks"])
        self.assertNotIn("compile_nsl", data["tasks"])
        self.assertIn("no_sudo", data["constraints"])
        self.assertIn("no_external_api", data["constraints"])
        self.assertIn("no_destructive_actions", data["constraints"])
        self.assertIn("stay_inside_project_root", data["constraints"])
        self.assertIn(data["target"], {"codex", "hermes", "gpt", "generic"})


if __name__ == "__main__":
    unittest.main()
