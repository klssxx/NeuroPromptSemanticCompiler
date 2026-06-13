# CHANGELOG — NeuroPrompt Semantic Compiler

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-06-13

First public, portfolio-ready release of NeuroPrompt Semantic Compiler.

### Added

- **Variables system `{{name}}`** — auto-detection, fill dialog (`Ctrl+Shift+V`), safe substitution before compilation.
- **Reusable templates page** — full CRUD (create, edit, duplicate, delete, import, export) with categories, tags and search.
- **Persistent version history** — every successful compilation is auto-saved; visual diff between any two versions.
- **Triple export** — Markdown (structured document), JSON (stable schema `neuroprompt/compilation-result/v1`), TXT (prompt only).
- **Field validator** — detects empty fields, unfilled variables, very short prompts; distinguishes errors from warnings.
- **Project save / load** — `.npsc.json` format with a versioned schema.
- **Simple and advanced modes** — advanced mode exposes 6 editable sections (context/role, query/task, specifications, quality criteria, output format, verification) that can be saved/loaded as `.nsect.json`.
- **About dialog** — version, license, privacy notes, limitations, GitHub link.
- **Export preview dialog** — Markdown, JSON, and text tabs with copy-to-clipboard and export-to-file.
- **Keyboard shortcuts** — `Ctrl+Enter` (compile), `Ctrl+Shift+C` (copy), `Ctrl+N/L` (new), `Ctrl+O` (open), `Ctrl+S` (save), `Ctrl+G` (save project), `Ctrl+Shift+O` (load project), `Ctrl+Shift+V` (variables), `Ctrl+M` (toggle mode), `F1` (help).
- **Static web demo** — see [`web-demo/`](web-demo/) for a no-install preview of the core flow.
- **Bilingual UI** — Spanish and English; launcher key labels and CLI fully translated.
- **Scripts** — `scripts/run.sh`, `scripts/smoke_test.sh`, `scripts/setup_venv_instructions.sh`.
- **Documentation** — `README.md` and `README.es.md`, `docs/FINAL_PATH_AUDIT.md`, `docs/PUBLICATION_PRIVACY_AUDIT.md`.

### Improved

- **GUI** — nine pages in advanced mode (including Templates and History).
- **Pre-compile validation** — the form is validated before sending the request to the compilation worker.
- **Error messages** — friendlier Spanish copy across the application.
- **i18n** — ~80 new translation keys for templates, history, validation, advanced mode and about dialog.
- **Theme** — optimised for KDE Plasma on X11; light and dark variants.

### Tests

- **103 tests passing** (non-GUI pytest suite).
- **0 syntax errors** across all `src/` Python files.
- GUI widget tests documented as `MANUAL_REVIEW_REQUIRED` (require `pytest-qt` and a real display).

### Technical

- Python 3.10+ and PySide6 6.11+.
- Compatible with KDE Plasma on X11; works on legacy NVIDIA Kepler GPUs.
- No third-party dependencies beyond PySide6 and `tiktoken` (optional, for token estimation).
- 100% local, no telemetry, no API keys, no internet access.
