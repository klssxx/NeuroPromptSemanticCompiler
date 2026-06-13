from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


APP_ID = "neuro-prompt-semantic-compiler"


def config_dir() -> Path:
    root = os.environ.get("NPSC_CONFIG_HOME")
    if root:
        return Path(root)
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_ID


def data_dir() -> Path:
    root = os.environ.get("NPSC_DATA_HOME")
    if root:
        return Path(root)
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_ID


DEFAULT_SETTINGS = {
    "theme": "dark",
    "language": "es",
    "advanced_mode": False,
    "startup_mode": "simple",
    "profile": "AUTO",
    "target": "codex",
    "level": "profile_default",
    "strict_validation": False,
    "preserve_original": True,
    "privacy_mode": "full_original",
    "custom_model_name": "",
    "last_section": "Panel principal",
    "window_width": 1320,
    "window_height": 860,
    "output_dir": "",
}


def settings_path() -> Path:
    return config_dir() / "settings.json"


def load_settings() -> dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {**DEFAULT_SETTINGS, **data}
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(data: dict[str, Any]) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**DEFAULT_SETTINGS, **data}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def reset_settings() -> None:
    save_settings(dict(DEFAULT_SETTINGS))
