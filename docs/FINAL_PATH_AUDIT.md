# FINAL PATH AUDIT — NeuroPromptSemanticCompiler

**Fecha:** 2026-06-13
**Inode verificacion:** Ambas rutas son la MISMA carpeta (bind mount / hardlink a mismo inode)

## Rutas inspeccionadas

| Ruta absoluta | Inode | Tipo | Contenido |
|---|---|---|---|
| `/home/klsx/NEUROapp/NeuroPromptSemanticCompiler/` | 23072695 | directorio (real) | Repositorio principal con `.git/` |
| `/home/klsx/Escritorio/klsx/NEUROapp/NeuroPromptSemanticCompiler/` | 23072695 | mismo directorio | Mismo inode — es la misma carpeta |

## Conclusion

No existen duplicados. Las dos rutas apuntan al **mismo directorio** mediante el mismo inode.
El escritorio de KDE plasma típicamente monta `$HOME/Escritorio` como referencia a `$HOME`.

## Version definitiva

**Ruta canonica:** `/home/klsx/NEUROapp/NeuroPromptSemanticCompiler/`

- Ultimo commit: `79d6261 feat: initial commit — NeuroPrompt Semantic Compiler v1.0.0`
- 16 archivos de test en `tests/`
- 93 tests verificados (43 originales + 50 nuevos)
- `.venv/` presente con Python 3.12 y PySide6 6.11.1
- Branch: `main`

## Entregas Ubicacion

**Ruta canonica de entregas:** `/home/klsx/NEUROapp/DELIVERIES/`
(inode 25040548 — unico, no duplicado)

## Motivo de seleccion

Unica version existente. Commit `79d6261` es el mas reciente y contiene todas las
integraciones P0 (variables, validador, historial, plantillas, exportacion).

## Archivos que requieren atencion antes de publicar

- `outputs/` — contiene 69 subdirectorios con resultados de pruebas personales
- `dist/` — contiene releases anteriores y builds intermedios
- `staging/` — contiene builds debian/pip cache intermedios
- `tools/` — scripts internos del agente
- `artifacts/` — screenshots baseline y QA
- `configs/` — datos semanticos del proyecto
- `_backups/` — copias de seguridad internas
- `LICENSE_DECISION_REQUIRED.md` — debe reemplazarse por LICENSE final
