from __future__ import annotations

import re
from dataclasses import dataclass, field

_VARIABLE_RE = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class VariableDefinition:
    name: str
    label: str = ""
    placeholder: str = ""
    default: str = ""
    required: bool = False

    def __post_init__(self) -> None:
        if not self.label:
            self.label = self.name.replace("_", " ").title()


@dataclass
class VariableFillForm:
    """Holds the current fill state for a set of detected variables."""
    variables: dict[str, VariableDefinition] = field(default_factory=dict)
    values: dict[str, str] = field(default_factory=dict)

    def set_value(self, name: str, value: str) -> None:
        self.values[name] = value

    def get_value(self, name: str) -> str:
        return self.values.get(name, "")

    def is_complete(self) -> bool:
        """Returns True if all required variables have non-empty values."""
        for name, var_def in self.variables.items():
            if var_def.required and not self.values.get(name, "").strip():
                return False
        return True

    def missing_required(self) -> list[str]:
        """Returns names of required variables that are empty."""
        missing = []
        for name, var_def in self.variables.items():
            if var_def.required and not self.values.get(name, "").strip():
                missing.append(name)
        return missing

    def unfilled(self) -> list[str]:
        """Returns names of all variables (required or not) that are empty."""
        return [name for name in self.variables if not self.values.get(name, "").strip()]


def detect_variables(text: str) -> list[str]:
    """Return sorted unique variable names found in text using {{name}} syntax."""
    found = set(_VARIABLE_RE.findall(text))
    return sorted(found)


def build_fill_form(
    text: str,
    overrides: dict[str, VariableDefinition] | None = None,
) -> VariableFillForm:
    """Detect variables in text and build a fill form with optional overrides."""
    names = detect_variables(text)
    overrides = overrides or {}
    form = VariableFillForm()
    for name in names:
        if name in overrides:
            form.variables[name] = overrides[name]
        else:
            form.variables[name] = VariableDefinition(name=name)
    return form


def fill_variables(text: str, values: dict[str, str], strict: bool = False) -> str:
    """Replace {{name}} placeholders in text with provided values.
    
    Args:
        text: Template text with {{variable}} placeholders.
        values: Mapping of variable name -> replacement value.
        strict: If True, raises ValueError for unfilled variables.
    
    Returns:
        Text with variables substituted.
    """
    def replacer(match: re.Match) -> str:
        name = match.group(1)
        if name in values:
            return values[name]
        if strict:
            raise ValueError(f"Variable '{name}' not provided in values")
        return match.group(0)  # keep original placeholder

    result = _VARIABLE_RE.sub(replacer, text)
    return result


def validate_template(text: str, require_variables: bool = False) -> dict:
    """Validate a template text and return a status dict.
    
    Returns:
        {
            "valid": bool,
            "variables": list[str],   # detected variable names
            "warnings": list[str],     # non-critical issues
            "errors": list[str],       # critical issues
        }
    """
    result = {
        "valid": True,
        "variables": [],
        "warnings": [],
        "errors": [],
    }

    if not text.strip():
        result["valid"] = False
        result["errors"].append("empty_template")
        return result

    variables = detect_variables(text)
    result["variables"] = variables

    if require_variables and not variables:
        result["warnings"].append("no_variables_detected")

    # Check for malformed variable syntax
    malformed = re.findall(r"\{[^{}]*[^{}]*\}", text)
    for m in malformed:
        if not _VARIABLE_RE.fullmatch(m):
            result["warnings"].append(f"malformed_variable_syntax: {m}")

    return result
