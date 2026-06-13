#!/usr/bin/env python3
"""Baseline screenshot capture — current state BEFORE visual polish.

Generates PNGs of the actual current MainWindow using only the post-rollback
APIs (no window.advanced_mode, no section_help_buttons, etc.).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from npsc_gui.main_window import MainWindow, MODE_SIMPLE, MODE_EXTREME

    out_dir = ROOT / "artifacts" / "baseline_2026"
    out_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1320, 860)
    window.show()
    app.processEvents()

    captured: list[str] = []

    def shot(name: str) -> None:
        path = out_dir / f"{name}.png"
        window.grab().save(str(path))
        captured.append(str(path))
        print(f"  saved {path.name}")

    # Simple mode (default)
    print("SIMPLE mode (default):")
    shot("simple_home_dark")

    # Switch to extreme mode
    print("EXTREME mode:")
    window._switch_to_mode(MODE_EXTREME)
    app.processEvents()
    shot("extreme_dashboard_dark")

    # Switch back to simple
    window._switch_to_mode(MODE_SIMPLE)
    app.processEvents()

    # Test compile in simple mode to see health dashboard populated
    print("Compile flow (simple):")
    window.simple_prompt_edit.setPlainText(
        "Organiza una lista de tareas para esta semana. "
        "Sin usar sudo. Máximo 5 elementos. "
        "Resaltar las urgentes. No compartas datos."
    )
    app.processEvents()
    # Click compile
    window.compile_current()
    # Wait for result via event loop
    deadline_iterations = 0
    while window.result is None and deadline_iterations < 500:
        app.processEvents()
        deadline_iterations += 1
    if window.result is None:
        print("  WARN: compile did not finish in time")
    shot("simple_result_dark")

    # Light theme (apply directly)
    print("Light theme test:")
    from npsc_gui.theme import get_qss
    window.setStyleSheet(get_qss("light"))
    app.processEvents()
    shot("extreme_dashboard_light")

    # Restore dark
    window.setStyleSheet(get_qss("dark"))
    app.processEvents()

    window.close()
    print("\n".join(captured))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
