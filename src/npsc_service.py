from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from compilation_profiles import (
    apply_profile_to_semantics,
    build_profile_status,
    get_profile,
    load_compilation_profiles,
    profile_default_level,
    profile_seed_limit,
    validate_profile_name,
)
from compiler_defaults import load_compiler_defaults, strict_policy
from context_loss_verifier import verify_context_loss
from exporters import export_json, export_text, prepare_output_dir
from hybrid_output import build_hybrid_output, build_profile_optimized_prompt
from model_adapter import adapter_layer, load_model_profiles, select_level
from nsl_compiler import compile_to_nsl
from nsl_parser import parse_nsl
from profile_selector import auto_select_profile
from rop_template import rop_payload
from semantic_ir import build_semantic_ir
from prompt_reconstructor import reconstruct_prompt
from report_builder import build_context_loss_report, build_run_summary, build_token_report_markdown
from semantic_dictionary import load_semantic_dictionary
from semantic_extractor import extract_semantics
from semantic_seed_mapper import suggest_seeds
from token_estimator import build_token_report
from utils import now_run_id


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class CompileRequest:
    original: str
    target: str = "codex"
    profile: str = "standard"
    level: str | None = None
    strict: bool = False
    preserve_original: bool = True
    privacy_mode: str = "full_original"
    custom_model_name: str = ""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_privacy_mode(value: str | None, preserve_original: bool = True) -> str:
    if value:
        selected = value.strip().lower()
    else:
        selected = "full_original" if preserve_original else "hash_only"
    if selected not in {"full_original", "hash_only", "redacted_preview"}:
        raise ValueError("privacy_mode must be full_original, hash_only or redacted_preview")
    return selected


def privacy_text(original: str, prompt_hash: str, privacy_mode: str) -> str:
    if privacy_mode == "hash_only":
        return f"[original prompt omitted; sha256={prompt_hash}]"
    if privacy_mode == "redacted_preview":
        return "[redacted preview] " + original[:80] + ("..." if len(original) > 80 else "")
    return original


def _privacy_needles(original: str) -> list[str]:
    parts = [original.strip()]
    parts.extend(p.strip() for p in re.split(r"[\n.!?]+", original) if len(p.strip()) >= 8)
    # Filter out empty strings to prevent replace("", placeholder) from
    # inserting the placeholder between every character.
    non_empty = [p for p in set(parts) if p]
    # Longer fragments first prevents partial replacements from leaving tails.
    return sorted(non_empty, key=len, reverse=True)


def scrub_private_payload(value: Any, original: str, prompt_hash: str, privacy_mode: str) -> Any:
    if privacy_mode != "hash_only":
        return value
    placeholder = f"[omitted_by_hash_only:{prompt_hash[:12]}]"
    needles = _privacy_needles(original)
    if isinstance(value, str):
        scrubbed = value
        for needle in needles:
            scrubbed = scrubbed.replace(needle, placeholder)
        return scrubbed
    if isinstance(value, list):
        return [scrub_private_payload(item, original, prompt_hash, privacy_mode) for item in value]
    if isinstance(value, dict):
        return {key: scrub_private_payload(item, original, prompt_hash, privacy_mode) for key, item in value.items()}
    return value


def evaluate_strict(report: dict[str, Any], policy: dict[str, Any] | None = None) -> tuple[bool, list[str]]:
    selected_policy = policy or strict_policy()
    reasons: list[str] = []
    min_score = int(selected_policy.get("min_score", 0))
    max_critical = int(selected_policy.get("max_critical_losses", 0))
    fail_on_missing_safety = bool(selected_policy.get("fail_on_missing_safety", True))
    fail_on_missing_goal = bool(selected_policy.get("fail_on_missing_goal", True))

    score = int(report.get("score", 0))
    critical_losses = list(report.get("critical_losses", []))
    if score < min_score:
        reasons.append(f"score_below_min:{score}<{min_score}")
    if len(critical_losses) > max_critical:
        reasons.append(f"critical_losses_exceeded:{len(critical_losses)}>{max_critical}")
    reasons.extend(str(item) for item in report.get("profile_failures", []))
    if fail_on_missing_goal and "missing_goal" in critical_losses:
        reasons.append("missing_goal")
    if fail_on_missing_safety:
        for tag in ("missing_no_sudo", "missing_no_external_api", "missing_no_destructive_actions", "missing_stay_inside_project_root"):
            if tag in critical_losses:
                reasons.append(tag)
    return len(reasons) == 0, sorted(set(reasons))


