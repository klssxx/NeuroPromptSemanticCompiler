"""Tool card — action card with icon placeholder, title, and description."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QFrame, QVBoxLayout


class ToolCard(QFrame):
    """Card representing a secondary tool/action."""

    def __init__(self, title: str = "", description: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NPSCToolCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(0)

        top = QHBoxLayout()
        top.setSpacing(8)

        self._icon = QLabel()
        self._icon.setObjectName("ToolCardIcon")
        self._icon.setFixedSize(28, 28)

        self._title = QLabel(title)
        self._title.setObjectName("ToolCardTitle")

        top.addWidget(self._icon)
        top.addWidget(self._title)
        top.addStretch(1)

        self._desc = QLabel(description)
        self._desc.setObjectName("ToolCardDesc")
        self._desc.setWordWrap(True)

        layout.addLayout(top)
        layout.addWidget(self._desc)

    def set_icon_text(self, text: str) -> None:
        self._icon.setText(text)

    def set_title(self, text: str) -> None:
        self._title.setText(text)

    def set_description(self, text: str) -> None:
        self._desc.setText(text)
