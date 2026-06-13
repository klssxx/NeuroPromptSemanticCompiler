# Glosario fácil

Este documento se genera desde `src/npsc_resources/configs/ui_glossary_es.json`.
La misma fuente se usa dentro de la página **Glosario** de la aplicación.

Total de términos: 71

## Uso básico

### AUTO - Automático

La aplicación elige el tipo de mejora más adecuado.

Es la opción recomendada si no sabes qué elegir.

**Cuándo usarlo:** Déjalo seleccionado para la mayoría de prompts.

**Ejemplo:** AUTO puede escoger FAST para una tarea simple o ADVANCED para una tarea compleja.

**Alias de búsqueda:** auto, automatico, recomendado

**Términos relacionados:** semantic_profile, fast, standard, advanced

**Nota técnica:** Valor interno de perfil: AUTO.

### Compilar - Mejorar y estructurar

Acción que transforma tu prompt original en resultados más claros.

La aplicación analiza lo que pides, conserva lo importante y genera un prompt listo para usar.

**Cuándo usarlo:** Pulsa Mejorar prompt cuando ya hayas pegado tu petición.

**Ejemplo:** Compilar crea Prompt listo para usar, informe completo y archivos técnicos.

**Alias de búsqueda:** compilar prompt, procesar, generar resultado

**Términos relacionados:** improve_prompt, execution_prompt, result

**Nota técnica:** El core ejecuta extracción semántica, selección de perfil, NSL, reconstrucción y validación.

### Mejorar prompt - Crear una versión más clara

Botón principal que inicia la compilación.

Analiza tu texto y genera una versión más clara para usar con otra IA.

**Cuándo usarlo:** Pulsa este botón después de pegar tu prompt original.

**Ejemplo:** Si no sabes qué tocar, deja AUTO y pulsa Mejorar prompt.

**Alias de búsqueda:** mejorar, optimizar prompt, boton mejorar

**Términos relacionados:** compile, prompt, execution_prompt

**Nota técnica:** Dispara el flujo de compilación compartido con CLI y servicio.

### Modo avanzado - Vista técnica

Vista que añade trazabilidad, JSON, NSL, reglas y perfil aplicado.

Sirve para auditar y entender detalles técnicos sin quitar el flujo sencillo.

**Cuándo usarlo:** Actívalo si quieres revisar o automatizar resultados.

**Ejemplo:** Muestra NSL compacto y JSON para programas.

**Alias de búsqueda:** avanzado, tecnico, detalles

**Términos relacionados:** simple_mode, compact_nsl, json_for_programs

**Nota técnica:** Control local de visibilidad en la GUI.

### Modo sencillo - Vista esencial

Vista que muestra lo necesario para mejorar y copiar un prompt.

Oculta detalles técnicos que no necesitas para el uso normal.

**Cuándo usarlo:** Úsalo si solo quieres mejorar un prompt y copiar el resultado.

**Ejemplo:** En modo sencillo ves Resumen, Prompt listo, Informe, Original y Validación.

**Alias de búsqueda:** sencillo, simple, basico

**Términos relacionados:** advanced_mode, execution_prompt

**Nota técnica:** Control de presentación; no cambia la compatibilidad del core.

### Prompt - Petición para una IA

Texto que le dice a una IA qué debe hacer.

Puede ser una pregunta, una tarea, un encargo largo o una lista de requisitos.

**Cuándo usarlo:** Escribe tu prompt en el Compilador.

**Ejemplo:** Resume este contrato y señala riesgos importantes.

**Alias de búsqueda:** peticion, instruccion, prompt

**Términos relacionados:** original_prompt, execution_prompt, improve_prompt

**Nota técnica:** El proyecto transforma prompts humanos en salidas semánticas trazables.

### Prompt listo para usar - Texto para copiar

Salida principal que debes copiar y pegar en otra IA.

Es el resultado pensado para uso diario. Los archivos técnicos son opcionales.

**Cuándo usarlo:** Cópialo cuando quieras usar el resultado de la compilación.

**Ejemplo:** Pulsa Copiar prompt listo para copiar este contenido.

**Alias de búsqueda:** execution_prompt.txt, prompt listo, copiar resultado, optimized_prompt

**Términos relacionados:** execution_prompt_file, result, audit_bundle

**Nota técnica:** Nombre de archivo principal: execution_prompt.txt. optimized_prompt.txt se conserva como alias compatible.

### Prompt original - Tu texto inicial

Texto que escribes o pegas antes de mejorar el prompt.

La aplicación intenta conservar su intención y restricciones importantes.

**Cuándo usarlo:** Pégalo en el Compilador antes de pulsar Mejorar prompt.

**Ejemplo:** Quiero que ordenes estas notas y respetes estas condiciones...

**Alias de búsqueda:** original, entrada, texto inicial

**Términos relacionados:** prompt, execution_prompt

**Nota técnica:** Puede omitirse de resultados según el modo de privacidad.

### Resultado - Salida generada

Contenido que aparece después de mejorar un prompt.

