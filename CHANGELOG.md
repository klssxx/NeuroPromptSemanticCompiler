# CHANGELOG.md — NeuroPrompt Semantic Compiler

## [1.0.0] — 2026-06-13

### Añadido
- **Sistema de variables `{{nombre}}`**: Detección automática, formulario de rellenado, sustitución segura antes de compilar
- **Página de plantillas reutilizables**: CRUD completo (crear, editar, duplicar, eliminar, importar, exportar) con categorías
- **Historial de versiones persistente**: Cada compilación se guarda automáticamente; comparación visual con diff unificado
- **Exportación mejorada**: Markdown (documento estructurado), JSON (esquema estable `neuroprompt/compilation-result/v1`), TXT (solo prompt)
- **Validador de campos**: Detecta variables sin rellenar, prompts vacíos, campos muy cortos; distingue errores de advertencias
- **Guardado/carga de proyectos**: Formato `.npsc.json` con esquema versionado
- **Diálogo de variables**: Ctrl+Shift+V para rellenar variables detectadas
- **Atajos de teclado**: Ctrl+G (guardar proyecto), Ctrl+Shift+O (cargar proyecto), Ctrl+Shift+V (variables)
- **50 tests nuevos**: variables, template_manager, version_history, export_manager, field_validator
- **Scripts**: `run.sh`, `smoke_test.sh`, `setup_venv_instructions.sh`
- **Web demo estática**: Demo visual del flujo de transformación (HTML/CSS/JS)
- **Documentación profesional**: README.md, README.es.md, AUDIT_FEATURE_MATRIX.md, IMPLEMENTATION_PLAN.md

### Mejorado
- **GUI**: 9 páginas en modo avanzado (añadidas Plantillas e Historial)
- **Validación pre-compilación**: El prompt se valida antes de enviar al worker
- **Auto-guardado en historial**: Cada compilación exitosa se guarda automáticamente
- **Mensajes de error**: Más comprensibles en español
- **i18n**: ~80 nuevas traducciones (templates, history, validation)

### Tests
- **93 tests pasando** (43 originales + 50 nuevos)
- 0 errores de sintaxis en todos los archivos Python

### Técnico
- Python 3.12.13 + PySide6 6.11.1
- Compatible con KDE Plasma X11
- Sin dependencias externas más allá de PySide6
- 100% local, sin telemetría
