# 04 — Style Guide

## Principles
1. Solid colors only — no gradients, no rgba alpha
2. Tempered cyan accent (#31B8D6 dark / #2AA4BE light) — not neon
3. Subtle 1px borders for grouping — never 2px except focus
4. Surface hierarchy via background lightness, not shadows or gradients
5. Accent color only on primary actions, focus, and selected states
6. All interactive elements must have visible :focus state
7. Both light and dark themes must meet WCAG AA contrast (4.5:1 for text)

## Component Patterns
- Buttons: solid bg + 1px border + 7px radius; hover = lighter bg + accent border
- Cards: solid bg + 1px border + 8px radius; hover = elevated bg
- Nav: transparent bg; checked = accent border-left + accent-tinted bg
- Inputs: darker bg + 1px border; focus = accent border
- Tabs: muted bg; selected = accent bottom border
- Progress: solid accent chunk, no gradient
- Scrollbar: minimal, dark handle, accent on hover