def compile_prompt(request: CompileRequest) -> dict[str, Any]:
    dictionary = load_semantic_dictionary()
    model_profiles = load_model_profiles()
    compilation_profiles = load_compilation_profiles()
    original = request.original
    target = request.target
    privacy_mode = normalize_privacy_mode(request.privacy_mode, request.preserve_original)
    prompt_hash = sha256_text(original)
    render_original = privacy_text(original, prompt_hash, privacy_mode)
    public_original = render_original if privacy_mode != "full_original" else original

    semantics = extract_semantics(original)
    requested_target = target
    if target == "auto":
        detected_target = str(semantics.get("target") or "").lower()
        if detected_target in model_profiles and detected_target not in {"auto", "generic"}:
            target = detected_target
        else:
            target = "codex"
    requested_profile = validate_profile_name(request.profile, compilation_profiles)
    auto_info: dict[str, Any] = {}
    applied_profile = requested_profile
    if requested_profile == "AUTO":
        auto_info = auto_select_profile(original, semantics)
        applied_profile = auto_info["auto_selected_profile"]

    profile = get_profile(applied_profile, compilation_profiles)
    technical_request = request.level or profile_default_level(applied_profile, profile)
    chosen_level = select_level(technical_request, target, model_profiles)
    profile_status = build_profile_status(
        requested_profile,
        applied_profile,
        profile,
        request.level,
        chosen_level,
        auto_info,
    )
    target_layer = adapter_layer(target, model_profiles, request.custom_model_name)
    if requested_target == "auto":
        target_layer["requested_target"] = "auto"
        target_layer["target_selection_reason"] = (
            "Detected from prompt semantics." if target == str(semantics.get("target") or "").lower() else "Fallback to codex for a safe general default."
        )
    defaults = load_compiler_defaults()
    selected_strict_policy = strict_policy()
    policy_layer = {
        "origin": "product_policy",
        "policy_constraints": list(defaults.get("critical_constraints", [])),
        "strict_policy": selected_strict_policy,
        "note": "Product policy is tracked separately from user constraints.",
    }
    compiler_trace = {
        "origin": "compiler_internal",
        "pipeline": [
            "semantic_extraction",
            "profile_resolution",
            "seed_mapping",
            "nsl_compilation",
            "prompt_reconstruction",
            "context_loss_verification",
            "artifact_export",
        ],
        "internal_outputs": ["compact_nsl.nsl", "execution_prompt.txt", "audit_bundle.md", "audit_bundle.json"],
    }

    profiled_semantics = apply_profile_to_semantics(semantics, applied_profile, profile)
    profiled_semantics["target"] = target
    profiled_semantics["target_adapter"] = target_layer
    profiled_semantics["policy_layer"] = policy_layer
    seeds = suggest_seeds(
        profiled_semantics,
        dictionary,
        target=target,
        level=chosen_level,
        limit=profile_seed_limit(applied_profile, profile),
    )

    safe_nsl = compile_to_nsl(profiled_semantics, seeds, level="safe", target=target)
    balanced_nsl = compile_to_nsl(profiled_semantics, seeds, level="balanced", target=target)
    aggressive_nsl = compile_to_nsl(profiled_semantics, seeds, level="aggressive", target=target)
    nsl_by_level = {"safe": safe_nsl, "balanced": balanced_nsl, "aggressive": aggressive_nsl}
    chosen_nsl = nsl_by_level.get(chosen_level, balanced_nsl)

    reconstructed = reconstruct_prompt(parse_nsl(chosen_nsl), dictionary, target=target)
    optimized_prompt = build_profile_optimized_prompt(
        render_original,
        reconstructed,
        applied_profile,
        profile,
        profiled_semantics,
        seeds,
        target,
    )
    verifier = verify_context_loss(original, profiled_semantics, optimized_prompt, chosen_nsl, applied_profile, profile)
    strict_passed, strict_reasons = evaluate_strict(verifier) if request.strict else (True, [])
    verifier["strict_requested"] = bool(request.strict)
    verifier["strict_status"] = "pass" if strict_passed else "blocked"
    verifier["strict_failures"] = strict_reasons
    token_report = build_token_report(original, safe_nsl, balanced_nsl, aggressive_nsl, optimized_prompt)
    hybrid_markdown = build_hybrid_output(render_original, profile_status, chosen_nsl, optimized_prompt, seeds, profiled_semantics, verifier, privacy_mode=privacy_mode)
    run_id = now_run_id("npsc")
    created_at = datetime.now(timezone.utc).isoformat()

    profile_payload = rop_payload(render_original) if applied_profile == "ROP" else {}
    semantic_ir_payload = build_semantic_ir(
        raw_prompt=original,
        sha256=prompt_hash,
        semantics=profiled_semantics,
        requested_profile=requested_profile,
        applied_profile=applied_profile,
        auto_info=auto_info,
        canonical_nsl=chosen_nsl,
        optimized_prompt=optimized_prompt,
        validation=verifier,
        profile_payload=profile_payload,
        compiler_trace=compiler_trace,
        policy_layer=policy_layer,
        target_adapter_layer=target_layer,
        privacy_mode=privacy_mode,
    )

    hybrid_json = {
        "schema": "npsc.hybrid_semantic_prompt.v1",
        "schema_version": "NPSC-HYBRID/1.0",
        "run_id": run_id,
        "created_at": created_at,
        **semantic_ir_payload,
        "target_model_profile": target,
        "compression_level": chosen_level,
        "hybrid_markdown": hybrid_markdown,
        "seeds": seeds,
        "raw_prompt_sha256": prompt_hash,
        "raw_prompt_original": original if privacy_mode == "full_original" else "",
        "privacy_mode": privacy_mode,
        "compact_nsl": chosen_nsl,
        "execution_prompt": optimized_prompt,
        "audit_bundle": {
            "markdown": hybrid_markdown,
            "semantic_ir": semantic_ir_payload,
            "validation": verifier,
        },
        "token_report": token_report,
        "transformations": [
            "semantic_extraction",
            "profile_resolution",
            "seed_mapping",
            "nsl_compilation",
            "prompt_reconstruction",
            "profile_prompt_rendering",
            "context_loss_verification",
        ],
        "warnings": verifier.get("warnings", []),
    }
    if privacy_mode == "hash_only":
        public_semantics = scrub_private_payload(profiled_semantics, original, prompt_hash, privacy_mode)
        public_chosen_nsl = scrub_private_payload(chosen_nsl, original, prompt_hash, privacy_mode)
        public_safe_nsl = scrub_private_payload(safe_nsl, original, prompt_hash, privacy_mode)
        public_balanced_nsl = scrub_private_payload(balanced_nsl, original, prompt_hash, privacy_mode)
        public_aggressive_nsl = scrub_private_payload(aggressive_nsl, original, prompt_hash, privacy_mode)
        public_optimized = scrub_private_payload(optimized_prompt, original, prompt_hash, privacy_mode)
        public_reconstructed = scrub_private_payload(reconstructed, original, prompt_hash, privacy_mode)
        public_hybrid_markdown = scrub_private_payload(hybrid_markdown, original, prompt_hash, privacy_mode)
        public_semantic_ir = scrub_private_payload(semantic_ir_payload, original, prompt_hash, privacy_mode)
        hybrid_json = scrub_private_payload(hybrid_json, original, prompt_hash, privacy_mode)
    else:
        public_semantics = profiled_semantics
        public_chosen_nsl = chosen_nsl
        public_safe_nsl = safe_nsl
        public_balanced_nsl = balanced_nsl
        public_aggressive_nsl = aggressive_nsl
        public_optimized = optimized_prompt
        public_reconstructed = reconstructed
        public_hybrid_markdown = hybrid_markdown
        public_semantic_ir = semantic_ir_payload

    return {
        "run_id": run_id,
        "created_at": created_at,
        "prompt_sha256": prompt_hash,
        "original": public_original,
        "privacy_mode": privacy_mode,
        "target": target,
        "requested_target": requested_target,
        "requested_profile": requested_profile,
        "applied_profile": applied_profile,
        "requested_level": request.level,
        "chosen_level": chosen_level,
        "profile": profile,
        "profile_status": profile_status,
        "auto_info": auto_info,
        "semantics": public_semantics,
        "seeds": seeds,
        "safe_nsl": public_safe_nsl,
        "balanced_nsl": public_balanced_nsl,
        "aggressive_nsl": public_aggressive_nsl,
        "chosen_nsl": public_chosen_nsl,
        "optimized_prompt": public_optimized,
        "reconstructed": public_reconstructed,
        "context_loss_report": verifier,
        "context_loss_markdown": build_context_loss_report(verifier),
        "token_report": token_report,
        "hybrid_markdown": public_hybrid_markdown,
        "hybrid_json": hybrid_json,
        "semantic_ir": public_semantic_ir,
        "strict_passed": strict_passed,
        "strict_failures": strict_reasons,
    }


