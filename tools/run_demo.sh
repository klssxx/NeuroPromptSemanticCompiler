#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="$ROOT/outputs/demo"
python3 src/npsc_cli.py --input examples/messy_prompt.txt --out "$OUT_DIR" --level all --target codex

echo "Demo generado en: $OUT_DIR"
