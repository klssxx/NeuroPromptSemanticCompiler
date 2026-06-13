from __future__ import annotations

import shutil
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from context_loss_verifier import verify_context_loss
from npsc_cli import run_cli, _strict_evaluation


class ContextLossTests(unittest.TestCase):
    def test_verifier_flags_missing_safety(self):
        original = "Necesito una app local sin sudo, sin API, no destructiva."
        semantics = {
            "role": "senior",
            "goal": "crear app",
            "context": ["local"],
            "tasks": ["compile_nsl"],
            "constraints": ["no_sudo", "no_external_api", "no_destructive_actions"],
            "priorities": ["safety"],
            "tools": ["python"],
            "output": ["cli"],
            "style": ["precise"],
            "target": "codex",
            "safety_constraints": ["no_sudo", "no_external_api", "no_destructive_actions"],
            "goal": "crear app local segura",
        }
        reconstructed = "Role: senior\nGoal: crear app"
        nsl = "NSL/0.1\nTARGET=codex\nC=no_sudo\n"
        report = verify_context_loss(original, semantics, reconstructed, nsl)
        self.assertIn("missing_no_external_api", report["critical_losses"])

    def test_cli_demo_generates_expected_files(self):
        out_dir = ROOT / "outputs" / "test_cli"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        code = run_cli([
            "--input", str(ROOT / "examples" / "messy_prompt.txt"),
            "--out", str(out_dir),
            "--level", "all",
            "--target", "codex",
        ])
        self.assertEqual(code, 0)
        required = [
            "raw_prompt_original.txt",
            "semantic_analysis.json",
            "semantic_seeds.json",
            "compiled_safe.nsl",
            "compiled_balanced.nsl",
            "compiled_aggressive.nsl",
            "canonical_nsl.nsl",
            "optimized_prompt.txt",
            "reconstructed_prompt.txt",
            "context_loss_report.md",
            "token_estimate_report.md",
            "run_summary.md",
        ]
        for name in required:
            self.assertTrue((out_dir / name).exists(), name)

    def test_strict_policy_thresholds(self):
        report = {
            "score": 72,
            "critical_losses": ["missing_no_external_api", "missing_goal"],
        }
        strict_policy = {
            "min_score": 80,
            "max_critical_losses": 0,
            "fail_on_missing_safety": True,
            "fail_on_missing_goal": True,
        }
        passed, reasons = _strict_evaluation(report, strict_policy)
        self.assertFalse(passed)
        self.assertIn("score_below_min:72<80", reasons)
        self.assertIn("missing_no_external_api", reasons)
        self.assertIn("missing_goal", reasons)


if __name__ == "__main__":
    unittest.main()
