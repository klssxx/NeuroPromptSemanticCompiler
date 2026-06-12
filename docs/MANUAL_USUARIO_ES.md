# Manual de usuario

NeuroPrompt Semantic Compiler transforma prompts humanos en salidas estructuradas para IA.

## Modos

- **Sencillo**: AUTO recomendado, lenguaje claro y acciones esenciales.
- **Avanzado**: NSL compacto, JSON para programas, reglas semánticas, validación y perfil aplicado.

El interruptor **Modo avanzado** está en la cabecera. Puedes activarlo o desactivarlo sin perder el prompt escrito.

## Uso GUI

1. Abre la aplicación con `./run_gui.sh`.
2. Entra en **Compilador**.
3. Pega o carga tu prompt.
4. Deja `AUTO` si no tienes claro qué tipo de mejora usar.
5. Pulsa **Mejorar prompt**.
6. Revisa **Resumen** y **Validación**.
7. Usa **Copiar prompt listo** para pegar el resultado en otra IA.
8. Usa **Guardar resultados** si quieres exportar el prompt listo, el informe completo, JSON, NSL y reportes.
9. Usa **Abrir carpeta de resultados** después de guardar.

## Glosario

Si no entiendes una palabra, abre **Glosario**. La página **Diccionario fácil** explica términos como NSL, JSON para programas, audit bundle, hash_only, safe y ROP con ejemplos.

## Perfiles

- `FAST`: tareas cortas.
- `STANDARD`: uso general.
- `ADVANCED`: código, arquitectura y restricciones.
- `ROP`: decisiones estratégicas, riesgos y escenarios.
- `RESEARCH_MAX`: investigación profunda y trazabilidad.
- `AUTO`: selección automática explicada.

## Privacidad

Todo se procesa localmente. No hay telemetría, login ni APIs obligatorias.
