# Technical Spec

## Architecture

Pipeline modular:

1. semantic_extraction
2. compilation_profile_resolution
3. auto_profile_selection
4. USER_INTENT_IR
5. semantic_seed_mapping
6. NSL_compilation
7. model_target_adaptation
8. TARGET_ADAPTER_LAYER
9. EFFECTIVE_PROMPT_IR
10. compact_nsl / execution_prompt / audit_bundle
11. context_loss_verification
12. reports_and_outputs

## NSL Fields

`ID TARGET R G CTX T C P TOOLS IN OUT STYLE RISKS SEEDS VERIFY`

## Compilation Profiles

La configuración canónica vive en `configs/compilation_profiles.json`.

Módulos:

- `src/compilation_profiles.py`: carga, valida y aplica perfiles semánticos.
- `src/profile_selector.py`: selecciona `AUTO` con heurísticas de longitud, tipo de tarea, riesgo, restricciones, evidencia y pérdida de contexto.
- `src/rop_template.py`: ROP/1.0 canónico.
- `src/semantic_ir.py`: IR `NPSC-HYBRID/1.0`.
- `src/hybrid_output.py`: genera `execution_prompt.txt`, `compact_nsl.nsl` y `audit_bundle.md`.
- `src/npsc_service.py`: servicio común para CLI y GUI.

Perfiles:

- `FAST`: compresión alta, baja verbosidad, validación ligera.
- `STANDARD`: perfil por defecto, equilibrio general.
- `ADVANCED`: preservación y estructura para código, arquitectura, docs y tareas complejas.
- `ROP`: Reality Optimization Protocol, con plantilla canónica seleccionable.
- `RESEARCH_MAX`: máxima preservación y validación estricta.
- `AUTO`: resuelve a uno de los perfiles anteriores y reporta `auto_selected_profile`, `selection_reason`, `risk_flags` y `fallback_profile`.

Los perfiles semánticos no sustituyen los perfiles de modelo. `--profile` controla intención semántica; `--target` controla modelo destino; `--level` controla compresión técnica.

## Seed Mapper

Selecciona seeds por:

- campos detectados en extractor
- restricciones críticas
- target model
- nivel de compresión
- perfil semántico aplicado

## Compression Levels

- safe: máxima preservación
- balanced: mejor equilibrio
- aggressive: máxima densidad con alertas de riesgo

El perfil puede recomendar un nivel técnico por defecto, pero `--level` puede sobrescribirlo. Si ambos entran en conflicto, `profile_report.json` y `run_summary.md` lo explican.

## Reconstruction

Reconstruye un execution prompt adaptado a target con contrato de salida operativo.

El execution prompt puede ser modulado por perfil:

- `FAST`: versión breve.
- `ADVANCED`: estructura ampliada.
- `ROP`: plantilla ROP integrada.
- `RESEARCH_MAX`: expansión deliberada, trazabilidad y validación estricta visible.

## Capas semánticas

La IR `NPSC-HYBRID/1.0` separa `USER_INTENT_IR`, `COMPILER_TRACE`, `POLICY_LAYER`, `TARGET_ADAPTER_LAYER` y `EFFECTIVE_PROMPT_IR`.

Los orígenes válidos son `user_explicit`, `user_inferred`, `product_policy`, `target_adapter`, `profile_template` y `compiler_internal`.

## Context Loss Verification

Compara original, semántica, NSL y execution prompt. Conserva score agregado por compatibilidad y expone `retention_score`, `precision_score`, `unsupported_addition_score`, `contradiction_score`, `constraint_traceability_score`, `compression_ratio_nsl`, `expansion_ratio_execution_prompt`, `utility_score` y `risk_score`.

Modo `--strict` valida contra `strict_policy` de `configs/compiler_defaults.json`:

- `min_score`
- `max_critical_losses`
- `fail_on_missing_safety`
- `fail_on_missing_goal`

La verificación también aplica reglas por perfil:

- `FAST`: advierte por pérdidas no críticas y falla por pérdida crítica.
- `STANDARD`: acepta pérdida baja o moderada sin pérdida crítica.
- `ADVANCED`: exige objetivo, restricciones y contrato de salida.
- `ROP`: exige protocolo de razonamiento, revisión adversarial, convergencia, autocrítica y output schema.
- `RESEARCH_MAX`: falla ante pérdida de matices importantes, restricciones, objetivos, formato o contexto crítico.

## Model Profiles

Perfiles en `configs/model_profiles.json` para:
`gpt,codex,hermes,claude,gemini,qwen,deepseek,llama,mistral,custom,gpt55_codex,generic`.

## GUI

La GUI principal está en `src/npsc_gui/` y se lanza con `./run_gui.sh`.

No usa el motor duplicado de la GUI externa ni `NSL-GUI/0.1`; llama directamente al core:

`extract_semantics -> apply_profile_to_semantics -> suggest_seeds -> compile_to_nsl -> reconstruct_prompt -> build_profile_optimized_prompt -> verify_context_loss -> build_semantic_ir -> export_artifacts`.

La GUI Tkinter en `app/` permanece como compatibilidad secundaria.

La GUI Qt usa worker con señales para progreso, cancelación cooperativa, errores y estado bloqueado por strict.

## Extension Points

- tokenizer real
- aprendizaje personalizado de seeds
- benchmark suite
- GUI local avanzada
- integración flujos Hermes/Codex
