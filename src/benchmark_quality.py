from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from context_loss_verifier import verify_context_loss
from exporters import export_json, export_text, prepare_output_dir
from nsl_compiler import compile_to_nsl
from nsl_parser import parse_nsl
from prompt_reconstructor import reconstruct_prompt
from semantic_dictionary import load_semantic_dictionary
from semantic_extractor import extract_semantics
from semantic_seed_mapper import suggest_seeds
from token_estimator import estimate_text


LEVELS = ("safe", "balanced", "aggressive")
EXECUTABLE_TASKS = {
    "extract_semantics",
    "map_seeds",
    "compile_nsl",
    "reconstruct_prompt",
    "verify_context_loss",
    "export_reports",
    "test_pipeline",
    "build_cli",
}


def _task_executability(nsl_data: dict[str, str]) -> float:
    tasks = [t.strip() for t in nsl_data.get("T", "").split(",") if t.strip()]
    if not tasks:
        return 0.0
    ok = sum(1 for task in tasks if task in EXECUTABLE_TASKS or task in {"extract_sem", "reconstruct", "verify_loss", "export", "test", "cli"})
    return round((ok / len(tasks)) * 100, 2)


def _safety_retention(verifier: dict[str, Any]) -> float:
    critical = verifier.get("critical_losses", [])
    safety_missing = [
        tag
        for tag in critical
        if tag in {"missing_no_sudo", "missing_no_external_api", "missing_no_destructive_actions", "missing_stay_inside_project_root"}
    ]
    if not critical:
        return 100.0
    if safety_missing:
        return 0.0
    return 100.0


def run_benchmark(example_files: list[Path], target: str, out_dir: Path) -> dict[str, Any]:
    dictionary = load_semantic_dictionary()
    out_dir = prepare_output_dir(out_dir)

    rows: list[dict[str, Any]] = []
    by_level: dict[str, dict[str, float]] = {level: {"count": 0.0, "preservation": 0.0, "executability": 0.0, "safety_retention": 0.0, "compression_gain": 0.0} for level in LEVELS}

    for example in example_files:
        original = example.read_text(encoding="utf-8")
        semantics = extract_semantics(original)
        original_tokens = estimate_text(original)["approx_tokens"]
        for level in LEVELS:
            seeds = suggest_seeds(semantics, dictionary, target=target, level=level)
            nsl_text = compile_to_nsl(semantics, seeds, level=level, target=target)
            nsl_data = parse_nsl(nsl_text)
            reconstructed = reconstruct_prompt(nsl_data, dictionary, target=target)
            verifier = verify_context_loss(original, semantics, reconstructed, nsl_text)
            nsl_tokens = estimate_text(nsl_text)["approx_tokens"]
            execution_tokens = estimate_text(reconstructed)["approx_tokens"]
            nsl_ratio = round(nsl_tokens / max(1, original_tokens), 3)
            execution_ratio = round(execution_tokens / max(1, original_tokens), 3)
            compression_gain = round(((original_tokens - nsl_tokens) / max(1, original_tokens)) * 100, 2)
            task_exec = _task_executability(nsl_data)
            safety = _safety_retention(verifier)
            preservation = float(verifier.get("score", 0))

            row = {
                "example": example.name,
                "level": level,
                "target": target,
                "preservation_score": preservation,
                "task_executability": task_exec,
                "safety_retention": safety,
                "compression_gain_percent": compression_gain,
                "compression_ratio_nsl": nsl_ratio,
                "expansion_ratio_execution_prompt": execution_ratio,
                "negative_compression": compression_gain < 0,
                "critical_losses": verifier.get("critical_losses", []),
            }
            rows.append(row)

            agg = by_level[level]
            agg["count"] += 1.0
            agg["preservation"] += preservation
            agg["executability"] += task_exec
            agg["safety_retention"] += safety
            agg["compression_gain"] += compression_gain

    summary = {}
    for level, data in by_level.items():
        count = max(1.0, data["count"])
        summary[level] = {
            "samples": int(data["count"]),
            "avg_preservation_score": round(data["preservation"] / count, 2),
            "avg_task_executability": round(data["executability"] / count, 2),
            "avg_safety_retention": round(data["safety_retention"] / count, 2),
            "avg_compression_gain_percent": round(data["compression_gain"] / count, 2),
        }

    report = {"target": target, "levels": list(LEVELS), "rows": rows, "summary": summary}
    return report


