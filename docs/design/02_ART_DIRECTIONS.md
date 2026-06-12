# 02 — Art Directions

## Route A — Plasma Native Premium (CHOSEN)

Concept: Clean, professional, deeply integrated with KDE Plasma X11 aesthetics.
Uses solid colors, subtle borders, tempered cyan accent.

- Palette: Breeze-inspired neutrals + tempered cyan (#31B8D6) accent
- Typography: Inter, 10.5pt base
- Navigation: Simplified sidebar (7 pages after merge), flat nav buttons
- Cards: Solid background, 1px border, 6px radius
- Buttons: Solid fill, hover tint, pressed accent
- Light mode: #F8F9FB base, #E8ECF0 cards, dark text
- Dark mode: #1B1E24 base, #252830 cards, light text
- Performance: Excellent — no gradients, no alpha compositing
- Risk: Lowest technical risk
- KDE X11 compat: Best

## Route B — Elite Technical Dashboard

Concept: Data-rich panel layout with metrics cards.
- Risk: Medium — more layout work, potential complexity
- Decision: Deferred; can evolve from Route A later

## Route C — Unique Futuristic Minimal

Concept: Ultra-minimal with strong typographic hierarchy.
- Risk: Medium-high — might feel too sparse, unusual for KDE
- Decision: Not chosen; conflicts with KDE integration goal

## Decision: Route A

Justification: Best balance of stability, KDE Plasma X11 integration, GTX 660
performance, maintainability, and accessibility. Solid colors eliminate GPU
compositing overhead. Breeze-inspired palette ensures visual coherence with the
desktop environment.
