"""Model Config - Kurulu modelleri algıla, kullanıcı seçimine göre kullan."""

import os
import json
import subprocess

import ollama

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONFIG_FILE = os.path.join(DATA_DIR, "model_config.json")

# Otomatik seçim için öncelik sırası
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

# İndirilebilir popüler modeller
POPULAR_MODELS = [
    {"name": "aya-expanse:8b", "size": "5.1 GB", "desc": "En iyi Türkçe, genel sohbet"},
    {"name": "llama3.2:3b", "size": "2.0 GB", "desc": "Küçük ve hızlı, basit işler"},
    {"name": "llama3.1:8b", "size": "4.7 GB", "desc": "Genel amaçlı, İngilizce güçlü"},
    {"name": "mistral:7b", "size": "4.1 GB", "desc": "Hızlı, kaliteli cevaplar"},
    {"name": "gemma2:9b", "size": "5.4 GB", "desc": "Google'ın modeli"},
    {"name": "codellama:7b", "size": "3.8 GB", "desc": "Kod yazma için"},
    {"name": "deepseek-coder-v2:16b", "size": "9.1 GB", "desc": "En iyi kod, RAM yoğun"},
    {"name": "qwen2.5:7b", "size": "4.4 GB", "desc": "Matematik ve mantık iyi"},
]


def get_installed_models() -> list[str]:
    """Kurulu tüm modelleri listele."""
    try:
        result = ollama.list()
        return [m.model for m in result.models]
    except Exception:
        return []


def get_installed_models_detailed() -> list[dict]:
    """Kurulu modelleri detaylı bilgi ile listele."""
    try:
        result = ollama.list()
        return [
            {
                "name": m.model,
                "size_mb": getattr(m, "size", 0) / (1024 * 1024) if getattr(m, "size", 0) else 0,
            }
            for m in result.models
        ]
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
    """Kurulu modelleri algıla. Kullanıcı override varsa onları koru."""
    installed = get_installed_models()

    # Mevcut config'i oku (kullanıcı override için)
    existing = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)

    # Kullanıcı seçimi hala kurulu mu?
    user_chat = existing.get("user_chat_model", "")
    user_code = existing.get("user_code_model", "")

    chat_model = user_chat if user_chat in installed else _find_best(installed, CHAT_MODEL_PRIORITY)
    code_model = user_code if user_code in installed else _find_best(installed, CODE_MODEL_PRIORITY)

    config = {
        "installed_models": installed,
        "chat_model": chat_model,
        "code_model": code_model,
        "user_chat_model": user_chat,
        "user_code_model": user_code,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    return config


def set_user_model(model_type: str, model_name: str):
    """Kullanıcının seçtiği modeli kaydet. model_type: 'chat' veya 'code'."""
    os.makedirs(DATA_DIR, exist_ok=True)
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

    if model_type == "chat":
        config["user_chat_model"] = model_name
        config["chat_model"] = model_name
    elif model_type == "code":
        config["user_code_model"] = model_name
        config["code_model"] = model_name

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def delete_model(model_name: str) -> bool:
    """Ollama'dan modeli sil."""
    try:
        ollama.delete(model_name)
        return True
    except Exception:
        return False


def pull_model(model_name: str, on_progress=None) -> bool:
    """Ollama'dan model indir. on_progress: callback(status_text)"""
    try:
        for chunk in ollama.pull(model_name, stream=True):
            if on_progress:
                status = chunk.get("status", "")
                if "total" in chunk and "completed" in chunk:
                    total = chunk.get("total", 1)
                    done = chunk.get("completed", 0)
                    pct = (done / total * 100) if total else 0
                    on_progress(f"{status} ({pct:.1f}%)")
                else:
                    on_progress(status)
        return True
    except Exception as e:
        if on_progress:
            on_progress(f"Hata: {e}")
        return False


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
