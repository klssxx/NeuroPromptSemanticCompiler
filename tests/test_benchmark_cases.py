"""B.7 tests: the 10-case labeled quality benchmark, executed for real.

Every case runs through the actual compile_prompt service and must satisfy
its labeled invariants (goal preservation, gap detection, no invention,
executability, critical-constraint retention, non-degradation). The
benchmark IS the test: the same run_case_benchmark() used programmatically
is what these assertions exercise.
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from benchmark_quality import evaluate_case, run_case_benchmark

CASES_PATH = Path(__file__).resolve().parent / "fixtures" / "prompt_cases" / "cases.json"
_CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]

assert len(_CASES) == 10, "the benchmark must keep exactly the 10 labeled cases"


def _case(cid: str) -> dict:
    return next(c for c in _CASES if c["id"] == cid)


class TestCaseByCase:
    def test_case01_ambiguous_detected(self):
        row = evaluate_case(_case("case01_ambiguous_coding_no_acceptance"))
        assert row["passed"], row

    def test_case02_safety_constraints_kept_and_nothing_invented(self):
        row = evaluate_case(_case("case02_spanish_safety_constraints"))
        assert row["passed"], row

    def test_case03_variables_surfaced(self):
        row = evaluate_case(_case("case03_unfilled_variables"))
        assert row["passed"], row

    def test_case04_contradiction_flagged_and_nothing_invented(self):
        row = evaluate_case(_case("case04_contradictory_requirements"))
        assert row["passed"], row

    def test_case05_empty_input_fails_controlled(self):
        row = evaluate_case(_case("case05_empty_input_fails_controlled"))
        assert row["passed"], row

    def test_case06_research_gap_detected(self):
        row = evaluate_case(_case("case06_research_needs_sources"))
        assert row["passed"], row

    def test_case07_json_contract_required(self):
        row = evaluate_case(_case("case07_json_output_schema"))
        assert row["passed"], row

    def test_case08_sensitive_data_no_invention(self):
        row = evaluate_case(_case("case08_potentially_sensitive_data"))
        assert row["passed"], row

    def test_case09_excellent_prompt_not_degraded(self):
        row = evaluate_case(_case("case09_already_excellent"))
        assert row["passed"], row
        assert row["input_quality_score"] >= 90, row
        assert row["quality_score"] >= row["input_quality_score"] - 5, row

    def test_case10_unknown_target_clear_valueerror(self):
        row = evaluate_case(_case("case10_unknown_target_clear_error"))
        assert row["passed"], row


class TestFullBenchmark:
    def test_all_ten_cases_pass_together(self):
        report = run_case_benchmark(_CASES)
        assert report["total"] == 10
        failed = [r["id"] for r in report["rows"] if not r["passed"]]
        assert report["failed"] == 0, f"failed cases: {failed}"
        assert report["passed"] == 10
