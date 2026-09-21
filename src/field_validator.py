from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldValidationResult:
    """Result of validating a form before export/compile."""
    valid: bool = True
    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)

    def add_error(self, field_name: str, message: str) -> None:
        self.errors.append({"field": field_name, "message": message})
        self.valid = False

    def add_warning(self, field_name: str, message: str) -> None:
        self.warnings.append({"field": field_name, "message": message})

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# Default known targets; callers may override with their loaded model_profiles.
_DEFAULT_TARGETS = frozenset({
    "codex", "gpt4", "gpt4o", "claude", "gemini", "mistral",
    "llama", "generic", "auto",
})


def validate_compile_form(
    prompt: str,
    variables: dict[str, str] | None = None,
    required_fields: list[str] | None = None,
    strict: bool = False,
    target: str | None = None,
    available_targets: set[str] | frozenset[str] | None = None,
) -> FieldValidationResult:
    """Validate a compilation form before processing.

    Args:
        prompt: The prompt text to compile.
        variables: {{var}} substitution values, keyed by variable name.
        required_fields: Field names that must be non-empty in *variables*.
        strict: When True, warnings are promoted to errors.
        target: The compilation target selected by the user/UI.
        available_targets: Set of valid target identifiers loaded from
            model_profiles.  Defaults to _DEFAULT_TARGETS.

    Returns:
        FieldValidationResult with errors and warnings.
    """
    result = FieldValidationResult()
    variables = variables or {}
    required_fields = required_fields or []
    known_targets = available_targets if available_targets is not None else _DEFAULT_TARGETS

    # --- prompt presence ---
    if not prompt.strip():
        result.add_error("prompt", "empty_prompt")
        return result

    # --- target validation (was placeholder) ---
    if target is not None:
        normalised = target.strip().lower()
        if normalised not in known_targets:
            msg = f"unknown_target: {target!r}. Known targets: {', '.join(sorted(known_targets))}"
            if strict:
                result.add_error("target", msg)
            else:
                result.add_warning("target", msg)

    # --- variable detection and fill-status ---
    from variables import detect_variables, build_fill_form
    detected = detect_variables(prompt)
    if detected:
        form = build_fill_form(prompt)
        unfilled = form.unfilled()

        if unfilled:
            msg = f"unfilled_variables: {', '.join(sorted(unfilled))}"
            if strict:
                result.add_error("variables", msg)
            else:
                result.add_warning("variables", msg)

        # Warn on empty-string values (invisible gap in compiled prompt)
        empty_valued = [
            name for name in detected
            if name in variables and variables[name] == ""
        ]
        if empty_valued:
            result.add_warning(
                "variables",
                f"empty_variable_value: {', '.join(sorted(empty_valued))}",
            )

        extra_vars = set(variables.keys()) - set(detected)
        if extra_vars:
            result.add_warning("variables", f"unused_variables: {', '.join(sorted(extra_vars))}")

    # --- required fields ---
    for req_field in required_fields:
        value = variables.get(req_field, "")
        if not value.strip():
            if strict:
                result.add_error(req_field, f"required_field_empty: {req_field}")
            else:
                result.add_warning(req_field, f"recommended_field_empty: {req_field}")

    # --- prompt length ---
    prompt_len = len(prompt.strip())
    if prompt_len < 10:
        result.add_warning("prompt", "prompt_too_short")
    elif prompt_len > 50000:
        result.add_warning("prompt", "prompt_very_long")

    return result


def validate_export_form(
    result_data: dict[str, Any],
    export_formats: list[str] | None = None,
    strict: bool = False,
) -> FieldValidationResult:
    """Validate before exporting a result.

    Args:
        result_data: The compiled result dict produced by compile_prompt /
            compile_for_gui.
        export_formats: List of requested export format names.
        strict: When True, warnings about missing compiled output become errors.
    """
    result = FieldValidationResult()
    export_formats = export_formats or ["markdown", "json", "txt"]

    if not result_data:
        result.add_error("result", "no_result_to_export")
        return result

    # Fix: OR condition — warn/error when EITHER compiled field is missing.
    missing_prompt = "optimized_prompt" not in result_data
    missing_nsl = "chosen_nsl" not in result_data
    if missing_prompt or missing_nsl:
        missing = []
        if missing_prompt:
            missing.append("optimized_prompt")
        if missing_nsl:
            missing.append("chosen_nsl")
        msg = f"no_compiled_output: missing fields: {', '.join(missing)}"
        if strict:
            result.add_error("result", msg)
        else:
            result.add_warning("result", msg)

    supported = {"markdown", "json", "txt"}
    unknown = set(export_formats) - supported
    if unknown:
        result.add_warning("formats", f"unsupported_formats: {', '.join(sorted(unknown))}")

    return result


def validate_template_form(
    name: str,
    content: str,
) -> FieldValidationResult:
    """Validate a template before saving."""
    result = FieldValidationResult()

    if not name.strip():
        result.add_error("name", "template_name_required")

    if not content.strip():
        result.add_error("content", "template_content_required")
        return result

    from variables import validate_template
    tpl_result = validate_template(content)
    for warning in tpl_result.get("warnings", []):
        result.add_warning("template", warning)
    for error in tpl_result.get("errors", []):
        result.add_error("template", error)

    return result