def artifact_payloads(result: dict[str, Any]) -> dict[str, tuple[str, Any]]:
    profile_selection = dict(result["profile_status"])
    profile_selection["raw_prompt_sha256"] = result["prompt_sha256"]
    profile_selection["created_at"] = result["created_at"]
    profile_selection["auto"] = result.get("auto_info", {})

    artifacts = {
        "canonical_nsl.nsl": ("text", result["chosen_nsl"]),
        "compiled_safe.nsl": ("text", result["safe_nsl"]),
        "compiled_balanced.nsl": ("text", result["balanced_nsl"]),
        "compiled_aggressive.nsl": ("text", result["aggressive_nsl"]),
        "optimized_prompt.txt": ("text", result["optimized_prompt"]),
        "reconstructed_prompt.txt": ("text", result["reconstructed"]),
        "hybrid_semantic_prompt.md": ("text", result["hybrid_markdown"]),
        "hybrid_semantic_prompt.json": ("json", result["hybrid_json"]),
        "semantic_ir.json": ("json", result["semantic_ir"]),
        "semantic_analysis.json": ("json", result["semantics"]),
        "semantic_seeds.json": ("json", {"target": result["target"], "level": result["chosen_level"], "profile": result["applied_profile"], "selected": result["seeds"]}),
        "profile_selection_report.json": ("json", profile_selection),
        "profile_report.json": ("json", result["profile_status"]),
        "context_loss_report.md": ("text", result["context_loss_markdown"]),
        "context_loss_report.json": ("json", result["context_loss_report"]),
        "token_estimate_report.json": ("json", result["token_report"]),
        "token_estimate_report.md": ("text", build_token_report_markdown(result["token_report"])),
    }
    if result.get("privacy_mode") == "full_original":
        artifacts["raw_prompt_original.txt"] = ("text", result["original"])
    return artifacts