Incluye el Prompt listo para usar y, opcionalmente, informes y datos técnicos.

**Cuándo usarlo:** Ve a Resultados después de compilar.

**Ejemplo:** El resultado principal está en la pestaña Prompt listo para usar.

**Alias de búsqueda:** salida, resultado, output

**Términos relacionados:** execution_prompt, artifact, save_results

**Nota técnica:** El resultado del core es un diccionario con varias salidas compatibles.

## Resultados

### Artefacto - Archivo generado

Archivo que crea la aplicación al guardar una compilación.

Puede contener tu prompt listo, un informe legible o datos técnicos.

**Cuándo usarlo:** Usa Guardar resultados cuando quieras conservar, revisar o compartir una compilación.

**Ejemplo:** execution_prompt.txt es el archivo principal para copiar y usar en otra IA.

**Alias de búsqueda:** artefactos, archivo generado, resultado guardado

**Términos relacionados:** execution_prompt, audit_bundle, markdown, json

**Nota técnica:** Término habitual en procesos de software para describir archivos producidos por una ejecución.

### Audit bundle - Informe completo

Informe con trazabilidad de la compilación.

Reúne el prompt original permitido por tu privacidad, el perfil aplicado, restricciones, métricas y trazabilidad.

**Cuándo usarlo:** Úsalo para revisar o archivar una compilación, no como texto principal para pegar en otra IA.

**Ejemplo:** audit_bundle.md es legible; audit_bundle.json sirve para automatización.

**Alias de búsqueda:** informe completo, audit_bundle, paquete de auditoria

**Términos relacionados:** audit_bundle_md, audit_bundle_json, markdown, json

**Nota técnica:** Nombre técnico conservado por compatibilidad: audit bundle.

### audit_bundle.md - Informe completo legible

Versión legible del informe completo.

Es un archivo de texto ordenado para revisar qué hizo la aplicación.

**Cuándo usarlo:** Úsalo para revisión humana o para archivar la ejecución.

**Ejemplo:** Abre audit_bundle.md si quieres ver perfil, métricas y advertencias.

**Alias de búsqueda:** audit bundle md, informe markdown, informe legible

**Términos relacionados:** audit_bundle, markdown

**Nota técnica:** Archivo interno/exportado estable: audit_bundle.md.

### Carpeta de resultados - Lugar donde se guardan archivos

Carpeta elegida para guardar los archivos generados.

Contiene el prompt listo, informes y archivos técnicos.

**Cuándo usarlo:** Ábrela después de Guardar resultados para revisar los archivos.

**Ejemplo:** Puedes elegir una carpeta dentro de outputs o de tu carpeta personal.

**Alias de búsqueda:** carpeta salida, output dir, outputs

**Términos relacionados:** save_results, artifact

**Nota técnica:** El path se guarda localmente en configuración XDG.

### execution_prompt.txt - Archivo del prompt listo

Archivo que guarda el Prompt listo para usar.

Es el archivo más importante si quieres reutilizar el resultado fuera de la aplicación.

**Cuándo usarlo:** Ábrelo o cópialo cuando necesites pegar el resultado en otra IA.

**Ejemplo:** Después de Guardar resultados, busca execution_prompt.txt en la carpeta elegida.

**Alias de búsqueda:** execution prompt, archivo principal, prompt listo txt

**Términos relacionados:** execution_prompt, save_results

**Nota técnica:** Nombre de archivo exportado estable: execution_prompt.txt.

### Guardar resultados - Exportar archivos

Acción que guarda los archivos generados en una carpeta.

Guarda el prompt listo, el informe y los archivos técnicos.

**Cuándo usarlo:** Úsalo cuando quieras conservar una compilación fuera de la app.

**Ejemplo:** Pulsa Guardar resultados y elige una carpeta.

**Alias de búsqueda:** guardar, guardar artefactos, exportar

**Términos relacionados:** artifact, folder_results, execution_prompt_file

**Nota técnica:** Internamente llama a export_artifacts y conserva los nombres de archivo existentes.

## Tipos de mejora

### ADVANCED - Mejora avanzada

Tipo de mejora para tareas con bastante contexto, condiciones o estructura.

Suele ser útil para programación, arquitectura, documentación técnica o trabajos con varios requisitos.

**Cuándo usarlo:** Úsalo cuando el prompt tenga varias partes importantes y no quieras perder trazabilidad.

**Ejemplo:** Elige ADVANCED para pedir cambios en un proyecto con tests, restricciones y entrega final.

**Alias de búsqueda:** advanced, perfil advanced, tarea compleja

**Términos relacionados:** semantic_profile, technical_detail_level, strict_validation

**Nota técnica:** Valor interno de perfil conservado como ADVANCED.

### FAST - Mejora rápida

Tipo de mejora para prompts simples y tareas rápidas.

Genera una salida breve y directa cuando no hace falta mucha estructura.

**Cuándo usarlo:** Úsalo para corregir, reescribir o aclarar textos sencillos.

**Ejemplo:** Corrige la ortografía de este correo.

**Alias de búsqueda:** fast, rapido, perfil rapido

