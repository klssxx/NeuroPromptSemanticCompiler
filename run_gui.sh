#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1 && [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python no encontrado / Python not found: $PYTHON_BIN" >&2
  echo "Instala Python 3.10+ o ejecuta con PYTHON=/ruta/python ./run_gui.sh" >&2
  exit 127
fi

if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec('PySide6') else 1)
PY
then
  cat >&2 <<'EOF'
PySide6 no está disponible en este intérprete.
PySide6 is not available in this Python interpreter.

Opciones sin sudo dentro del proyecto:
  python3 -m venv .venv
  .venv/bin/python -m pip install -U pip
  .venv/bin/python -m pip install -r requirements.txt
  ./run_gui.sh

Paquetes de distro habituales (si prefieres usar el gestor del sistema):
  Ubuntu/Xubuntu/Kubuntu/Debian: python3-pyside6.qtwidgets python3-pyside6.qtsvg
  Fedora: python3-pyside6
  Arch/CachyOS/Manjaro: pyside6
EOF
  exit 1
fi

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON_BIN" -m npsc_gui.main "$@"
