#!/usr/bin/env bash
# scripts/run.sh — Launch NeuroPrompt Semantic Compiler (source mode)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ── Detect Python ──
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "ERROR: Python 3 not found. Install Python 3.10+ and run:" >&2
  echo "  cd $ROOT && python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt" >&2
  exit 127
fi

# ── Check PySide6 ──
if ! "$PYTHON" -c "import PySide6" >/dev/null 2>&1; then
  echo "ERROR: PySide6 is not available in this Python interpreter." >&2
  echo "" >&2
  echo "To install (inside .venv):" >&2
  echo "  cd $ROOT" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/python -m pip install -r requirements.txt" >&2
  echo "" >&2
  echo "Or with uv:" >&2
  echo "  cd $ROOT && uv pip install -r requirements.txt" >&2
  exit 1
fi

# ── Launch ──
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" -m npsc_gui.main "$@"
