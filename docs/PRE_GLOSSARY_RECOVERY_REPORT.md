# Informe de recuperación previa al cierre del glosario

Fecha local: 2026-06-02

## Contexto

La sesión anterior fue interrumpida con Ctrl+C después de pegar accidentalmente un prompt perteneciente a otra aplicación. Esta recuperación no rehace la implementación del glosario: solo documenta el estado encontrado, conserva copia previa y valida la release candidate existente.

## Alcance

Ruta inspeccionada:

```text
/home/klsx/NeuroPromptSemanticCompiler
```

Backup creado antes de ajustes adicionales:

```text
backups/pre_glossary_recovery_20260602_160119
```

El proyecto no contiene directorio `.git`. Por tanto, no es posible comparar el estado actual contra un commit base ni distinguir cambios por autor mediante `git diff`.

## Método de inspección

La revisión se basó en:

- archivos presentes;
- nombres de archivos y carpetas;
- rutas internas;
- marcas de tiempo;
- estructura del proyecto;
- artefactos generados;
- búsqueda de términos y tecnologías ajenas;
- validaciones ejecutadas durante el cierre de `1.0.0rc2`.

No se borraron archivos automáticamente y no se revirtieron archivos dudosos sin evidencia inequívoca.

## Búsquedas de indicios ajenos

Se ejecutaron búsquedas seguras dentro del proyecto, excluyendo copias de seguridad, `.venv`, `dist`, `artifacts` y `staging` cuando correspondía, para localizar indicios como:

```text
Tabler
MASTERPROMPT
pack interno
Electron
React
Next.js
Flask
FastAPI
Vite
package.json
app://
rutas externas
localhost
```

Resultado: no se encontraron nombres, rutas, componentes ni scripts inequívocamente pertenecientes a otra aplicación en el árbol principal del proyecto.

Observaciones:

- `app/` aparece como GUI Tkinter heredada y está documentada como compatibilidad secundaria del propio proyecto.
- `staging/` contiene copias generadas para verificación/build y dependencias instaladas en entornos temporales previos.
- Las rutas `/home/klsx/NeuroPromptSemanticCompiler` encontradas pertenecen al propio proyecto o a informes de validación.
- No se encontró contenido relacionado con el pack de iconos Tabler en el árbol principal.

## Estado encontrado

La release candidate ya presente antes de esta recuperación era:

```text
1.0.0rc2
```

Artefactos encontrados:

```text
dist/neuro-prompt-semantic-compiler-1.0.0rc2.tar.gz
dist/neuroprompt_semantic_compiler-1.0.0rc2-py3-none-any.whl
dist/neuroprompt-semantic-compiler_1.0.0rc2_all.deb
dist/SHA256SUMS
dist/RELEASE_MANIFEST.md
```

Recursos del glosario encontrados:

```text
src/npsc_resources/configs/ui_glossary_es.json
src/npsc_gui/glossary.py
docs/GLOSARIO_ES.md
```

## Recursos del glosario dentro de paquetes

Verificación realizada sobre los paquetes `1.0.0rc2`:

- tarball: incluye `src/npsc_resources/configs/ui_glossary_es.json` y `docs/GLOSARIO_ES.md`;
- wheel: incluye `npsc_resources/configs/ui_glossary_es.json`;
- `.deb`: incluye `usr/share/neuro-prompt-semantic-compiler/src/npsc_resources/configs/ui_glossary_es.json` y `usr/share/neuro-prompt-semantic-compiler/docs/GLOSARIO_ES.md`.

## Decisiones de recuperación

- No se reimplementó el glosario.
- No se modificó el core semántico.
- No se promocionó la versión a `1.0.0`.
- No se implementó ningún pack de iconos Tabler.
- No se borraron carpetas ni archivos.
- No se revirtieron archivos porque no hubo evidencia inequívoca de cambios accidentales ajenos en el árbol principal.

## Limitación principal

Al no existir repositorio `.git`, el diagnóstico no puede tener la certeza de una comparación contra commit base. La conclusión se limita a la inspección estructural y a las validaciones ejecutadas en el estado actual.
