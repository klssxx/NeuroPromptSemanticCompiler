# Refinement Baseline Report

Fecha: 2026-06-02
Ruta: /home/klsx/NeuroPromptSemanticCompiler
Backup: backups/refinement_20260602_113203

## Baseline solicitado

- `PYTHONPATH=src .venv/bin/python -m compileall -q src app tests`: OK.
- `QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v`: OK, 23 tests.
- `QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m pytest tests -q`: NO EJECUTABLE; `.venv` no contiene pytest (`No module named pytest`). No se instala por restricción del usuario.

## Defectos de auditoría a corregir

1. Mezcla entre intención de usuario y pipeline interno NPSC.
2. FAST y execution prompt inflan casos simples.
3. Score de preservación autorreferencial sin precisión ni adiciones no soportadas.
4. `preserve_original=False` no elimina el prompt original de JSON/Markdown/IR.
5. `strict` no se aplica desde servicio compartido.
6. Seeds de política mezcladas con restricciones de usuario.
7. Diccionario de seeds por debajo de 150.
8. `pytest -q` raíz debe ignorar backups/outputs/dist/staging/egg-info/cachés.
9. Tarball debe excluir artefactos históricos y no incluirse a sí mismo.
10. Wheel instalado fuera del repo debe encontrar configs/assets.
11. `.desktop` instalable debe usar `npsc-gui`.
12. Cancelación Qt debe usar worker real.
13. Adaptadores target y modelo custom deben mejorar trazabilidad.
14. README debe reflejar strict real desde config.
15. QA visual reproducible pendiente.
