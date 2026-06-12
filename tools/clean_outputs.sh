#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/outputs"

find "$OUT" -mindepth 1 -maxdepth 1 ! -name '.gitkeep' -exec rm -rf {} +

echo "Outputs limpiados en: $OUT"
