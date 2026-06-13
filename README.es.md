🌐 **Language:** [English](README.md) · [Español](README.es.md)

# NeuroPrompt Semantic Compiler

NeuroPrompt Semantic Compiler convierte prompts humanos desordenados en instrucciones compactas, estructuradas y legibles por modelo usando NSL v0.1 y NPSC-HYBRID/1.0.

No es un resumidor ciego. Es un compilador semántico de intención: preserva objetivos, restricciones, riesgos, contexto del modelo destino y metadatos de verificación mientras hace que los prompts sean más fáciles de usar con sistemas de IA.

## Frase central

Not fewer words by losing meaning; more power per token by transmitting structured intention.

## Funciones

- GUI de escritorio PySide6 / Qt Widgets con modo sencillo y modo experto.
- CLI para compilación reproducible de prompts.
- Perfiles semánticos: `FAST`, `STANDARD`, `ADVANCED`, `ROP`, `RESEARCH_MAX`, `AUTO`.
- Modelos destino: GPT, Codex, Claude, Gemini, Qwen, DeepSeek, Llama, Mistral, Hermes, generic y custom.
- Modos de privacidad: `full_original`, `hash_only`, `redacted_preview`.
- Base bilingüe: castellano e inglés en consola, etiquetas clave de GUI y metadatos del lanzador.
- Local-first: sin telemetría, sin llamadas a APIs externas y sin ejecución remota.

## Inicio rápido desde código fuente

```bash
cd NeuroPromptSemanticCompiler
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements.txt
./run_gui.sh
```

Ejemplo CLI:

```bash
PYTHONPATH=src .venv/bin/python -m npsc_cli \
  --text "Crea una herramienta local. No uses sudo. Evita acciones destructivas." \
  --out outputs/demo \
  --target codex \
  --profile auto \
  --privacy-mode hash_only \
  --language es
```

Etiquetas CLI en inglés:

```bash
PYTHONPATH=src .venv/bin/python -m npsc_cli \
  --text "Build a local tool. Do not use sudo." \
  --out outputs/demo-en \
  --target codex \
  --profile auto \
  --language en
```

## Compatibilidad Linux

El proyecto está diseñado para funcionar en la mayoría de distribuciones Linux modernas con Python 3.10+ y PySide6/Qt 6:

- Ubuntu, Xubuntu, Kubuntu, Debian y derivadas
- Fedora y derivadas
- Arch, CachyOS, Manjaro y derivadas
- Otros escritorios compatibles con XDG y launchers Qt/GTK

La GUI usa Qt Widgets nativos, no Electron, no web view y evita efectos pesados de GPU. Debería funcionar en GPUs antiguas siempre que el plugin Qt de plataforma funcione correctamente.

Notas por distribución: [docs/LINUX_INSTALL.es.md](docs/LINUX_INSTALL.es.md)

## Archivos de salida

Cada ejecución exporta artefactos únicos:

- `canonical_nsl.nsl`
- `compiled_safe.nsl`
- `compiled_balanced.nsl`
- `compiled_aggressive.nsl`
- `optimized_prompt.txt`
- `reconstructed_prompt.txt`
- `hybrid_semantic_prompt.md`
- `hybrid_semantic_prompt.json`
- `semantic_ir.json`
- `semantic_analysis.json`
- `semantic_seeds.json`
- `profile_selection_report.json`
- `profile_report.json`
- `context_loss_report.md`
- `context_loss_report.json`
- `token_estimate_report.md`
- `token_estimate_report.json`
- `run_summary.md`

Archivos principales:

- `optimized_prompt.txt`: prompt listo para copiar a otro modelo o agente.
- `canonical_nsl.nsl`: representación compacta canónica en NSL.
- `hybrid_semantic_prompt.*`: bundle completo de trazabilidad.

## Launcher e icono

El icono del lanzador se entrega como SVG y como PNGs renderizados en `assets/icons/`.

Metadatos de escritorio:

- `NeuroPromptSemanticCompiler.desktop`
- `packaging/desktop/neuro-prompt-semantic-compiler.desktop`

Instalación local sin sudo:

```bash
bash tools/install_local_user.sh
```

Desinstalación:

```bash
bash tools/uninstall_local_user.sh
```

## Validación

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
bash tools/check_runtime.sh
```

Comprobaciones opcionales de proyecto/release:

```bash
bash tools/verify_project.sh
bash tools/build_release.sh
```

## Empaquetado para GitHub/GitLab

Antes de publicar, excluye carpetas generadas como `.venv/`, `staging/`, `_backups/`, `outputs/`, `artifacts/`, `dist/`, `build/`, `*.egg-info`, `__pycache__/` y `.pytest_cache/`.

Puedes generar un archivo limpio con:

```bash
bash tools/export_source_clean.sh
```

## Limitaciones

- La estimación de tokens es aproximada (`chars / 4`).
- La extracción semántica es heurística, no basada en ML.
- La cobertura completa de textos GUI aún no está traducida al 100%; launcher, settings clave y CLI ya tienen ruta bilingüe.
- Antes de publicar una release final conviene hacer una revisión visual humana en una sesión gráfica real, no solo con `QT_QPA_PLATFORM=offscreen`.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Ver `LICENSE` para más detalles.
