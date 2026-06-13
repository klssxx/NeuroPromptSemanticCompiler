from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils import ensure_dir, write_text


def export_markdown_result(result: dict[str, Any], out_dir: str | Path, basename: str = "result") -> Path:
    """Export compilation result as structured Markdown."""
    out = ensure_dir(out_dir)
    path = out / f"{basename}.md"

    lines = []
    lines.append("# NeuroPrompt Semantic Compiler — Result\n")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")

    # Metadata
    if "target" in result:
        lines.append(f"- **Target:** {result['target']}")
    if "profile" in result:
        lines.append(f"- **Profile:** {result['profile']}")
    if "level" in result:
        lines.append(f"- **Level:** {result['level']}")
    if "score" in result:
        lines.append(f"- **Score:** {result['score']}")
    lines.append("")

    # Structured prompt
    if "optimized_prompt" in result:
        lines.append("## Compiled Prompt\n")
        lines.append("```")
        lines.append(result["optimized_prompt"])
        lines.append("```")
        lines.append("")

    # NSL
    if "chosen_nsl" in result:
        lines.append("## NSL v0.1\n")
        lines.append("```nsl")
        lines.append(result["chosen_nsl"])
        lines.append("```")
        lines.append("")

    # Semantic IR
    if "semantic_ir" in result and result["semantic_ir"]:
        lines.append("## Semantic IR\n")
        ir = result["semantic_ir"]
        if isinstance(ir, dict):
            for key, value in ir.items():
                if isinstance(value, list):
                    lines.append(f"### {key}")
                    for item in value:
                        lines.append(f"- {item}")
                    lines.append("")
                else:
                    lines.append(f"### {key}")
                    lines.append(str(value))
                    lines.append("")

    # Context loss report
    if "context_loss" in result:
        report = result["context_loss"]
        lines.append("## Context Loss Report\n")
        score = report.get("score", "?")
        lines.append(f"**Score:** {score}\n")
        critical = report.get("critical_losses", [])
        if critical:
            lines.append("### Critical Losses")
            for item in critical:
                lines.append(f"- {item}")
            lines.append("")
        warnings = report.get("warnings", [])
        if warnings:
            lines.append("### Warnings")
            for item in warnings:
                lines.append(f"- {item}")
            lines.append("")

    # Token report
    if "token_report" in result:
        tr = result["token_report"]
        lines.append("## Token Report\n")
        if isinstance(tr, dict):
            for key, value in tr.items():
                lines.append(f"- **{key}:** {value}")
        else:
            lines.append(str(tr))
        lines.append("")

    # Original prompt
    if "original" in result:
        lines.append("## Original Prompt\n")
        lines.append("```")
        lines.append(result["original"])
        lines.append("```")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def export_json_result(result: dict[str, Any], out_dir: str | Path, basename: str = "result") -> Path:
    """Export compilation result as structured JSON with a stable schema."""
    out = ensure_dir(out_dir)
    path = out / f"{basename}.json"

    export_data = {
        "$schema": "neuroprompt/compilation-result/v1",
        "generator": "NeuroPrompt Semantic Compiler",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }

    path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def export_txt_result(result: dict[str, Any], out_dir: str | Path, basename: str = "result") -> Path:
    """Export just the compiled prompt as plain text."""
    out = ensure_dir(out_dir)
    path = out / f"{basename}.txt"

    content = result.get("optimized_prompt", result.get("chosen_nsl", ""))
    if not content:
        content = json.dumps(result, indent=2, ensure_ascii=False)

    path.write_text(content, encoding="utf-8")
    return path


def export_all_formats(result: dict[str, Any], out_dir: str | Path, basename: str = "result") -> dict[str, Path]:
    """Export to all three formats at once."""
    return {
        "markdown": export_markdown_result(result, out_dir, basename),
        "json": export_json_result(result, out_dir, basename),
        "txt": export_txt_result(result, out_dir, basename),
    }
