from __future__ import annotations

import math
from typing import Any


def estimate_text(text: str) -> dict[str, Any]:
    chars = len(text)
    words = len([w for w in text.split() if w.strip()])
    tokens = int(math.ceil(chars / 4))
    return {"chars": chars, "words": words, "approx_tokens": tokens}


def estimate_counters(text: str) -> tuple[int, int]:
    """Return (chars, approx_tokens) with minimal allocation for live UI counters."""
    chars = len(text)
    tokens = int(math.ceil(chars / 4))
    return chars, tokens


def build_token_report(original: str, safe_nsl: str, balanced_nsl: str, aggressive_nsl: str, optimized_prompt: str) -> dict[str, Any]:
    base = estimate_text(original)
    safe = estimate_text(safe_nsl)
    balanced = estimate_text(balanced_nsl)
    aggressive = estimate_text(aggressive_nsl)
    optimized = estimate_text(optimized_prompt)

    def reduction(before: int, after: int) -> float:
        if before <= 0:
            return 0.0
        return round(((before - after) / before) * 100, 2)

    return {
        "original": base,
        "safe_nsl": safe,
        "balanced_nsl": balanced,
        "aggressive_nsl": aggressive,
        "optimized_prompt": optimized,
        "reductions_percent": {
            "original_to_safe_nsl": reduction(base["approx_tokens"], safe["approx_tokens"]),
            "original_to_balanced_nsl": reduction(base["approx_tokens"], balanced["approx_tokens"]),
            "original_to_aggressive_nsl": reduction(base["approx_tokens"], aggressive["approx_tokens"]),
            "original_to_optimized_prompt": reduction(base["approx_tokens"], optimized["approx_tokens"]),
        },
        "note": "Token estimation is approximate (ceil(chars/4)), not exact tokenizer output.",
    }
