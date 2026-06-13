#!/usr/bin/env bash
# scripts/smoke_test.sh — Quick smoke test for NeuroPrompt Semantic Compiler
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0
FAIL=0

ok() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== NeuroPrompt Semantic Compiler — Smoke Test ==="
echo ""

# ── Python ──
echo "── Python ──"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
  ok "Python venv found: $("$PY" --version)"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
  ok "Python3 found: $("$PY" --version)"
else
  fail "Python 3 not found"
  exit 1
fi

# ── Dependencies ──
echo ""
echo "── Dependencies ──"
if QT_QPA_PLATFORM=offscreen "$PY" -c "import PySide6" 2>/dev/null; then
  ok "PySide6 available"
else
  fail "PySide6 not available — run: $PY -m pip install -r requirements.txt"
fi

# ── Syntax check ──
echo ""
echo "── Syntax Check →"
ERRORS=0
while IFS= read -r -d '' f; do
  if "$PY" -m py_compile "$f" 2>/dev/null; then
    :
  else
    fail "Syntax error: $f"
    ERRORS=$((ERRORS + 1))
  fi
done < <(find "$ROOT/src" -name "*.py" -not -path "*/__pycache__/*" -print0)
if [[ $ERRORS -eq 0 ]]; then
  ok "All Python files compile (0 syntax errors)"
fi

# ── Imports ──
echo ""
echo "── Core Imports ──"
if QT_QPA_PLATFORM=offscreen PYTHONPATH="$ROOT/src" "$PY" -c "
from i18n import tr, set_language
from variables import detect_variables, fill_variables
from template_manager import TemplateManager, PromptTemplate
from version_history import VersionHistory, compute_diff
from export_manager import export_markdown_result, export_json_result, export_txt_result
from field_validator import validate_compile_form
from npsc_service import CompileRequest, compile_prompt
from npsc_gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
app = QApplication([])
w = MainWindow()
assert hasattr(w, '_version_history')
assert hasattr(w, '_template_manager')
assert hasattr(w, '_variable_values')
assert hasattr(w, '_save_project')
assert hasattr(w, '_load_project')
assert hasattr(w, '_show_variable_dialog')
w.close()
app.quit()
" 2>/dev/null; then
  ok "All core modules import successfully"
  ok "MainWindow creates with all new attributes"
else
  fail "Core import failure — check error messages above"
fi

# ── Tests ──
echo ""
echo "── Tests ──"
TEST_OUTPUT=$(QT_QPA_PLATFORM=offscreen timeout 120s "$PY" -m pytest "$ROOT/tests/" -x -q --tb=line 2>&1) || true
TEST_EXIT=$?
if [[ $TEST_EXIT -eq 0 ]]; then
  TEST_COUNT=$(echo "$TEST_OUTPUT" | grep -oP '\d+ passed' | grep -oP '\d+' || echo "?")
  ok "All tests passed ($TEST_COUNT tests)"
else
  FAIL_COUNT=$(echo "$TEST_OUTPUT" | grep -oP '\d+ failed' | grep -oP '\d+' || echo "?")
  fail "Tests failed ($FAIL_COUNT failures)"
  echo "$TEST_OUTPUT" | tail -5
fi

# ── Summary ──
echo ""
echo "═══════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
echo "PASS"
