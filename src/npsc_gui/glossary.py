from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from importlib import resources
from typing import Any


GLOSSARY_RESOURCE = "ui_glossary_es.json"
GLOSSARY_PACKAGE = "npsc_resources.configs"

CATEGORIES = [
    "Todas",
    "Uso básico",
    "Resultados",
    "Tipos de mejora",
    "Nivel de detalle",
    "Privacidad",
    "Validación",
    "Modelos",
    "Formatos técnicos",
    "Métricas",
]

REQUIRED_FIELDS = {
    "id",
    "term",
    "simple_name",
    "category",
    "aliases",
    "short_definition",
    "plain_explanation",
    "when_to_use",
    "example",
    "related_terms",
    "technical_note",
}


def normalize_query(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in folded if not unicodedata.combining(char))


@lru_cache(maxsize=1)
def load_glossary() -> list[dict[str, Any]]:
    with resources.files(GLOSSARY_PACKAGE).joinpath(GLOSSARY_RESOURCE).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data.get("terms", data)
    if not isinstance(entries, list):
        raise ValueError("El glosario debe contener una lista de terminos.")
    return sorted(entries, key=lambda item: normalize_query(str(item["term"])))


def validate_glossary(entries: list[dict[str, Any]] | None = None) -> list[str]:
    problems: list[str] = []
    selected = entries or load_glossary()
    seen: set[str] = set()
    for entry in selected:
        missing = sorted(REQUIRED_FIELDS - set(entry))
        if missing:
            problems.append(f"{entry.get('id', '<sin id>')}: faltan {', '.join(missing)}")
        entry_id = str(entry.get("id", ""))
        if entry_id in seen:
            problems.append(f"id duplicado: {entry_id}")
        seen.add(entry_id)
        if entry.get("category") not in CATEGORIES[1:]:
            problems.append(f"{entry_id}: categoria desconocida {entry.get('category')!r}")
    return problems


def get_entry(entry_id: str) -> dict[str, Any] | None:
    normalized = normalize_query(entry_id)
    for entry in load_glossary():
        candidates = [entry["id"], entry["term"], entry["simple_name"], *entry.get("aliases", [])]
        if any(normalize_query(str(candidate)) == normalized for candidate in candidates):
            return entry
    return None


def search_glossary(query: str = "", category: str = "Todas") -> list[dict[str, Any]]:
    normalized = normalize_query(query.strip())
    matches: list[dict[str, Any]] = []
    for entry in load_glossary():
        if category != "Todas" and entry.get("category") != category:
            continue
        haystack = " ".join(
            [
                str(entry.get("term", "")),
                str(entry.get("simple_name", "")),
                " ".join(str(alias) for alias in entry.get("aliases", [])),
                str(entry.get("short_definition", "")),
                str(entry.get("plain_explanation", "")),
                str(entry.get("technical_note", "")),
            ]
        )
        if not normalized or normalized in normalize_query(haystack):
            matches.append(entry)
    return matches


def format_entry(entry: dict[str, Any], advanced: bool = False) -> str:
    related = ", ".join(entry.get("related_terms", [])) or "sin terminos relacionados"
    lines = [
        f"{entry['term']} - {entry['simple_name']}",
        "",
        entry["short_definition"],
        "",
        entry["plain_explanation"],
        "",
        f"Cuándo usarlo: {entry['when_to_use']}",
        f"Ejemplo: {entry['example']}",
        f"Categoría: {entry['category']}",
        f"Relacionado: {related}",
    ]
    if advanced:
        lines.extend(["", f"Nota técnica: {entry['technical_note']}", f"ID interno del glosario: {entry['id']}"])
    return "\n".join(lines)