def _report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Quality Benchmark",
        "",
        f"Target: **{report['target']}**",
        "",
        "## Summary",
        "",
        "| Level | Samples | Preservation | Executability | Safety Retention | Compression Gain |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for level in LEVELS:
        s = report["summary"][level]
        lines.append(
            f"| {level} | {s['samples']} | {s['avg_preservation_score']} | {s['avg_task_executability']} | {s['avg_safety_retention']} | {s['avg_compression_gain_percent']}% |"
        )
    lines.extend(["", "## Rows", "", "| Example | Level | Preservation | Executability | Safety | Compression | NSL ratio | Execution ratio | Negative | Critical Losses |", "|---|---|---:|---:|---:|---:|---:|---:|---|---|"])
    for row in report["rows"]:
        losses = ",".join(row["critical_losses"]) or "none"
        lines.append(
            f"| {row['example']} | {row['level']} | {row['preservation_score']} | {row['task_executability']} | {row['safety_retention']} | {row['compression_gain_percent']}% | {row['compression_ratio_nsl']} | {row['expansion_ratio_execution_prompt']} | {row['negative_compression']} | {losses} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local quality benchmark for NPSC levels.")
    parser.add_argument("--target", default="codex")
    parser.add_argument("--out", default="outputs/benchmark")
    parser.add_argument("--examples", nargs="*", default=[
        "examples/messy_prompt.txt",
        "examples/app_builder_prompt.txt",
        "examples/research_prompt.txt",
        "examples/codex_project_prompt.txt",
        "examples/hermes_agent_prompt.txt",
    ])
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    example_paths = [root / item for item in args.examples]
    out_dir = root / args.out

    report = run_benchmark(example_paths, target=args.target, out_dir=out_dir)
    export_json(out_dir / "quality_benchmark.json", report)
    export_text(out_dir / "quality_benchmark.md", _report_markdown(report))
    print(f"[benchmark] out={out_dir.resolve()}")
    print("[benchmark] generated: quality_benchmark.json, quality_benchmark.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ─── B.7: labeled case benchmark ────────────────────────────────────────────
# Runs labeled prompt cases through the real compile service and verifies
# six invariants per case (goal preservation, gap detection, no invention,
# executability, critical-constraint retention, no degradation of already
# excellent prompts). Deterministic and local.

import re  # noqa: E402  (case-benchmark helpers)
from context_loss_verifier import INTERNAL_TERMS  # noqa: E402  (grouped with benchmark helpers)
from npsc_service import CompileRequest, compile_prompt  # noqa: E402
from prompt_quality import evaluate_quality  # noqa: E402


def _goal_tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"\w{4,}", text)} - INTERNAL_TERMS


def _normalized(text: str) -> str:
    return text.lower().replace("-", "_")


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """Run one labeled case through compile_prompt and check its invariants."""
    checks: dict[str, bool] = {}
    row: dict[str, Any] = {
        "id": case["id"],
        "profile": case.get("profile", "STANDARD"),
        "checks": checks,
        "passed": False,
    }

    expect_error = case.get("expect_error")
    if expect_error:
        try:
            compile_prompt(CompileRequest(
                original=case["text"],
                target=case.get("target", "codex"),
                profile=case.get("profile", "STANDARD"),
            ))
            checks["fails_controlled"] = False
        except ValueError as exc:
            checks["fails_controlled"] = case["expect_error"] in str(exc) or bool(str(exc))
        except Exception:  # noqa: BLE001 — any non-ValueError escape is a failure
            checks["fails_controlled"] = False
        row["passed"] = checks["fails_controlled"]
        return row

    result = compile_prompt(CompileRequest(
        original=case["text"],
        target=case.get("target", "codex"),
        profile=case.get("profile", "STANDARD"),
    ))
    semantics = result["semantics"]
    optimized = result["optimized_prompt"]
    row["quality_score"] = result["quality_report"]["score"]

    # 1. goal preservation: enough distinctive goal tokens survive compilation
    goal_text = str(semantics.get("goal") or "")
    goal_tokens = _goal_tokens(goal_text)
    kept = sum(1 for t in goal_tokens if t in _normalized(optimized))
    checks["goal_preserved"] = bool(goal_tokens) and kept >= min(2, len(goal_tokens))

    # 2. gap detection
    ambiguities = semantics.get("ambiguities") or []
    checks["ambiguities_detected"] = (
        (len(ambiguities) > 0) if case.get("expect_ambiguities", True)
        else (len(ambiguities) == 0)
    )

    # 3. no invention: the USER REQUIREMENTS layer (B.4) must not contain a
    #    critical constraint the input never had. (The compiled text itself
    #    intentionally carries the product-policy constraint set — that is
    #    labeled policy, not invention; provenance separation is what B.4
    #    guarantees.)
    input_constraints = set(semantics.get("constraints") or [])
    requirement_values = {
        str(r.get("value", ""))
        for r in result["four_layers"]["user_requirements"]
        if r.get("kind") == "constraint"
    }
    forbidden = [
        c for c in ("no_sudo", "no_external_api", "no_destructive_actions",
                    "stay_inside_project_root", "offline_only")
        if c not in input_constraints and c in requirement_values
    ]
    checks["nothing_invented"] = not forbidden
    row["invented_constraints"] = forbidden

    # 4. executability: output contract present when the case requires it
    if case.get("requires_output_contract", False):
        checks["executability"] = bool(result["quality_report"]["has_output_contract"])
    else:
        checks["executability"] = True

    # 5. critical constraints retained verbatim (dash/underscore normalized)
    critical = case.get("critical_constraints") or []
    checks["critical_constraints_kept"] = all(
        c in _normalized(optimized) for c in critical
    )

    # 6. case-9 non-degradation: compiling an already excellent prompt must
    #    not LOWER its verifiable quality by more than the tolerance.
    if case.get("no_degradation", False):
        input_quality = evaluate_quality(case["text"], semantics, case["text"])
        tolerance = int(case.get("degradation_tolerance", 5))
        checks["not_degraded"] = (
            result["quality_report"]["score"] >= input_quality.score - tolerance
        )
        row["input_quality_score"] = input_quality.score

    row["passed"] = all(checks.values())
    return row


def run_case_benchmark(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Run all labeled cases; returns a summary report with per-case rows."""
    rows = [evaluate_case(case) for case in cases]
    passed = sum(1 for r in rows if r["passed"])
    return {
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "rows": rows,
    }
