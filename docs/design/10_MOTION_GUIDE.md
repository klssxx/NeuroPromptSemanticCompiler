# 10 — Motion Guide

## Allowed Interactions
- Hover state changes (bg color shift, border color shift) — instant, no animation
- Focus ring appears on keyboard focus — instant
- Pressed state on buttons — instant
- Progress bar fills — smooth via Qt built-in
- Tab/page switch — instant (no slide animation)

## Prohibited (GTX 660 Performance)
- CSS/QSS transitions or animations (not supported by QSS anyway)
- Blur effects (KWin blur or Qt GraphicsBlur)
- Transparency/alpha blending on large surfaces
- Gradient animations
- Skeleton loading animations
- Particle effects or shader effects

## Reduced Motion
- Already minimal — QSS doesn't support animation
- No changes needed for prefers-reduced-motion
