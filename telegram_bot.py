"""HAD3M-EIA Telegram Botu — Yerel AI'a Telegram üzerinden erişim.

AI modeli yerel çalışır, sadece mesajlar Telegram üzerinden geçer.
Belgeler ve model bilgisayarında kalır.

Kullanım:
1. @BotFather'dan bot oluştur, token al
2. Token'ı data/settings.json'a yaz veya çalıştırırken gir
3. python3 telegram_bot.py

Komutlar:
/start      — Başlat
/sor        — Soru sor (RAG)
/tartis     — İki kişilik tartıştır
/kisilikler — Mevcut kişilikleri listele
/model      — Aktif model bilgisi
/yardim     — Yardım
"""

import os
import sys
import json
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
)

# Proje modülleri
sys.path.insert(0, os.path.dirname(__file__))
from rag_engine import RAGEngine
from debate import debate, persona_manager, get_personality_names
from model_config import detect_models, get_chat_model

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_telegram_token() -> str:
    """Token'ı settings.json'dan oku veya kullanıcıdan iste."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            token = settings.get("telegram_token", "")
            if token:
                return token

    # Token yok, kullanıcıdan iste
    print("\n" + "=" * 50)
    print("TELEGRAM BOT KURULUMU")
    print("=" * 50)
    print("\n1. Telegram'da @BotFather'a git")
    print("2. /newbot komutunu yaz")
    print("3. Bot'a isim ver (ör: HAD3M-EIA)")
    print("4. Username ver (ör: had3m_eia_bot)")
    print("5. Verilen token'ı buraya yapıştır:\n")

    token = input("Token: ").strip()
    if not token:
        print("Token girilmedi, çıkılıyor.")
        sys.exit(1)

    # Kaydet
    os.makedirs(DATA_DIR, exist_ok=True)
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
    settings["telegram_token"] = token
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

    print(f"\nToken kaydedildi! Bir daha sorulmayacak.")
    return token


# Engine global olarak başlatılacak
engine = None


def init_engine():
    global engine
    print("Engine başlatılıyor...")
    engine = RAGEngine(on_status=lambda m: print(f"  {m}"))
    print("Engine hazır!")


# === Telegram Komutları ===

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 HAD3M-EIA Telegram Botu\n\n"
        "Yerel AI asistanına Telegram üzerinden erişiyorsun.\n"
        "AI modeli bilgisayarında çalışıyor, veriler yerelde kalıyor.\n\n"
        "Komutlar:\n"
        "/sor <soru> — Soru sor\n"
        "/tartis <kişilik1> vs <kişilik2>: <konu>\n"
        "/kisilikler — Mevcut kişilikleri listele\n"
        "/model — Aktif model bilgisi\n"
        "/yardim — Bu mesaj\n\n"
        "Veya direkt mesaj yaz, soru olarak algılanır."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args) if context.args else ""
    if not question:
        await update.message.reply_text("Kullanım: /sor <sorunuz>")
        return

    await update.message.reply_text("🤔 Düşünüyor...")

    try:
        answer = engine.ask(question)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")


async def cmd_debate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    if " vs " not in text or ":" not in text:
        await update.message.reply_text(
            "Kullanım: /tartis <kişilik1> vs <kişilik2>: <konu>\n"
            "Örnek: /tartis CEO vs CFO: Reklam bütçesini artırmalı mıyız"
        )
        return

    vs_part, topic = text.split(":", 1)
    p1, p2 = [x.strip() for x in vs_part.split(" vs ", 1)]
    topic = topic.strip()

    names = get_personality_names()
    if p1 not in names or p2 not in names:
        await update.message.reply_text(
            f"❌ Kişilik bulunamadı.\nMevcut: {', '.join(names)}"
        )
        return

    await update.message.reply_text(f"⚔️ Tartışma başlıyor: {p1} vs {p2}\nKonu: {topic}")

    messages = []

    def on_msg(persona, msg):
        messages.append(f"**{persona}:**\n{msg}")

    try:
        debate(topic, p1, p2, rounds=2, on_message=on_msg)
        # Mesajları gönder
        for msg in messages:
            await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")


async def cmd_personas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    names = get_personality_names()
    if not names:
        await update.message.reply_text("Henüz kişilik oluşturulmamış. GUI'den oluştur.")
        return

    text = "👥 Mevcut Kişilikler:\n\n"
    for name in names:
        p = persona_manager.get(name)
        role = p.get("role", "?")
        traits = p.get("traits", [])
        trait_str = ", ".join(traits[:5]) if traits else "—"
        text += f"• **{name}** ({role})\n  Özellikler: {trait_str}\n\n"

    await update.message.reply_text(text)


async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = detect_models()
    text = (
        f"🧠 Model Bilgisi:\n\n"
        f"Sohbet: {config.get('chat_model', '?')}\n"
        f"Kod: {config.get('code_model', '?')}\n"
        f"Kurulu: {', '.join(config.get('installed_models', []))}"
    )
    await update.message.reply_text(text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direkt mesajları soru olarak algıla."""
    question = update.message.text.strip()
    if not question:
        return

    await update.message.reply_text("🤔 Düşünüyor...")

    try:
        answer = engine.ask(question)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")


def main():
    token = get_telegram_token()
    init_engine()

    print("\n" + "=" * 50)
    print("🤖 HAD3M-EIA Telegram Botu başlatılıyor...")
    print("=" * 50)
    print("Bot çalışıyor! Telegram'dan mesaj gönderebilirsin.")
    print("Durdurmak için Ctrl+C\n")

    app = Application.builder().token(token).build()

    # Komut handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("yardim", cmd_help))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("sor", cmd_ask))
    app.add_handler(CommandHandler("tartis", cmd_debate))
    app.add_handler(CommandHandler("kisilikler", cmd_personas))
    app.add_handler(CommandHandler("model", cmd_model))

    # Direkt mesajlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