**Términos relacionados:** semantic_profile, standard, auto

**Nota técnica:** Valor interno de perfil conservado como FAST.

### Perfil semántico - Tipo de mejora

Control que decide qué clase de mejora necesita tu prompt.

En la interfaz se muestra como Tipo de mejora para evitar jerga.

**Cuándo usarlo:** Déjalo en AUTO si no sabes qué opción elegir.

**Ejemplo:** FAST, STANDARD, ADVANCED, ROP y RESEARCH_MAX son tipos de mejora.

**Alias de búsqueda:** tipo de mejora, perfil, semantic profile

**Términos relacionados:** auto, fast, standard, advanced

**Nota técnica:** Nombre técnico anterior: Perfil semántico.

### RESEARCH_MAX - Investigación máxima

Tipo de mejora con máxima preservación y trazabilidad.

Está pensado para investigación profunda, riesgos, negocio o decisiones importantes.

**Cuándo usarlo:** Úsalo cuando perder contexto sería costoso.

**Ejemplo:** Analizar una estrategia con evidencias, hipótesis y riesgos.

**Alias de búsqueda:** research max, investigacion profunda, maxima preservacion

**Términos relacionados:** semantic_profile, strict_validation, intended_expansion

**Nota técnica:** Valor interno de perfil conservado como RESEARCH_MAX.

### ROP - Análisis de realidad y decisiones

Tipo de mejora para decisiones complejas con hipótesis, riesgos y escenarios.

Genera una estructura más amplia para razonar, comparar opciones y revisar supuestos.

**Cuándo usarlo:** Úsalo para estrategia, negocio, probabilidades o decisiones importantes.

**Ejemplo:** Comparar dos estrategias con riesgos, coste y probabilidad de éxito.

**Alias de búsqueda:** reality optimization protocol, estrategia, decisiones

**Términos relacionados:** semantic_profile, intended_expansion

**Nota técnica:** ROP significa Reality Optimization Protocol.

### STANDARD - Mejora equilibrada

Tipo de mejora equilibrado para uso general.

Combina claridad, tamaño razonable y conservación de información.

**Cuándo usarlo:** Úsalo si quieres una opción manual general.

**Ejemplo:** Sirve para prompts de trabajo cotidianos con varias instrucciones.

**Alias de búsqueda:** standard, estandar, normal

**Términos relacionados:** auto, fast, advanced

**Nota técnica:** Valor interno de perfil conservado como STANDARD.

## Nivel de detalle

### aggressive - Más compacto

Nivel técnico que intenta reducir más el tamaño de la representación NSL.

Puede ahorrar espacio, pero requiere revisar que no se haya perdido ningún matiz importante.

**Cuándo usarlo:** Úsalo solo si entiendes la salida técnica o necesitas máxima densidad.

**Ejemplo:** Puede servir para comparar versiones NSL, no como opción principal para principiantes.

**Alias de búsqueda:** agresivo, mas compacto, compacto

**Términos relacionados:** safe, balanced, technical_detail_level

**Nota técnica:** Valor interno de nivel técnico: aggressive.

### all - Generar todos los niveles

Opción que genera varias versiones técnicas para comparar.

Permite revisar salidas conservadoras, equilibradas y compactas en una misma ejecución.

**Cuándo usarlo:** Úsalo si quieres auditar diferencias entre niveles técnicos.

**Ejemplo:** Genera compiled_safe.nsl, compiled_balanced.nsl y compiled_aggressive.nsl.

**Alias de búsqueda:** todos, todos los niveles, safe balanced aggressive

**Términos relacionados:** safe, balanced, aggressive

**Nota técnica:** Valor interno de compatibilidad: all.

### balanced - Equilibrado

Nivel técnico intermedio entre preservar y compactar.

Busca una salida clara sin hacerla demasiado larga ni demasiado comprimida.

**Cuándo usarlo:** Úsalo si quieres una opción técnica razonable para revisión avanzada.

**Ejemplo:** Es una buena comparación frente a safe y aggressive.

**Alias de búsqueda:** balanceado, equilibrio, balanced

**Términos relacionados:** safe, aggressive, technical_detail_level

**Nota técnica:** Valor interno de nivel técnico: balanced.

### Nivel de detalle técnico - Cuánta estructura técnica generar

Control que ajusta la densidad de la salida técnica.

En uso normal deja Automático según el tipo de mejora.

**Cuándo usarlo:** Cámbialo solo si quieres comparar niveles NSL.

**Ejemplo:** Conservador preserva más; Más compacto requiere revisión.

**Alias de búsqueda:** compresion tecnica, nivel tecnico, detalle tecnico

**Términos relacionados:** profile_default, safe, balanced, aggressive, all

**Nota técnica:** Etiqueta humana para el antiguo control Compresión técnica.

### profile_default - Automático según el tipo de mejora

Opción que deja que el perfil elegido decida el nivel técnico.

Es la opción recomendada porque evita tener que entender safe, balanced o aggressive.

**Cuándo usarlo:** Déjala seleccionada salvo que quieras comparar niveles técnicos.

