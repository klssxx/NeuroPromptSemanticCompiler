from __future__ import annotations

import locale
import os

SUPPORTED_LANGUAGES = {"es", "en"}
_DEFAULT_LANGUAGE = "es"
_current_language = _DEFAULT_LANGUAGE

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "app.subtitle": {
        "es": "Compilador semántico",
        "en": "Semantic compiler",
    },
    "status.ready": {
        "es": "Listo",
        "en": "Ready",
    },
    "mode.activate_extreme": {
        "es": "Activar modo extremo",
        "en": "Activate expert mode",
    },
    "mode.activate_simple": {
        "es": "Volver al modo sencillo",
        "en": "Back to simple mode",
    },
    "mode.simple_status": {
        "es": "Modo: Sencillo",
        "en": "Mode: Simple",
    },
    "mode.extreme_status": {
        "es": "Modo: Extremo",
        "en": "Mode: Expert",
    },
    "mode.simple_header": {
        "es": "Modo sencillo",
        "en": "Simple mode",
    },
    "mode.extreme_header": {
        "es": "Modo extremo",
        "en": "Expert mode",
    },
    "settings.title": {
        "es": "Configuración",
        "en": "Settings",
    },
    "settings.theme": {
        "es": "Tema visual:",
        "en": "Visual theme:",
    },
    "settings.theme.dark": {
        "es": "Oscuro",
        "en": "Dark",
    },
    "settings.theme.light": {
        "es": "Claro",
        "en": "Light",
    },
    "settings.startup_mode": {
        "es": "Modo de inicio:",
        "en": "Startup mode:",
    },
    "settings.language": {
        "es": "Idioma / Language:",
        "en": "Language / Idioma:",
    },
    "settings.language.es": {
        "es": "Castellano",
        "en": "Spanish",
    },
    "settings.language.en": {
        "es": "Inglés",
        "en": "English",
    },
    "settings.reset": {
        "es": "Restablecer configuración",
        "en": "Reset settings",
    },
    "settings.xdg_note": {
        "es": "Configuración persistente local XDG. No se usa red ni telemetría.",
        "en": "Local persistent XDG settings. No network or telemetry is used.",
    },
    "error.no_result": {
        "es": "Sin resultado para renderizar",
        "en": "No result to render",
    },
    "cli.profile_requested": {
        "es": "Perfil solicitado",
        "en": "Requested profile",
    },
    "cli.profile_explained": {
        "es": "Perfil explicado",
        "en": "Explained profile",
    },
    "cli.compression": {
        "es": "Compresión",
        "en": "Compression",
    },
    "cli.validation": {
        "es": "Validación",
        "en": "Validation",
    },
    "cli.optimized_prompt": {
        "es": "prompt optimizado",
        "en": "optimized prompt",
    },
    "cli.strict_failed": {
        "es": "modo estricto falló",
        "en": "strict mode failed",
    },
}


def normalize_language(value: str | None) -> str:
    if not value:
        return _DEFAULT_LANGUAGE
    lowered = value.strip().lower().replace("_", "-")
    if lowered == "auto":
        return detect_language()
    prefix = lowered.split("-", 1)[0]
    return prefix if prefix in SUPPORTED_LANGUAGES else _DEFAULT_LANGUAGE


def detect_language() -> str:
    for candidate in (
        os.environ.get("NPSC_LANG"),
        os.environ.get("LANGUAGE"),
        os.environ.get("LC_ALL"),
        os.environ.get("LC_MESSAGES"),
        os.environ.get("LANG"),
        locale.getlocale()[0],
    ):
        if candidate:
            prefix = str(candidate).split(":", 1)[0].replace("_", "-").split("-", 1)[0].lower()
            if prefix in SUPPORTED_LANGUAGES:
                return prefix
    return _DEFAULT_LANGUAGE


def set_language(value: str | None) -> str:
    global _current_language
    _current_language = normalize_language(value)
    return _current_language


def get_language() -> str:
    return _current_language


def tr(key: str, language: str | None = None) -> str:
    lang = normalize_language(language) if language else _current_language
    options = _TRANSLATIONS.get(key)
    if not options:
        return key
    return options.get(lang) or options.get(_DEFAULT_LANGUAGE) or key
