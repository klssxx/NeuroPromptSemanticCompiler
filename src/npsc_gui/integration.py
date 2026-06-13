"""Integration hooks for connecting advanced mode page, about dialog, and export preview
into the existing MainWindow without a full rewrite.

This module provides factory functions and signal handlers that main_window.py
can call to add the new functionality.
"""
from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from npsc_gui.about_dialog import AboutDialog
from npsc_gui.export_preview import ExportPreviewDialog


def open_about_dialog(parent: QWidget, language: str = "es") -> None:
    """Show the About dialog as a modal."""
    dlg = AboutDialog(parent, language=language)
    dlg.exec()


def open_export_preview(parent: QWidget) -> None:
    """Show the Export Preview dialog if there is a result to preview.

    The parent (MainWindow) must have a `result` attribute containing
    the compilation result dict.
    """
    result = getattr(parent, "result", None)
    if not result:
        from PySide6.QtWidgets import QMessageBox
        lang = language(widget=parent)
        QMessageBox.information(
            parent,
            "Sin resultado",
            "No hay ningun resultado que previsualizar. Compila un prompt primero."
            if lang == "es"
            else "No result to preview. Compile a prompt first."
        )
        return
    dlg = ExportPreviewDialog(result, parent)
    dlg.exec()


def language(widget: QWidget) -> str:
    """Detect the current language from a widget that has compile_current."""
    # Try to read from the widget's settings if available
    w = widget
    while w is not None:
        settings = getattr(w, "settings", None)
        if settings and isinstance(settings, dict):
            return settings.get("language", "es")
        w = w.parent()
    return "es"
