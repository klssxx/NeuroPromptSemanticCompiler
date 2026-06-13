# Final Competition Report

Fecha: 2026-06-02
Versión: 1.0.0rc2

## Resumen

La aplicación queda como release candidate local para Ubuntu/Kubuntu. El core sigue desacoplado de Qt, la GUI canónica es PySide6/Qt Widgets, el modo sencillo prioriza `Prompt listo para usar` y el modo avanzado conserva NSL compacto, JSON para programas, reglas semánticas, restricciones con origen y métricas.

## Correcciones principales

- `hash_only`: el servicio ya no devuelve el prompt original en `result["original"]` ni en JSON/Markdown/NSL/reportes públicos.
- FAST: NSL agresivo usa forma escasa y hasta tres seeds; para prompts mínimos se reporta overhead de esquema si el NSL expande.
- Métricas: añadidos `original_token_estimate`, `nsl_token_estimate`, `execution_prompt_token_estimate`, `nsl_size_ratio`, `execution_size_ratio`, `nsl_token_change_percent`, `execution_token_change_percent`.
- GUI: el botón principal se llama `Mejorar prompt`; `Copiar prompt listo` copia `execution_prompt.txt`, no el audit bundle.
- UX de vocabulario: añadida página **Glosario** antes de **Acerca de**, con 71 términos buscables por alias, descripción y texto sin acentos.
- Lenguaje visible: `Guardar resultados`, `Informe completo`, `JSON para programas`, `Reglas semánticas` y `Restricciones y origen` sustituyen jerga innecesaria sin cambiar valores internos.
- Modelo destino `auto`: se resuelve en servicio y cae a `codex` si no hay señal fiable.
- Release: tarball limpio, wheel probado fuera del repo, `.deb` construido con `dpkg-deb` e inspeccionado sin instalar.
- Instalador local: `tools/install_local_user.sh` y `tools/uninstall_local_user.sh` probados con HOME temporal.

## Evidencias

- `PYTHONPATH=src .venv/bin/python -m compileall -q src app tests`: pasa.
- `QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v`: 41 tests OK.
- `./verify_app.sh`: pasa.
- `bash tools/verify_project.sh`: pasa.
- `bash tools/benchmark_quality.sh`: pasa.
- `QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python tools/capture_gui_screenshots.py`: pasa.
- `bash tools/build_release.sh`: pasa y genera tarball, wheel, `.deb`, `SHA256SUMS` y manifiesto.
- `desktop-file-validate packaging/desktop/neuro-prompt-semantic-compiler.desktop`: pasa.
- `appstreamcli validate --no-net packaging/appstream/io.github.npsc.NeuroPromptSemanticCompiler.metainfo.xml`: pasa.
- Capturas offscreen: `artifacts/gui_qa/*.png`, todas no vacías.
- Capturas UX/glosario: `glossary_empty.png`, búsquedas de artefacto/NSL/hash_only, ayuda reestructurada y etiquetas simples/avanzadas.
- `python3 -m pytest -q`: omitido por entorno; `pytest` no está instalado.
- Instalador local probado con HOME temporal: pasa.
- Wheel instalado y ejecutado fuera del repo en `/tmp`: pasa.
- Prueba `hash_only` con secreto en `/tmp`: sin fuga detectada por grep.
- Strict CLI: devuelve exit code `2` ante bloqueo real.

## Artefactos

- `dist/neuro-prompt-semantic-compiler-1.0.0rc2.tar.gz`
- `dist/neuroprompt_semantic_compiler-1.0.0rc2-py3-none-any.whl`
- `dist/neuroprompt-semantic-compiler_1.0.0rc2_all.deb`
- `artifacts/gui_qa/neuro-prompt-semantic-compiler-gui-qa-1.0.0rc2.tar.gz`

## Limitaciones

- `.venv` no contiene `pytest` ni `setuptools`; `unittest` cubre la suite principal y el wheel se construye con `setuptools` local del sistema vía `PYTHONPATH=/usr/lib/python3/dist-packages`, sin instalar nada.
- La GUI se validó en offscreen; antes de marcar `1.0.0` conviene revisión visual manual con DISPLAY real.
- AppStream usa una homepage prevista para validar metadata. Debe sustituirse por la URL real al publicar.
- El `.deb` se construyó e inspeccionó, pero no se instaló porque requeriría permisos de sistema.

## Puertas esenciales

- Core funcional: sí.
- GUI Qt offscreen: sí.
- Modo sencillo: sí.
- Modo avanzado: sí.
- Botón principal copia `execution_prompt.txt`: sí.
- AUTO razonable en golden tests: sí.
- Sin contaminación de tareas internas: sí.
- `hash_only` sin persistencia pública del original: sí.
- Métricas honestas de expansión/reducción: sí.
- Strict compartido CLI/GUI/service: sí.
- Seeds válidas >=150: sí, 158.
- Tarball limpio: sí.
- Wheel fuera del repo: sí.
- Glosario incluido en tarball, wheel y `.deb`: sí.
- Instalador local sin sudo: sí.
- `.desktop` y AppStream: sí.
