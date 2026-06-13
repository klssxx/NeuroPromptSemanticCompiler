🌐 **Idioma:** [English](README.md) · [Español](README.es.md)

# NeuroPrompt Semantic Compiler

> Herramienta de escritorio que transforma solicitudes informales para IA en especificaciones estructuradas, reutilizables, versionadas y exportables.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PySide6 6.11+](https://img.shields.io/badge/PySide6-6.11+-green.svg)](https://www.qt.io/qt-for-python)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-103%20passed-brightgreen.svg)](#validación)

**NeuroPrompt Semantic Compiler (NPSC)** es una aplicación de escritorio ligera y **100% local** que convierte prompts desordenados en instrucciones claras, estructuradas, versionadas y exportables. Funciona sin conexión, sin telemetría y sin claves API.

---

## El problema

Escribir buenos prompts es difícil. La mayoría se redactan deprisa, mezclan varias intenciones, omiten restricciones y resultan imposibles de reutilizar, comparar o entregar a otra persona. NPSC resuelve esto con un proceso pequeño y opinado:

```text
Petición informal
   → especificación estructurada
   → validación de campos
   → perfil de modelo
   → prompt versionado y exportable
```

---

## Funcionalidades

- **Modo sencillo** — Escribe una petición breve y obtén un prompt estructurado con un solo clic.
- **Modo avanzado** — Edita individualmente las seis secciones del prompt (contexto/rol, consulta/tarea, especificaciones, criterios de calidad, formato de salida, verificación) y guárdalas como archivos `.nsect.json`.
- **Plantillas reutilizables** — Crea, edita, duplica, busca y etiqueta plantillas.
- **Variables rellenables** — Usa marcadores `{{variable}}` y rellénalos antes de compilar.
- **Historial de versiones** — Cada compilación se guarda localmente; compara dos versiones con un diff visual.
- **Exportación triple** — Markdown, JSON (esquema estable) y texto plano.
- **Perfiles de modelo** — `AUTO`, `FAST`, `STANDARD`, `ADVANCED`, `ROP`, `RESEARCH_MAX`; destinos Hermes, Codex, Claude, GPT, Gemini, Qwen, DeepSeek, Llama, Mistral, genérico.
- **Validador de campos** — Detecta campos vacíos, variables sin rellenar y prompts demasiado cortos antes de compilar.
- **Guardado de proyectos** — Persiste sesiones completas como JSON.
- **Bilingüe** — Español e inglés.
- **Tema oscuro/claro** — Optimizado para KDE Plasma sobre X11.
- **Demo web estática** — Consulta [`web-demo/`](web-demo/) para una vista previa del flujo principal sin instalar nada.

---

## Instalación

### Requisitos

- Python 3.10 o superior
- PySide6 6.11 o superior

### Opción A — con `uv` (recomendado)

```bash
git clone https://github.com/<tu-usuario>/NeuroPromptSemanticCompiler.git
cd NeuroPromptSemanticCompiler
uv venv .venv
uv pip install -r requirements.txt
./scripts/run.sh
```

### Opción B — con venv estándar

```bash
git clone https://github.com/<tu-usuario>/NeuroPromptSemanticCompiler.git
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

---

## Uso

1. Escribe tu petición informal en el editor principal.
2. Elige un perfil (por defecto `AUTO`) y un modelo destino.
3. Pulsa **COMPILAR PROMPT** (o `Ctrl+Enter`).
4. Copia el resultado o expórtalo en Markdown, JSON o TXT.

### Atajos de teclado

| Atajo | Acción |
|---|---|
| `Ctrl+Enter` | Compilar prompt |
| `Ctrl+Shift+C` | Copiar prompt compilado |
| `Ctrl+N` / `Ctrl+L` | Nuevo prompt |
| `Ctrl+O` | Abrir archivo de texto |
| `Ctrl+S` | Guardar resultados |
| `Ctrl+G` | Guardar proyecto |
| `Ctrl+Shift+O` | Cargar proyecto |
| `Ctrl+Shift+V` | Rellenar variables |
| `Ctrl+M` | Alternar modo sencillo / avanzado |
| `F1` | Abrir glosario / ayuda |

### Demo web (sin instalación)

Abre [`web-demo/index.html`](web-demo/index.html) en cualquier navegador o visita la URL de GitHub Pages del repositorio cuando esté habilitada.

---

## Estructura del proyecto

```text
NeuroPromptSemanticCompiler/
├── src/
│   ├── npsc_gui/              # Capa GUI con PySide6
│   │   ├── main_window.py     # Ventana principal, modos, integración
│   │   ├── advanced_mode_page.py
│   │   ├── about_dialog.py
│   │   ├── export_preview.py
│   │   ├── integration.py
│   │   ├── template_page.py
│   │   ├── tooltips.py
│   │   └── ...
│   ├── variables.py           # Detección y relleno de {{variables}}
│   ├── template_manager.py    # CRUD de plantillas
│   ├── version_history.py     # Snapshots + diff visual
│   ├── export_manager.py      # Exportadores Markdown / JSON / TXT
│   ├── field_validator.py     # Validación del formulario
│   ├── npsc_service.py        # Punto de entrada de la compilación
│   ├── nsl_compiler.py        # Compilador NSL
│   ├── semantic_extractor.py  # Extracción semántica ligera
│   ├── token_estimator.py     # Conteo de tokens con tiktoken
│   └── ...
├── tests/                     # 103 tests pasando (pytest)
├── examples/                  # Ejemplos de peticiones informales
├── web-demo/                  # Demo HTML estática
├── docs/                      # Documentación adicional
├── scripts/
│   ├── run.sh                 # Lanzar la aplicación
│   ├── smoke_test.sh          # Verificación rápida
│   └── setup_venv_instructions.sh
├── requirements.txt
├── pyproject.toml
└── README.es.md
```

---

## Validación

```bash
# Suite de tests (no requiere display cuando se ejecuta headless)
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -q

# O usando el smoke test incluido
./scripts/smoke_test.sh
```

Estado actual: **103 tests pasando** (suite no-GUI). Los tests de widgets GUI se ejecutan manualmente con un display real.

---

## Formatos de exportación

### Markdown

Documento estructurado con secciones, metadatos, prompt compilado, NSL e informe de validación.

### JSON

```json
{
  "$schema": "neuroprompt/compilation-result/v1",
  "generator": "NeuroPrompt Semantic Compiler",
  "exported_at": "2026-06-13T...",
  "result": { /* objeto de resultado estable y versionado */ }
}
```

### TXT

Solo el prompt compilado, listo para copiar y pegar.

---

## Perfiles de modelo

| Perfil | Estilo | Uso recomendado |
|---|---|---|
| `AUTO` | Auto-detección | Dejar que la app elija |
| `FAST` | Compacto | Tareas simples y rápidas |
| `STANDARD` | Equilibrado | Uso general |
| `ADVANCED` | Operativo, orientado a archivos | Programación, arquitectura |
| `ROP` | Fases, escenarios, evidencias | Decisiones complejas |
| `RESEARCH_MAX` | Máxima preservación | Investigación profunda |

---

## Privacidad

- **No** se conecta a internet
- **No** envía telemetría
- **No** utiliza claves API
- **No** accede a archivos fuera de su directorio de datos
- Todos los datos se almacenan localmente en `~/.local/share/neuro-prompt-semantic-compiler/`

Auditoría de privacidad específica: [`docs/PUBLICATION_PRIVACY_AUDIT.md`](docs/PUBLICATION_PRIVACY_AUDIT.md).

---

## Roadmap

- [ ] Instalador Linux empaquetado (AppImage / Flatpak)
- [ ] Más temas visuales
- [ ] Más idiomas
- [ ] Plugins de exportación
- [ ] Formato de intercambio offline de plantillas
- [ ] Capturas reales y demo web enriquecida (build TypeScript)

Detalles de empaquetado: [`docs/FINAL_PATH_AUDIT.md`](docs/FINAL_PATH_AUDIT.md).

---

## Capturas

*Las capturas reales de la aplicación se añadirán en una actualización futura. Mientras tanto, la [demo web estática](web-demo/) ofrece una vista previa visual del flujo principal.*

---

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del repositorio.
2. Crea una rama para tu feature.
3. Asegúrate de que `pytest` y `scripts/smoke_test.sh` pasen.
4. Envía un pull request.

Más detalles en [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Ver [`LICENSE`](LICENSE).

---

## Idioma

Este README también está disponible en inglés: [`README.md`](README.md).