**Ejemplo:** FAST puede elegir un nivel más compacto; RESEARCH_MAX puede elegir uno más conservador.

**Alias de búsqueda:** perfil por defecto, default profile, automatico por perfil

**Términos relacionados:** technical_detail_level, safe, balanced, aggressive

**Nota técnica:** Valor interno de nivel: profile_default. El controlador lo convierte a None para usar el default del perfil.

### safe - Conservador

Nivel técnico que prioriza conservar información.

Suele ser menos compacto, pero reduce el riesgo de perder detalles.

**Cuándo usarlo:** Úsalo para prompts importantes o con restricciones fuertes.

**Ejemplo:** safe es apropiado si no quieres que la compresión elimine matices.

**Alias de búsqueda:** seguro, conservador, preserva mas

**Términos relacionados:** balanced, aggressive, technical_detail_level

**Nota técnica:** Valor interno de nivel técnico: safe.

## Privacidad

### full_original - Guardar original completo

Modo de privacidad que conserva el prompt original completo en resultados técnicos.

Da máxima trazabilidad, pero guarda más contenido sensible si tu prompt lo contiene.

**Cuándo usarlo:** Úsalo cuando trabajes con texto no sensible o necesites auditoría completa.

**Ejemplo:** El informe puede incluir el prompt original completo.

**Alias de búsqueda:** original completo, guardar todo, full original

**Términos relacionados:** privacy, hash_only, redacted_preview

**Nota técnica:** Valor interno de privacidad: full_original.

### hash_only - Guardar solo huella digital

Modo de privacidad que no conserva el prompt original en resultados públicos.

Guarda una huella SHA-256 y metadatos permitidos para comprobar identidad sin exponer el texto.

**Cuándo usarlo:** Úsalo si el prompt contiene datos sensibles.

**Ejemplo:** El informe muestra una huella, no el texto completo.

**Alias de búsqueda:** solo hash, huella, sin original

**Términos relacionados:** sha256, fingerprint, privacy

**Nota técnica:** Valor interno de privacidad: hash_only.

### Huella digital - Identificador del texto

Código calculado a partir del texto para identificarlo sin mostrarlo.

Si el texto cambia, la huella cambia. No sirve para recuperar el prompt original.

**Cuándo usarlo:** Úsala para comprobar que dos ejecuciones partieron del mismo texto sin guardar el contenido.

**Ejemplo:** SHA-256 genera una huella larga de letras y números.

**Alias de búsqueda:** huella, fingerprint, hash

**Términos relacionados:** sha256, hash_only

**Nota técnica:** La huella se calcula localmente con SHA-256.

### Local-first - Primero en tu equipo

Enfoque donde el procesamiento se hace en tu equipo.

La aplicación no envía tus prompts a servidores externos.

**Cuándo usarlo:** Es una garantía de privacidad del flujo normal de NPSC.

**Ejemplo:** Puedes compilar prompts sin conexión de red.

**Alias de búsqueda:** local first, local, sin nube

**Términos relacionados:** offline, privacy

**Nota técnica:** Principio de diseño del proyecto.

### Offline - Sin conexión externa

La aplicación funciona localmente sin enviar prompts a internet.

No usa APIs externas para compilar tu texto.

**Cuándo usarlo:** Tenlo presente si trabajas con información privada.

**Ejemplo:** Puedes ejecutar ./run_gui.sh y compilar localmente.

**Alias de búsqueda:** sin internet, sin red, offline

**Términos relacionados:** local_first, privacy

**Nota técnica:** La política del proyecto prohíbe llamadas externas en el flujo normal.

### Privacidad - Qué se guarda del texto original

Control que decide cuánto del prompt original se conserva en archivos técnicos.

Puedes guardar el original completo, solo una huella o una vista parcial recortada.

**Cuándo usarlo:** Elige una opción más protectora si tu prompt contiene información sensible.

**Ejemplo:** Guardar solo huella digital corresponde a hash_only.

**Alias de búsqueda:** privacy, datos sensibles, guardar original

**Términos relacionados:** full_original, hash_only, redacted_preview

**Nota técnica:** Control visible que mapea a privacy_mode del core.

### redacted_preview - Guardar vista parcial recortada

Modo de privacidad que conserva solo una vista corta del prompt original.

Permite reconocer la ejecución sin guardar todo el contenido.

**Cuándo usarlo:** Úsalo si quieres una pista visual del texto, pero no el prompt completo.

**Ejemplo:** El informe puede mostrar solo los primeros caracteres marcados como vista recortada.

**Alias de búsqueda:** preview recortada, redacted, vista parcial

**Términos relacionados:** privacy, full_original, hash_only

**Nota técnica:** Valor interno de privacidad: redacted_preview.

### SHA-256 - Algoritmo de huella digital

Método para crear una huella digital del prompt.

Permite identificar un texto sin guardarlo completo.

**Cuándo usarlo:** Aparece especialmente cuando usas Guardar solo huella digital.

**Ejemplo:** Dos prompts iguales generan la misma huella SHA-256.

