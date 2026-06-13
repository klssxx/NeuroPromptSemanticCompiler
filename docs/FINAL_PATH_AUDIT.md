# FINAL PATH AUDIT — NeuroPromptSemanticCompiler

**Fecha:** 2026-06-13
**Verificacion:** Las rutas locales originales fueron redacted para publicacion; el repositorio no debe depender de rutas absolutas del mantenedor.

## Rutas inspeccionadas

| Ruta absoluta | Inode | Tipo | Contenido |
|---|---|---|---|
| `<project-root>/` | n/a | directorio fuente | Repositorio principal con `.git/` |
| `<project-root-alias>/` | n/a | alias local opcional | Misma carpeta en el entorno original de desarrollo |

## Conclusion

En el entorno original de desarrollo no existian duplicados reales: las rutas locales inspeccionadas apuntaban al mismo directorio. Para publicacion, este documento usa placeholders y evita depender de rutas absolutas del mantenedor.
El escritorio de KDE plasma puede exponer aliases locales como `$HOME/Escritorio`; esos aliases no son requisitos del proyecto.

## Version definitiva

**Ruta canonica:** `<project-root>/`

- Ultimo commit: `79d6261 feat: initial commit — NeuroPrompt Semantic Compiler v1.0.0`
- 16 archivos de test en `tests/`
- 93 tests verificados (43 originales + 50 nuevos)
- `.venv/` presente con Python 3.12 y PySide6 6.11.1
- Branch: `main`

## Entregas Ubicacion

**Ruta canonica de entregas:** `<deliveries-root>/`
(ubicacion local de entregas del mantenedor; no requerida para ejecutar el proyecto)

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
