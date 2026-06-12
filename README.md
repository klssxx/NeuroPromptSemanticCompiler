🌐 **Language:** [English](README.md) · [Español](README.es.md)

# NeuroPrompt Semantic Compiler

NeuroPrompt Semantic Compiler converts messy human prompts into compact, structured, model-readable instructions using NSL v0.1 and NPSC-HYBRID/1.0.

It is not a blind summarizer. It is a semantic compiler for intent: preserving goals, constraints, risks, target model context, and verification metadata while making prompts easier to use with AI systems.

## Core phrase

Not fewer words by losing meaning; more power per token by transmitting structured intention.

## Features

- PySide6 / Qt Widgets desktop GUI with simple and expert modes.
- CLI for reproducible prompt compilation.
- Semantic profiles: `FAST`, `STANDARD`, `ADVANCED`, `ROP`, `RESEARCH_MAX`, `AUTO`.
- Model targets: GPT, Codex, Claude, Gemini, Qwen, DeepSeek, Llama, Mistral, Hermes, generic and custom.
- Privacy modes: `full_original`, `hash_only`, `redacted_preview`.
- Bilingual foundation: Spanish and English console/UI labels for key settings and launcher metadata.
- Local-first: no telemetry, no external API calls, no remote execution.

## Quick start from source

```bash
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements.txt
./run_gui.sh
```

CLI example:

```bash
PYTHONPATH=src .venv/bin/python -m npsc_cli \
  --text "Build a local tool. Do not use sudo. Avoid destructive actions." \
  --out outputs/demo \
  --target codex \
  --profile auto \
  --privacy-mode hash_only \
  --language en
```

Spanish CLI labels:

```bash
PYTHONPATH=src .venv/bin/python -m npsc_cli \
  --text "Crea una herramienta local. No uses sudo." \
  --out outputs/demo-es \
  --target codex \
  --profile auto \
  --language es
```

## Linux compatibility

The project is designed to run on most modern Linux distributions with Python 3.10+ and PySide6/Qt 6:

- Ubuntu, Xubuntu, Kubuntu, Debian and derivatives
- Fedora and derivatives
- Arch, CachyOS, Manjaro and derivatives
- Other XDG-compatible desktops using Qt/GTK launchers

The GUI uses native Qt Widgets, no Electron, no web view, and avoids GPU-heavy effects. It should work on old GPUs as long as the Qt platform plugin is functional.

Detailed distro notes: [docs/LINUX_INSTALL.md](docs/LINUX_INSTALL.md)

## Output files

Each run exports unique artifacts:

- `canonical_nsl.nsl`
- `compiled_safe.nsl`
- `compiled_balanced.nsl`
- `compiled_aggressive.nsl`
- `optimized_prompt.txt`
- `reconstructed_prompt.txt`
- `hybrid_semantic_prompt.md`
- `hybrid_semantic_prompt.json`
- `semantic_ir.json`
- `semantic_analysis.json`
- `semantic_seeds.json`
- `profile_selection_report.json`
- `profile_report.json`
- `context_loss_report.md`
- `context_loss_report.json`
- `token_estimate_report.md`
- `token_estimate_report.json`
- `run_summary.md`

Main files:

- `optimized_prompt.txt`: prompt ready to copy into another model or agent.
- `canonical_nsl.nsl`: canonical compact NSL representation.
- `hybrid_semantic_prompt.*`: full traceability bundle.

## Desktop launcher and icon

The launcher icon is provided as SVG plus rendered PNG sizes in `assets/icons/`.

Desktop metadata lives in:

- `NeuroPromptSemanticCompiler.desktop`
- `packaging/desktop/neuro-prompt-semantic-compiler.desktop`

For user-local installation without sudo:

```bash
bash tools/install_local_user.sh
```

Uninstall:

```bash
bash tools/uninstall_local_user.sh
```

## Validation

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
bash tools/check_runtime.sh
```

Optional project/release checks:

```bash
bash tools/verify_project.sh
bash tools/build_release.sh
```

## Packaging for GitHub/GitLab

Before publishing, exclude generated folders such as `.venv/`, `staging/`, `_backups/`, `outputs/`, `artifacts/`, `dist/`, `build/`, `*.egg-info`, `__pycache__/`, and `.pytest_cache/`.

A clean upload archive can be produced with:

```bash
bash tools/export_source_clean.sh
```

## Limitations

- Token estimation is approximate (`chars / 4`).
- Semantic extraction is heuristic, not ML-based.
- Full GUI text coverage is not yet completely translated; key launcher, settings and CLI language paths are bilingual.
- Final release publication should include a human visual pass in a real desktop session, not only `QT_QPA_PLATFORM=offscreen`.