**Alias de búsqueda:** sha, sha256, hash sha

**Términos relacionados:** fingerprint, hash_only

**Nota técnica:** Algoritmo criptográfico estándar usado localmente.

## Validación

### Advertencia - Aviso de revisión

Mensaje que indica algo que conviene revisar.

No siempre bloquea el resultado, pero no deberías ignorarlo en tareas importantes.

**Cuándo usarlo:** Lee las advertencias antes de copiar resultados críticos.

**Ejemplo:** Puede avisar de posible pérdida de matices.

**Alias de búsqueda:** warning, aviso, revisar

**Términos relacionados:** validation, blocked, strict_validation

**Nota técnica:** Lista técnica en context_loss_report.warnings.

### Bloqueado - Resultado detenido

Estado que indica que la validación estricta no aprobó el resultado.

La aplicación detectó pérdida o riesgo suficiente como para no marcar la salida como válida.

**Cuándo usarlo:** Revisa las advertencias y corrige el prompt original antes de usar el resultado.

**Ejemplo:** Un resultado puede quedar bloqueado si falta una restricción crítica.

**Alias de búsqueda:** bloqueado, blocked, strict blocked

**Términos relacionados:** strict_validation, warning, validation

**Nota técnica:** Valor de estado interno habitual: blocked.

### Constraint - Restricción

Condición que la salida debe respetar.

Una restricción puede indicar cosas que no se deben hacer o límites que deben conservarse.

**Cuándo usarlo:** Revísala si tu prompt incluye normas importantes.

**Ejemplo:** No usar sudo es una restricción.

**Alias de búsqueda:** constraint, restriccion, condicion obligatoria

**Términos relacionados:** restriction, constraints_origin, semantic_rule

**Nota técnica:** Nombre técnico en varias estructuras internas: constraint.

### Preservación semántica - Conservar el significado

Medida de si el resultado mantiene la intención original.

No se trata solo de acortar texto; lo importante es no perder lo que pediste.

**Cuándo usarlo:** Revísala en el resumen o validación después de compilar.

**Ejemplo:** Un prompt con reglas críticas necesita alta preservación semántica.

**Alias de búsqueda:** preservacion, conservar significado, semantic preservation

**Términos relacionados:** retention_score, validation

**Nota técnica:** Concepto central del verificador de pérdida de contexto.

### Restricción - Condición obligatoria

Regla o límite que la salida debe respetar.

La aplicación intenta detectarlas y conservarlas en el prompt listo.

**Cuándo usarlo:** Inclúyelas claramente en el prompt original si son importantes.

**Ejemplo:** No usar sudo, no llamar APIs externas y trabajar dentro del proyecto.

**Alias de búsqueda:** restriccion, regla, constraint

**Términos relacionados:** constraint, constraints_origin

**Nota técnica:** Se normaliza internamente como constraint cuando procede.

### Restricciones y origen - Condiciones trazadas

Vista que muestra qué condiciones se detectaron y de dónde vienen.

Ayuda a comprobar que las reglas importantes del prompt no se perdieron.

**Cuándo usarlo:** Úsala en modo avanzado para auditar una compilación importante.

**Ejemplo:** Puede mostrar que no_sudo viene del prompt original o de una política del producto.

**Alias de búsqueda:** constraints y origen, origen de restricciones, trazabilidad

**Términos relacionados:** constraint, restriction, constraint_traceability_score

**Nota técnica:** Antes aparecía como Constraints y origen.

### strict - Validación estricta

Modo que bloquea resultados con pérdidas o riesgos críticos.

No mejora el prompt por sí solo; cambia la exigencia de validación.

**Cuándo usarlo:** Actívalo para prompts importantes, seguridad o restricciones fuertes.

**Ejemplo:** Puede bloquear una salida si falta una condición crítica.

**Alias de búsqueda:** estricto, strict mode, bloquear si falla

**Términos relacionados:** strict_validation, blocked, validation

**Nota técnica:** Flag interno compartido por CLI, servicio y GUI.

### Validación - Revisión del resultado

Proceso que revisa pérdida semántica, advertencias y restricciones.

Te ayuda a decidir si el resultado se puede usar o necesita revisión.

**Cuándo usarlo:** Mírala después de compilar, especialmente si aparecen advertencias.

**Ejemplo:** La pestaña Validación muestra puntuaciones y avisos.

**Alias de búsqueda:** validacion, comprobacion, revision

**Términos relacionados:** strict_validation, semantic_preservation, warning

**Nota técnica:** Se basa en context_loss_report.

### Validación estricta - Revisión exigente

Opción que impide aprobar salidas con problemas críticos.

Es útil cuando no basta con una advertencia y prefieres detener el resultado.

**Cuándo usarlo:** Úsala en trabajos importantes o con reglas de seguridad.

**Ejemplo:** Si falta no_sudo, la validación estricta puede bloquear.

**Alias de búsqueda:** validacion estricta, strict, bloquear

**Términos relacionados:** strict, blocked, warning

