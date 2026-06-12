# LEEME PRIMERO

NeuroPrompt Semantic Compiler mejora una petición escrita por una persona y genera un prompt claro, trazable y listo para usar con otra IA. Funciona localmente y no envía tus textos a servidores externos.

## Abrir la aplicación

```bash
cd /home/klsx/NeuroPromptSemanticCompiler
./run_gui.sh
```

## Flujo básico

1. Escribe o pega tu petición.
2. Deja `AUTO` como perfil recomendado.
3. Pulsa `Mejorar prompt`.
4. Copia `Prompt listo para usar`.

## ¿No entiendes una palabra?

Abre Glosario dentro de la aplicación. Encontrarás explicaciones sencillas y ejemplos.

## Qué botón copiar

Usa `Copiar prompt listo`. Ese botón copia `execution_prompt.txt`, que es la salida pensada para pegar en otra IA.

## Dónde se guardan los resultados

Desde la GUI pulsa `Guardar resultados`. Se guardan `execution_prompt.txt`, `compact_nsl.nsl`, `audit_bundle.md`, `audit_bundle.json` y reportes de validación.

## Modo sencillo y avanzado

El modo sencillo muestra lo esencial. El modo avanzado añade NSL compacto, JSON para programas, reglas semánticas, restricciones con origen, métricas y validación detallada.

## Si PySide6 falta

Ejecuta:

```bash
tools/check_runtime.sh
```

No instales nada con sudo. PySide6 debe estar disponible en el entorno local del proyecto.

## Archivo útil para revisión

Para revisar la release, sube:

```text
dist/neuro-prompt-semantic-compiler-1.0.0rc2.tar.gz
artifacts/gui_qa/neuro-prompt-semantic-compiler-gui-qa-1.0.0rc2.tar.gz
```
