"""Multi-AI Takım Çalışması — Senin oluşturduğun AI'lar sırayla bir görev üzerinde çalışır.

Performans notu: M2 Pro 16GB'da AI'lar sırayla çalışır (paralel değil), RAM sorunu yok.
Her AI ~15-30 saniye, 4 AI'lı takım = ~1-2 dakika.
"""

import os
import json
from datetime import datetime

import ollama

from model_config import get_chat_model
from debate import persona_manager


def run_team_task(ai_names: list[str], task: str, on_message=None) -> dict:
    """
    Seçilen AI'ları sırayla görev üzerinde çalıştır.

    ai_names: katılımcı AI isimleri (2+)
    task: ortak görev
    on_message: callback(ai_name, message, color)

    Döndürür: {"results": [{ai, message}, ...], "summary": "final özet"}
    """
    on_message = on_message or (lambda *a: None)
    model = get_chat_model()
    results = []
    accumulated = ""

    for i, ai_name in enumerate(ai_names):
        persona = persona_manager.get(ai_name)
        if not persona:
            continue

        color = persona.get("color", "#8e44ad")
        system_prompt = persona_manager.get_system_prompt(ai_name)

        # Önceki AI'ların katkılarını ekle
        if accumulated:
            user_msg = (
                f"Ortak görev: {task}\n\n"
                f"Takım üyeleri şu ana kadar şunları söyledi:\n{accumulated}\n\n"
                f"Sen {ai_name} olarak, kendi bakış açınla katkıda bulun. "
                f"Öncekileri tekrar etme, farklı bir açı getir veya onları geliştir. "
                f"Kısa ve öz ol (3-5 cümle)."
            )
        else:
            user_msg = (
                f"Takım görevi: {task}\n\n"
                f"Sen {ai_name}'sın. Görev hakkında kendi bakış açınla görüşünü söyle. "
                f"Kısa ve öz ol (3-5 cümle)."
            )

        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
            )
            msg = response["message"]["content"]
        except Exception as e:
            msg = f"[Hata: {e}]"

        on_message(ai_name, msg, color)
        results.append({"ai_name": ai_name, "message": msg})
        accumulated += f"\n\n{ai_name}: {msg}"

    # Final özet / konsensüs
    summary = ""
    if len(results) >= 2:
        try:
            summary_response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content":
                        "Sen tarafsız bir takım lideri ve moderatörsün. Türkçe yaz."},
                    {"role": "user", "content": (
                        f"Görev: {task}\n\n"
                        f"Takım üyeleri şöyle katkıda bulundu:{accumulated}\n\n"
                        f"Şunları yap:\n"
                        f"1. Ortak noktaları özetle (max 3 madde)\n"
                        f"2. Farklı görüşleri belirt\n"
                        f"3. Somut aksiyon önerisi sun (max 3 madde)\n"
                        f"Kısa ve net ol."
                    )},
                ],
            )
            summary = summary_response["message"]["content"]
            on_message("🏛 Takım Özeti", summary, "#7f8c8d")
        except Exception as e:
            summary = f"Özet hatası: {e}"

    # Kaydet
    _save_team_result(ai_names, task, results, summary)

    return {"results": results, "summary": summary}


def _save_team_result(ai_names: list[str], task: str, results: list, summary: str):
    """Takım çıktısını kaydet."""
    data_dir = os.path.join(os.path.dirname(__file__), "data", "team_results")
    os.makedirs(data_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_task = task[:30].replace(" ", "_").replace("/", "-")
    path = os.path.join(data_dir, f"team_{safe_task}_{ts}.json")

    data = {
        "task": task,
        "team": ai_names,
        "results": results,
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
