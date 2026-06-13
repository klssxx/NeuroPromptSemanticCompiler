from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nsl_compiler import compile_to_nsl


class NSLCompilerTests(unittest.TestCase):
    def test_compiler_generates_safe_balanced_aggressive(self):
        semantics = {
            "role": "senior_ai_tool_builder",
            "goal": "build semantic prompt compiler",
            "context": ["ubuntu", "python", "local_first"],
            "tasks": ["extract_semantics", "compile_nsl", "reconstruct_prompt"],
            "constraints": ["no_sudo", "no_external_api", "no_destructive_actions", "stay_inside_project_root"],
            "priorities": ["safety", "semantic_preservation", "clarity"],
            "tools": ["python", "argparse", "json"],
            "output": ["cli", "files", "tests", "reports"],
            "style": ["precise", "operational"],
            "risks": ["missing_constraints"],
            "input": "messy_human_prompt",
        }
        seeds = [{"id": "S001"}, {"id": "S002"}]

        safe = compile_to_nsl(semantics, seeds, level="safe", target="codex")
        balanced = compile_to_nsl(semantics, seeds, level="balanced", target="codex")
        aggressive = compile_to_nsl(semantics, seeds, level="aggressive", target="codex")

        self.assertIn("NSL/0.1", safe)
        self.assertIn("TARGET=codex", balanced)
        self.assertIn("C=no_sudo,no_external_api,no_destructive_actions,stay_inside_project_root", aggressive)
        self.assertNotEqual(safe, aggressive)


if __name__ == "__main__":
    unittest.main()
