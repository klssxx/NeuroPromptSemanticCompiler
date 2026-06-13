# NeuroPrompt Semantic Compiler

> Transforma solicitudes informales en especificaciones estructuradas, reutilizables, versionadas, verificables y exportables para distintos modelos de IA.

**NeuroPrompt Semantic Compiler** es una aplicación de escritorio ligera que convierte prompts desordenados en instrucciones claras y estructuradas usando un flujo de compilación semántico. Funciona 100% local, sin telemetría, sin conexión a internet.

## Características

- **Modo sencillo**: Escribe una petición breve y obtén un prompt estructurado sin complicaciones
- **Modo avanzado**: Control total sobre las 7 secciones del prompt (contexto, tarea, especificaciones, calidad, formato, verificación)
- **Variables rellenables**: Usa `{{variable}}` en tus prompts y rellénalas antes de compilar
- **Plantillas reutilizables**: Crea, edita, duplica y organiza plantillas por categoría
- **Historial de versiones**: Cada compilación se guarda automáticamente; compara versiones con diff visual
- **Exportación triple**: Markdown, JSON (esquema estable) y texto plano
- **Perfiles de modelo**: Hermes, Codex, Claude, GPT, Gemini, Qwen, DeepSeek, Llama, Mistral, genérico
- **Validador de campos**: Detecta variables sin rellenar, campos vacíos y prompts muy cortos
- **Guardado de proyectos**: Guarda y carga proyectos en formato JSON
- **Bilingüe**: Español e inglés
- **Tema oscuro/claro**: Interfaz adaptada para KDE Plasma X11

## Capturas

*Las capturas de pantalla se añadirán en una actualización posterior.*
Mientras tanto, puedes ver la [demo web estática](web-demo/).

## Instalación local

### Requisitos

- Python 3.10+
- PySide6 6.11+

### Opción A: Con uv (recomendado)

```bash
cd NeuroPromptSemanticCompiler
uv venv .venv
uv pip install -r requirements.txt
./scripts/run.sh
```

### Opción B: Con venv estándar

```bash
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

## Uso básico

1. **Escribe** tu prompt informal en el campo principal
2. **Selecciona** un perfil (AUTO recomendado) y un modelo objetivo
3. **Pulsa** "COMPILAR PROMPT"
4. **Copia** el resultado o expórtalo en Markdown, JSON o TXT

### Atajos de teclado

| Atajo | Acción |
|---|---|
| Ctrl+Enter | Compilar prompt |
| Ctrl+Shift+C | Copiar prompt compilado |
| Ctrl+N / Ctrl+L | Nuevo prompt (limpiar) |
| Ctrl+O | Cargar archivo de texto |
| Ctrl+S | Guardar resultados |
| Ctrl+G | Guardar proyecto |
| Ctrl+Shift+O | Cargar proyecto |
| Ctrl+Shift+V | Rellenar variables |
| Ctrl+M | Cambiar modo simple/avanzado |
| F1 | Abrir ayuda (glosario) |

## Estructura del proyecto

```
NeuroPromptSemanticCompiler/
├── src/
│   └── npsc_gui/
│       ├── main.py              # Punto de entrada GUI
│       ├── main_window.py       # Ventana principal (modos simple/avanzado)
│       ├── controller.py        # Controlador de compilación
│       ├── settings.py          # Persistencia de configuración
│       ├── theme.py             # Tema visual (dark/light)
│       ├── template_page.py     # Página de plantillas
│       ├── history_page.py      # Página de historial/diff
│       └── components/          # Componentes UI reutilizables
├── src/
│   ├── variables.py             # Sistema de variables {{nombre}}
│   ├── template_manager.py      # CRUD de plantillas
│   ├── version_history.py       # Historial de versiones + diff
│   ├── export_manager.py        # Exportación Markdown/JSON/TXT
│   ├── field_validator.py       # Validador de campos
│   ├── npsc_service.py          # Servicio de compilación
│   ├── nsl_compiler.py          # Compilador NSL
│   ├── semantic_extractor.py    # Extracción semántica
│   └── ...                      # Otros módulos core
├── tests/                       # 93 tests (pytest)
├── examples/                    # 7 ejemplos de uso
├── web-demo/                    # Demo estática para GitHub Pages
├── docs/                        # Documentación
├── scripts/
│   ├── run.sh                   # Lanzar aplicación
│   ├── smoke_test.sh            # Verificación rápida
│   └── setup_venv_instructions.sh
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Exportaciones

### Markdown
Documento estructurado con secciones, metadatos, prompt compilado, NSL y reporte de validación.

### JSON
```json
{
  "$schema": "neuroprompt/compilation-result/v1",
  "generator": "NeuroPrompt Semantic Compiler",
  "exported_at": "2026-06-13T...",
  "result": { ... }
}
```

### TXT
Solo el prompt compilado, listo para copiar.

## Perfiles de modelo

| Perfil | Estructura | Uso recomendado |
|---|---|---|
| AUTO | Auto-detección | Dejar que la app elija |
| FAST | Compacto | Tareas simples y rápidas |
| STANDARD | Equilibrado | Uso general |
| ADVANCED | Operativo, orientado a archivos | Programación, arquitectura |
| ROP | Fases, escenarios, evidencias | Decisiones complejas |
| RESEARCH_MAX | Máxima preservación | Investigación profunda |

## Tests

```bash
# Todos los tests
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -v

# Smoke test (verificación rápida)
./scripts/smoke_test.sh
```

**Estado actual:** 93 tests pasando.

## Limitaciones conocidas

- La aplicación no envía nada a internet; es 100% local
- La web demo es estática y no tiene todas las funcionalidades de la app de escritorio
- Los temas visuales están optimizados para KDE Plasma X11
- No incluye instalador gráfico (se ejecuta desde código fuente)

## Roadmap

- [ ] Secciones editables en modo avanzado (contexto, tarea, especificaciones...)
- [ ] Instalador gráfico para Linux
- [ ] Más temas visuales
- [ ] Soporte para más idiomas
- [ ] Plugins de exportación

## Privacidad

Esta aplicación:
- **No** se conecta a internet
- **No** envía telemetría
- **No** accede a archivos del sistema fuera de su directorio de datos
- **No** incluye claves API
- Todos los datos se almacenan localmente en `~/.local/share/neuro-prompt-semantic-compiler/`

## Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del repositorio
2. Crea una rama para tu feature
3. Ejecuta los tests antes de hacer commit
4. Envía un pull request

## Licencia

Ver `LICENSE_DECISION_REQUIRED.md` — Pendiente de elección por el propietario del proyecto.

---

**Estado del proyecto:** Funcional y listo para uso local. Pendiente de revisión humana antes de publicación.
