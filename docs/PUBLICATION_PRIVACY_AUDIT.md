# PUBLICATION PRIVACY AUDIT — NeuroPromptSemanticCompiler

**Fecha:** 2026-06-13
**Auditor:** OWL (Hermes Agent)
**Estado:** COMPLETADO

## Patrones revisados

| Patron | Buscado en | Resultado |
|---|---|---|
| Rutas `/home/klsx/` | `src/**/*.py` | No encontrado |
| Emails personales | `src/**/*.py` | No encontrado |
| API keys / tokens | `src/**/*.py` | No encontrado (solo "token" como termino NLP) |
| Passwords / secrets | `src/**/*.py` | No encontrado |
| Archivos `.env` | Todo el proyecto | No encontrado |
| Credenciales Git | Todo el proyecto | No encontrado |
| Variables de entorno sensibles | `src/**/*.py` | Solo XDG estandar (XDG_CONFIG_HOME, LANG) |
| `klsx` en outputs/ | `outputs/**` | Encontrado — EXCLUIDO de entrega |
| `klsx` en `_backups/` | `_backups/**` | Encontrado — EXCLUIDO de entrega |
| `klsx` en `dist/`, `staging/`, `tools/`, `artifacts/` | Varios | Encontrado — EXCLUIDO de entrega |

## Archivos inspeccionados

- `src/` (todos los .py) — Limpio
- `configs/*.json` — Sin credenciales, solo datos semanticos del proyecto
- `outputs/` — Contiene resultados de pruebas con rutas locales — EXCLUIDO
- `_backups/` — Copias de seguridad con rutas locales — EXCLUIDO
- `dist/` — Builds anteriores — EXCLUIDO
- `staging/` — Artefactos de build — EXCLUIDO
- `tools/` — Scripts internos del agente — EXCLUIDO
- `artifacts/` — Screenshots baseline y QA — EXCLUIDO

## Incidencias encontradas

1. **`outputs/`** — 69 subdirectorios con resultados de pruebas que contienen rutas `/home/klsx/`.
   - **Mitigacion:** Excluido de ambos ZIPs de entrega.

2. **`_backups/`** — 3 copias de seguridad con rutas locales.
   - **Mitigacion:** Excluido de ambos ZIPs de entrega.

3. **`staging/wheel_check/venv/`** — Entorno virtual empaquetado con rutas locales.
   - **Mitigacion:** Excluido de ambos ZIPs de entrega.

4. **`dist/`** — Releases anteriores con manifests que contienen rutas locales.
   - **Mitigacion:** Excluido de ambos ZIPs de entrega.

## Archivos excluidos de la publicacion

```
.venv/
.git/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
outputs/
dist/
staging/
tools/
artifacts/
_backups/
*.pyc
uv.lock
NeuroPromptSemanticCompiler.desktop
run_gui.sh
verify_app.sh
SAFETY.md
ROLLBACK_UI_REDESIGN.md
UI_REDESIGN_REPORT.md
UI_TEST_REPORT.md
TECHNICAL_SPEC.md
PROJECT_VISION.md
DESIGN.md
CODE_OF_CONDUCT.md
LEEME_PRIMERO.md
ROADMAP.md
architecture-diagram.html
configs/
src/npsc_resources/
packaging/
web-demo/
docs/design/
docs/*_REPORT*.md
docs/*_AUDIT*.md (este archivo se incluye)
docs/IMPLEMENTATION_P0_PLAN.md
docs/AUDIT_FEATURE_MATRIX.md
docs/COMPRESSION_LEVELS.md
docs/CONTEXTUAL_HELP_REFINEMENT_REPORT.md
docs/EVALUATION_METHOD.md
docs/FINAL_COMPETITION_*.md
docs/GLOSARIO_ES.md
docs/GUIA_RAPIDA_ES.md
docs/MANUAL_USUARIO_ES.md
docs/MANUAL_VISUAL_QA_CHECKLIST_ES.md
docs/MENTAL_MODEL.md
docs/NSL_SPEC.md
docs/PRE_GLOSSARY_RECOVERY_REPORT.md
docs/PRIVACIDAD.md
docs/REFINEMENT_*.md
docs/RELEASE_READINESS_REPORT.md
docs/SEMANTIC_SEEDS.md
docs/UI_LANGUAGE_AND_GLOSSARY_AUDIT_ES.md
docs/VISUAL_POLISH_PLAN_*.md
docs/ARQUITECTURA.md
docs/DISTRIBUCION_UBUNTU.md
docs/LINUX_INSTALL*.md
```

## Aclaracion: "User profile updated"

El mensaje "Self-improvement review: User profile updated" se refiere a la actualizacion del archivo de perfil de usuario de Hermes Agent (`~/.hermes/profiles/default/user.yaml` o memoria del agente). Este archivo:

- **Ubicacion:** Fuera del directorio del proyecto, en el home del usuario (`~/.hermes/`).
- **Contenido:** Preferencias de idioma, estilo de comunicacion, notas de entorno.
- **Afecta a la aplicacion:** NO. Es configuracion del agente Hermes, no de NPSC.
- **Incluido en ZIP:** NO. Esta fuera del directorio del proyecto.
- **Requiere .gitignore:** NO aplica (ya fuera del repo).

## Resultado final

El codigo fuente del proyecto esta limpio de credenciales, tokens, emails personales y rutas privadas. Los unicos archivos con datos personales son artefactos de desarrollo (outputs, backups, dist, staging) que seran excluidos de la entrega publica.

**VEREDICTO:** SEGURO PARA PUBLICAR (con las exclusiones documentadas).
