# Rollback — UI Redesign (Modo sencillo / Modo extremo)

## Backup

`<project-root>/_backups/mode-redesign-20260609-025641/`

## Archivos modificados

- `src/npsc_gui/main_window.py` — Rediseño completo + fixes de sincronización
- `src/npsc_gui/theme.py` — QSS para modo simple
- `src/npsc_gui/settings.py` — Añadido `startup_mode`
- `tests/test_compilation_profiles.py` — Actualizado para `_switch_to_mode()`
- `tests/test_glossary_ux.py` — Actualizado para `_switch_to_mode()`

## Rollback

```bash
B="<project-root>/_backups/mode-redesign-20260609-025641"
P="<project-root>"
cp "$B/src/npsc_gui/main_window.py" "$P/src/npsc_gui/main_window.py"
cp "$B/src/npsc_gui/theme.py" "$P/src/npsc_gui/theme.py"
cp "$B/src/npsc_gui/settings.py" "$P/src/npsc_gui/settings.py"
cp "$B/tests/test_compilation_profiles.py" "$P/tests/test_compilation_profiles.py"
cp "$B/tests/test_glossary_ux.py" "$P/tests/test_glossary_ux.py"
```

## Relaunch

```bash
cd <project-root> && bash run_gui.sh
```
