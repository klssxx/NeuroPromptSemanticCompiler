# CLI

Uso básico:

```bash
python3 src/npsc_cli.py --text "Organiza una lista de tareas." --out outputs/direct --target codex
```

Perfiles semánticos:

```bash
python3 src/npsc_cli.py --text "Corrige la ortografía." --out outputs/fast --target gpt --profile fast
python3 src/npsc_cli.py --input examples/app_builder_prompt.txt --out outputs/advanced --target codex --profile advanced
python3 src/npsc_cli.py --text "Evalúa estrategia con riesgos." --out outputs/rop --target gpt --profile rop
python3 src/npsc_cli.py --input examples/research_prompt.txt --out outputs/research --target claude --profile research_max
python3 src/npsc_cli.py --text "Prompt ambiguo con restricciones." --out outputs/auto --target codex --profile auto
```

`--profile` controla la intención semántica. `--level` controla la compresión técnica.

Artefactos principales:

- `hybrid_semantic_prompt.md`: mejor salida para pegar en otra IA.
- `hybrid_semantic_prompt.json`: salida machine-oriented.
- `semantic_ir.json`: representación intermedia.
- `canonical_nsl.nsl`: NSL canónico.
- `context_loss_report.md/json`: validación de pérdida.
