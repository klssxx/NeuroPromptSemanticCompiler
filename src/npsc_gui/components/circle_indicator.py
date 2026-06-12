"""Circle indicator — ring with central value for preservation score.

States: idle, active, success, error.
Zero GPU effects. Uses QSS border-color for the ring; content is QLabel.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class CircleIndicator(QFrame):
    """Circular ring indicator showing a numeric score.

    The ring is a QFrame with border-radius 50% and a thick border.
    The inner value and label are QLabels.
    """

    def __init__(self, size: int = 140, ring_width: int = 4, parent=None) -> None:
        super().__init__(parent)
        self._size = size
        self._ring_width = ring_width
        self.setObjectName("NPSCCircle")
        self.setFixedSize(size, size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        self._value_label = QLabel("—")
        self._value_label.setObjectName("CircleValue")
        self._value_label.setAlignment(Qt.AlignCenter)

        self._sub_label = QLabel("preservación")
        self._sub_label.setObjectName("CircleLabel")
        self._sub_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._value_label)
        layout.addWidget(self._sub_label)

        # Set circular border-radius programmatically based on size
        half = size // 2
        self.setStyleSheet(f"QFrame#NPSCCircle {{ border-radius: {half}px; }}")

        self.set_state("idle")

    def set_value(self, text: str) -> None:
        self._value_label.setText(text)

    def set_sublabel(self, text: str) -> None:
        self._sub_label.setText(text)

    def set_state(self, state: str) -> None:
        """Set visual state: idle, active, success, error."""
        self.setProperty("circleState", state)
        self.style().unpolish(self)
        self.style().polish(self)