**Nota técnica:** Usa strict_policy desde compiler_defaults.json.

## Modelos

### CLI - Uso por terminal

Forma de usar la aplicación escribiendo comandos en una terminal.

Es útil para usuarios avanzados o automatización.

**Cuándo usarlo:** Usa la GUI si prefieres botones; usa CLI si quieres scripts.

**Ejemplo:** python3 src/npsc_cli.py --input examples/messy_prompt.txt --out outputs/demo

**Alias de búsqueda:** terminal, linea de comandos, command line

**Términos relacionados:** offline, local_first, json_for_programs

**Nota técnica:** CLI significa Command Line Interface.

### Modelo de destino - IA donde pegarás el resultado

Modelo o familia de modelos para la que se adapta el prompt.

Ayuda a ajustar estilo y estructura del Prompt listo para usar.

**Cuándo usarlo:** Elige AUTO si no sabes cuál corresponde.

**Ejemplo:** Codex, GPT, Claude, Hermes o custom.

**Alias de búsqueda:** target, modelo destino, modelo

**Términos relacionados:** auto, custom_model

**Nota técnica:** Valor interno enviado como target al core.

### Modelo personalizado - Modelo no listado

Opción para escribir el nombre de un modelo que no aparece en la lista.

No añade capacidades nuevas; solo documenta el destino y usa valores seguros.

**Cuándo usarlo:** Úsalo si vas a pegar el resultado en un modelo local o poco común.

**Ejemplo:** MiModeloLocal-7B puede registrarse como nombre visible.

**Alias de búsqueda:** custom, modelo custom, mi modelo

**Términos relacionados:** target_model, auto

**Nota técnica:** El target interno puede seguir siendo custom con custom_model_name.

### Modelo personalizado - Modelo no listado

Modelo escrito manualmente por el usuario.

La aplicación lo registra como destino, pero no inventa capacidades específicas.

**Cuándo usarlo:** Úsalo si tu modelo no aparece en la lista.

**Ejemplo:** Puedes escribir el nombre de un modelo local.

**Alias de búsqueda:** modelo personalizado, custom model, custom

**Términos relacionados:** custom_model, model_target

**Nota técnica:** Entrada relacionada con target=custom.

## Formatos técnicos

### audit_bundle.json - Informe completo para programas

Versión estructurada del informe completo.

Está pensada para scripts, validaciones o futuras integraciones.

**Cuándo usarlo:** Normalmente no necesitas abrirlo; consérvalo si quieres trazabilidad técnica.

**Ejemplo:** Un script puede leer audit_bundle.json para revisar métricas automáticamente.

**Alias de búsqueda:** audit bundle json, informe json, json de auditoria

**Términos relacionados:** audit_bundle, json_for_programs

**Nota técnica:** Archivo interno/exportado estable: audit_bundle.json.

### compact_nsl.nsl - Archivo NSL compacto

Archivo que contiene el NSL compacto elegido.

Es útil si quieres inspeccionar la estructura técnica de la compilación.

**Cuándo usarlo:** No lo necesitas para usar el prompt en otra IA.

**Ejemplo:** Abre compact_nsl.nsl solo si quieres ver campos como R, G, CTX, T, C y OUT.

**Alias de búsqueda:** compact_nsl, archivo nsl, nsl file

**Términos relacionados:** compact_nsl, nsl

**Nota técnica:** Nombre de archivo exportado estable: compact_nsl.nsl.

### Core - Motor interno

Parte interna que realiza la compilación semántica.

La interfaz muestra botones; el core hace el análisis y genera los resultados.

**Cuándo usarlo:** Solo necesitas este término si revisas documentación técnica.

**Ejemplo:** La GUI llama al core sin cambiar sus valores internos.

**Alias de búsqueda:** motor, nucleo, core semantico

**Términos relacionados:** compile, cli, ir

**Nota técnica:** Se conserva separado de la capa de presentación.

### IR - Representación interna

Estructura técnica que la aplicación usa entre el prompt original y las salidas.

No necesitas verla para usar la app; sirve para trazabilidad y exportación.

**Cuándo usarlo:** Úsala solo en revisión técnica avanzada.

**Ejemplo:** semantic_ir.json guarda parte de esta representación.

**Alias de búsqueda:** semantic ir, representacion intermedia, internal representation

**Términos relacionados:** core, json_for_programs

**Nota técnica:** IR significa Intermediate Representation.

### JSON - Archivo estructurado

Formato de texto pensado para que lo lean programas.

Normalmente no necesitas abrirlo ni copiarlo para usar tu prompt.

**Cuándo usarlo:** Úsalo para automatización, scripts o futuras integraciones.

**Ejemplo:** audit_bundle.json contiene datos que un script puede procesar.

**Alias de búsqueda:** json, datos estructurados, archivo json

**Términos relacionados:** json_for_programs, json_machine_oriented

**Nota técnica:** JSON significa JavaScript Object Notation.

### JSON machine-oriented - JSON para programas

Nombre técnico del JSON pensado para programas.

La app lo muestra como JSON para programas para que sea más claro.

