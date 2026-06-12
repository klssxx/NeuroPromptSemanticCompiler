# Manual visual QA

## Objetivo

Validar que la GUI Qt es legible, usable y coherente antes de publicar.

## Captura reproducible

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python tools/capture_gui_screenshots.py
```

Las capturas se guardan en:

```text
artifacts/gui_qa/
```

## Capturas esperadas

- `dashboard.png`
- `compiler_simple.png`
- `compiler_advanced.png`
- `results.png`
- `validation.png`
- `constraints_origin.png`
- `custom_model.png`
- `strict_blocked.png`

## Checklist humano pendiente

- Abrir `./run_gui.sh` en sesión Ubuntu con `DISPLAY`.
- Verificar contraste y foco visible.
- Verificar escalado al 100 %, 125 % y 150 % si está disponible.
- Verificar que el modo sencillo no abruma con detalles técnicos.
- Verificar que el modo avanzado muestra NSL, JSON, seeds, métricas y constraints con origen.
- Verificar que `hash_only` no muestra texto sensible en vistas serializadas.
- Verificar que `strict` bloquea visualmente salidas no aprobadas.
- Verificar que el campo de modelo custom aparece solo con target `custom`.

## Limitación

El render offscreen confirma creación de widgets y capturas, pero no sustituye revisión visual humana en escritorio real.
