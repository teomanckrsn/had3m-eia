"""Model Config - Kurulu modelleri algıla, en uygununu seç."""

import os
import json

import ollama

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONFIG_FILE = os.path.join(DATA_DIR, "model_config.json")

# Model öncelik sırası: en iyi → en basit
# Her kategoride ilk bulunan kullanılır
CHAT_MODEL_PRIORITY = [
    "deepseek-coder-v2:16b",
    "llama3.1:14b",
    "aya-expanse:8b",
    "llama3.2:3b",
    "mistral:7b",
    "gemma2:9b",
]

CODE_MODEL_PRIORITY = [
    "deepseek-coder-v2:16b",
    "codellama:13b",
    "codellama:7b",
    "aya-expanse:8b",
    "llama3.2:3b",
]


def get_installed_models() -> list[str]:
    """Kurulu tüm modelleri listele."""
    try:
        result = ollama.list()
        return [m.model for m in result.models]
    except Exception:
        return []


def _find_best(installed: list[str], priority: list[str]) -> str:
    """Öncelik listesine göre en iyi kurulu modeli bul."""
    for model in priority:
        for inst in installed:
            if model in inst:
                return inst
    return ""


def detect_models() -> dict:
    """Kurulu modelleri algıla ve en uygunlarını seç."""
    installed = get_installed_models()

    config = {
        "installed_models": installed,
        "chat_model": _find_best(installed, CHAT_MODEL_PRIORITY),
        "code_model": _find_best(installed, CODE_MODEL_PRIORITY),
    }

    # Kaydet
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    return config


def get_config() -> dict:
    """Mevcut config'i oku veya yeniden algıla."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return detect_models()


def get_chat_model() -> str:
    return get_config().get("chat_model", "aya-expanse:8b")


def get_code_model() -> str:
    return get_config().get("code_model", "aya-expanse:8b")
