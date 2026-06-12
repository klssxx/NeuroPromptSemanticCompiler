---
version: alpha
name: NeuroPrompt
description: Centro de control semántico offline para compilación de prompts. Híbrido entre utilidad de escritorio y compilador técnico.
colors:
  primary: "#2B8BC8"
  secondary: "#A4A8AE"
  tertiary: "#4CB8F5"
  neutral: "#272B32"
  success: "#30B87A"
  warning: "#E5A51A"
  error: "#E04E65"
  info: "#4CB8F5"
  bg-base: "#1A1D20"
  bg-surface: "#21242A"
  bg-card: "#272B32"
  bg-elevated: "#2F333B"
  bg-input: "#1C1F22"
  bg-sidebar: "#1E2126"
  text-primary: "#E8EAED"
  text-secondary: "#A4A8AE"
  text-muted: "#6C717A"
  border-subtle: "#363A42"
  border-input: "#4A5060"
  border-focus: "#2B8BC8"
typography:
  h1:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5
  metric:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: 800
    lineHeight: 1
  label:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.3px"
    fontFeature: "c2sc, smcp"
  mono:
    fontFamily: "JetBrains Mono"
    fontSize: 11px
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 4px
  md: 8px
  lg: 12px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 7px 18px
  button-primary-hover:
    backgroundColor: "#3CA4E0"
  button-secondary:
    backgroundColor: "{colors.bg-elevated}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.sm}"
    padding: 5px 12px
  button-danger:
    backgroundColor: transparent
    textColor: "{colors.error}"
    rounded: "{rounded.sm}"
  card:
    backgroundColor: "{colors.bg-card}"
    borderColor: "{colors.border-subtle}"
    rounded: "{rounded.md}"
    padding: 14px
  card-hover:
    borderColor: "{colors.tertiary}"
  status-chip-ok:
    backgroundColor: "rgba(48,184,122,0.12)"
    textColor: "{colors.success}"
  status-chip-warn:
    backgroundColor: "rgba(229,165,26,0.12)"
    textColor: "{colors.warning}"
  status-chip-error:
    backgroundColor: "rgba(224,78,101,0.12)"
    textColor: "{colors.error}"
  status-chip-info:
    backgroundColor: "rgba(76,184,245,0.12)"
    textColor: "{colors.info}"
  nav-item-active:
    backgroundColor: "rgba(43,139,200,0.1)"
    textColor: "{colors.tertiary}"
    borderLeft: "2px solid {colors.tertiary}"
  circle-ring:
    border: "4px solid {colors.border-subtle}"
    size: 140px
  circle-ring-active:
    borderColor: "{colors.primary}"
  circle-ring-success:
    borderColor: "{colors.success}"
---

## Overview

NeuroPrompt adopta el lenguaje visual de una utilidad de escritorio premium (tipo Driver Booster / Auslogics BoostSpeed) con identidad propia: azul profundo como acento, fondo oscuro elegante (no negro puro), y un híbrido entre indicador circular dominante y organización modular.

El diseño prioriza tres cosas simultáneamente: (1) la acción principal ("Mejorar prompt") siempre visible y prominente, (2) el prompt accesible sin navegar, y (3) resultados con colores semánticos inmediatos.

## Colors

- **Primary (#2B8BC8):** Azul profundo para botones primarios, enlaces y acento de navegación. Distinto del azul Breeze KDE (#3DAEE9) para identidad propia.
- **Tertiary (#4CB8F5):** Azul brillante para métricas activas y highlights. Uso limitado a valores que merecen atención.
- **Success (#30B87A):** Verde para preservación OK, restricciones cumplidas, operaciones completadas sin errores.
- **Warning (#E5A51A):** Ámbar para advertencias, pérdidas parciales, estados que requieren atención.
- **Error (#E04E65):** Rojo para errores críticos, validación fallida, pérdida de restricciones. Nunca decorativo.
- **Info (#4CB8F5):** Azul brillante para estados de progreso e información neutral destacada.

## Typography

Inter para toda la interfaz (coincide con la fuente del tema actual). JetBrains Mono para NSL y JSON en pestañas técnicas.

Jerarquía por peso y tamaño, no por color:
- h1 (28px/800): valor métrico principal del círculo
- h2 (13px/700): títulos de sección y tarjetas
- body (12px/400): texto general
- metric (20px/800): valores numéricos en tarjetas de resultado
- label (10px/700/sc): etiquetas uppercase compactas

## Layout

Layout híbrido con tres zonas:

1. **Sidebar izquierda (190px):** Navegación agrupada en 3 secciones — Principal (Resumen, Compilar, Resultados, Validación), Herramientas (Perfiles, Glosario), Sistema (Configuración).
2. **Contenido central:** Hero = círculo de preservación (140px) + panel de prompt lado a lado. Debajo: 4 tarjetas de resultado semántico. Al final: 3 tarjetas de herramientas.
3. **Barra de progreso minimalista (3px):**_strip_ horizontal en la parte inferior del contenido, no un QProgressBar tradicional.

## Components

Los componentes clave se reutilizan entre vistas:

- **StatusChip:** pastilla con dot + texto, 4 variantes cromáticas (ok/warn/error/info). Aparece en el header y en resultados.
- **CircleIndicator:** anillo circular con valor numérico central. Estados: idle, active (azul), success (verde), error (rojo).
- **ResultCard:** tarjeta cuadrada con valor grande + label pequeña. Color del valor determinado por semántica.
- **ToolCard:** tarjeta rectangular con icono + título + descripción.
- **PromptPanel:** textarea con tabs internos (Original / Listo / Informe) y footer de selects.
- **NavGroup:** grupo de items de navegación con label uppercase.

## Elevation

Sin sombras reales (GTX 660). Separación por:
- Diferencia de fondo (bg-base < bg-card < bg-elevated)
- Bordes de 1px border-subtle
- Border-color accent en hover

## Components

`button-primary` es el único botón con color sólido. Todo lo demás es outline o ghost. Esto mantiene la jerarquía clara: si hay un botón azul en pantalla, es la acción principal.