**Cuándo usarlo:** Consúltalo solo si necesitas integración técnica.

**Ejemplo:** El modo avanzado puede mostrar el nombre técnico entre paréntesis.

**Alias de búsqueda:** machine oriented json, json machine, json para maquinas

**Términos relacionados:** json, json_for_programs

**Nota técnica:** Nombre técnico conservado: JSON machine-oriented.

### JSON para programas - Datos para automatización

Archivo estructurado pensado para automatización, scripts o integraciones.

No es el texto principal para pegar en otra IA. Para eso usa Prompt listo para usar.

**Cuándo usarlo:** Úsalo si vas a procesar resultados con código.

**Ejemplo:** Una integración puede leer métricas desde JSON para programas.

**Alias de búsqueda:** json programas, json tecnico, machine oriented

**Términos relacionados:** json, json_machine_oriented

**Nota técnica:** Etiqueta visible recomendada para JSON machine-oriented.

### Markdown - Informe legible recomendado

Archivo de texto ordenado y fácil de leer.

Es la mejor opción para revisar o compartir un informe con una persona.

**Cuándo usarlo:** Ábrelo cuando quieras leer el informe completo sin usar herramientas técnicas.

**Ejemplo:** audit_bundle.md es un informe en Markdown.

**Alias de búsqueda:** md, markdown, texto ordenado

**Términos relacionados:** audit_bundle_md, audit_bundle

**Nota técnica:** Extensión habitual: .md.

### NPSC-HYBRID - Formato híbrido del informe

Esquema técnico que combina informe legible y datos estructurados.

Sirve para conservar compatibilidad con salidas anteriores y trazabilidad.

**Cuándo usarlo:** Normalmente basta con saber que forma parte del informe completo.

**Ejemplo:** NPSC-HYBRID/1.0 aparece en JSON e informes técnicos.

**Alias de búsqueda:** npsc hybrid, hybrid semantic prompt, hibrido

**Términos relacionados:** audit_bundle, json_for_programs, markdown

**Nota técnica:** Schema/version conservado: NPSC-HYBRID/1.0.

### NSL - Lenguaje semántico compacto

Formato técnico compacto que resume la intención del prompt.

No necesitas entenderlo para usar la aplicación. Para uso normal copia Prompt listo para usar.

**Cuándo usarlo:** Úsalo si quieres revisión avanzada o automatización.

**Ejemplo:** NSL puede incluir campos como objetivo, contexto, tareas y restricciones.

**Alias de búsqueda:** nsl, nsl/0.1, semantic language

**Términos relacionados:** compact_nsl, compact_nsl_file

**Nota técnica:** NSL/0.1 es la versión canónica actual.

### NSL compacto - Resumen técnico estructurado

Representación técnica resumida de la intención y condiciones del prompt.

Resume intención, contexto, tareas, restricciones y salida esperada. Para uso normal copia Prompt listo para usar.

**Cuándo usarlo:** Úsalo para revisión avanzada o automatización.

**Ejemplo:** compact_nsl.nsl guarda esta representación en archivo.

**Alias de búsqueda:** compact nsl, nsl compacto, compact_nsl.nsl

**Términos relacionados:** nsl, compact_nsl_file, execution_prompt

**Nota técnica:** NSL/0.1 es el formato compacto canónico del proyecto.

### Regla semántica - Criterio de significado

Criterio reutilizable que ayuda a conservar intención o seguridad.

En modo avanzado aparecen como reglas semánticas para explicar por qué se añadieron ciertas instrucciones.

**Cuándo usarlo:** Úsalas solo para auditoría avanzada.

**Ejemplo:** Una regla puede indicar que las restricciones críticas deben sobrevivir a toda transformación.

**Alias de búsqueda:** seed, regla, semantic seed

**Términos relacionados:** seed, seeds, constraints_origin

**Nota técnica:** Etiqueta humana para seeds.

### Seed - Regla semántica

Señal interna reutilizable que guía la compilación.

Ayuda al sistema a conservar criterios importantes. En la GUI se explica como regla semántica.

**Cuándo usarlo:** Solo necesitas revisarla en modo avanzado.

**Ejemplo:** S202 puede representar una regla de conservación de restricciones.

**Alias de búsqueda:** seed, semilla, semantic seed

**Términos relacionados:** seeds, semantic_rule

**Nota técnica:** Nombre técnico conservado: seed.

### Seeds - Reglas semánticas

Conjunto de reglas internas seleccionadas para una compilación.

Explican parte de la estructura añadida al prompt listo.

**Cuándo usarlo:** Revísalas si necesitas auditar por qué se generó cierta instrucción.

**Ejemplo:** El modo avanzado muestra las reglas semánticas seleccionadas.

**Alias de búsqueda:** seeds, semillas, reglas semanticas

**Términos relacionados:** seed, semantic_rule

**Nota técnica:** Nombre técnico conservado en JSON: seeds.

## Métricas

### constraint_traceability_score - Trazabilidad de restricciones

Métrica que revisa si las restricciones conservan su origen.

