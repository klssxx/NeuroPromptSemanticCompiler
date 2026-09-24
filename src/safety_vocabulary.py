"""Single source of truth for safety constraint phrases.

Both ``semantic_extractor`` and ``context_loss_verifier`` import from here.
Never add phrases directly to either module — add them here only.

Structure
---------
PHRASES : dict[str, list[str]]
    Maps each canonical constraint key to the full list of natural-language
    triggers (lower-case, language-mixed) that should activate it.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Master vocabulary
# ---------------------------------------------------------------------------
PHRASES: dict[str, list[str]] = {
    "no_sudo": [
        # Spanish
        "sin sudo",
        "no uses sudo",
        "no use sudo",
        "no usar sudo",
        # English
        "no sudo",
        "without sudo",
        "avoid sudo",
        "no_sudo",
        "without sudo privileges",
    ],
    "no_external_api": [
        # Spanish
        "sin api",
        "sin apis",
        "no uses api",
        "no usar api",
        "no usar apis",
        "sin apis externas",
        # English
        "no api",
        "no external api",
        "no external apis",
        "without api",
        "avoid external api",
        "no_external_api",
    ],
    "no_destructive_actions": [
        # Spanish
        "no destructiva",
        "no destructivo",
        "no destructivas",
        "nada destructivo",
        "no destruir",
        "no borrar",
        "sin borrar",
        # English
        "no destructive",
        "no delete",
        "do not delete",
        "avoid destructive",
        "no_destructive_actions",
        "non-destructive",
    ],
    "stay_inside_project_root": [
        # Spanish
        "no tocar fuera",
        "sin tocar fuera del proyecto",
        "fuera del proyecto",
        "dentro del proyecto",
        "no salir del proyecto",
        # English
        "stay inside",
        "inside root",
        "inside project root",
        "within project root",
        "within the project",
        "do not modify outside",
        "stay_inside_project_root",
    ],
    "offline_only": [
        # Spanish
        "sin internet",
        "sin conexión",
        "sin conexion",
        # English
        "offline",
        "no internet",
        "without internet",
        "no network",
        "offline_only",
    ],
}

# Ordered list of all canonical constraint keys
ALL_KEYS: list[str] = list(PHRASES.keys())


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def phrases_for(constraint_key: str) -> list[str]:
    """Return all trigger phrases for *constraint_key*, or [] if unknown."""
    return PHRASES.get(constraint_key, [])


def all_phrases() -> list[str]:
    """Flat list of every phrase across all constraints."""
    result: list[str] = []
    for phrases in PHRASES.values():
        result.extend(phrases)
    return result


def canonical_constraints(text: str) -> list[str]:
    """Return canonical keys for every safety constraint detected in *text*.

    Performs a simple case-insensitive substring search so this function can
    replace the scattered phrase-matching logic in both the extractor and the
    verifier with a single call.
    """
    lowered = text.lower()
    detected: list[str] = []
    for key, phrases in PHRASES.items():
        if any(phrase.lower() in lowered for phrase in phrases):
            if key not in detected:
                detected.append(key)
    return detected


def contains_constraint(text: str, constraint_key: str) -> bool:
    """Return True if *text* contains any phrase for *constraint_key*."""
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in PHRASES.get(constraint_key, []))
