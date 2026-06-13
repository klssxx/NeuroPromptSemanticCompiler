# NeuroPrompt Semantic Compiler

> Desktop tool that transforms informal AI requests into structured, reusable, versioned and exportable prompt specifications.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PySide6 6.11+](https://img.shields.io/badge/PySide6-6.11+-green.svg)](https://www.qt.io/qt-for-python)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-110%20passed-brightgreen.svg)](#tests)

NeuroPrompt Semantic Compiler (NPSC) is a lightweight, **100% local** desktop application that converts rough, informal AI requests into clean, structured, versioned and exportable prompt specifications. It works offline, sends nothing to the internet, and never asks for API keys.

---

## The problem

Prompting well is hard. Most prompts are written in a hurry, mix several intentions, miss constraints, and become impossible to reuse, compare, or hand over to a teammate. NPSC solves that with a small, opinionated pipeline:

```text
Informal request
   → structured specification
   → field validation
   → model profile
   → versioned, exportable prompt
```

---

## Features

- **Simple mode** — Write a short request, get a structured prompt with one click.
- **Advanced mode** — Edit the six prompt sections individually (context/role, query/task, specifications, quality criteria, output format, verification) and save/load them as `.nsect.json` files.
- **Reusable templates** — Create, edit, duplicate, search and tag prompt templates.
- **Fillable variables** — Use `{{variable}}` placeholders and fill them before compiling.
- **Version history** — Every compilation is stored locally; compare any two versions with a visual diff.
- **Triple export** — Markdown, JSON (stable schema) and plain text.
- **Model profiles** — `AUTO`, `FAST`, `STANDARD`, `ADVANCED`, `ROP`, `RESEARCH_MAX`; targets for Hermes, Codex, Claude, GPT, Gemini, Qwen, DeepSeek, Llama, Mistral, generic.
- **Field validator** — Detects empty fields, unfilled variables, and overly short prompts before compilation.
- **Project save/load** — Persist full sessions as JSON.
- **Bilingual UI** — Spanish and English.
- **Dark / light theme** — Optimised for KDE Plasma on X11.
- **Static web demo** — See [`web-demo/`](web-demo/) for a no‑install preview of the core flow.

---

## Installation

### Requirements

- Python 3.10 or newer
- PySide6 6.11 or newer

### Option A — with `uv` (recommended)

```bash
git clone https://github.com/klssxx/NeuroPromptSemanticCompiler.git
cd NeuroPromptSemanticCompiler
uv venv .venv
uv pip install -r requirements.txt
./scripts/run.sh
```

### Option B — with a standard venv

```bash
git clone https://github.com/klssxx/NeuroPromptSemanticCompiler.git
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

---

## Usage

1. Write your informal request in the main editor.
2. Pick a profile (default `AUTO`) and a target model.
3. Click **COMPILAR PROMPT** (or press `Ctrl+Enter`).
4. Copy the result, or export it as Markdown, JSON, or TXT.

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Compile prompt |
| `Ctrl+Shift+C` | Copy compiled prompt |
| `Ctrl+N` / `Ctrl+L` | New prompt |
| `Ctrl+O` | Open a text file |
| `Ctrl+S` | Save results |
| `Ctrl+G` | Save project |
| `Ctrl+Shift+O` | Open project |
| `Ctrl+Shift+V` | Fill variables |
| `Ctrl+M` | Toggle simple / advanced mode |
| `F1` | Open glossary / help |

### Web demo (no install required)

Open [`web-demo/index.html`](web-demo/index.html) directly in a browser, or visit the published GitHub Pages demo: https://klssxx.github.io/NeuroPromptSemanticCompiler/

---

## Project structure

```text
NeuroPromptSemanticCompiler/
├── src/
│   ├── npsc_gui/              # PySide6 GUI layer
│   │   ├── main_window.py     # Main window, modes, integration
│   │   ├── advanced_mode_page.py
│   │   ├── about_dialog.py
│   │   ├── export_preview.py
│   │   ├── integration.py
│   │   ├── template_page.py
│   │   ├── tooltips.py
│   │   └── ...
│   ├── variables.py           # {{variable}} detection and filling
│   ├── template_manager.py    # CRUD over reusable templates
│   ├── version_history.py     # Snapshots + visual diff
│   ├── export_manager.py      # Markdown / JSON / TXT exporters
│   ├── field_validator.py     # Compile form validation
│   ├── npsc_service.py        # Compilation service entry point
│   ├── nsl_compiler.py        # NSL prompt compiler
│   ├── semantic_extractor.py  # Lightweight semantic extraction
│   ├── token_estimator.py     # tiktoken-based token counting
│   └── ...
├── tests/                     # 110 tests passing (pytest)
├── examples/                  # Example informal requests
├── web-demo/                  # Static HTML demo
├── docs/                      # Additional documentation
├── scripts/
│   ├── run.sh                 # Launch the desktop app
│   ├── smoke_test.sh          # Quick end-to-end verification
│   └── setup_venv_instructions.sh
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Tests

```bash
# All tests (no GUI display required when running headless)
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -q

# Or via the bundled smoke test
./scripts/smoke_test.sh
```

Current status: **110 tests passing** (non-GUI suite). GUI widget tests are run manually on a developer machine with a display.

---

## Export formats

### Markdown

A structured document with sections, metadata, the compiled prompt, the NSL representation, and the validation report.

### JSON

```json
{
  "$schema": "neuroprompt/compilation-result/v1",
  "generator": "NeuroPrompt Semantic Compiler",
  "exported_at": "2026-06-13T...",
  "result": { /* stable, versioned result object */ }
}
```

### TXT

Just the compiled prompt, ready to copy and paste.

---

## Model profiles

| Profile | Style | Recommended for |
|---|---|---|
| `AUTO` | Auto-detection | Let the app decide |
| `FAST` | Compact | Simple, low-latency tasks |
| `STANDARD` | Balanced | General use |
| `ADVANCED` | Operational, file-oriented | Programming, architecture |
| `ROP` | Phases, scenarios, evidence | Complex decisions |
| `RESEARCH_MAX` | Maximum preservation | Deep research |

---

## Privacy

- **No** internet connection
- **No** telemetry
- **No** API keys
- **No** access to files outside the app data directory
- All data stored locally under `~/.local/share/neuro-prompt-semantic-compiler/`

A dedicated privacy audit is available at [`docs/PUBLICATION_PRIVACY_AUDIT.md`](docs/PUBLICATION_PRIVACY_AUDIT.md).

---

## Roadmap

- [ ] Bundled Linux installer (AppImage / Flatpak)
- [ ] More visual themes
- [ ] Additional language packs
- [ ] Export plugins
- [ ] Cloud-less optional collaborative templates (offline exchange format)
- [ ] Inline screenshots and a richer web demo (TypeScript build)

See [`docs/FINAL_PATH_AUDIT.md`](docs/FINAL_PATH_AUDIT.md) for the project's packaging decisions.

---

## Screenshots

*Real application screenshots will be added in a future update. In the meantime, the [static web demo](web-demo/) gives a quick visual preview of the core flow.*

---

## Contributing

Pull requests are welcome. Please:

1. Fork the repository.
2. Create a feature branch.
3. Make sure `pytest` and `scripts/smoke_test.sh` pass.
4. Open a pull request.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

---

## License

This project is released under the **MIT License**. See [`LICENSE`](LICENSE) for the full text.

---

## Language

This README is also available in Spanish: [`README.es.md`](README.es.md).
