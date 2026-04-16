"""Sohbet Geçmişi Yöneticisi — her AI için ayrı konuşma geçmişi tutar.

Şimdilik yerel (data/chats/<ai_name>.json), ileride cloud'a geçirilebilir.
"""

import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHATS_DIR = os.path.join(DATA_DIR, "chats")


def _safe_filename(name: str) -> str:
    """İsimden güvenli dosya adı oluştur."""
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name)


class ChatHistory:
    """Bir AI'ın sohbet geçmişini yönetir."""

    def __init__(self, ai_name: str):
        self.ai_name = ai_name
        os.makedirs(CHATS_DIR, exist_ok=True)
        self.file_path = os.path.join(CHATS_DIR, f"{_safe_filename(ai_name)}.json")
        self.messages = self._load()

    def _load(self) -> list:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def add_message(self, role: str, content: str):
        """role: 'user' veya 'assistant'"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def get_messages(self) -> list:
        return list(self.messages)

    def clear(self):
        self.messages = []
        self._save()

    def get_for_llm(self, max_messages: int = 20) -> list:
        """LLM'e gönderilecek formatta son N mesajı döndür."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages[-max_messages:]
        ]

    def search(self, query: str) -> list:
        """Mesajlarda arama yap. Eşleşenleri döndür."""
        if not query:
            return list(self.messages)
        q = query.lower().strip()
        return [m for m in self.messages if q in m["content"].lower()]


def search_all_chats(query: str) -> list:
    """Tüm AI sohbet geçmişlerinde arama yap."""
    import os
    results = []
    if not os.path.exists(CHATS_DIR):
        return results
    for fname in os.listdir(CHATS_DIR):
        if not fname.endswith(".json"):
            continue
        ai_name = fname[:-5]
        try:
            with open(os.path.join(CHATS_DIR, fname), "r", encoding="utf-8") as f:
                messages = json.load(f)
                q = query.lower().strip()
                for m in messages:
                    if q in m["content"].lower():
                        results.append({
                            "ai_name": ai_name,
                            "role": m["role"],
                            "content": m["content"],
                            "timestamp": m.get("timestamp", ""),
                        })
        except Exception:
            continue
    return results
