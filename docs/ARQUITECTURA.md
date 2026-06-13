# Arquitectura

El core es independiente de la GUI.

Flujo:

`extract_semantics -> apply_profile_to_semantics -> suggest_seeds -> compile_to_nsl -> reconstruct_prompt -> build_profile_optimized_prompt -> verify_context_loss -> build_semantic_ir -> export_artifacts`

Módulos clave:

- `src/npsc_service.py`: servicio común para CLI y GUI.
- `src/compilation_profiles.py`: perfiles semánticos.
- `src/profile_selector.py`: AUTO.
- `src/rop_template.py`: ROP/1.0 canónico.
- `src/semantic_ir.py`: NPSC-HYBRID/1.0.
- `src/npsc_gui/`: GUI Qt Widgets.

La GUI secundaria no es dependencia de ejecución.
