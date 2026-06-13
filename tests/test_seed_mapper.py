from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from semantic_dictionary import load_semantic_dictionary
from semantic_seed_mapper import suggest_seeds


class SeedMapperTests(unittest.TestCase):
    def test_safety_seeds_are_included_when_constraints_detected(self):
        semantics = {
            "goal": "build semantic compiler",
            "constraints": [
                "no_sudo",
                "no_external_api",
                "no_destructive_actions",
                "stay_inside_project_root",
            ],
            "safety_constraints": [
                "no_sudo",
                "no_external_api",
                "no_destructive_actions",
                "stay_inside_project_root",
            ],
        }
        dictionary = load_semantic_dictionary()
        selected = suggest_seeds(semantics, dictionary, target="codex", level="balanced")
        names = {seed["name"] for seed in selected}
        self.assertTrue(any("no_sudo" in name for name in names))
        self.assertTrue(any("no_external_api" in name for name in names))
        self.assertTrue(any("no_destructive" in name for name in names))
        self.assertTrue(any("stay_inside_root" in name for name in names))


if __name__ == "__main__":
    unittest.main()
