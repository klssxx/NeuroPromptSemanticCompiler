"""Advanced mode page with 6 editable sections plus informal prompt preserving."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit,
    QPushButton, QScrollArea, QSizePolicy, QSplitter, QVBoxLayout, QWidget,
)

from i18n import tr


ADVANCED_SECTION_KEYS = [
    "context_role",
    "query_task",
    "specifications",
    "quality_criteria",
    "output_format",
    "verification",
]

ADVANCED_SECTION_DEFAULTS_EN = {
    "context_role": "Context and role",
    "query_task": "Query or task",
    "specifications": "Specifications",
    "quality_criteria": "Quality criteria",
    "output_format": "Output format",
    "verification": "Verification",
}

ADVANCED_SECTION_DEFAULTS_ES = {
    "context_role": "Contexto y rol",
    "query_task": "Consulta o tarea",
    "specifications": "Especificaciones",
    "quality_criteria": "Criterios de calidad",
    "output_format": "Formato de salida",
    "verification": "Verificacion",
}

ADVANCED_SECTION_PLACEHOLDERS_EN = {
    "context_role": "Who should the AI act as? What is the background context?",
    "query_task": "What exactly do you want the AI to do? Be specific.",
    "specifications": "Technical details, constraints, scope, edge cases...",
    "quality_criteria": "What makes a good response? What to avoid?",
    "output_format": "Structure, length, style, language, markdown...",
    "verification": "How to validate the output? Checklists, tests...",
}

ADVANCED_SECTION_PLACEHOLDERS_ES = {
    "context_role": "¿Como debe actuar la IA? ¿Cual es el contexto?",
    "query_task": "¿Que quieres que haga la IA? Se especifico.",
    "specifications": "Detalles tecnicos, restricciones, alcance...",
    "quality_criteria": "¿Que hace una buena respuesta? ¿Que evitar?",
    "output_format": "Estructura, longitud, estilo, idioma, markdown...",
    "verification": "¿Como validar la salida? Checklists, pruebas...",
}


def section_label(key: str) -> str:
    lang = "es"  # will be overridden by caller using i18n
    defaults = ADVANCED_SECTION_DEFAULTS_ES.get(key, key)
    return defaults


class EditableSectionCard(QFrame):
    """A single collapsible editable section in advanced mode."""

    content_changed = Signal(str, str)  # section_key, new_text

    def __init__(self, section_key: str, label_text: str, placeholder_text: str,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._section_key = section_key
        self.setObjectName("AdvancedSectionCard")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        spacing = 4
        layout.setSpacing(spacing)

        # Header row: label + collapse toggle
        header = QHBoxLayout()
        self._header_lbl = QLabel(label_text)
        self._header_lbl.setObjectName("SectionTitle")
        header.addWidget(self._header_lbl)
        header.addStretch(1)

        self._collapse_btn = QPushButton("−")
        self._collapse_btn.setFixedSize(24, 24)
        self._collapse_btn.setObjectName("CollapseBtn")
        self._collapse_btn.setCheckable(True)
        self._collapse_btn.setChecked(False)
        self._collapse_btn.clicked.connect(self._toggle_collapse)
        header.addWidget(self._collapse_btn)
        layout.addLayout(header)

        # Editor
        self._editor = QPlainTextEdit()
        self._editor.setPlaceholderText(placeholder_text)
        self._editor.setMinimumHeight(60)
        self._editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self._editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._editor)

        # Word/char count
        self._stats_lbl = QLabel("0 chars")
        self._stats_lbl.setObjectName("Muted")
        layout.addWidget(self._stats_lbl)

    def _toggle_collapse(self, checked: bool) -> None:
        self._editor.setVisible(not checked)
        self._collapse_btn.setText("+" if checked else "−")

    def _on_text_changed(self) -> None:
        text = self._editor.toPlainText()
        self._stats_lbl.setText(f"{len(text)} chars")
        self.content_changed.emit(self._section_key, text)

    def get_text(self) -> str:
        return self._editor.toPlainText()

    def set_text(self, text: str) -> None:
        self._editor.blockSignals(True)
        self._editor.setPlainText(text)
        self._editor.blockSignals(False)
        self._stats_lbl.setText(f"{len(text)} chars")

    def set_label(self, text: str) -> None:
        self._header_lbl.setText(text)

    def set_placeholder(self, text: str) -> None:
        self._editor.setPlaceholderText(text)


class AdvancedModePage(QWidget):
    """Full advanced mode page: 6 editable sections + informal prompt preview."""

    sections_changed = Signal(dict)  # {section_key: text}
    compile_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._sections: dict[str, EditableSectionCard] = {}
        self._editing = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        # Title
        title_row = QHBoxLayout()
        title = QLabel(tr("mode.advanced.title") if hasattr(tr, "__call__") else "Modo Avanzable — Secciones editables")
        title.setObjectName("SimpleTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)

        self._mode_indicator = QLabel("ADVANCED")
        self._mode_indicator.setObjectName("ModeIndicator")
        title_row.addWidget(self._mode_indicator)
        layout.addLayout(title_row)

        subtitle = QLabel("Edita cada seccion individualmente o escribe tu prompt informal. "
                          "Todas las secciones son opcionales.")
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Splitter: sections on top, informal preview at bottom
        splitter = QSplitter(Qt.Vertical)

        # Scrollable sections area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sections_container = QWidget()
        sections_layout = QVBoxLayout(sections_container)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(8)

        lang = "es"
        defaults = ADVANCED_SECTION_DEFAULTS_ES
        placeholders = ADVANCED_SECTION_PLACEHOLDERS_ES

        for key in ADVANCED_SECTION_KEYS:
            card = EditableSectionCard(
                section_key=key,
                label_text=defaults.get(key, key),
                placeholder_text=placeholders.get(key, ""),
            )
            card.content_changed.connect(self._on_section_changed)
            self._sections[key] = card
            sections_layout.addWidget(card)

        sections_layout.addStretch(1)
        scroll.setWidget(sections_container)
        splitter.addWidget(scroll)

        # Informal prompt area
        informal_container = QWidget()
        informal_layout = QVBoxLayout(informal_container)
        informal_layout.setContentsMargins(0, 4, 0, 0)
        informal_layout.setSpacing(4)
        informal_header = QLabel("Prompt informal original (se conserva, no se modifica)")
        informal_header.setObjectName("Muted")
        informal_layout.addWidget(informal_header)
        self._informal_preview = QPlainTextEdit()
        self._informal_preview.setReadOnly(True)
        self._informal_preview.setPlaceholderText("El prompt informal aparecera aqui cuando escribas en el modo simple o lo pegues aqui.")
        self._informal_preview.setMaximumHeight(120)
        informal_layout.addWidget(self._informal_preview)
        splitter.addWidget(informal_container)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, 1)

        # Action row
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self._check_btn = QPushButton("Revisar campos")
        self._check_btn.clicked.connect(self._review_fields)
        action_row.addWidget(self._check_btn)

        self._compile_btn = QPushButton("COMPILAR (ADVANCED)")
        self._compile_btn.setObjectName("PrimaryButton")
        self._compile_btn.setMinimumHeight(36)
        self._compile_btn.clicked.connect(self.compile_requested.emit)
        action_row.addWidget(self._compile_btn)

        self._save_sections_btn = QPushButton("Guardar secciones")
        self._save_sections_btn.clicked.connect(self._save_sections)
        action_row.addWidget(self._save_sections_btn)

        self._load_sections_btn = QPushButton("Cargar secciones")
        self._load_sections_btn.clicked.connect(self._load_sections)
        action_row.addWidget(self._load_sections_btn)

        action_row.addStretch(1)
        layout.addLayout(action_row)

    @Slot(str, str)
    def _on_section_changed(self, key: str, text: str) -> None:
        data = {k: card.get_text() for k, card in self._sections.items()}
        self.sections_changed.emit(data)

    def get_sections_data(self) -> dict[str, str]:
        return {k: card.get_text() for k, card in self._sections.items()}

    def set_sections_data(self, data: dict[str, str]) -> None:
        for key, text in data.items():
            if key in self._sections:
                self._sections[key].set_text(text or "")

    def get_combined_prompt(self) -> str:
        """Combine all filled sections into a structured prompt.

        The informal input is always preserved at the top.
        """
        parts = []

        # Informal input first (always preserved)
        informal = self.get_informal_input()
        if informal.strip():
            parts.append(informal.strip())

        # Then each filled section
        defaults = ADVANCED_SECTION_DEFAULTS_ES
        for key in ADVANCED_SECTION_KEYS:
            text = self._sections[key].get_text().strip()
            if text:
                label = defaults.get(key, key)
                parts.append(f"[{label}]\n{text}")

        return "\n\n".join(parts)

    def get_informal_input(self) -> str:
        return self._informal_preview.toPlainText()

    def set_informal_input(self, text: str) -> None:
        self._informal_preview.setPlainText(text)

    def _review_fields(self) -> None:
        empty = []
        filled = []
        defaults = ADVANCED_SECTION_DEFAULTS_ES
        for key in ADVANCED_SECTION_KEYS:
            text = self._sections[key].get_text().strip()
            if text:
                filled.append(defaults.get(key, key))
            else:
                empty.append(defaults.get(key, key))

        msg_parts = []
        if filled:
            msg_parts.append(f"Secciones completas ({len(filled)}):\n" + "\n".join(f"  • {s}" for s in filled))
        if empty:
            msg_parts.append(f"Secciones vacias ({len(empty)}):\n" + "\n".join(f"  ○ {s}" for s in empty))

        informal = self.get_informal_input().strip()
        if informal:
            preview = informal[:80] + ("..." if len(informal) > 80 else "")
            msg_parts.append(f"\nPrompt informal: {preview}")

        if not msg_parts:
            QMessageBox.information(self, "Revision de campos", "Todas las estan vacias. Escribe o pega un prompt primero.")
        else:
            QMessageBox.information(self, "Revision de campos", "\n\n".join(msg_parts))

    def _save_sections(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        import json
        from pathlib import Path
        from datetime import datetime, timezone

        from npsc_gui.settings import data_dir

        data = self.get_sections_data()
        informal = self.get_informal_input()
        if not any(v.strip() for v in data.values()) and not informal.strip():
            QMessageBox.warning(self, "Sin contenido", "No hay nada que guardar. Escribe algo primero.")
            return

        default = str(data_dir() / "projects")
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar secciones", default, "Secciones NPSC (*.nsect.json)"
        )
        if not path:
            return
        if not path.endswith(".nsect.json"):
            path += ".nsect.json"

        project = {
            "schema_version": "1.0",
            "type": "advanced_sections",
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "informal_input": informal,
            "sections": data,
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(project, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _load_sections(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        import json
        from pathlib import Path

        from npsc_gui.settings import data_dir

        default = str(data_dir() / "projects")
        path, _ = QFileDialog.getOpenFileName(
            self, "Cargar secciones", default, "Secciones NPSC (*.nsect.json)"
        )
        if not path:
            return

        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo cargar:\n{exc}")
            return

        informal = data.get("informal_input", "")
        if informal:
            self.set_informal_input(informal)

        sections = data.get("sections", {})
        self.set_sections_data(sections)

    def clear_all(self) -> None:
        for card in self._sections.values():
            card.set_text("")
        self._informal_preview.clear()
