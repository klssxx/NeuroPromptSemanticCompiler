"""About dialog for NeuroPrompt Semantic Compiler."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

try:
    from PySide6.QtWidgets import QApplication
    _clipboard_available = True
except Exception:
    _clipboard_available = False


APP_NAME = "NeuroPrompt Semantic Compiler"
APP_VERSION = "1.0.0"
APP_TAGLINE_EN = "Semantic prompt compiler — offline, private, local."
APP_TAGLINE_ES = "Compilador semantico de prompts — offline, privado, local."
LICENSE_TEXT = "MIT License"
REPO_URL = "https://github.com/neuroprompt/neuroprompt-semantic-compiler"
PRIVACY_NOTE = (
    "This application runs entirely locally. No data is sent to external servers. "
    "All compilation, templates, history, and exports stay on your machine."
)
PRIVACY_NOTE_ES = (
    "Esta aplicacion se ejecuta completamente en local. No se envia ningun dato a "
    "servidores externos. Toda la compilacion, plantillas, historial y exportaciones "
    "se quedan en tu maquina."
)
LIMITATIONS = [
    "Requires PySide6 (Qt 6.7+) for the GUI.",
    "No cloud sync, no telemetry, no external API calls during compilation.",
    "Export formats: Markdown, JSON (stable schema), plain text.",
    "Variable engine: {{variable}} syntax with pre-compilation substitution.",
    "Template manager: local JSON persistence.",
    "Version history: session-based, with visual diff.",
]


class AboutDialog(QDialog):
    """Modal about dialog with version, license, privacy, limitations, and copy buttons."""

    def __init__(self, parent: QWidget | None = None, language: str = "es") -> None:
        super().__init__(parent)
        self._lang = language
        self.setWindowTitle("Acerca de NeuroPrompt Semantic Compiler" if language == "es" else "About NeuroPrompt Semantic Compiler")
        self.setMinimumSize(520, 480)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Brand icon placeholder
        icon_lbl = QLabel("N")
        icon_lbl.setObjectName("BrandGlyph")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(48, 48)
        layout.addWidget(icon_lbl, alignment=Qt.AlignHCenter)

        # App name
        name = QLabel(APP_NAME)
        name.setObjectName("SimpleTitle")
        name.setAlignment(Qt.AlignCenter)
        layout.addWidget(name)

        # Version
        ver = QLabel(f"v{APP_VERSION}")
        ver.setObjectName("Muted")
        ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver)

        # Tagline
        tagline = QLabel(APP_TAGLINE_ES if self._lang == "es" else APP_TAGLINE_EN)
        tagline.setObjectName("Muted")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setWordWrap(True)
        layout.addWidget(tagline)

        layout.addSpacing(8)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("Separator")
        layout.addWidget(sep)

        # Privacy section
        priv_title = QLabel("Privacidad" if self._lang == "es" else "Privacy")
        priv_title.setObjectName("SectionTitle")
        layout.addWidget(priv_title)

        priv_body = QLabel(PRIVACY_NOTE_ES if self._lang == "es" else PRIVACY_NOTE)
        priv_body.setWordWrap(True)
        priv_body.setObjectName("HelpText")
        layout.addWidget(priv_body)

        layout.addSpacing(4)

        # License + repo row
        row = QHBoxLayout()
        lic_lbl = QLabel(f"Licencia / License: {LICENSE_TEXT}")
        lic_lbl.setObjectName("HelpText")
        row.addWidget(lic_lbl)
        row.addStretch(1)

        self._repo_btn = QPushButton("GitHub (proximamente)" if self._lang == "es" else "GitHub (coming soon)")
        self._repo_btn.setObjectName("LinkButton")
        self._repo_btn.setEnabled(True)
        self._repo_btn.clicked.connect(self._open_repo_page)
        row.addWidget(self._repo_btn)
        layout.addLayout(row)

        layout.addSpacing(4)

        # Limitations
        lim_title = QLabel("Limitaciones conocidas" if self._lang == "es" else "Known limitations")
        lim_title.setObjectName("SectionTitle")
        layout.addWidget(lim_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(120)
        lim_container = QWidget()
        lim_layout = QVBoxLayout(lim_container)
        lim_layout.setContentsMargins(4, 2, 4, 2)
        lim_layout.setSpacing(2)
        for item in LIMITATIONS:
            lbl = QLabel(f"• {item}")
            lbl.setWordWrap(True)
            lbl.setObjectName("HelpText")
            lim_layout.addWidget(lbl)
        lim_layout.addStretch(1)
        scroll.setWidget(lim_container)
        layout.addWidget(scroll)

        layout.addSpacing(4)

        # Copy prompt button (convenience)
        self._copy_ver_btn = QPushButton(
            "Copiar version al portapapeles" if self._lang == "es" else "Copy version to clipboard"
        )
        self._copy_ver_btn.clicked.connect(self._copy_version)
        layout.addWidget(self._copy_ver_btn)

        # OK button
        layout.addSpacing(4)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _open_repo_page(self) -> None:
        QDesktopServices.openUrl(QUrl(REPO_URL))

    def _copy_version(self) -> None:
        if _clipboard_available:
            QApplication.clipboard().setText(f"{APP_NAME} v{APP_VERSION}")
