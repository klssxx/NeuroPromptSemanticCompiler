#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
else
  PYTHON_BIN="${PYTHON:-python3}"
fi

echo "NPSC runtime check"
echo "Proyecto: $ROOT"
echo "Python: $PYTHON_BIN"

"$PYTHON_BIN" - <<'PY'
import importlib.util
import sys

print("Python version:", sys.version.split()[0])
for name in ["PySide6", "setuptools", "pytest"]:
    spec = importlib.util.find_spec(name)
    print(f"{name}:", "disponible" if spec else "no disponible")
PY

for tool in desktop-file-validate appstreamcli dpkg-deb apt-cache; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "$tool: $(command -v "$tool")"
  else
    echo "$tool: no disponible"
  fi
done
