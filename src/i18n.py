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

    # ── Template page ──
    "tpl.page.title": {
        "es": "Plantillas reutilizables",
        "en": "Reusable templates",
    },
    "tpl.action.new": {
        "es": "Nueva plantilla",
        "en": "New template",
    },
    "tpl.action.import": {
        "es": "Importar",
        "en": "Import",
    },
    "tpl.action.export_all": {
        "es": "Exportar todas",
        "en": "Export all",
    },
    "tpl.action.use": {
        "es": "Usar plantilla",
        "en": "Use template",
    },
    "tpl.action.edit": {
        "es": "Editar",
        "en": "Edit",
    },
    "tpl.action.duplicate": {
        "es": "Duplicar",
        "en": "Duplicate",
    },
    "tpl.action.delete": {
        "es": "Eliminar",
        "en": "Delete",
    },
    "tpl.filter.all": {
        "es": "Todas",
        "en": "All",
    },
    "tpl.filter.category": {
        "es": "Categoría:",
        "en": "Category:",
    },
    "tpl.tab.content": {
        "es": "Contenido",
        "en": "Content",
    },
    "tpl.tab.meta": {
        "es": "Metadatos",
        "en": "Metadata",
    },
    "tpl.field.name": {
        "es": "Nombre:",
        "en": "Name:",
    },
    "tpl.field.category": {
        "es": "Categoría:",
        "en": "Category:",
    },
    "tpl.field.description": {
        "es": "Descripción:",
        "en": "Description:",
    },
    "tpl.field.target": {
        "es": "Modelo objetivo:",
        "en": "Target model:",
    },
    "tpl.field.profile": {
        "es": "Perfil:",
        "en": "Profile:",
    },
    "tpl.field.content": {
        "es": "Contenido de la plantilla",
        "en": "Template content",
    },
    "tpl.placeholder.content": {
        "es": "Escribe aquí la plantilla. Usa {{variable}} para campos rellenables...",
        "en": "Write the template here. Use {{variable} for fillable fields...",
    },
    "tpl.variable.hint": {
        "es": "Sintaxis de variables: {{nombre_variable}} — se detectan automáticamente",
        "en": "Variable syntax: {{variable_name}} — detected automatically",
    },
    "tpl.editor.title": {
        "es": "Editar plantilla",
        "en": "Edit template",
    },
    "tpl.create.title": {
        "es": "Nueva plantilla",
        "en": "New template",
    },
    "tpl.error.name_required": {
        "es": "El nombre de la plantilla es obligatorio.",
        "en": "Template name is required.",
    },
    "tpl.error.content_required": {
        "es": "El contenido de la plantilla no puede estar vacío.",
        "en": "Template content cannot be empty.",
    },
    "tpl.delete.title": {
        "es": "Eliminar plantilla",
        "en": "Delete template",
    },
    "tpl.delete.confirm": {
        "es": "¿Eliminar la plantilla «{name}»? Esta acción no se puede deshacer.",
        "en": "Delete template «{name}»? This cannot be undone.",
    },
    "tpl.import.title": {
        "es": "Importar plantilla",
        "en": "Import template",
    },
    "tpl.export.title": {
        "es": "Exportar plantillas",
        "en": "Export templates",
    },
    "tpl.export.done": {
        "es": "Se exportaron {count} plantillas.",
        "en": "{count} templates exported.",
    },

    # ── History page ──
    "history.page.title": {
        "es": "Historial de versiones",
        "en": "Version history",
    },
    "history.action.new": {
        "es": "Guardar versión actual",
        "en": "Save current version",
    },
    "history.action.clear_all": {
        "es": "Borrar todo el historial",
        "en": "Clear all history",
    },
    "history.action.restore": {
        "es": "Restaurar",
        "en": "Restore",
    },
    "history.action.delete": {
        "es": "Eliminar versión",
        "en": "Delete version",
    },
    "history.tab.content": {
        "es": "Contenido",
        "en": "Content",
    },
    "history.tab.diff": {
        "es": "Diferencias",
        "en": "Differences",
    },
    "history.tab.meta": {
        "es": "Metadatos",
        "en": "Metadata",
    },
    "history.compare.label": {
        "es": "Comparar con:",
        "en": "Compare with:",
    },
    "history.compare.btn": {
        "es": "Comparar",
        "en": "Compare",
    },
    "history.compare.select_first": {
        "es": "Selecciona una versión en la lista primero.",
        "en": "Select a version from the list first.",
    },
    "history.compare.same": {
        "es": "Has seleccionado la misma versión dos veces.",
        "en": "You selected the same version twice.",
    },
    "history.diff.summary": {
        "es": "Añadidas: {added} | Eliminadas: {removed} | Líneas antes: {total_old} / después: {total_new}",
        "en": "Added: {added} | Removed: {removed} | Lines before: {total_old} / after: {total_new}",
    },
    "history.diff.removed": {
        "es": "ELIMINADO:",
        "en": "REMOVED:",
    },
    "history.diff.added": {
        "es": "AÑADIDO:",
        "en": "ADDED:",
    },
    "history.diff.unified": {
        "es": "Diferencias unificadas:",
        "en": "Unified diff:",
    },
    "history.save.no_result": {
        "es": "No hay resultado que guardar. Compila un prompt primero.",
        "en": "No result to save. Compile a prompt first.",
    },
    "history.save.no_content": {
        "es": "El resultado no tiene contenido exportable.",
        "en": "The result has no exportable content.",
    },
    "history.save.name_default": {
        "es": "Versión guardada",
        "en": "Saved version",
    },
    "history.save.done": {
        "es": "Versión guardada: {name}",
        "en": "Version saved: {name}",
    },
    "history.delete.title": {
        "es": "Eliminar versión",
        "en": "Delete version",
    },
    "history.delete.confirm": {
        "es": "¿Eliminar esta versión del historial?",
        "en": "Delete this version from history?",
    },
    "history.restore.done": {
        "es": "Versión restaurada: {name}",
        "en": "Version restored: {name}",
    },
    "history.clear.title": {
        "es": "Borrar historial",
        "en": "Clear history",
    },
    "history.clear.confirm": {
        "es": "¿Eliminar TODAS las versiones del historial? Esta acción no se puede deshacer.",
        "en": "Delete ALL versions from history? This cannot be undone.",
    },

    # ── Validation messages ──
    "validation.errors_found": {
        "es": "Se encontraron errores:",
        "en": "Errors found:",
    },
    "validation.warnings_found": {
        "es": "Advertencias:",
        "en": "Warnings:",
    },
    "validation.ok": {
        "es": "Validación correcta",
        "en": "Validation passed",
    },
    "validation.error.empty_prompt": {
        "es": "El prompt está vacío",
        "en": "Prompt is empty",
    },
    "validation.error.unfilled_variables": {
        "es": "Variables sin rellenar",
        "en": "Unfilled variables",
    },
    "validation.error.required_field": {
        "es": "Campo obligatorio vacío",
        "en": "Required field empty",
    },
    "validation.warning.prompt_short": {
        "es": "El prompt es muy corto",
        "en": "Prompt is very short",
    },
    "validation.warning.prompt_long": {
        "es": "El prompt es muy largo",
        "en": "Prompt is very long",
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
