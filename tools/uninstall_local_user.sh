#!/usr/bin/env bash
set -euo pipefail

APP_ID="neuro-prompt-semantic-compiler"
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
INSTALL_BASE="$XDG_DATA_HOME/$APP_ID"
BIN_DIR="$HOME/.local/bin"
DESKTOP_FILE="$XDG_DATA_HOME/applications/neuro-prompt-semantic-compiler.desktop"
ICON_FILE="$XDG_DATA_HOME/icons/hicolor/scalable/apps/neuro-prompt-semantic-compiler.svg"
CONFIG_DIR="$XDG_CONFIG_HOME/$APP_ID"

python3 - <<PY
from pathlib import Path
import shutil

for file_path in [Path("$BIN_DIR/npsc"), Path("$BIN_DIR/npsc-gui"), Path("$DESKTOP_FILE"), Path("$ICON_FILE")]:
    if file_path.exists() or file_path.is_symlink():
        file_path.unlink()

for dir_path in [Path("$INSTALL_BASE"), Path("$CONFIG_DIR")]:
    if dir_path.exists():
        shutil.rmtree(dir_path)
PY

echo "Desinstalacion local completada para $APP_ID."
