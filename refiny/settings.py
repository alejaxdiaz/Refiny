import json
import os
import pathlib

SETTINGS_PATH = pathlib.Path(os.environ["APPDATA"]) / "Refiny" / "settings.json"

DEFAULTS = {
    "api_provider": "openai",
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "claude_api_key": "",
    "claude_model": "claude-haiku-4-5-20251001",
    "hotkey": "ctrl+shift+r",
}


def load() -> dict:
    if not SETTINGS_PATH.exists():
        return dict(DEFAULTS)
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULTS, **data}
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
