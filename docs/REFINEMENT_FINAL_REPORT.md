# Refinement Final Report

Fecha: 2026-06-02

## Backup

- `backups/refinement_20260602_113203`

## Reparaciones principales

- Separada intención del usuario de `compiler_trace`.
- Eliminada contaminación por tareas internas en prompts simples.
- Añadidas capas `USER_INTENT_IR`, `COMPILER_TRACE`, `POLICY_LAYER`, `TARGET_ADAPTER_LAYER` y `EFFECTIVE_PROMPT_IR`.
- Añadidas salidas `compact_nsl.nsl`, `execution_prompt.txt`, `audit_bundle.md` y `audit_bundle.json`.
- FAST ya no infla el caso simple `Corrige la ortografía de este correo.`.
- Añadidas métricas separadas: retención, precisión, adiciones no soportadas, contradicción, trazabilidad, ratios, utilidad y riesgo.
- `hash_only` elimina texto sensible de JSON, Markdown, IR, NSL, execution prompt y reportes exportados.
- `strict` se evalúa desde servicio compartido con `configs/compiler_defaults.json`.
- Seeds ampliadas a 158 y validadas.
- Pytest configurado para ignorar backups, outputs, dist, staging, egg-info y cachés.
- Wheel validado fuera del repo cuando `setuptools` está disponible vía `PYTHONPATH=/usr/lib/python3/dist-packages`.
- Tarball reescrito con staging limpio y exclusiones.
- `.desktop` instalable corregido a `Exec=npsc-gui`.
- GUI Qt usa worker, señales, cancelación cooperativa y estado bloqueado por strict.
- QA visual offscreen generado en `artifacts/gui_qa/`.

## Limitaciones reales

- `.venv` no contiene `pytest`; no se instaló.
- `.venv` no contiene `setuptools`; el comando wheel exacto sin `PYTHONPATH` falla. La validación alternativa con setuptools del sistema en modo solo lectura sí construye e instala el wheel.
- `.deb` no construido: falta `debhelper-compat (= 13)`.
- QA visual humana en sesión con `DISPLAY` sigue pendiente.

## Evidencias clave

- `unittest`: 27 tests OK.
- `privacy_hash_only_ok`: texto sensible no aparece en artefactos exportados.
- `strict_exit=2`: strict bloquea salida por score bajo.
- `service_strict_status blocked`: servicio comparte la misma política.
- `validate_semantic_dictionary`: 158 seeds válidos.
- Wheel instalado fuera del repo ejecutó `npsc` y generó artefactos.
- AppStream validó correctamente.
