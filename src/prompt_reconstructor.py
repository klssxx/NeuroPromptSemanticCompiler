from __future__ import annotations

from typing import Any


def _seed_expansions(seed_ids: list[str], dictionary: list[dict[str, Any]]) -> list[str]:
    by_id = {seed["id"]: seed for seed in dictionary}
    lines = []
    for sid in seed_ids:
        seed = by_id.get(sid)
        if seed:
            lines.append(f"- {sid}: {seed.get('expansion', seed.get('meaning', ''))}")
    return lines


def reconstruct_prompt(nsl_data: dict[str, str], dictionary: list[dict], target: str) -> str:
    role = nsl_data.get("R", "semantic_compiler_operator")
    goal = nsl_data.get("G", "deliver requested objective")
    context = nsl_data.get("CTX", "")
    tasks = nsl_data.get("T", "")
    constraints = nsl_data.get("C", "")
    priorities = nsl_data.get("P", "")
    outputs = nsl_data.get("OUT", "")
    style = nsl_data.get("STYLE", "")
    seeds = [s.strip() for s in nsl_data.get("SEEDS", "").split(",") if s.strip()]

    seed_lines = _seed_expansions(seeds[:10], dictionary)

    common = [
        f"Role: {role}",
        f"Goal: {goal}",
        f"Context: {context}",
        f"Tasks: {tasks}",
        f"Constraints: {constraints}",
        f"Priorities: {priorities}",
        f"Expected output: {outputs}",
        f"Style: {style}",
        "Mandatory safety: keep no_sudo, no_external_api, no_destructive_actions, stay_inside_project_root if present.",
    ]

    if target == "codex":
        body = [
            "You are Codex acting in operational execution mode.",
            *common,
            "Execution requirements:",
            "- Work inside the provided project root only.",
            "- Create/modify concrete files and run tests.",
            "- Provide verification commands and outcome status.",
            "- If blocked, report exact blocker and fallback steps.",
            "Final answer contract: changed files, test results, verification summary, next actions.",
        ]
    elif target == "hermes":
        body = [
            "You are Hermes in safe execution mode.",
            *common,
            "Execution phases:",
            "1) Read context and boundaries.",
            "2) Build artifacts.",
            "3) Verify non-destructive constraints.",
            "4) Run tests and reports.",
            "5) Produce final summary and fallback if blocked.",
            "Do not run destructive commands or escalate privileges.",
        ]
    elif target == "gpt":
        body = [
            "You are an advanced GPT model following strict structured instructions.",
            *common,
            "Provide hierarchical response with: plan, execution, verification, final contract.",
            "State assumptions explicitly and avoid hiding constraints.",
        ]
    else:
        body = [
            f"You are target model '{target}' operating with explicit safe structure.",
            *common,
            "Use direct natural instructions with clear steps and checks.",
        ]

    if seed_lines:
        body.extend(["Seed guidance:", *seed_lines])

    return "\n".join(body).strip() + "\n"
