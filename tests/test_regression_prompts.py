from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from semantic_extractor import extract_semantics


class RegressionPromptTests(unittest.TestCase):
    def test_noisy_spanish_prompt_retains_safety_and_goal(self):
        text = (
            "mmm mira, necesito algo tipo compilador semántico, no un resumen barato, "
            "que saque intención y tareas reales, local en ubuntu, sin sudo, sin APIs, "
            "no borrar nada, no tocar fuera del proyecto, y con reportes + tests para hermes."
        )
        data = extract_semantics(text)
        self.assertIn("no_sudo", data["constraints"])
        self.assertIn("no_external_api", data["constraints"])
        self.assertIn("no_destructive_actions", data["constraints"])
        self.assertIn("stay_inside_project_root", data["constraints"])
        self.assertEqual(data["target"], "hermes")
        self.assertNotIn("compile_nsl", data["tasks"])
        self.assertNotIn("verify_context_loss", data["tasks"])

    def test_noisy_english_prompt_detects_codex_and_constraints(self):
        text = (
            "Need a local semantic compiler, not just a summary thing; "
            "keep all safety constraints, no sudo, no external api, no destructive actions, "
            "stay inside project root, output files/reports/tests for codex."
        )
        data = extract_semantics(text)
        self.assertEqual(data["target"], "codex")
        self.assertIn("no_sudo", data["constraints"])
        self.assertIn("no_external_api", data["constraints"])
        self.assertIn("stay_inside_project_root", data["constraints"])
        self.assertIn("create_tests", data["tasks"])

    def test_ambiguous_prompt_still_generates_pipeline_baseline(self):
        text = "Maybe improve this somehow, maybe cleaner maybe compact, not sure, for models."
        data = extract_semantics(text)
        self.assertEqual(data["tasks"], ["answer_user_request"])
        self.assertIn(data["target"], {"generic", "gpt"})


if __name__ == "__main__":
    unittest.main()
