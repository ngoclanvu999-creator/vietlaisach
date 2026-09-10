import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
CONFIG_FILE = BASE_DIR / "app_settings.json"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "gemini_model": "gemini-2.5-flash",
    "default_subject": "toan",  # 'toan' or 'vatly'
    "default_add_count": 2,
    "default_rewrite_level": "medium",  # 'light', 'medium', 'deep'
    "enable_casio": True,
    "enable_traps": True,
    "enable_summary_box": True,
    "enable_dual_solutions": True,
    "output_format": "a4"  # 'a4' or 'b5'
}

def load_settings() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_settings(settings: dict) -> dict:
    current = load_settings()
    current.update(settings)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current
