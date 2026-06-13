"""Result card — semantic metric card with value + label.

Color determined by semantic property: success, info, warning, error, muted.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout


class ResultCard(QFrame):
    """Compact card showing a semantic result metric."""

    def __init__(self, label: str = "", value: str = "—", semantic: str = "muted", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NPSCResultCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)

        self._value = QLabel(value)
        self._value.setObjectName("ResultCardValue")
        self._value.setAlignment(Qt.AlignCenter)

        self._label = QLabel(label)
        self._label.setObjectName("ResultCardLabel")
        self._label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._value)
        layout.addWidget(self._label)
        self.set_semantic(semantic)

    def set_value(self, text: str) -> None:
        self._value.setText(text)

    def set_label(self, text: str) -> None:
        self._label.setText(text)

    def set_semantic(self, semantic: str) -> None:
        """Set semantic color: success, info, warning, error, muted."""
        self.setProperty("semantic", semantic)
        self._value.setProperty("semantic", semantic)
        for w in (self, self._value):
            w.style().unpolish(w)
            w.style().polish(w)
