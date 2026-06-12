from __future__ import annotations

from typing import Any

from utils import compact_join, now_run_id

CANONICAL_FIELDS = [
    "ID", "TARGET", "R", "G", "CTX", "T", "C", "P", "TOOLS", "IN", "OUT", "STYLE", "RISKS", "SEEDS", "VERIFY"
]


ABBR = {
    "extract_semantics": "extract_sem",
    "map_seeds": "map_seeds",
    "compile_nsl": "compile_nsl",
    "reconstruct_prompt": "reconstruct",
    "verify_context_loss": "verify_loss",
    "export_reports": "export",
    "test_pipeline": "test",
    "build_cli": "cli",
}


CRITICAL = ["no_sudo", "no_external_api", "no_destructive_actions", "stay_inside_project_root"]


def _ensure_critical_constraints(constraints: list[str], source_constraints: list[str]) -> list[str]:
    out = list(constraints)
    for item in CRITICAL:
        if item in source_constraints and item not in out:
            out.append(item)
    return out


def compile_to_nsl(semantics: dict[str, Any], seeds: list[dict[str, Any]], level: str, target: str) -> str:
    run_id = now_run_id("run")

    role = semantics.get("role", "semantic_compiler_operator")
    goal = semantics.get("goal", "compile semantic instruction")
    context = list(semantics.get("context", []))
    tasks = list(semantics.get("tasks", []))
    constraints = _ensure_critical_constraints(list(semantics.get("constraints", [])), list(semantics.get("constraints", [])))
    priorities = list(semantics.get("priorities", []))
    tools = list(semantics.get("tools", []))
    outputs = list(semantics.get("output", []))
    style = list(semantics.get("style", []))
    risks = list(semantics.get("risks", []))

    if level == "safe":
        risks = [r for r in risks if r != "overcompression"] + ["low_compression_risk"]
    elif level == "aggressive":
        tasks = [ABBR.get(t, t) for t in tasks]
        context = [c.replace("project", "proj") for c in context]
        style = list(dict.fromkeys(style + ["dense"]))
        risks = list(dict.fromkeys(risks + ["compression_may_reduce_nuance"]))
    else:
        style = list(dict.fromkeys(style + ["balanced_density"]))

    seed_ids = [seed["id"] for seed in seeds]

    if level == "aggressive" and semantics.get("semantic_compilation_profile") == "FAST":
        compact_lines = ["NSL/0.1", f"TARGET={target}", f"G={goal}"]
        if tasks:
            compact_lines.append(f"T={','.join(tasks[:3])}")
        if constraints:
            compact_lines.append(f"C={','.join(constraints)}")
        if outputs:
            compact_lines.append(f"OUT={','.join(outputs[:2])}")
        if seed_ids:
            compact_lines.append(f"SEEDS={','.join(seed_ids[:3])}")
        return "\n".join(compact_lines) + "\n"

    values = {
        "ID": run_id,
        "TARGET": target,
        "R": role,
        "G": goal,
        "CTX": compact_join(context, sep=";"),
        "T": ",".join(tasks),
        "C": ",".join(constraints),
        "P": ">".join(priorities),
        "TOOLS": ",".join(tools),
        "IN": semantics.get("input", "messy_human_prompt"),
        "OUT": ",".join(outputs),
        "STYLE": ",".join(style),
        "RISKS": ",".join(risks),
        "SEEDS": ",".join(seed_ids),
        "VERIFY": "context_loss,critical_constraints,run_summary",
    }

    lines = ["NSL/0.1"]
    for field in CANONICAL_FIELDS:
        lines.append(f"{field}={values.get(field, '')}")
    return "\n".join(lines) + "\n"
