from __future__ import annotations


def parse_nsl(nsl_text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw in nsl_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "NSL/0.1":
            parsed["_header"] = line
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed
