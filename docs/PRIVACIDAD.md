# Privacidad

La aplicación procesa prompts localmente.

No requiere:

- cuenta
- API key
- internet
- login
- telemetría
- anuncios

La configuración local usa rutas XDG:

- `~/.config/neuro-prompt-semantic-compiler/`
- `~/.local/share/neuro-prompt-semantic-compiler/`

En tests se pueden usar `NPSC_CONFIG_HOME` y `NPSC_DATA_HOME` para redirigir escritura a carpetas temporales.

## Modos de privacidad

`full_original` - en la GUI, **Guardar original completo**

Conserva el prompt original en artefactos públicos como `raw_prompt_original.txt`, JSON y Markdown de auditoría.

`hash_only` - en la GUI, **Guardar solo huella digital**

No devuelve ni persiste el prompt original completo en estructuras públicas del servicio, GUI, JSON, Markdown, NSL ni reportes. Conserva SHA-256, longitud aproximada y metadatos permitidos. El texto original se usa solo de forma efímera durante la compilación.

`redacted_preview` - en la GUI, **Guardar vista parcial recortada**

Conserva una previsualización recortada marcada como `[redacted preview]`.

## Limitación honesta

`hash_only` reduce persistencia y exposición local del prompt original, pero no es cifrado. Si una persona tiene acceso al proceso en ejecución o al sistema mientras se compila, aplican las garantías normales del sistema operativo.

Si no entiendes un término de privacidad, abre **Glosario** dentro de la aplicación.
