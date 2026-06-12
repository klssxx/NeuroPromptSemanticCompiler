from __future__ import annotations

from typing import Any

from compilation_profiles import render_rop_template
from constraint_normalizer import critical_constraints


CRITICAL_CONSTRAINTS = [
    "no_sudo",
    "no_external_api",
    "no_destructive_actions",
    "stay_inside_project_root",
]


def _seed_lines(seeds: list[dict[str, Any]], limit: int | None = None) -> list[str]:
    selected = seeds[:limit] if limit else seeds
    if not selected:
        return ["- none"]
    return [
        f"- {seed.get('id', '')}: {seed.get('name', seed.get('meaning', ''))}"
        for seed in selected
    ]


def _list_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- none"]


def _critical_constraints(semantics: dict[str, Any]) -> list[str]:
    return critical_constraints(semantics.get("constraints", []))


def build_profile_optimized_prompt(
    original: str,
    reconstructed: str,
    profile_name: str,
    profile: dict[str, Any],
    semantics: dict[str, Any],
    seeds: list[dict[str, Any]],
    target: str,
) -> str:
    constraints = _critical_constraints(semantics)
    directives = profile.get("prompt_directives", [])

    if profile_name == "FAST":
        lines = [str(semantics.get("goal", "answer the user request")).strip()]
        user_tasks = [t for t in semantics.get("tasks", []) if not t.startswith(("extract_", "compile_", "verify_", "export_"))]
        if len(user_tasks) > 1 and len(str(semantics.get("goal", ""))) > 120:
            lines.append(f"Intent: {', '.join(user_tasks[:3])}")
        if constraints:
            lines.append(f"Constraints: {', '.join(constraints)}")
        outputs = list(semantics.get("output", []))
        if outputs and outputs != ["direct_answer"] and len(str(semantics.get("goal", ""))) > 120:
            lines.append(f"Output: {', '.join(outputs[:3])}")
        return "\n".join(lines).strip() + "\n"

    if profile_name == "ROP":
        core = [
            "# ROP Semantic Prompt",
            "",
            render_rop_template(original, profile).strip(),
            "",
            "CORE NSL RECONSTRUCTION:",
            reconstructed.strip(),
        ]
        return "\n".join(core).strip() + "\n"

    if profile_name == "RESEARCH_MAX":
        lines = [
            "# RESEARCH_MAX Semantic Prompt",
            "",
            "ORIGINAL PROMPT PRESERVED:",
            original.strip(),
            "",
            "RECONSTRUCTED MODEL PROMPT:",
            reconstructed.strip(),
            "",
            "STRICT PRESERVATION REQUIREMENTS:",
            "- Preserve objectives, constraints, context, format, nuance and critical unknowns.",
            "- Do not compress away important caveats or edge cases.",
            "- Separate facts, assumptions, hypotheses and unknowns.",
            "- Report any missing evidence or uncertainty explicitly.",
            "",
            "PROFILE DIRECTIVES:",
            *_list_lines([str(item) for item in directives]),
        ]
        return "\n".join(lines).strip() + "\n"

    if profile_name == "ADVANCED":
        lines = [
            "# ADVANCED Semantic Prompt",
            "",
            reconstructed.strip(),
            "",
            "Additional structure:",
            "- Preserve context and output contract.",
            "- Surface assumptions, risks and verification checks.",
            "- Keep technical constraints explicit.",
            "",
            "Profile directives:",
            *_list_lines([str(item) for item in directives]),
        ]
        return "\n".join(lines).strip() + "\n"

    lines = [
        "# STANDARD Semantic Prompt",
        "",
        reconstructed.strip(),
        "",
        "Profile directives:",
        *_list_lines([str(item) for item in directives]),
    ]
    return "\n".join(lines).strip() + "\n"


