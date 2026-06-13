#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 src/benchmark_quality.py --target codex --out outputs/benchmark
echo "Benchmark generado en: $ROOT/outputs/benchmark"
