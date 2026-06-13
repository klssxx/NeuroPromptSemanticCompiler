"""Export preview dialog — shows a preview before saving to disk."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QMessageBox, QPlainTextEdit, QPushButton, QTabWidget,
    QVBoxLayout, QWidget,
)


def _build_markdown_preview(result: dict) -> str:
    """Build a markdown string from the compilation result (in-memory, no file I/O)."""
    lines = []
    lines.append("# NeuroPrompt Semantic Compiler — Result\n")
    lines.append(f"**Profile:** {result.get('applied_profile', result.get('profile', 'N/A'))}")
    lines.append(f"**Target:** {result.get('target', 'N/A')}")
    lines.append("")

    if "optimized_prompt" in result:
        lines.append("## Compiled Prompt\n")
        lines.append(result["optimized_prompt"])
        lines.append("")

    if "chosen_nsl" in result:
        lines.append("## NSL\n")
        lines.append("```")
        lines.append(result["chosen_nsl"])
        lines.append("```")
        lines.append("")

    if "context_loss_report" in result:
        report = result["context_loss_report"]
        score = report.get("score", "N/A")
        lines.append(f"## Validation Score: {score}/100\n")
        warnings = report.get("warnings", [])
        if warnings:
            lines.append("### Warnings\n")
            for w in warnings:
                lines.append(f"- {w}")
            lines.append("")

    if "original" in result:
        lines.append("## Original Prompt\n")
        lines.append(result["original"][:500])
        if len(result["original"]) > 500:
            lines.append("...")
        lines.append("")

    return "\n".join(lines)


def _build_text_preview(result: dict) -> str:
    """Build a plain text string from the compilation result."""
    lines = []
    lines.append("=" * 60)
    lines.append("NeuroPrompt Semantic Compiler — Result")
    lines.append("=" * 60)
    lines.append("")

    if "optimized_prompt" in result:
        lines.append("COMPILED PROMPT:")
        lines.append("-" * 40)
        lines.append(result["optimized_prompt"])
        lines.append("")

    if "context_loss_report" in result:
        report = result["context_loss_report"]
        score = report.get("score", "N/A")
        lines.append(f"Validation Score: {score}/100")
        lines.append("")

    return "\n".join(lines)


class ExportPreviewDialog(QDialog):
    """Modal dialog showing export preview in multiple formats before saving."""

    def __init__(self, result: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result = result
        self.setWindowTitle("Export Preview / Vista previa de exportacion")
        self.setMinimumSize(640, 480)
        self._build_ui()
        self._populate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        info = QLabel("Preview the content before saving. You can copy directly or export to file.")
        info.setWordWrap(True)
        info.setObjectName("Muted")
        layout.addWidget(info)

        self._tabs = QTabWidget()

        self._md_preview = QPlainTextEdit()
        self._md_preview.setReadOnly(True)
        self._tabs.addTab(self._md_preview, "Markdown")

        self._json_preview = QPlainTextEdit()
        self._json_preview.setReadOnly(True)
        self._tabs.addTab(self._json_preview, "JSON")

        self._txt_preview = QPlainTextEdit()
        self._txt_preview.setReadOnly(True)
        self._tabs.addTab(self._txt_preview, "Plain Text")

        layout.addWidget(self._tabs, 1)

        row = QHBoxLayout()
        row.setSpacing(8)

        copy_btn = QPushButton("Copy current format")
        copy_btn.clicked.connect(self._copy_current)
        row.addWidget(copy_btn)

        row.addStretch(1)

        export_btn = QPushButton("Export to file...")
        export_btn.setObjectName("PrimaryButton")
        export_btn.clicked.connect(self._export_to_file)
        row.addWidget(export_btn)

        layout.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self) -> None:
        result = self._result

        try:
            md = _build_markdown_preview(result)
        except Exception:
            md = result.get("hybrid_markdown", result.get("optimized_prompt", ""))
        self._md_preview.setPlainText(md)

        try:
            json_data = result.get("hybrid_json", result)
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        except Exception:
            json_str = json.dumps({"optimized_prompt": result.get("optimized_prompt", "")}, indent=2, ensure_ascii=False)
        self._json_preview.setPlainText(json_str)

        try:
            txt = _build_text_preview(result)
        except Exception:
            txt = result.get("optimized_prompt", "")
        self._txt_preview.setPlainText(txt)

    def _copy_current(self) -> None:
        from PySide6.QtWidgets import QApplication
        idx = self._tabs.currentIndex()
        if idx == 0:
            text = self._md_preview.toPlainText()
        elif idx == 1:
            text = self._json_preview.toPlainText()
        else:
            text = self._txt_preview.toPlainText()
        QApplication.clipboard().setText(text)

    def _export_to_file(self) -> None:
        idx = self._tabs.currentIndex()
        if idx == 0:
            text = self._md_preview.toPlainText()
            filter_str = "Markdown (*.md)"
            default_ext = ".md"
        elif idx == 1:
            text = self._json_preview.toPlainText()
            filter_str = "JSON (*.json)"
            default_ext = ".json"
        else:
            text = self._txt_preview.toPlainText()
            filter_str = "Text (*.txt)"
            default_ext = ".txt"

        path, _ = QFileDialog.getSaveFileName(self, "Export", "", filter_str)
        if not path:
            return
        if not path.endswith(default_ext):
            path += default_ext

        try:
            Path(path).write_text(text, encoding="utf-8")
            QMessageBox.information(self, "Exported", f"File saved:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not save:\n{exc}")
