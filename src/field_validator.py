"""Field validation helpers for NPSC forms.

Changelog
---------
P1 fix (item 5)
    ``validate_compile_form`` now accepts ``target`` and ``known_targets``
    so callers can validate the target/model selection against the available
    model profiles.  Both params default to ``None`` for full backward
    compatibility.
P2 fix (item 14)
    ``assert_prompt_not_empty`` provides a service-level guardrail so
    ``compile_prompt`` / ``compile_for_gui`` cannot silently process an
    empty or whitespace-only prompt regardless of the caller.
P2 doc
    ``validate_export_form`` docstring clarifies the NOR-condition logic.
"""
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


# ---------------------------------------------------------------------------
# Service-level guardrail  (P2 fix item 14)
# ---------------------------------------------------------------------------

def assert_prompt_not_empty(prompt: str) -> None:
    """Raise ``ValueError`` if *prompt* is empty or whitespace-only.

    Intended to be called at the very top of ``compile_prompt`` and
    ``compile_for_gui`` in ``npsc_service.py`` so the invariant
    "prompt must not be empty" is enforced inside the service layer
    regardless of whether the caller ran ``validate_compile_form`` first.

    Raises:
        ValueError: with message ``prompt must not be empty or whitespace-only``.
    """
    if not prompt or not prompt.strip():
        raise ValueError("prompt must not be empty or whitespace-only")


# ---------------------------------------------------------------------------
# Form validators
# ---------------------------------------------------------------------------

def validate_compile_form(
    prompt: str,
    variables: dict[str, str] | None = None,
    required_fields: list[str] | None = None,
    strict: bool = False,
    target: str | None = None,
    known_targets: list[str] | None = None,
) -> FieldValidationResult:
    """Validate a compilation form before processing.

    Args:
        prompt: The prompt text to compile.
        variables: If prompt contains {{var}} substitutions, the provided values.
        required_fields: List of field names that must be non-empty.
        strict: If True, warnings become errors.
        target: The requested model/target identifier (e.g. ``"codex"``).
            Pass ``None`` to skip target validation (backward-compatible).
        known_targets: Exhaustive list of valid target identifiers drawn from
            ``model_profiles``.  When both *target* and *known_targets* are
            provided and the target is not in the list, emits an error
            (strict=True) or warning (strict=False).
            Pass ``None`` to skip target validation (backward-compatible).

    Returns:
        FieldValidationResult with errors and warnings.
    """
    result = FieldValidationResult()
    variables = variables or {}
    required_fields = required_fields or []

    # Check empty prompt
    if not prompt.strip():
        result.add_error("prompt", "empty_prompt")
        return result  # No point checking further

    # Check for unfilled variables
    from variables import detect_variables, build_fill_form
    detected = detect_variables(prompt)
    if detected:
        form = build_fill_form(prompt)
        unfilled = form.unfilled()

        if unfilled:
            msg = f"unfilled_variables: {', '.join(unfilled)}"
            if strict:
                result.add_error("variables", msg)
            else:
                result.add_warning("variables", msg)

        extra_vars = set(variables.keys()) - set(detected)
        if extra_vars:
            result.add_warning(
                "variables",
                f"unused_variables: {', '.join(sorted(extra_vars))}",
            )

    # Check required fields
    for req_field in required_fields:
        value = variables.get(req_field, "")
        if not value.strip():
            if strict:
                result.add_error(req_field, f"required_field_empty: {req_field}")
            else:
                result.add_warning(req_field, f"recommended_field_empty: {req_field}")

    # Check prompt length
    prompt_len = len(prompt.strip())
    if prompt_len < 10:
        result.add_warning("prompt", "prompt_too_short")
    elif prompt_len > 50000:
        result.add_warning("prompt", "prompt_very_long")

    # P1 fix (item 5): validate target against known model profiles
    if target is not None and known_targets is not None:
        if target not in known_targets:
            msg = (
                f"unknown_target: '{target}' not in known profiles "
                f"({', '.join(sorted(known_targets))})"
            )
            if strict:
                result.add_error("target", msg)
            else:
                result.add_warning("target", msg)

    return result


def validate_export_form(
    result_data: dict[str, Any],
    export_formats: list[str] | None = None,
) -> FieldValidationResult:
    """Validate before exporting a result.

    Emits a ``no_compiled_output`` warning when *neither* ``optimized_prompt``
    *nor* ``chosen_nsl`` is present in *result_data* (NOR condition — the
    warning fires only when **both** fields are absent, not when just one is).

    Args:
        result_data: The compiled result dict to export.
        export_formats: Requested output formats.  Defaults to
            ``["markdown", "json", "txt"]``.

    Returns:
        FieldValidationResult with errors and warnings.
    """
    result = FieldValidationResult()
    export_formats = export_formats or ["markdown", "json", "txt"]

    if not result_data:
        result.add_error("result", "no_result_to_export")
        return result

    # NOR: warn only when neither compiled-output key is present
    if "optimized_prompt" not in result_data and "chosen_nsl" not in result_data:
        result.add_warning("result", "no_compiled_output")

    supported = {"markdown", "json", "txt"}
    unknown = set(export_formats) - supported
    if unknown:
        result.add_warning("formats", f"unsupported_formats: {', '.join(unknown)}")

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
