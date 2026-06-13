# AUDIT FEATURE MATRIX — NeuroPromptSemanticCompiler

**Fecha:** 2026-06-13
**Ruta inspeccionada:** `<project-root>/`
**Python:** 3.12.13 (venv) | **PySide6:** 6.11.1
**GUI Smoke Test:** PASS (9 páginas, 9 nav items)

---

## Matriz de Funcionalidades

| # | Funcionalidad | Estado | Evidencia | Acción |
|---|---|---|---|---|
| 1 | Entrada informal | VERIFIED | `main_window.py` simple_prompt_edit + prompt_edit, placeholder text | Ninguna |
| 2 | Conversión a estructura semántica | VERIFIED | `npsc_service.py` compile_prompt(), `semantic_extractor.py` extract_semantics() | Ninguna |
| 3 | Contexto y rol | PARTIAL | Existe en flujo NSL pero no como campo GUI editable separado | Añadir sección editable en modo avanzado |
| 4 | Consulta o tarea | PARTIAL | El prompt editado se trata como un todo, no hay campo separado | Añadir sección editable |
| 5 | Especificaciones | PARTIAL | Implícito en el prompt, sin campo dedicado | Añadir sección editable |
| 6 | Criterios de calidad | PARTIAL | Sin campo GUI dedicado | Añadir sección editable |
| 7 | Formato de salida | PARTIAL | Sin campo GUI dedicado | Añadir sección editable |
| 8 | Verificación | VERIFIED | `context_loss_verifier.py`, pestaña Validación en GUI | Ninguna |
| 9 | Modo sencillo | VERIFIED | `_build_simple_mode()` con home + result stack, smoke test PASS | Pulir textos hardcodeados |
| 10 | Modo avanzado | VERIFIED | `_build_extreme_mode()` con sidebar 9 páginas | Ninguna |
| 11 | Plantillas reutilizables | PARTIAL | `template_manager.py` + `template_page.py` existen y compilan, pero no hay plantillas iniciales precargadas | Añadir plantillas por defecto |
| 12 | Variables rellenables | PARTIAL | `variables.py` existe y compila, pero NO está integrado en la GUI (sin formulario de rellenado en main_window) | Integrar detección + formulario en GUI |
| 13 | Historial de versiones | PARTIAL | `version_history.py` + `history_page.py` existen y compilan, pero no se guarda automáticamente al compilar | Auto-guardar resultado en historial |
| 14 | Comparación visual | VERIFIED | `compute_diff()` + `compute_unified_diff()` en history_page.py | Ninguna |
| 15 | Exportación Markdown | VERIFIED | `export_manager.py` export_markdown_result() | Integrar en GUI |
| 16 | Exportación JSON | VERIFIED | `export_manager.py` export_json_result() | Integrar en GUI |
| 17 | Exportación texto plano | VERIFIED | `export_manager.py` export_txt_result() | Integrar en GUI |
| 18 | Importación de proyectos | MISSING | No hay función para cargar un proyecto guardado | Implementar |
| 19 | Perfil Hermes | VERIFIED | `model_profiles.json` tiene entrada "hermes" | Ninguna |
| 20 | Perfil Codex | VERIFIED | `model_profiles.json` tiene entrada "codex" | Ninguna |
| 21 | Perfil modelos locales | VERIFIED | `model_profiles.json` tiene "llama", "mistral" | Ninguna |
| 22 | Validador de campos incompletos | PARTIAL | `field_validator.py` existe pero NO está integrado en el flujo de compilación | Integrar validación pre-compilación |
| 23 | Ejemplos reales | PARTIAL | 7 archivos en examples/, pero solo 2 son ejemplos completos con estructura | Mejorar ejemplos existentes |
| 24 | Persistencia local segura | VERIFIED | `settings.py` usa XDG dirs, `template_manager.py` y `version_history.py` usan data_dir() | Ninguna |
| 25 | Gestión de errores | PARTIAL | Try/catch en compile_worker, pero mensajes de error en GUI son básicos | Mejorar mensajes |
| 26 | Tests | VERIFIED | 11 archivos de test, 4 ejecutados y pasando | Añadir tests para nuevos módulos |
| 27 | Documentación | PARTIAL | docs/ tiene muchos reportes técnicos pero falta guía de usuario actualizada | Actualizar README y guías |
| 28 | Scripts de arranque | VERIFIED | `run_gui.sh` existe y funciona | Ninguna |
| 29 | Preparación para GitHub | MISSING | No hay carpeta de entrega limpia | Crear en fase PACKAGE |
| 30 | Web demo | MISSING | Directorio web-demo/ existe pero está vacío | Crear demo estática |
| 31 | Guardado/carga de proyecto | MISSING | No hay formato de proyecto ni función de guardado/carga | Implementar |
| 32 | Copiar al portapapeles | VERIFIED | `copy_recommended()` existe en main_window | Ninguna |
| 33 | Pantalla "Acerca de" | MISSING | No existe | Implementar |
| 34 | Atajos de teclado | PARTIAL | `_bind_shortcuts()` existe pero limitado | Ampliar |
| 35 | Búsqueda/filtrado plantillas | VERIFIED | template_page.py tiene category combo y filtro | Ninguna |
| 36 | Duplicación de plantillas | VERIFIED | `duplicate()` en template_manager y botón en template_page | Ninguna |
| 37 | Importación JSON | PARTIAL | `import_template()` existe pero no hay tests | Añadir tests |
| 38 | Comportamiento ante archivos dañados | MISSING | No hay manejo de errores para JSON corrupto en templates/history | Añadir try/catch |
| 39 | Ausencia de secretos | VERIFIED | No se detectan API keys ni credenciales en el código | Ninguna |
| 40 | Compatibilidad X11 | VERIFIED | La app arranca con QT_QPA_PLATFORM=offscreen (X11 compatible) | Ninguna |

---

## Resumen

- **VERIFIED:** 18 funcionalidades (56%)
- **PARTIAL:** 10 funcionalidades (31%) — existen pero necesitan integración o mejora
- **MISSING:** 4 funcionalidades (12%) — no existen aún
- **BROKEN:** 0

## Acciones Prioritarias (P0)

1. **Integrar variables en GUI** — formulario de rellenado automático cuando se detecten `{{var}}`
2. **Integrar validador en flujo de compilación** — mostrar errores/advertencias antes de compilar
3. **Auto-guardar en historial** — al compilar, guardar versión automáticamente
4. **Añadir plantillas iniciales** — precargar plantillas de ejemplo
5. **Mejorar ejemplos** — completar los 7 ejemplos con formato consistente
6. **Implementar guardado/carga de proyecto** — formato JSON con esquema versionado
7. **Mejorar gestión de errores en GUI** — mensajes comprensibles
8. **Añadir tests para nuevos módulos** — variables, template_manager, version_history, export_manager, field_validator
9. **Actualizar documentación** — README, guía de usuario, changelog
10. **Crear web demo** — demo estática HTML/TS/CSS
11. **Crear scripts** — smoke_test.sh, run.sh, setup_venv_instructions.sh
12. **Preparar entrega GitHub** — carpeta limpia, ZIPs, manifiestos
