# Metodo de evaluacion

NPSC separa reduccion tecnica, expansion de prompt y fidelidad semantica. No llama compresion a una salida que crece.

## Benchmark local

```bash
bash tools/benchmark_quality.sh
```

Artefactos generados:

- `outputs/benchmark/quality_benchmark.json`
- `outputs/benchmark/quality_benchmark.md`

## Metricas principales

- `original_token_estimate`: estimacion aproximada de tokens del prompt original.
- `nsl_token_estimate`: estimacion aproximada de tokens del NSL.
- `execution_prompt_token_estimate`: estimacion aproximada de tokens del prompt listo.
- `nsl_size_ratio`: `nsl/original`. Menor que 1.0 es reduccion; mayor que 1.0 es expansion.
- `execution_size_ratio`: `execution_prompt/original`. ROP y RESEARCH_MAX pueden expandir deliberadamente.
- `nsl_token_change_percent`: cambio porcentual del NSL.
- `execution_token_change_percent`: cambio porcentual del prompt listo.
- `retention_score`: cuanto contenido importante del original se conserva.
- `precision_score`: penaliza añadidos no respaldados y contradicciones.
- `unsupported_addition_score`: mide añadidos sin origen claro en usuario, politica, adaptador o plantilla.
- `contradiction_score`: mide contradicciones detectadas.
- `constraint_traceability_score`: mide si las restricciones tienen origen y aparecen trazadas.
- `utility_score`: utilidad estimada de la salida.
- `risk_score`: riesgo agregado.

## Interpretacion

Si un ratio es mayor que `1.0`, hay expansion. Si es menor que `1.0`, hay reduccion. Para prompts extremadamente breves, `compact_nsl.nsl` puede crecer por overhead de esquema; en FAST se marca con `fast_nsl_schema_overhead_for_short_prompt`.

La compresion negativa no se oculta. El benchmark separa NSL compacto de `execution_prompt.txt`.
