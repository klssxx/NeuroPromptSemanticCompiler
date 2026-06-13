# IMPLEMENTATION PLAN — NeuroPromptSemanticCompiler

**Fecha:** 2026-06-13
**Basado en:** `docs/AUDIT_FEATURE_MATRIX.md`

---

## P0 — Obligatorio (orden de ejecución)

### 0. Backup de seguridad
- Crear copia de seguridad versionada antes de modificar nada

### 1. Integrar variables en GUI
- Añadir panel de variables detectadas en modo simple y avanzado
- Formulario automático con campos para cada `{{variable}}`
- Previsualización con variables sustituidas
- Indicador visual de variables sin rellenar

### 2. Integrar validador en flujo de compilación
- Llamar `validate_compile_form()` antes de compilar
- Mostrar diálogo de advertencias con opción de continuar
- Bloquear compilación solo en errores críticos (prompt vacío)

### 3. Auto-guardar en historial
- Al completar compilación, guardar versión automáticamente
- Usar las primeras 60 chars del prompt como nombre

### 4. Añadir plantillas iniciales
- Crear 7 plantillas de ejemplo precargadas
- Categorías: Desarrollo, Auditoría, Investigación, Documentación, Corrección, Planificación, README

### 5. Mejorar ejemplos
- Formato consistente para los 7 ejemplos
- Incluir: petición informal, resultado estructurado, perfil, variables

### 6. Implementar guardado/carga de proyecto
- Formato JSON con schema_version
- Diálogo de guardar/abrir en ambas modos
- Persistencia en `data_dir() / "projects"`

### 7. Mejorar gestión de errores en GUI
- Mensajes de error comprensibles en español/inglés
- Diálogo de error con detalles técnicos colapsables

### 8. Tests para nuevos módulos
- `tests/test_variables.py`
- `tests/test_template_manager.py`
- `tests/test_version_history.py`
- `tests/test_export_manager.py`
- `tests/test_field_validator.py`

### 9. Documentación
- Actualizar README.md y README.es.md
- Crear docs/USER_GUIDE.md
- Crear docs/DEVELOPMENT.md
- Actualizar CHANGELOG.md

### 10. Scripts
- `scripts/smoke_test.sh`
- `scripts/run.sh`
- `scripts/setup_venv_instructions.sh`

### 11. Web demo
- Crear demo estática en `web-demo/`
- HTML + CSS + TypeScript
- Mostrar flujo de transformación

### 12. Empaquetado GitHub
- Crear carpeta `DELIVERIES/NeuroPromptSemanticCompiler-github-ready/`
- Crear ZIPs de repositorio y release
- Generar SHA256SUMS.txt y DELIVERY_MANIFEST.md
- Crear LICENSE_DECISION_REQUIRED.md
- Crear docs/GITHUB_PUBLISH_GUIDE.md

---

## P1 — Recomendado (después de P0)

- Duplicación rápida de plantillas (ya existe, verificar)
- Búsqueda y filtrado de plantillas (ya existe, verificar)
- Vista previa antes de exportar
- Metadatos de proyecto (nombre, versión, fecha, tags)
- Importación de JSON exportado
- Pantalla "Acerca de"
- Atajos de teclado ampliados
- Registro local de errores

## P2 — Opcional

- Demo web TypeScript (si hay tiempo)
- Animaciones sutiles
- Temas adicionales
