#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="NeuroPromptSemanticCompiler"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
OUT_DIR="$ROOT/dist"
ARCHIVE="$OUT_DIR/${NAME}-source-clean-${STAMP}.tar.gz"
MANIFEST="$OUT_DIR/${NAME}-source-clean-${STAMP}.manifest.txt"

mkdir -p "$OUT_DIR"

cd "$ROOT"

tar \
  --exclude='./.git' \
  --exclude='./.venv' \
  --exclude='./venv' \
  --exclude='./__pycache__' \
  --exclude='*/__pycache__' \
  --exclude='./.pytest_cache' \
  --exclude='./.mypy_cache' \
  --exclude='./.ruff_cache' \
  --exclude='./build' \
  --exclude='./dist' \
  --exclude='./staging' \
  --exclude='./outputs' \
  --exclude='./artifacts' \
  --exclude='./_backups' \
  --exclude='./backups' \
  --exclude='./*.egg-info' \
  --exclude='./*.tar.gz' \
  --exclude='./*.whl' \
  --exclude='./.coverage' \
  --exclude='./htmlcov' \
  -czf "$ARCHIVE" \
  --transform "s#^\.#$NAME#" \
  .

tar -tzf "$ARCHIVE" | sort > "$MANIFEST"

if grep -E '(^|/)(\.venv|venv|staging|outputs|artifacts|_backups|backups|__pycache__|\.pytest_cache)(/|$)' "$MANIFEST"; then
  echo "ERROR: generated directory leaked into archive" >&2
  exit 1
fi

printf 'Archive: %s\n' "$ARCHIVE"
printf 'Manifest: %s\n' "$MANIFEST"
printf 'Files: %s\n' "$(wc -l < "$MANIFEST")"
printf 'Size: %s\n' "$(du -h "$ARCHIVE" | awk '{print $1}')"
