# Visual Polish Plan — NPSC v1.0.0rc2

Target: `/home/klsx/NEUROapp/NeuroPromptSemanticCompiler/`
Scope: **OPTION 2** (medium polish + one new component area)
Date: 2026-06-11
Base hardware: i5 / GTX 660 Kepler / 12 GB RAM / CachyOS KDE X11

## Verificación previa

- Tests: 41/41 passing (v1.0.0rc2)
- Backup exists: `_backups/mode-redesign-20260609-025641/` (pre-rollback snapshot)
- Baseline screenshots: `artifacts/baseline_2026/`
- Existing components ready to reuse: `ScanRing`, `HealthDashboard`, `StatusChip`, `CircleIndicator`, `ToolCard`, `ResultCard`, `NavGroup/NavItem`
- Existing tokens: `circle_idle/active/success/error_border`, `state_success/warning/error/info`, light+dark themes

## Diagnóstico visual (capturas nuevas, no las obsoletas de `screenshots/`)

| # | Problema | Evidencia | Fix |
|---|----------|-----------|-----|
| 1 | Duplicación de tarjetas: `HealthDashboard` (4 pills) + 4 `ResultCard` (mismas 4 categorías) en `_build_dashboard` línea 771-782 | Captura `extreme_dashboard_dark.png` muestra 2 filas de "Preservación / Restricciones / Avisos / Errores" | Quitar la fila de `ResultCard` (dejar solo `HealthDashboard`) |
| 2 | `HealthDashboard` fila 1 "Preservación" muestra "—" muted todo el tiempo hasta compilar | Captura línea 1: "Preservación: —" en gris | `MetricPill` debe distinguir "score 0 = no data" vs "score 100 = full". Ajustar el valor inicial a `0/100` con label "score" más informativo. |
| 3 | Emojis 🔍 ✅ 📄 en `ToolCard` icon_text (línea 793, 795, 797) se ven improvisados | Captura sección Herramientas | Reemplazar por glifos técnicos: ⌕ (U+2315 telephone recorder / search-like), ✓ (U+2713 check), ❒ (U+2752 black square) — consistentes con tipografía monoespaciada del editor. O mejor: usar QChar/QPainter simple shapes. **Decisión**: glifos Unicode es suficiente y sin riesgo. |
| 4 | Botón "Mejorar prompt" (azul) arriba + "Mejorar" (azul) en quick row duplican acción | Captura muestra dos botones azules con mismo label casi idéntico | Quitar el botón "Mejorar" del quick row (línea 735). El hero button "Mejorar prompt" es el primario. |
| 5 | RuntimeWarning: `QFrame.metric` override returns NoneType (pitfall #14 skill) | Captura stderr | Renombrar método en algún componente que use `metric()` → `get_metric()` o eliminar override si no es necesario. Auditar. |
| 6 | Espaciado de cards y botones: márgenes un poco estrechos en algunos puntos | Captura visual | Ajustar `padding: 14px 16px` en `.NPSCCard { ... }` y `min-height: 32px` en botones de acción (no principales) para mejor touch target. |
| 7 | QSS: títulos de sección ("Herramientas", "Estado del sistema") tienen peso inconsistente | Captura | Estandarizar: 13px Medium, color text_secondary, letter-spacing 0.5px, uppercase. |

## Cambios NO incluidos (out of scope, OPCION 2)

- ❌ Cambiar arquitectura dual-mode (intacta)
- ❌ Rediseñar grid 3×2 → 2×2 (intacto)
- ❌ Microanimaciones (no en Kepler, seguro pero fuera de scope)
- ❌ Onboarding tour (fuera de scope)
- ❌ Nuevos temas (light+dark ya están)

## Archivos a modificar

1. `src/npsc_gui/main_window.py` — quitar 4 ResultCard duplicados, quitar botón "Mejorar" duplicado
2. `src/npsc_gui/components/health_dashboard.py` — mejorar valor inicial y label de "score"
3. `src/npsc_gui/main_window.py` (línea 793-797) — reemplazar emojis por glifos Unicode en `set_icon_text`
4. `src/npsc_gui/theme.py` — pulir QSS: `.SectionTitle`, `.NPSCCard`, `.PrimaryButton`, `.NPSCSidebar`
5. Auditar y renombrar `metric()` override en `health_dashboard.py` (pitfall #14)

## Verificación post-cambio

- `PYTHONPATH=src .venv/bin/python -m pytest tests/ --tb=short` → debe seguir 41/41
- Regenerar `artifacts/baseline_2026/` con script actualizado → comparar visual
- Confirmar 0 RuntimeWarnings nuevos
- Diff y documento de rollback

## Plan de rollback (si algo falla)

```bash
B="/home/klsx/NEUROapp/NeuroPromptSemanticCompiler/_backups/pre-visual-polish-20260611-XXXXXX"
P="/home/klsx/NEUROapp/NeuroPromptSemanticCompiler"
cp "$B/src/npsc_gui/main_window.py" "$P/src/npsc_gui/main_window.py"
cp "$B/src/npsc_gui/theme.py" "$P/src/npsc_gui/theme.py"
cp "$B/src/npsc_gui/components/health_dashboard.py" "$P/src/npsc_gui/components/health_dashboard.py"
```
