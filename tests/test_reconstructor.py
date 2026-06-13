from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from semantic_dictionary import load_semantic_dictionary
from prompt_reconstructor import reconstruct_prompt


class ReconstructorTests(unittest.TestCase):
    def test_reconstructed_prompt_keeps_safety_constraints(self):
        data = {
            "R": "codex_engineer",
            "G": "build local app",
            "CTX": "ubuntu;local_first",
            "T": "extract_semantics,compile_nsl",
            "C": "no_sudo,no_external_api,no_destructive_actions,stay_inside_project_root",
            "P": "safety>clarity",
            "OUT": "cli,files,tests,reports",
            "STYLE": "precise,operational",
            "SEEDS": "S001,S002",
        }
        dictionary = load_semantic_dictionary()
        prompt = reconstruct_prompt(data, dictionary, target="codex")
        self.assertIn("no_sudo", prompt)
        self.assertIn("no_external_api", prompt)
        self.assertIn("no_destructive_actions", prompt)


if __name__ == "__main__":
    unittest.main()
