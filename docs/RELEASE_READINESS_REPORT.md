# Release Readiness Report

## Checklist

- Core funcional: sí.
- CLI compatible: sí.
- GUI Qt conectada al core: sí.
- GUI Qt smoke test offscreen: sí.
- Tooltips en controles relevantes: sí.
- Glosario buscable desde la GUI: sí.
- Glosario situado antes de Acerca de: sí.
- Documentación del glosario generada desde JSON único: sí.
- Modo sencillo/avanzado: sí.
- Acciones de exportación/copiar/abrir carpeta: sí.
- ROP/1.0: sí.
- NPSC-HYBRID/1.0: sí.
- Icono SVG y PNG: sí.
- AppStream preparado: sí.
- Debian metadata mínimo: sí.
- Tests automatizados: sí.
- Paquete `.deb` construido e inspeccionado sin instalar: sí, `dist/neuroprompt-semantic-compiler_1.0.0rc2_all.deb`.
- Tarball de release: sí, `dist/neuro-prompt-semantic-compiler-1.0.0rc2.tar.gz`.
- Tarball limpio auditado: sí, sin `.venv`, `dist`, `backups`, `_backups`, `outputs`, `artifacts`, caches ni self-include.
- Wheel instalado en entorno aislado de `staging/wheel_check`: sí, `dist/neuroprompt_semantic_compiler-1.0.0rc2-py3-none-any.whl`.
- Wheel construido usando `setuptools` disponible vía `PYTHONPATH=/usr/lib/python3/dist-packages` porque `.venv` no contiene `setuptools`.
- Instalador local de usuario probado con HOME temporal: sí.
- Capturas offscreen generadas: sí, `artifacts/gui_qa/`.
- `.desktop` validado: sí.
- AppStream validado: sí.
- `python3 -m pytest -q`: no disponible en el entorno (`No module named pytest`).

## Publicación pendiente

1. Revisar licencia y nombre de organización.
2. Añadir capturas reales.
3. Revisar política Debian definitiva para PySide6 antes de publicar `.deb`.
4. Crear repositorio remoto manualmente y sustituir la homepage provisional de AppStream.

## Comandos de publicación local

```bash
./verify_app.sh
bash tools/verify_project.sh
bash tools/build_release.sh
desktop-file-validate packaging/desktop/neuro-prompt-semantic-compiler.desktop
appstreamcli validate --no-net packaging/appstream/io.github.npsc.NeuroPromptSemanticCompiler.metainfo.xml
```

## Riesgos restantes

- El `.deb` construido con `dpkg-deb` es inspeccionable, pero no se ha instalado ni probado en sistema porque eso requeriría permisos de sistema.
- La URL de homepage de AppStream es una URL de repositorio prevista; debe ajustarse al publicar.
- PySide6 está en `.venv` local y en `requirements.txt`; una instalación desde código fuente debe instalarlo en su entorno.
- La validación interactiva final debe hacerse en una sesión gráfica Ubuntu para comprobar escalado real, foco de teclado y capturas.
