# DESIGN SYSTEM — NeuroPrompt Semantic Compiler

**Route chosen:** A — Plasma Native Premium
**Reason:** Lowest risk for KDE X11 + GTX 660 legacy. Breeze-inspired solid colors, no GPU-expensive effects, professional maturity.

## Color Tokens

### Dark Palette (default)

| Token | Hex | Role |
|---|---|---|
| bg_base | #1B1E20 | Window background |
| bg_surface | #232629 | Panels, sidebar surface |
| bg_card | #292D31 | Card containers |
| bg_elevated | #31363B | Elevated elements, popovers |
| bg_input | #1D1F22 | Text fields, combos |
| border_subtle | #3B4045 | Subtle dividers |
| border_focus | #1D99F3 | Focus rings (accessibility) |
| text_primary | #EFF0F1 | Main text |
| text_secondary | #B0B3B5 | Secondary text |
| text_muted | #7A7C7E | Hints, timestamps |
| accent_primary | #2980B9 | Primary actions |
| accent_brand | #3DAEE9 | Brand accent (cyan, desaturated from neon) |
| state_success | #27AE60 | Pass, completion |
| state_warning | #F39C12 | Warning, processing |
| state_error | #DA4453 | Error, blocked |

### Light Palette

| Token | Hex | Role |
|---|---|---|
| bg_base | #F8F9FA | Window background |
| bg_surface | #FFFFFF | Panels, cards |
| bg_elevated | #F0F1F2 | Popovers, headers |
| border_subtle | #D5D6D7 | Subtle dividers |
| border_focus | #1D99F3 | Focus rings |
| text_primary | #1B1E20 | Main text |
| accent_primary | #2980B9 | Primary actions (same hue, works on light) |

## Typography

| Level | Size | Weight | Token |
|---|---|---|---|
| App title | 18pt | 800 | #AppTitle |
| Section title | 13pt | 800 | #SectionTitle |
| Body | 10.5pt | 400 | default |
| Metric | 20pt | 800 | #MetricValue |
| Muted | 10.5pt | 400 | #Muted |

## Spacing

- Content margins: 10px
- Widget spacing: 10px
- Button padding: 7px 14px
- Input padding: 6px
- Card border-radius: 6px
- Button border-radius: 5px

## Effects Policy

- **Allowed:** solid colors, 1px borders, hover color change, focus ring (2px solid #1D99F3)
- **Prohibited:** gradients with >1 stop, rgba alpha, backdrop-filter blur, box-shadow, animations >200ms, transparency layers, compositing that triggers software rendering path on GTX 660

## Focus & Accessibility

- Every interactive widget gets `:focus { border: 2px solid #1D99F3; outline: none; }`
- Minimum click target: 32px height
- Text contrast: WCAG AA minimum (4.5:1 for normal text, 3:1 for large text)
- Keyboard navigation: Tab order follows layout, Enter activates, Escape closes

## Mode Support

- Dark: default, matches KDE Breeze Dark
- Light: selectable from Settings page, matches KDE Breeze Light
- Theme persists in XDG config (settings.json → "theme" key)
- Theme applies immediately without restart
