#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_ID="neuro-prompt-semantic-compiler"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
INSTALL_BASE="$XDG_DATA_HOME/$APP_ID"
INSTALL_DIR="$INSTALL_BASE/app"
VENV_DIR="$INSTALL_BASE/.venv"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$XDG_DATA_HOME/applications"
ICON_DIR="$XDG_DATA_HOME/icons/hicolor/scalable/apps"
CONFIG_DIR="$XDG_CONFIG_HOME/$APP_ID"

if [[ -n "${PYTHON:-}" ]]; then
  BOOTSTRAP_PYTHON="$PYTHON"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  BOOTSTRAP_PYTHON="$ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  BOOTSTRAP_PYTHON="python3"
else
  echo "ERROR: Python 3 not found. Install Python 3.10+ or run with PYTHON=/path/to/python." >&2
  exit 127
fi

echo "Instalacion local de NeuroPrompt Semantic Compiler"
echo "Raiz fuente: $ROOT"
echo "Destino app: $INSTALL_DIR"
echo "Runtime venv: $VENV_DIR"
echo "Python bootstrap: $BOOTSTRAP_PYTHON"

"$BOOTSTRAP_PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10):
    print("ERROR: Python 3.10+ requerido.", file=sys.stderr)
    raise SystemExit(2)
print(f"Python OK: {sys.version.split()[0]}")
PY

mkdir -p "$INSTALL_BASE" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR" "$CONFIG_DIR"

ROOT="$ROOT" INSTALL_DIR="$INSTALL_DIR" "$BOOTSTRAP_PYTHON" - <<'PY'
import os
import shutil
from pathlib import Path

root = Path(os.environ["ROOT"]).resolve()
dest = Path(os.environ["INSTALL_DIR"]).resolve()
excluded = {
    ".venv",
    "dist",
    "backups",
    "_backups",
    "outputs",
    "artifacts",
    "staging",
    "build",
    ".pytest_cache",
}

if dest.exists():
    shutil.rmtree(dest)
dest.parent.mkdir(parents=True, exist_ok=True)

def ignore(_dir, names):
    ignored = []
    for name in names:
        if name in excluded or name == "__pycache__" or name.endswith(".egg-info"):
            ignored.append(name)
        elif name.endswith((".pyc", ".pyo")) or name == ".coverage":
            ignored.append(name)
    return ignored

shutil.copytree(root, dest, ignore=ignore)
PY

rm -rf "$VENV_DIR"
if command -v uv >/dev/null 2>&1; then
  uv venv --python "$BOOTSTRAP_PYTHON" "$VENV_DIR"
  uv pip install --python "$VENV_DIR/bin/python" -r "$INSTALL_DIR/requirements.txt"
else
  "$BOOTSTRAP_PYTHON" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
  "$VENV_DIR/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"
fi

"$VENV_DIR/bin/python" - <<'PY'
import importlib.util
import sys

missing = [name for name in ["PySide6"] if importlib.util.find_spec(name) is None]
if missing:
    print("Faltan dependencias runtime:", ", ".join(missing), file=sys.stderr)
    raise SystemExit(2)
print("Runtime PySide6 OK")
PY

cat > "$BIN_DIR/npsc" <<EOF
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$INSTALL_DIR"
VENV_PYTHON="$VENV_DIR/bin/python"
if [[ ! -x "\$VENV_PYTHON" ]]; then
  echo "NPSC runtime Python not found: \$VENV_PYTHON" >&2
  echo "Reinstall with: bash $INSTALL_DIR/tools/install_local_user.sh" >&2
  exit 127
fi
PYTHONPATH="\$APP_DIR/src" exec "\$VENV_PYTHON" "\$APP_DIR/src/npsc_cli.py" "\$@"
EOF

cat > "$BIN_DIR/npsc-gui" <<EOF
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$INSTALL_DIR"
VENV_PYTHON="$VENV_DIR/bin/python"
if [[ ! -x "\$VENV_PYTHON" ]]; then
  echo "NPSC runtime Python not found: \$VENV_PYTHON" >&2
  echo "Reinstall with: bash $INSTALL_DIR/tools/install_local_user.sh" >&2
  exit 127
fi
PYTHONPATH="\$APP_DIR/src" exec "\$VENV_PYTHON" -m npsc_gui.main "\$@"
EOF

chmod +x "$BIN_DIR/npsc" "$BIN_DIR/npsc-gui"

cp "$ROOT/assets/icons/neuro-prompt-semantic-compiler.svg" "$ICON_DIR/neuro-prompt-semantic-compiler.svg"
cat > "$DESKTOP_DIR/neuro-prompt-semantic-compiler.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=NeuroPrompt Semantic Compiler
GenericName=Semantic Prompt Compiler
Comment=Mejora prompts localmente y genera salidas semanticas verificables
Exec=$BIN_DIR/npsc-gui
Icon=neuro-prompt-semantic-compiler
Terminal=false
Categories=Utility;
Keywords=prompt;AI;semantic;compiler;NSL;
EOF

echo "$INSTALL_DIR" > "$CONFIG_DIR/install_path"
echo "$VENV_DIR/bin/python" > "$CONFIG_DIR/runtime_python"

echo "Instalacion local completada."
echo "Ejecuta: $BIN_DIR/npsc-gui"
echo "Si $BIN_DIR no esta en PATH, añade ~/.local/bin a tu PATH o ejecuta la ruta completa."
