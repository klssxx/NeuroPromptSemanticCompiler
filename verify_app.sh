#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

PYTHONPATH="$ROOT/src" "$PYTHON" -m py_compile src/npsc_gui/main.py src/npsc_gui/main_window.py src/npsc_gui/controller.py
QT_QPA_PLATFORM=offscreen PYTHONPATH="$ROOT/src" "$PYTHON" - <<'PY'
from PySide6.QtWidgets import QApplication
from npsc_gui.main_window import MainWindow
app = QApplication([])
window = MainWindow()
window.show()
window.close()
app.quit()
print("qt gui smoke ok")
PY

QT_QPA_PLATFORM=offscreen PYTHONPATH="$ROOT/src" "$PYTHON" -m unittest discover -s tests -v
echo "PASS"
