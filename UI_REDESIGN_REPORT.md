# UI Redesign Report — Modo sencillo / Modo extremo

## Framework

PySide6 (Qt 6.x) desktop, KDE-compatible.

## Entry point

`src/npsc_gui/main.py` → `MainWindow` in `src/npsc_gui/main_window.py`

## Architecture

Top-level `QStackedWidget` (`mode_stack`):
- Index 0: Modo sencillo (home + result sub-stack)
- Index 1: Modo extremo (sidebar + 7 pages + 10 result tabs)

## Sincronización bidireccional de prompt

Implementada en dos métodos:
- `_on_simple_prompt_changed()` → escribe en `prompt_edit` con `blockSignals(True)`
- `_on_extreme_prompt_changed()` → escribe en `simple_prompt_edit` con `blockSignals(True)`, solo cuando `_current_mode == MODE_EXTREME`

**No hay loop infinito** porque cada handler bloquea las señales del otro `QPlainTextEdit` antes de escribir.

`load_example()`, `load_file()`, `paste_prompt()` → escriben en el `prompt_edit` del modo actual → el `textChanged` handler correspondiente sincroniza al otro.

## Bugs corregidos (Critic review)

| # | Bug | Fix |
|---|-----|-----|
| 1 | `prompt_edit` changes not synced to `simple_prompt_edit` | Added `_on_extreme_prompt_changed()` connected to `prompt_edit.textChanged` |
| 2 | Prompt text loss when clearing in extreme mode | Sync only overwrites if texts differ |
| 3 | `simple_stack` not reset by `new_prompt()` from extreme | `new_prompt()` now always resets both modes |
| 4 | No cancel in simple mode | Added `simple_cancel_btn` (hidden by default) |
| 5 | `_sync_simple_combos_to_extreme_on_change` missing | Added lightweight combo sync during typing |

## Tests

41/41 passing. No new pytest tests for mode-switching edge cases (recommended future work).

## Known limitations

- Visual inspection not performed (offscreen QPA)
- No dedicated simple-mode history view
- Inline styles (status_dot, tab_active) don't update with theme switching
- Tests don't cover mode-switching edge cases yet
