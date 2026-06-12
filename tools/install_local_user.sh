#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_ID="neuro-prompt-semantic-compiler"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
INSTALL_BASE="$XDG_DATA_HOME/$APP_ID"
INSTALL_DIR="$INSTALL_BASE/app"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$XDG_DATA_HOME/applications"
ICON_DIR="$XDG_DATA_HOME/icons/hicolor/scalable/apps"
CONFIG_DIR="$XDG_CONFIG_HOME/$APP_ID"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
else
  PYTHON_BIN="${PYTHON:-python3}"
fi

echo "Instalacion local de NeuroPrompt Semantic Compiler"
echo "Raiz fuente: $ROOT"
echo "Destino: $INSTALL_DIR"
echo "Python: $PYTHON_BIN"

"$PYTHON_BIN" - <<'PY'
import importlib.util
import sys

missing = []
for name in ["PySide6"]:
    if importlib.util.find_spec(name) is None:
        missing.append(name)
if missing:
    print("Faltan dependencias locales:", ", ".join(missing), file=sys.stderr)
    print("Instala las dependencias en un entorno local del proyecto antes de ejecutar este instalador.", file=sys.stderr)
    raise SystemExit(2)
PY

mkdir -p "$INSTALL_BASE" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR" "$CONFIG_DIR"

ROOT="$ROOT" INSTALL_DIR="$INSTALL_DIR" "$PYTHON_BIN" - <<'PY'
import os
import shutil
from pathlib import Path

root = Path(os.environ["ROOT"]).resolve()
dest = Path(os.environ["INSTALL_DIR"]).resolve()
excluded = {".venv", "dist", "backups", "_backups", "outputs", "artifacts", "staging", "build", ".pytest_cache"}

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

cat > "$BIN_DIR/npsc" <<EOF
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$INSTALL_DIR"
PYTHONPATH="\$APP_DIR/src" exec "$PYTHON_BIN" "\$APP_DIR/src/npsc_cli.py" "\$@"
EOF

cat > "$BIN_DIR/npsc-gui" <<EOF
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$INSTALL_DIR"
PYTHONPATH="\$APP_DIR/src" exec "$PYTHON_BIN" -m npsc_gui.main "\$@"
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
echo "Instalacion local completada."
echo "Ejecuta: $BIN_DIR/npsc-gui"
echo "Si $BIN_DIR no esta en PATH, añade ~/.local/bin a tu PATH o ejecuta la ruta completa."
