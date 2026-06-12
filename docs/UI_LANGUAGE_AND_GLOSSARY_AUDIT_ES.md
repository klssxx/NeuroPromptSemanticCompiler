# Auditoría de lenguaje UI y glosario

Fecha: 2026-06-02

## Diagnóstico

La aplicación funcionaba, pero varias etiquetas visibles exponían valores internos o términos técnicos sin contexto suficiente. El problema principal no estaba en el core, sino en la capa de presentación: usuarios no técnicos podían encontrar `artifact`, `audit bundle`, `JSON machine-oriented`, `safe`, `hash_only`, `strict`, `seed` o métricas en inglés antes de entender qué acción debían realizar.

## Decisión aplicada

- Mantener valores internos, nombres de archivo y serialización sin cambios.
- Mostrar etiquetas humanas en la GUI.
- Dejar el detalle técnico en modo avanzado y en el glosario.
- Usar `src/npsc_resources/configs/ui_glossary_es.json` como fuente única para definiciones.

## Hallazgos principales

| Término actual | Ubicación | Problema | Texto humano propuesto | Valor interno conservado | Modo | Glosario |
|---|---|---|---|---|---|---|
| Perfil semántico | GUI Compilador, docs | Jerga antes de explicar perfiles | Tipo de mejora | profile / FAST / STANDARD / ADVANCED / ROP / RESEARCH_MAX / AUTO | sencillo | sí |
| Compresión técnica | GUI Compilador, docs | Suena a ajuste de archivo, no a detalle técnico | Nivel de detalle técnico | profile_default / safe / balanced / aggressive / all | sencillo y avanzado | sí |
| profile_default | Combo de nivel | Valor interno expuesto | Automático según el tipo de mejora · recomendado | profile_default | sencillo | sí |
| safe | Combo de nivel, docs | Inglés técnico sin explicación | Conservador · preserva más información | safe | sencillo y avanzado | sí |
| balanced | Combo de nivel, docs | Inglés técnico sin explicación | Equilibrado | balanced | sencillo y avanzado | sí |
| aggressive | Combo de nivel, docs | Riesgo no evidente | Más compacto · requiere revisión | aggressive | sencillo y avanzado | sí |
| all | Combo de nivel | Valor interno poco claro | Generar todos los niveles | all | avanzado | sí |
| full_original | Combo privacidad | Valor interno expuesto | Guardar original completo | full_original | sencillo | sí |
| hash_only | Combo privacidad | Valor interno y concepto criptográfico | Guardar solo huella digital | hash_only | sencillo y avanzado | sí |
| redacted_preview | Combo privacidad | Inglés técnico | Guardar vista parcial recortada | redacted_preview | sencillo | sí |
| Guardar todos los artefactos | Botón resultados | “Artefactos” confunde a usuarios no técnicos | Guardar resultados | export_artifacts | sencillo | sí |
| artefactos guardados | Barra de estado | Jerga innecesaria | archivos generados y guardados | artifact_payloads | sencillo | sí |
| Artefactos generados | Panel principal | Jerga visible en primera pantalla | Archivos generados | artifact_payloads | sencillo | sí |
| Audit bundle | Pestaña resultados | Nombre técnico como etiqueta principal | Informe completo | audit_bundle.md/json | sencillo y avanzado | sí |
| JSON machine-oriented | Pestaña resultados | Inglés y orientación técnica sin explicación | JSON para programas | hybrid_json | avanzado | sí |
| Compact NSL | Pestaña resultados | Inglés técnico | NSL compacto | chosen_nsl / compact_nsl.nsl | avanzado | sí |
| Seeds | Pestaña resultados | Término interno | Reglas semánticas | seeds | avanzado | sí |
| Constraints y origen | Pestaña resultados | Mezcla de idiomas | Restricciones y origen | effective_prompt_ir | avanzado | sí |
| Markdown | README/docs | Se menciona como formato sin explicar utilidad | Informe legible recomendado: Markdown | audit_bundle.md | sencillo y avanzado | sí |
| JSON | README/docs | Puede parecer salida que se debe copiar | JSON para programas | audit_bundle.json / hybrid_json | avanzado | sí |
| NSL | GUI/docs | Formato central pero opaco | NSL compacto, con explicación | NSL/0.1 | avanzado | sí |
| strict | Estado/docs | Valor interno visible | Validación estricta / Bloqueado por validación estricta | strict | avanzado | sí |
| SHA-256 | Resumen | Criptografía sin contexto | Huella digital (SHA-256) | prompt_sha256 | avanzado | sí |
| retention_score | Resumen/métricas | Inglés técnico | Conservación de contenido | retention_score | avanzado | sí |
| precision_score | Resumen/métricas | Inglés técnico | Precisión del resultado | precision_score | avanzado | sí |
| unsupported_addition_score | Resumen/métricas | Inglés técnico largo | Añadidos no respaldados | unsupported_addition_score | avanzado | sí |
| nsl_size_ratio | Resumen/métricas | Métrica sin interpretación | Tamaño del NSL | nsl_size_ratio | avanzado | sí |
| execution_size_ratio | Resumen/métricas | Métrica sin interpretación | Tamaño del prompt listo | execution_size_ratio | avanzado | sí |
| overhead | Docs de evaluación | Concepto técnico no explicado | Coste extra de estructura | overhead marker | avanzado | sí |
| ROP | Perfiles/docs | Acrónimo no evidente | Análisis de realidad y decisiones | ROP | avanzado | sí |
| RESEARCH_MAX | Perfiles/docs | Valor interno y largo | Investigación máxima | RESEARCH_MAX | avanzado | sí |
| Modelo custom | GUI | Mezcla idioma | Modelo personalizado | custom / custom_model_name | sencillo | sí |

## Resultado esperado

El modo sencillo prioriza acciones: pegar prompt, mejorar, copiar Prompt listo para usar y guardar resultados. El modo avanzado conserva trazabilidad técnica con nombres reconocibles y acceso al glosario.