def build_hybrid_output(
    original: str,
    profile_status: dict[str, Any],
    nsl_text: str,
    optimized_prompt: str,
    seeds: list[dict[str, Any]],
    semantics: dict[str, Any],
    context_loss_report: dict[str, Any],
    privacy_mode: str = "full_original",
) -> str:
    profile_name = profile_status.get("applied_profile", "STANDARD")
    if privacy_mode == "hash_only":
        original_section = "[original prompt omitted: privacy_mode=hash_only]"
    elif privacy_mode == "redacted_preview":
        original_section = original[:80] + ("..." if len(original) > 80 else "")
    else:
        original_section = original.strip()
    lines = [
        "# Hybrid Semantic Prompt",
        "",
        "## Fuente",
        f"- privacy_mode: {privacy_mode}",
        "",
        "## Prompt original",
        original_section,
        "",
        "## Perfil aplicado",
        f"- requested_profile: {profile_status.get('requested_profile', profile_name)}",
        f"- applied_profile: {profile_name}",
        f"- semantic_purpose: {profile_status.get('semantic_purpose', '')}",
        f"- compression: {profile_status.get('compression', '')}",
        f"- verbosity: {profile_status.get('verbosity', '')}",
        f"- output_length: {profile_status.get('output_length', '')}",
        f"- requested_level: {profile_status.get('requested_level') or '(profile default)'}",
        f"- chosen_level: {profile_status.get('chosen_level', '')}",
    ]

    if profile_status.get("level_conflict"):
        lines.extend(["", "## Conflicto profile/level", str(profile_status["level_conflict"])])

    auto_info = profile_status.get("auto") or {}
    if auto_info:
        lines.extend(
            [
                "",
                "## Auto Select",
                f"- auto_selected_profile: {auto_info.get('auto_selected_profile', profile_name)}",
                f"- selection_reason: {auto_info.get('selection_reason', '')}",
                f"- risk_flags: {', '.join(auto_info.get('risk_flags', [])) or 'none'}",
                f"- fallback_profile: {auto_info.get('fallback_profile', '')}",
            ]
        )

    lines.extend(
        [
            "",
            "## compact_nsl.nsl",
            "```text",
            nsl_text.strip(),
            "```",
            "",
            "## execution_prompt.txt",
            optimized_prompt.strip(),
            "",
            "## audit_bundle",
            "- Este bloque es trazabilidad, no compresion.",
            f"- retention_score: {context_loss_report.get('retention_score', context_loss_report.get('score', 0))}",
            f"- precision_score: {context_loss_report.get('precision_score', 0)}",
            f"- unsupported_addition_score: {context_loss_report.get('unsupported_addition_score', 0)}",
            f"- compression_ratio_nsl: {context_loss_report.get('compression_ratio_nsl', 0)}",
            f"- expansion_ratio_execution_prompt: {context_loss_report.get('expansion_ratio_execution_prompt', 0)}",
            "",
            "## Seeds seleccionadas",
            *_seed_lines(seeds),
            "",
            "## Restricciones criticas preservadas",
            *_list_lines(_critical_constraints(semantics)),
            "",
            "## Nivel de compresion",
            f"- semantic_profile_compression: {profile_status.get('compression', '')}",
            f"- technical_level: {profile_status.get('chosen_level', '')}",
            "",
            "## Reporte de perdida de contexto",
            f"- score: {context_loss_report.get('score', 0)}",
            f"- aggregate_score_formula: {context_loss_report.get('aggregate_score_formula', '')}",
            f"- recommendation: {context_loss_report.get('recommendation', '')}",
            f"- profile_status: {context_loss_report.get('profile_status', '')}",
            f"- critical_losses: {', '.join(context_loss_report.get('critical_losses', [])) or 'none'}",
            f"- warnings: {', '.join(context_loss_report.get('warnings', [])) or 'none'}",
            f"- profile_failures: {', '.join(context_loss_report.get('profile_failures', [])) or 'none'}",
        ]
    )

    if profile_name == "ROP":
        lines.extend(["", "## ROP integrado", "La plantilla ROP esta integrada en el prompt optimizado."])
    if profile_name == "RESEARCH_MAX":
        lines.extend(["", "## RESEARCH_MAX", "Maxima preservacion y validacion estricta activadas."])

    return "\n".join(lines).strip() + "\n"