Cuanto mayor sea, más claro queda de dónde viene cada condición.

**Cuándo usarlo:** Úsala para auditoría avanzada de prompts con reglas críticas.

**Ejemplo:** Una restricción de seguridad debería aparecer trazada hasta el prompt o la política.

**Alias de búsqueda:** constraint traceability, trazabilidad de condiciones

**Términos relacionados:** constraints_origin, constraint

**Nota técnica:** Campo técnico de validación conservado por compatibilidad.

### contradiction_score - Riesgo de contradicción

Métrica que penaliza contradicciones detectadas.

Ayuda a ver si la salida dice algo incompatible con el prompt original.

**Cuándo usarlo:** Revísala en prompts con reglas o decisiones delicadas.

**Ejemplo:** Sería una contradicción pedir no usar red y que el resultado proponga una API externa.

**Alias de búsqueda:** contradiccion, contradiction

**Términos relacionados:** validation, precision_score

**Nota técnica:** Campo técnico de validación conservado por compatibilidad.

### execution_size_ratio - Tamaño del prompt listo

Compara el tamaño del prompt listo con el prompt original.

Puede ser mayor que 1 si la aplicación añade estructura útil de forma intencionada.

**Cuándo usarlo:** Revísalo si te preocupa que el resultado sea demasiado largo.

**Ejemplo:** ROP y RESEARCH_MAX pueden expandir porque añaden análisis y trazabilidad.

**Alias de búsqueda:** ratio execution, tamano prompt listo

**Términos relacionados:** intended_expansion, overhead

**Nota técnica:** Campo técnico conservado por compatibilidad.

### expansión intencionada - Crecimiento útil

Cuando el resultado es más largo porque añade estructura útil.

No siempre más corto es mejor. Algunos perfiles amplían para conservar contexto y reglas.

**Cuándo usarlo:** Tenlo en cuenta con ROP o RESEARCH_MAX.

**Ejemplo:** Un prompt de investigación puede crecer porque añade escenarios, evidencia y verificación.

**Alias de búsqueda:** expansion, crece a proposito, expansion intencionada

**Términos relacionados:** execution_size_ratio, overhead

**Nota técnica:** Se distingue de crecimiento accidental o pérdida de compresión.

### nsl_size_ratio - Tamaño del NSL

Compara el tamaño del NSL con el prompt original.

Menor que 1 suele indicar reducción; mayor que 1 puede indicar overhead o expansión útil.

**Cuándo usarlo:** Revísalo solo si estás analizando tamaño y densidad técnica.

**Ejemplo:** Un prompt muy corto puede producir nsl_size_ratio mayor que 1.

**Alias de búsqueda:** ratio nsl, tamano nsl, compression ratio nsl

**Términos relacionados:** metrics_overhead, compact_nsl

**Nota técnica:** Campo técnico conservado por compatibilidad.

### overhead - Coste extra de estructura

Texto adicional que aparece por la estructura técnica del formato.

En prompts muy cortos, un formato estructurado puede ocupar más aunque sea correcto.

**Cuándo usarlo:** Tenlo en cuenta si ves ratios mayores que 1 en prompts breves.

**Ejemplo:** compact_nsl.nsl puede crecer por campos obligatorios del esquema.

**Alias de búsqueda:** sobrecoste, estructura extra, overhead

**Términos relacionados:** nsl_size_ratio, intended_expansion

**Nota técnica:** Se reporta como overhead, no como pérdida automática.

### precision_score - Precisión del resultado

Métrica que penaliza añadidos no respaldados y contradicciones.

Ayuda a comprobar que el resultado no inventa cosas importantes.

**Cuándo usarlo:** Revísala si la fidelidad del resultado es importante.

**Ejemplo:** Una precisión baja puede indicar que se añadió información que no estaba en el prompt.

**Alias de búsqueda:** precision, score precision, precision del resultado

**Términos relacionados:** unsupported_addition_score, contradiction_score

**Nota técnica:** Campo técnico de validación conservado por compatibilidad.

### retention_score - Conservación de contenido

Métrica que estima cuánto contenido importante se conserva.

Una puntuación alta sugiere que la salida mantiene mejor la intención original.

**Cuándo usarlo:** Revísala si el prompt original tiene muchos detalles importantes.

**Ejemplo:** Un retention_score bajo requiere revisar el resultado antes de usarlo.

**Alias de búsqueda:** retention, retencion, conservacion

**Términos relacionados:** semantic_preservation, validation

**Nota técnica:** Campo técnico de validación conservado por compatibilidad.

### unsupported_addition_score - Añadidos no respaldados

Métrica que detecta información añadida sin apoyo en el prompt original.

Ayuda a controlar que el resultado no invente requisitos.

**Cuándo usarlo:** Revísala en validación avanzada.

**Ejemplo:** Sería problemático añadir una herramienta que el usuario no pidió.

**Alias de búsqueda:** unsupported addition, anadidos, inventado

**Términos relacionados:** precision_score, validation

**Nota técnica:** Campo técnico de validación conservado por compatibilidad.
