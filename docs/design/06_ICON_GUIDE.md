# 06 — Icon Guide

## Application Icon
- Path: assets/icons/neuro-prompt-semantic-compiler.svg
- Size: 512x512 viewBox, renders at any size
- Style: Dark rounded rectangle with cyan bracket symbols and node graph
- Valid SVG with proper xmlns, title, desc for accessibility

## Internal Icons
- Brand glyph: "N" monogram in QLabel#BrandGlyph
- Settings gear: "⚙" unicode character in header
- Help: "?" unicode character in header
- Context help: "?" in QToolButton circles

## Guidelines
- Use unicode symbols for simple actions (gear, help)
- All icons must have accessible labels or tooltips
- No external icon dependencies (no icon theme lookup)
