#!/usr/bin/env bash
# scripts/setup_venv_instructions.sh — Show setup instructions (does NOT install)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cat <<'INSTRUCTIONS'
╔══════════════════════════════════════════════════════════════╗
║  NeuroPrompt Semantic Compiler — Setup Instructions         ║
╚══════════════════════════════════════════════════════════════╝

This script shows the commands needed to set up the project.
It does NOT install anything automatically.

── Option A: Using uv (recommended) ──────────────────────────

  cd PROJECT_DIR
  uv venv .venv
  uv pip install -r requirements.txt
  ./scripts/run.sh

── Option B: Using standard venv ─────────────────────────────

  cd PROJECT_DIR
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
  ./scripts/run.sh

── Option C: Using uv run (no persistent venv) ───────────────

  cd PROJECT_DIR
  uv run --python 3.12 ./scripts/run.sh

── Run tests ─────────────────────────────────────────────────

  cd PROJECT_DIR
  QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -v

── Run smoke test ────────────────────────────────────────────

  cd PROJECT_DIR
  ./scripts/smoke_test.sh

Replace PROJECT_DIR with the actual path:
  PROJECT_DIR="CURRENT_DIR"

INSTRUCTIONS

echo "Current directory: $ROOT"
echo "Python version: $(python3 --version 2>&1)"
echo "uv version: $(uv --version 2>&1)"
