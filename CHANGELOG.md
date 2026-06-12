# Changelog

## 1.0.0rc2 - 2026-06-02

- Added searchable in-app **Glosario** before **Acerca de**, backed by `ui_glossary_es.json`.
- Replaced visible jargon with human labels: `Guardar resultados`, `Informe completo`, `JSON para programas`, `NSL compacto`, `Reglas semánticas` and `Restricciones y origen`.
- Preserved internal CLI/service values for profiles, technical levels and privacy modes.
- Added generated `docs/GLOSARIO_ES.md` and vocabulary audit documentation.
- Added glossary/UX tests and QA screenshots for glossary, help and simple/advanced labels.

## 1.0.0rc1 - 2026-06-02

- Fixed `hash_only` privacy leak in public service results.
- Clarified output hierarchy: `execution_prompt.txt` is the primary prompt to copy; audit bundles are traceability outputs.
- Added honest ratio metrics: `nsl_size_ratio`, `execution_size_ratio`, token estimates and token change percentages.
- Made FAST use sparse compact NSL in aggressive mode and reduced decorative seeds.
- Added model target `auto` with service-side safe fallback.
- Updated Qt GUI copy action to copy the prompt ready for use, not the audit bundle.
- Added local user install/uninstall/runtime scripts without sudo.
- Updated release builder to create clean tarball, wheel, inspected `.deb`, `SHA256SUMS` and release manifest.
- Validated PySide6 offscreen screenshots and packaged GUI QA screenshots.

## 0.1.0 - 2026-06-02

- Added semantic compilation profiles: FAST, STANDARD, ADVANCED, ROP, RESEARCH_MAX and AUTO.
- Added canonical `ROP/1.0`.
- Added `NPSC-HYBRID/1.0` JSON/Markdown output.
- Added lossless SHA-256 traceability.
- Added Qt Widgets GUI with QSS, SVG icon and centralized tooltips.
- Added AppStream, desktop metadata, release script and documentation.

## 0.1.0
- Initial MVP release of NeuroPrompt Semantic Compiler.
- NSL v0.1 compiler, parser, reconstructor, and verifier.
- Model adapters and semantic seed mapping.
- CLI, reports, tests, and demo tooling.
