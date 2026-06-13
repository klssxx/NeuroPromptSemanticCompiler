"""Status chip — small semantic pill with dot + text.

Variants: ok, warn, error, info.
Colors controlled via QSS property chipState.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QFrame


class StatusChip(QFrame):
    """Semantic status indicator chip (dot + text)."""

    def __init__(self, text: str = "", state: str = "ok", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NPSCChip")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 3, 10, 3)
        layout.setSpacing(5)

        self._dot = QLabel()
        self._dot.setObjectName("ChipDot")
        self._dot.setFixedSize(6, 6)

        self._text = QLabel(text)
        self._text.setObjectName("ChipText")

        layout.addWidget(self._dot)
        layout.addWidget(self._text)
        self.set_state(state)

    def set_text(self, text: str) -> None:
        self._text.setText(text)

    def set_state(self, state: str) -> None:
        """Set variant: ok, warn, error, info."""
        self.setProperty("chipState", state)
        for w in (self, self._dot, self._text):
            w.style().unpolish(w)
            w.style().polish(w)
