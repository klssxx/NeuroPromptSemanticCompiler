from __future__ import annotations

from typing import Any


def build_context_loss_report(report: dict[str, Any]) -> str:
    lines = [
        "# Context Loss Report",
        "",
        f"Score: **{report.get('score', 0)} / 100**",
        f"Recommendation: **{report.get('recommendation', 'balanced')}**",
        f"Profile: **{report.get('profile', 'STANDARD')}**",
        f"Profile status: **{report.get('profile_status', 'pass')}**",
        "",
        "## Critical Losses",
    ]
    critical = report.get("critical_losses", [])
    if critical:
        lines.extend([f"- {item}" for item in critical])
    else:
        lines.append("- none")

    lines.extend(["", "## Warnings"])
    warnings = report.get("warnings", [])
    if warnings:
        lines.extend([f"- {item}" for item in warnings])
    else:
        lines.append("- none")

    lines.extend(["", "## Profile Failures"])
    profile_failures = report.get("profile_failures", [])
    if profile_failures:
        lines.extend([f"- {item}" for item in profile_failures])
    else:
        lines.append("- none")

    lines.extend(["", "## Preserved Fields"])
    preserved = report.get("preserved_fields", [])
    if preserved:
        lines.extend([f"- {item}" for item in preserved])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Semantic Preservation",
            f"- objective_preservation: {report.get('objective_preservation', 'unknown')}",
            f"- critical_constraint_preservation: {report.get('critical_constraint_preservation', 'unknown')}",
            f"- deliverable_preservation: {report.get('deliverable_preservation', 'unknown')}",
            f"- output_schema_preservation: {report.get('output_schema_preservation', 'unknown')}",
            f"- role_preservation: {report.get('role_preservation', 'unknown')}",
            f"- context_preservation: {report.get('context_preservation', 'unknown')}",
            f"- semantic_retention_score: {report.get('semantic_retention_score', report.get('score', 0))}",
            f"- retention_score: {report.get('retention_score', 0)}",
            f"- precision_score: {report.get('precision_score', 0)}",
            f"- unsupported_addition_score: {report.get('unsupported_addition_score', 0)}",
            f"- contradiction_score: {report.get('contradiction_score', 0)}",
            f"- constraint_traceability_score: {report.get('constraint_traceability_score', 0)}",
            f"- compression_ratio_nsl: {report.get('compression_ratio_nsl', 0)}",
            f"- expansion_ratio_execution_prompt: {report.get('expansion_ratio_execution_prompt', 0)}",
            f"- utility_score: {report.get('utility_score', 0)}",
            f"- risk_score: {report.get('risk_score', 0)}",
            f"- aggregate_score_formula: {report.get('aggregate_score_formula', '')}",
        ]
    )

    omissions = report.get("possible_omissions", [])
    lines.extend(["", "## Possible Omissions"])
    if omissions:
        lines.extend([f"- {item}" for item in omissions])
    else:
        lines.append("- none")

    lines.extend(["", "## Missing Fields"])
    missing = report.get("missing_fields", [])
    if missing:
        lines.extend([f"- {item}" for item in missing])
    else:
        lines.append("- none")

    return "\n".join(lines).strip() + "\n"


def build_token_report_markdown(token_report: dict[str, Any]) -> str:
    lines = [
        "# Token Estimate Report",
        "",
        token_report.get("note", "Approximate token estimation."),
        "",
        "## Approximate Token Counts",
    ]
    for key in ["original", "safe_nsl", "balanced_nsl", "aggressive_nsl", "optimized_prompt"]:
        item = token_report.get(key, {})
        lines.append(f"- {key}: chars={item.get('chars', 0)}, words={item.get('words', 0)}, approx_tokens={item.get('approx_tokens', 0)}")

    lines.extend(["", "## Reduction Percentages"])
    for name, value in token_report.get("reductions_percent", {}).items():
        lines.append(f"- {name}: {value}%")

    return "\n".join(lines).strip() + "\n"


def build_run_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# Run Summary",
        "",
        f"Run ID: {summary.get('run_id', 'unknown')}",
        f"Target: {summary.get('target', 'generic')}",
        f"Requested profile: {summary.get('requested_profile', 'STANDARD')}",
        f"Applied profile: {summary.get('applied_profile', 'STANDARD')}",
        f"Requested level: {summary.get('requested_level', 'balanced')}",
        f"Chosen level: {summary.get('chosen_level', 'balanced')}",
        f"Context loss score: {summary.get('score', 0)}",
        f"Profile status: {summary.get('profile_status', 'pass')}",
        f"Critical losses: {', '.join(summary.get('critical_losses', [])) or 'none'}",
        f"Output directory: {summary.get('out_dir', '')}",
        "",
        "Artifacts:",
    ]
    lines.extend([f"- {item}" for item in summary.get("artifacts", [])])
    if summary.get("level_conflict"):
        lines.extend(["", "Profile/level note:", str(summary["level_conflict"])])
    auto_info = summary.get("auto") or {}
    if auto_info:
        lines.extend(
            [
                "",
                "Auto Select:",
                f"- auto_selected_profile: {auto_info.get('auto_selected_profile', '')}",
                f"- selection_reason: {auto_info.get('selection_reason', '')}",
                f"- risk_flags: {', '.join(auto_info.get('risk_flags', [])) or 'none'}",
                f"- fallback_profile: {auto_info.get('fallback_profile', '')}",
            ]
        )
    return "\n".join(lines).strip() + "\n"
