#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required_files=(
  "README.md"
  "PROJECT_VISION.md"
  "TECHNICAL_SPEC.md"
  "ROADMAP.md"
  "SAFETY.md"
  "CHANGELOG.md"
  "requirements.txt"
  "pyproject.toml"
  ".gitignore"
  "configs/semantic_dictionary.json"
  "configs/model_profiles.json"
  "configs/compiler_defaults.json"
  "configs/compilation_profiles.json"
  "configs/extraction_patterns.json"
  "assets/icons/neuro-prompt-semantic-compiler.svg"
  "assets/icons/neuro-prompt-semantic-compiler-512.png"
  "src/constraint_normalizer.py"
  "src/compiler_defaults.py"
  "src/resource_paths.py"
  "src/rop_template.py"
  "src/semantic_ir.py"
  "src/npsc_service.py"
  "src/npsc_gui/main.py"
  "src/npsc_gui/main_window.py"
  "src/npsc_gui/controller.py"
  "src/npsc_gui/theme.py"
  "src/npsc_gui/tooltips.py"
  "src/npsc_gui/glossary.py"
  "src/npsc_resources/configs/ui_glossary_es.json"
  "app/main.py"
  "app/storage.py"
  "app/ui_helpers.py"
  "src/npsc_cli.py"
  "src/compilation_profiles.py"
  "src/profile_selector.py"
  "src/hybrid_output.py"
  "src/semantic_extractor.py"
  "src/semantic_dictionary.py"
  "src/semantic_seed_mapper.py"
  "src/nsl_compiler.py"
  "src/nsl_parser.py"
  "src/prompt_reconstructor.py"
  "src/context_loss_verifier.py"
  "src/token_estimator.py"
  "src/model_adapter.py"
  "src/exporters.py"
  "src/report_builder.py"
  "src/benchmark_quality.py"
  "src/utils.py"
  "tools/benchmark_quality.sh"
  "tools/capture_gui_screenshots.py"
  "tools/generate_glossary_docs.py"
  "tools/launch_gui.sh"
  "run_gui.sh"
  "verify_app.sh"
  "packaging/desktop/neuro-prompt-semantic-compiler.desktop"
  "packaging/appstream/io.github.npsc.NeuroPromptSemanticCompiler.metainfo.xml"
  "docs/CLI.md"
  "docs/GUIA_RAPIDA_ES.md"
  "docs/GLOSARIO_ES.md"
  "docs/UI_LANGUAGE_AND_GLOSSARY_AUDIT_ES.md"
  "docs/ARQUITECTURA.md"
  "docs/REFINEMENT_BASELINE_REPORT.md"
  "docs/MANUAL_VISUAL_QA_CHECKLIST_ES.md"
  "LICENSE"
)

for f in "${required_files[@]}"; do
  [[ -f "$f" ]] || { echo "Falta archivo requerido: $f"; exit 1; }
done

echo "[verify] archivos requeridos: OK"

PYTHON_BIN="python3"
if [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

"$PYTHON_BIN" -m py_compile app/main.py app/storage.py app/ui_helpers.py src/compiler_defaults.py src/resource_paths.py src/compilation_profiles.py src/profile_selector.py src/hybrid_output.py src/npsc_service.py src/rop_template.py src/semantic_ir.py src/npsc_gui/main.py src/npsc_gui/main_window.py src/npsc_gui/glossary.py
echo "[verify] py_compile perfiles/gui: OK"

PYTHONPATH="$ROOT/src" "$PYTHON_BIN" tools/generate_glossary_docs.py >/dev/null
echo "[verify] glosario generado: OK"

QT_QPA_PLATFORM=offscreen PYTHONPATH="$ROOT/src" "$PYTHON_BIN" - <<'PY'
from PySide6.QtWidgets import QApplication
from npsc_gui.main_window import MainWindow
app = QApplication([])
window = MainWindow()
window.close()
app.quit()
print("[verify] qt smoke: OK")
PY

PYTHONPATH="$ROOT/src" "$PYTHON_BIN" -m unittest discover -s tests -v

echo "[verify] tests: OK"

bash tools/run_demo.sh
bash tools/benchmark_quality.sh

artifacts=(
  "outputs/demo/prompt_original.txt"
  "outputs/demo/semantic_analysis.json"
  "outputs/demo/semantic_seeds.json"
  "outputs/demo/profile_report.json"
  "outputs/demo/profile_selection_report.json"
  "outputs/demo/semantic_ir.json"
  "outputs/demo/compiled_safe.nsl"
  "outputs/demo/compiled_balanced.nsl"
  "outputs/demo/compiled_aggressive.nsl"
  "outputs/demo/chosen_compilation.nsl"
  "outputs/demo/compact_nsl.nsl"
  "outputs/demo/execution_prompt.txt"
  "outputs/demo/audit_bundle.md"
  "outputs/demo/audit_bundle.json"
  "outputs/demo/optimized_prompt.txt"
  "outputs/demo/reconstructed_prompt.txt"
  "outputs/demo/context_loss_report.md"
  "outputs/demo/context_loss_report.json"
  "outputs/demo/hybrid_semantic_prompt.md"
  "outputs/demo/hybrid_semantic_prompt.json"
  "outputs/demo/canonical_nsl.nsl"
  "outputs/demo/token_estimate_report.md"
  "outputs/demo/run_summary.md"
)
for f in "${artifacts[@]}"; do
  [[ -f "$f" ]] || { echo "Falta artefacto de demo: $f"; exit 1; }
done

echo "[verify] artefactos demo: OK"

[[ -f "outputs/benchmark/quality_benchmark.json" ]] || { echo "Falta benchmark JSON"; exit 1; }
[[ -f "outputs/benchmark/quality_benchmark.md" ]] || { echo "Falta benchmark MD"; exit 1; }

echo "[verify] benchmark: OK"
echo "PASS"
