# UI Test Report — Modo sencillo / Modo extremo

## Resumen

| Métrica | Valor |
|---------|-------|
| Tests automatizados | **41/41 passed** (44s) |
| Smoke tests GUI | **19/19 passed** (offscreen) |
| Bugs corregidos post-Critic | 4 |

## Bugs corregidos

1. **Sincronización prompt_edit → simple_prompt_edit**: Añadido `_on_extreme_prompt_changed()`.
2. **Pérdida de texto al borrar en extremo**: Sync solo sobrescribe si los textos difieren.
3. **simple_stack no reseteaba desde extremo**: `new_prompt()` ahora resetea ambos modos.
4. **Sin cancelar en modo simple**: Añadido `simple_cancel_btn`.

## Comandos de verificación

```bash
cd /home/klsx/NEUROapp/NeuroPromptSemanticCompiler
PYTHONPATH=src .venv/bin/python -m pytest tests/ --tb=short
bash run_gui.sh
```
