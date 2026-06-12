from __future__ import annotations

import argparse
from pathlib import Path
import sys

from compilation_profiles import get_profile, supported_profile_names, validate_profile_name
from i18n import set_language, tr
from model_adapter import load_model_profiles
from npsc_service import CompileRequest, compile_prompt, evaluate_strict, export_artifacts, result_json_for_console
from utils import read_text


def _strict_evaluation(report: dict, strict_policy: dict) -> tuple[bool, list[str]]:
    return evaluate_strict(report, strict_policy)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NeuroPrompt Semantic Compiler CLI")
    parser.add_argument("--input", help="Input prompt path")
    parser.add_argument("--text", help="Inline prompt text")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--level", choices=["safe", "balanced", "aggressive", "all"], help="Technical compression level")
    parser.add_argument("--profile", choices=[p.lower() for p in supported_profile_names()], default="standard", help="Semantic compilation profile")
    parser.add_argument("--target", required=True, choices=list(load_model_profiles().keys()))
    parser.add_argument("--explain-profile", action="store_true", help="Print profile explanation and exit after validation")
    parser.add_argument("--output-format", choices=["markdown", "json", "all"], default="all", help="Console output format; artifacts are still exported")
    parser.add_argument("--show", action="store_true", help="Print optimized prompt")
    parser.add_argument("--strict", action="store_true", help="Fail on critical context losses")
    parser.add_argument("--privacy-mode", choices=["full_original", "hash_only", "redacted_preview"], default="full_original", help="Original prompt persistence mode")
    parser.add_argument("--custom-model-name", default="", help="Visible model name when --target custom is used")
    parser.add_argument("--language", choices=["es", "en", "auto"], default="es", help="Console language / idioma de consola")
    return parser


def _load_prompt(args: argparse.Namespace) -> str:
    if args.input and args.text:
        raise ValueError("Use only one of --input or --text")
    if args.input:
        return read_text(args.input)
    if args.text:
        return args.text
    raise ValueError("Either --input or --text is required")


def run_cli(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    set_language(args.language)

    original = _load_prompt(args)
    requested_profile = validate_profile_name(args.profile)
    if args.explain_profile:
        profile_name = "STANDARD" if requested_profile == "AUTO" else requested_profile
        profile = get_profile(profile_name)
        print(f"{tr('cli.profile_requested')}: {requested_profile}")
        print(f"{tr('cli.profile_explained')}: {profile_name}")
        print(profile.get("purpose", ""))
        print(f"{tr('cli.compression')}: {profile.get('compression', '')}")
        print(f"{tr('cli.validation')}: {profile.get('validation', {}).get('mode', '')}")
        return 0

    result = compile_prompt(
        CompileRequest(
            original=original,
            target=args.target,
            profile=args.profile,
            level=args.level,
            strict=args.strict,
            privacy_mode=args.privacy_mode,
            custom_model_name=args.custom_model_name,
        )
    )
    artifacts = export_artifacts(result, args.out)

    print(
        f"[NPSC] target={result['target']} profile={result['applied_profile']} "
        f"requested_level={result['requested_level'] or 'profile_default'} chosen={result['chosen_level']} "
        f"score={result['context_loss_report'].get('score', 0)}"
    )
    if result.get("auto_info"):
        print(f"[NPSC] auto_selected_profile={result['auto_info'].get('auto_selected_profile')} reason={result['auto_info'].get('selection_reason')}")
    if result["profile_status"].get("level_conflict"):
        print(f"[NPSC] profile_level_note={result['profile_status']['level_conflict']}")
    print(f"[NPSC] sha256={result['prompt_sha256']}")
    print(f"[NPSC] outputs={Path(args.out).resolve()}")

    if args.output_format == "json":
        print(result_json_for_console(result, artifacts))
    elif args.output_format == "markdown":
        print(result["hybrid_markdown"])

    if args.show:
        print(f"\n--- {tr('cli.optimized_prompt')} ---\n")
        print(result["optimized_prompt"])

    if args.strict:
        passed, reasons = evaluate_strict(result["context_loss_report"])
        if not passed:
            print(f"[NPSC] {tr('cli.strict_failed')}: {','.join(reasons)}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
