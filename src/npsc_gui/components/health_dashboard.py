"""HealthDashboard — Auslogics-style module status panel showing
compilation health, metrics, and quick-access tool categories.

Displays 4 metric cards with semantic colors.
Designed for the right sidebar or dashboard bottom strip.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)


class MetricPill(QFrame):
    """Single metric display: large value + small label."""

    def __init__(self, label: str, value: str = "—", semantic: str = "muted", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NPSCMetricPill")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(2)

        self._val = QLabel(value)
        self._val.setAlignment(Qt.AlignCenter)
        self._val.setObjectName("MetricPillValue")
        vfont = self._val.font()
        vfont.setPointSize(18)
        vfont.setWeight(QFont.Bold)
        self._val.setFont(vfont)

        self._lbl = QLabel(label)
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setObjectName("MetricPillLabel")

        layout.addWidget(self._val)
        layout.addWidget(self._lbl)
        self.set_semantic(semantic)

    def set_value(self, text: str) -> None:
        self._val.setText(text)

    def set_semantic(self, semantic: str) -> None:
        colors = {
            "success": "#30B87A", "info": "#4CB8F5",
            "warning": "#E5A51A", "error": "#E04E65", "muted": "#6C717A",
        }
        c = colors.get(semantic, "#6C717A")
        self._val.setStyleSheet(f"color: {c}; background: transparent; border: none;")


class HealthDashboard(QFrame):
    """Dashboard panel with metric pills row."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NPSCHealthDash")
        self._metrics: dict[str, MetricPill] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Title
        title = QLabel("Estado del sistema")
        title.setObjectName("HealthSectionTitle")
        layout.addWidget(title)

        # Metrics row
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(6)
        for key, label, val, sem in [
            ("score", "Preservación", "—/100", "muted"),
            ("constraints", "Restricciones", "0", "info"),
            ("warnings", "Avisos", "0", "warning"),
            ("errors", "Errores", "0", "muted"),
        ]:
            pill = MetricPill(label, val, sem)
            self._metrics[key] = pill
            metrics_row.addWidget(pill)
        layout.addLayout(metrics_row)

    def get_metric(self, key: str) -> MetricPill | None:
        """Return the MetricPill for `key`, or None.

        Renamed from `metric()` to avoid clashing with QFrame.metric(int)
        which returns an int — pitfall #14 of the PySide6 skill.
        """
        return self._metrics.get(key)

    def update_metrics(self, score: int, constraints: int, warnings: int, errors: int) -> None:
        # Score is shown as N/100 to make the scale explicit and reduce ambiguity
        # with a bare integer (a "0" can mean "no data" or "0% preservation" otherwise).
        self._metrics["score"].set_value(f"{score}/100")
        self._metrics["score"].set_semantic(
            "success" if score >= 85 else "warning" if score >= 60 else "error"
        )
        self._metrics["constraints"].set_value(str(constraints))
        self._metrics["warnings"].set_value(str(warnings))
        self._metrics["warnings"].set_semantic("warning" if warnings > 0 else "muted")
        self._metrics["errors"].set_value(str(errors))
        self._metrics["errors"].set_semantic("error" if errors > 0 else "muted")
