# Contextual Help Refinement Report

Fecha: 2026-06-02

## Diagnostico

Se encontraron ayudas largas aplicadas con `apply_tooltip(...)` y `setToolTip(...)` en superficies demasiado grandes:

- Sidebar: botones de seccion con explicaciones largas.
- Tarjetas del panel principal: tooltip en toda la tarjeta.
- Barra de estado: tooltip en cada etiqueta de estado.
- Editor de prompt y areas de resultados: tooltips sobre zonas extensas.
- Pestañas de resultados: `setToolTip` en widget y tab.
- Paginas informativas: tooltips sobre `QTextEdit`.

Clasificacion:

1. Explicacion larga contextual: secciones principales, perfil, target, compresion, strict, privacidad, modelo custom y pestanas de resultados.
2. Ayuda breve de boton: mejorar prompt, copiar, guardar, abrir carpeta, limpiar, cargar ejemplo, cancelar.
3. Tooltip invasivo: tarjetas completas, sidebar, status bar, areas de texto, widgets contenedores y pestañas completas.

## Cambios aplicados

- Nuevo componente `ContextHelpButton` basado en `QToolButton`.
- Nueva burbuja `ContextHelpPopover` basada en `QFrame` con `QLabel` y `wordWrap=True`.
- Iconos `?` en la esquina superior derecha de cada seccion principal.
- Iconos `?` junto a opciones tecnicas: perfil semantico, modelo destino, compresion, validacion estricta, privacidad, modelo custom y modo avanzado.
- Tooltips largos retirados de contenedores y areas extensas.
- Tooltips breves conservados solo en botones operativos.

## Verificacion esperada

- La ayuda aparece solo al pasar el cursor o enfocar el icono `?`.
- Escape cierra la burbuja.
- Cambiar de seccion o pestaña cierra burbujas activas.
- La GUI sigue siendo usable a 1366x768.