def export_artifacts(result: dict[str, Any], out_dir: str | Path) -> list[str]:
    output_dir = prepare_output_dir(out_dir)
    written: list[str] = []
    for name, (kind, payload) in artifact_payloads(result).items():
        path = output_dir / name
        if kind == "json":
            export_json(path, payload)
        else:
            export_text(path, str(payload))
        written.append(name)

    summary = {
        "run_id": result["run_id"],
        "target": result["target"],
        "requested_profile": result["requested_profile"],
        "applied_profile": result["applied_profile"],
        "requested_level": result["requested_level"] or "(profile default)",
        "chosen_level": result["chosen_level"],
        "score": result["context_loss_report"].get("score", 0),
        "profile_status": result["context_loss_report"].get("profile_status", "pass"),
        "strict_status": result["context_loss_report"].get("strict_status", "not_requested"),
        "critical_losses": result["context_loss_report"].get("critical_losses", []),
        "level_conflict": result["profile_status"].get("level_conflict"),
        "auto": result.get("auto_info", {}),
        "out_dir": str(Path(output_dir).resolve()),
        "artifacts": written + ["run_summary.md"],
    }
    export_text(output_dir / "run_summary.md", build_run_summary(summary))
    written.append("run_summary.md")
    return written


def result_json_for_console(result: dict[str, Any], artifacts: list[str] | None = None) -> str:
    payload = {
        "run_id": result["run_id"],
        "target": result["target"],
        "requested_profile": result["requested_profile"],
        "applied_profile": result["applied_profile"],
        "chosen_level": result["chosen_level"],
        "score": result["context_loss_report"].get("score", 0),
        "profile_status": result["context_loss_report"].get("profile_status", "pass"),
        "raw_prompt_sha256": result["prompt_sha256"],
        "auto": result.get("auto_info", {}),
        "artifacts": artifacts or [],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def compile_for_gui(original: str, target: str, requested_profile: str, requested_level: str) -> dict[str, Any]:
    """Lightweight compile path for GUI/tests — no privacy, no export, no token report."""
    dictionary = load_semantic_dictionary()
    model_profiles = load_model_profiles()
    compilation_profiles = load_compilation_profiles()

    semantics = extract_semantics(original)
    normalized_profile = validate_profile_name(requested_profile, compilation_profiles)
    auto_info: dict[str, Any] = {}
    applied_profile = normalized_profile
    if normalized_profile == "AUTO":
        auto_info = auto_select_profile(original, semantics)
        applied_profile = auto_info["auto_selected_profile"]

    profile = get_profile(applied_profile, compilation_profiles)
    technical_request = None if requested_level == "profile_default" else requested_level
    chosen_level = select_level(technical_request or profile_default_level(applied_profile, profile), target, model_profiles)
    profile_status = build_profile_status(
        normalized_profile,
        applied_profile,
        profile,
        technical_request,
        chosen_level,
        auto_info,
    )

    profiled_semantics = apply_profile_to_semantics(semantics, applied_profile, profile)
    profiled_semantics["target"] = target
    seeds = suggest_seeds(
        profiled_semantics,
        dictionary,
        target=target,
        level=chosen_level,
        limit=profile_seed_limit(applied_profile, profile),
    )

    nsl_by_level = {
        "safe": compile_to_nsl(profiled_semantics, seeds, level="safe", target=target),
        "balanced": compile_to_nsl(profiled_semantics, seeds, level="balanced", target=target),
        "aggressive": compile_to_nsl(profiled_semantics, seeds, level="aggressive", target=target),
    }
    chosen_nsl = nsl_by_level.get(chosen_level, nsl_by_level["balanced"])
    reconstructed = reconstruct_prompt(parse_nsl(chosen_nsl), dictionary, target=target)
    optimized = build_profile_optimized_prompt(
        original,
        reconstructed,
        applied_profile,
        profile,
        profiled_semantics,
        seeds,
        target,
    )
    verifier = verify_context_loss(original, profiled_semantics, optimized, chosen_nsl, applied_profile, profile)
    hybrid = build_hybrid_output(original, profile_status, chosen_nsl, optimized, seeds, profiled_semantics, verifier)

    return {
        "profile_status": profile_status,
        "semantics": profiled_semantics,
        "seeds": seeds,
        "nsl": chosen_nsl,
        "optimized": optimized,
        "hybrid": hybrid,
        "report": build_context_loss_report(verifier),
        "verifier": verifier,
    }
