from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from npsc_gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("NeuroPrompt Semantic Compiler")
    app.setOrganizationName("NPSC")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
