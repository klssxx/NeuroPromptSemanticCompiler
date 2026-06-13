#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from npsc_gui.glossary import CATEGORIES, load_glossary, validate_glossary


def main() -> int:
    problems = validate_glossary()
    if problems:
        raise SystemExit("Glosario invalido:\n" + "\n".join(problems))
    entries = load_glossary()
    lines = [
        "# Glosario fácil",
        "",
        "Este documento se genera desde `src/npsc_resources/configs/ui_glossary_es.json`.",
        "La misma fuente se usa dentro de la página **Glosario** de la aplicación.",
        "",
        f"Total de términos: {len(entries)}",
        "",
    ]
    by_category = {category: [] for category in CATEGORIES[1:]}
    for entry in entries:
        by_category.setdefault(entry["category"], []).append(entry)
    for category in CATEGORIES[1:]:
        terms = by_category.get(category, [])
        if not terms:
            continue
        lines.extend([f"## {category}", ""])
        for entry in terms:
            aliases = ", ".join(entry.get("aliases", []))
            related = ", ".join(entry.get("related_terms", []))
            lines.extend(
                [
                    f"### {entry['term']} - {entry['simple_name']}",
                    "",
                    entry["short_definition"],
                    "",
                    entry["plain_explanation"],
                    "",
                    f"**Cuándo usarlo:** {entry['when_to_use']}",
                    "",
                    f"**Ejemplo:** {entry['example']}",
                    "",
                    f"**Alias de búsqueda:** {aliases}",
                    "",
                    f"**Términos relacionados:** {related}",
                    "",
                    f"**Nota técnica:** {entry['technical_note']}",
                    "",
                ]
            )
    out = ROOT / "docs" / "GLOSARIO_ES.md"
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
