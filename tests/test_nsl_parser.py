from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nsl_parser import parse_nsl


class NSLParserTests(unittest.TestCase):
    def test_roundtrip_like_parse(self):
        text = """NSL/0.1
# comment
ID=demo_1
TARGET=codex
R=senior
G=build_compiler
C=no_sudo,no_external_api
"""
        parsed = parse_nsl(text)
        self.assertEqual(parsed["_header"], "NSL/0.1")
        self.assertEqual(parsed["TARGET"], "codex")
        self.assertEqual(parsed["C"], "no_sudo,no_external_api")


if __name__ == "__main__":
    unittest.main()
