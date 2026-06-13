# PROJECT INSPECTION — NeuroPrompt Semantic Compiler

**Date:** 2026-06-09
**MODE:** AUDIT
**PHASE:** GATE_0 (complete, moving to implementation)

## System Facts Verified

| Fact | Value |
|---|---|
| OS | CachyOS Linux |
| Desktop | KDE Plasma |
| Session | X11 (confirmed: Xorg running, Wayland NOT running) |
| Kernel | 7.0.11-1-cachyos |
| CPU | Intel Core i5-4570 @ 3.20GHz (4c/4t, AVX2) |
| RAM | 11 GiB |
| GPU | NVIDIA GeForce GTX 660 Kepler 2GB |
| GPU Driver | 470.256.02 (legacy 470xx branch) |
| Python (project) | 3.12.13 (via uv venv) |
| Python (system) | 3.14.5 (incompatible with PySide6) |
| PySide6 | 6.11.1 |
| Package manager | pacman (CachyOS) |

## Project Facts Verified

| Fact | Value |
|---|---|
| Language | Python 3.10+ |
| Framework UI | PySide6 / Qt Widgets |
| Build system | setuptools + pyproject.toml |
| Theme system | QSS string in theme.py |
| Theme mode | Dark only (before this redesign) |
| Pages/Screens | 10 sidebar pages |
| Assets | SVG icon + PNG 16-512 |
| Tests | 41 unit tests + 14 subtests |
| CLI | Functional (npsc_cli.py) |
| GUI | Functional (npsc_gui/) |
| Desktop integration | .desktop file + install_local_user.sh |

## Current Visual Problems

1. **Dark-only** — no light mode, alienates users who prefer light themes or follow KDE's color scheme
2. **Heavy GPU effects** — multiple qlineargradient stops and rgba alpha in QSS, unnecessary on GTX 660 legacy
3. **Cyberpunk aesthetic** — neon pink (#FF5EB8) gradients on primary button, looks gaming/immature for a professional tool
4. **No focus indicators** — keyboard users have no visual cue for focused widgets (accessibility failure)
5. **Excessive sidebar pages** — 10 pages for a tool with 1 main workflow is over-navigating
6. **No empty/loading/error states** — results tabs just show blank when no data
7. **Hardcoded dark colors** — not following KDE system theme, no automatic palette sync

## Risks

### CachyOS specific
- Python 3.14 incompatible with PySide6 — must use venv with 3.12
- No dpkg-deb — .deb packaging path doesn't exist
- AppStream URL-not-reachable warning expected (repo not published yet)

### KDE Plasma X11 specific
- QSS can conflict with KDE's Breeze style — use simple colors, not complex effects
- Some Qt properties may not polish correctly under some KDE themes

### Hardware (i5-4570 + GTX 660)
- Gradient rendering in QSS adds CPU overhead (no GPU acceleration for Qt stylesheets)
- Alpha compositing (rgba) triggers software blending path
- Must avoid blur, transparency, shadow effects

## What Not To Touch

- Core logic (semantic_extractor, nsl_compiler, etc.)
- Test files
- JSON configs
- CLI interface
- Python APIs / service layer
- Scripts that work (verify_app.sh, install_local_user.sh)
- System configuration (GPU, drivers, kernel, DE)

## Resume Point

GATE_0 complete. Proceeding to implementation (user gave full authorization).
