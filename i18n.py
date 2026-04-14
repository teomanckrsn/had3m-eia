"""Çoklu dil desteği (i18n) — Türkçe / İngilizce."""

import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

TRANSLATIONS = {
    "tr": {
        # Genel
        "app_title": "HAD3M-EIA",
        "ready": "Hazır!",
        "error": "Hata",
        "save": "Kaydet",
        "cancel": "İptal",
        "delete": "Sil",
        "close": "Kapat",
        "yes": "Evet",
        "no": "Hayır",
        "settings": "Ayarlar",
        "language": "Dil",

        # Üst bar butonları
        "add_file": "📂 Dosya Ekle",
        "clear": "🗑 Temizle",
        "create_ai": "🤖 Yapay Zeka Oluştur",
        "relationships": "🔗 İlişkiler",
        "file_manager": "📁 Dosya",
        "browser": "🌐 Tarayıcı",
        "dev_team": "💻 Kodla",
        "settings_btn": "⚙️ Ayarlar",
        "no_files": "Henüz dosya yüklenmedi",

        # Modlar
        "chat_mode": "💬 Sohbet",
        "debate_mode": "⚔️ Tartışma",
        "persona_1": "Kişilik 1:",
        "persona_2": "vs",
        "rounds": "Tur:",
        "auto_debate": "🔄 Otonom",
        "stop": "⏹",

        # Sohbet
        "type_question": "Sorunuzu yazın...",
        "type_debate_topic": "Tartışma konusunu yazın...",
        "send": "Gönder",
        "thinking": "Düşünüyor...",
        "chat_label": "Sohbet",

        # Kişilik oluşturma
        "create_persona_title": "Yapay Zeka Oluştur",
        "persona_name": "İsim:",
        "persona_role": "Rol:",
        "persona_description": "Tanım:",
        "persona_color": "Renk:",
        "pick_color": "Renk Seç",
        "persona_traits": "Karakter Özellikleri (istediğin kadar seç):",
        "persona_desc_placeholder": "Uzmanlık alanını ve bakış açısını tanımlayın (opsiyonel)...",
        "persona_name_placeholder": "ör: Pazarlama Müdürü",
        "persona_role_placeholder": "ör: Dijital pazarlama uzmanı",

        # İzinler
        "permissions": "İzinler",
        "can_move_files": "Dosya taşıyabilir",
        "can_use_browser": "Tarayıcı kullanabilir",
        "can_create_files": "Dosya oluşturabilir",
        "can_write_code": "Kod yazabilir",
        "can_debate": "Tartışmaya katılabilir",

        # Karakter özellikleri kategorileri
        "trait_motivation": "Motivasyon & Enerji",
        "trait_thinking": "Düşünme Tarzı",
        "trait_communication": "İletişim Tarzı",
        "trait_risk": "Risk & Karar",
        "trait_business": "İş Yaklaşımı",

        # Karakter özellikleri
        "trait_ambitious": "Hırslı",
        "trait_positive": "Pozitif",
        "trait_calm": "Sakin",
        "trait_aggressive": "Agresif",
        "trait_analytical": "Analitik",
        "trait_creative": "Yaratıcı",
        "trait_strategic": "Stratejik",
        "trait_practical": "Pratik",
        "trait_detail_oriented": "Detaycı",
        "trait_diplomatic": "Diplomatik",
        "trait_direct": "Dobra",
        "trait_persuasive": "İkna Edici",
        "trait_listener": "Dinleyici",
        "trait_risk_taker": "Risk Alan",
        "trait_cautious": "Temkinli",
        "trait_decisive": "Kararlı",
        "trait_customer_focused": "Müşteri Odaklı",
        "trait_cost_focused": "Maliyet Odaklı",
        "trait_growth_focused": "Büyüme Odaklı",
        "trait_quality_focused": "Kalite Odaklı",
        "trait_speed_focused": "Hız Odaklı",

        # İlişkiler
        "relationships_title": "Kişilik İlişkileri",
        "define_relationship": "🔗 İlişki Tanımla",
        "who": "Kim:",
        "to_whom": "→ Kime:",
        "opinion": "Düşüncesi:",
        "opinion_placeholder": "ör: Çok temkinli buluyorum, bazen fırsat kaçırıyoruz yüzünden",
        "save_relationship": "İlişki Kaydet",
        "current_relationships": "Mevcut İlişkiler:",
        "no_relationships": "Henüz ilişki tanımlanmamış.",

        # Dosya yöneticisi
        "file_manager_title": "Dosya Yöneticisi",
        "move_file": "📦 Dosya Taşı",
        "source": "Kaynak:",
        "destination": "Hedef:",
        "select": "Seç",
        "move": "Taşı",
        "undo": "↩ Geri Al",
        "create_new": "📝 Yeni Dosya / Klasör Oluştur",
        "path": "Yol:",
        "create_file": "📄 Dosya Oluştur",
        "create_folder": "📁 Klasör Oluştur",
        "move_history": "Taşıma Geçmişi:",

        # Tarayıcı
        "browser_title": "HAD3M-EIA — Tarayıcı Agent",
        "allowed_sites": "🔒 İzin Verilen Siteler",
        "add_domain": "Ekle",
        "remove_domain": "Çıkar",
        "task": "🎯 Görev",
        "go": "Git",
        "screenshot": "Screenshot",
        "start_browser": "▶ Tarayıcı Aç",
        "stop_browser": "⏹ Tarayıcı Kapat",
        "page_text": "📄 Sayfa Metni",
        "click": "Tıkla",
        "fill": "Doldur",

        # Geliştirme ekibi
        "dev_team_title": "HAD3M-EIA — Geliştirme Ekibi",
        "project": "🏗 Proje",
        "project_name": "Ad:",
        "project_desc": "Açıklama:",
        "add_design": "🖼 Tasarım Görseli Ekle",
        "no_image": "Görsel eklenmedi (opsiyonel)",
        "team": "Ekip:",
        "start_team": "▶ Ekibi Çalıştır",
        "team_output": "Ekip Çıktısı",

        # Geri bildirim
        "feedback_saved_like": "Geri bildirim kaydedildi 👍 — Agent öğreniyor!",
        "feedback_saved_dislike": "Geri bildirim kaydedildi 👎 — Agent öğreniyor!",

        # Otonom tartışma
        "debate_complete": "Tartışma tamamlandı! Dosyalar: data/debates/",
        "debate_stopping": "Tartışma durduruluyor...",
    },

    "en": {
        # General
        "app_title": "HAD3M-EIA",
        "ready": "Ready!",
        "error": "Error",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "close": "Close",
        "yes": "Yes",
        "no": "No",
        "settings": "Settings",
        "language": "Language",

        # Top bar buttons
        "add_file": "📂 Add File",
        "clear": "🗑 Clear",
        "create_ai": "🤖 Create AI",
        "relationships": "🔗 Relations",
        "file_manager": "📁 Files",
        "browser": "🌐 Browser",
        "dev_team": "💻 Code",
        "settings_btn": "⚙️ Settings",
        "no_files": "No files loaded",

        # Modes
        "chat_mode": "💬 Chat",
        "debate_mode": "⚔️ Debate",
        "persona_1": "Persona 1:",
        "persona_2": "vs",
        "rounds": "Rounds:",
        "auto_debate": "🔄 Auto",
        "stop": "⏹",

        # Chat
        "type_question": "Type your question...",
        "type_debate_topic": "Type debate topic...",
        "send": "Send",
        "thinking": "Thinking...",
        "chat_label": "Chat",

        # Persona creation
        "create_persona_title": "Create AI Persona",
        "persona_name": "Name:",
        "persona_role": "Role:",
        "persona_description": "Description:",
        "persona_color": "Color:",
        "pick_color": "Pick Color",
        "persona_traits": "Character Traits (select as many as you want):",
        "persona_desc_placeholder": "Define expertise and perspective (optional)...",
        "persona_name_placeholder": "e.g. Marketing Director",
        "persona_role_placeholder": "e.g. Digital marketing expert",

        # Permissions
        "permissions": "Permissions",
        "can_move_files": "Can move files",
        "can_use_browser": "Can use browser",
        "can_create_files": "Can create files",
        "can_write_code": "Can write code",
        "can_debate": "Can join debates",

        # Trait categories
        "trait_motivation": "Motivation & Energy",
        "trait_thinking": "Thinking Style",
        "trait_communication": "Communication Style",
        "trait_risk": "Risk & Decision",
        "trait_business": "Business Approach",

        # Traits
        "trait_ambitious": "Ambitious",
        "trait_positive": "Positive",
        "trait_calm": "Calm",
        "trait_aggressive": "Aggressive",
        "trait_analytical": "Analytical",
        "trait_creative": "Creative",
        "trait_strategic": "Strategic",
        "trait_practical": "Practical",
        "trait_detail_oriented": "Detail-oriented",
        "trait_diplomatic": "Diplomatic",
        "trait_direct": "Direct",
        "trait_persuasive": "Persuasive",
        "trait_listener": "Listener",
        "trait_risk_taker": "Risk Taker",
        "trait_cautious": "Cautious",
        "trait_decisive": "Decisive",
        "trait_customer_focused": "Customer Focused",
        "trait_cost_focused": "Cost Focused",
        "trait_growth_focused": "Growth Focused",
        "trait_quality_focused": "Quality Focused",
        "trait_speed_focused": "Speed Focused",

        # Relationships
        "relationships_title": "Persona Relationships",
        "define_relationship": "🔗 Define Relationship",
        "who": "From:",
        "to_whom": "→ To:",
        "opinion": "Opinion:",
        "opinion_placeholder": "e.g. I find them too cautious, we miss opportunities",
        "save_relationship": "Save Relationship",
        "current_relationships": "Current Relationships:",
        "no_relationships": "No relationships defined yet.",

        # File manager
        "file_manager_title": "File Manager",
        "move_file": "📦 Move File",
        "source": "Source:",
        "destination": "Destination:",
        "select": "Select",
        "move": "Move",
        "undo": "↩ Undo",
        "create_new": "📝 Create New File / Folder",
        "path": "Path:",
        "create_file": "📄 Create File",
        "create_folder": "📁 Create Folder",
        "move_history": "Move History:",

        # Browser
        "browser_title": "HAD3M-EIA — Browser Agent",
        "allowed_sites": "🔒 Allowed Sites",
        "add_domain": "Add",
        "remove_domain": "Remove",
        "task": "🎯 Task",
        "go": "Go",
        "screenshot": "Screenshot",
        "start_browser": "▶ Open Browser",
        "stop_browser": "⏹ Close Browser",
        "page_text": "📄 Page Text",
        "click": "Click",
        "fill": "Fill",

        # Dev team
        "dev_team_title": "HAD3M-EIA — Dev Team",
        "project": "🏗 Project",
        "project_name": "Name:",
        "project_desc": "Description:",
        "add_design": "🖼 Add Design Image",
        "no_image": "No image added (optional)",
        "team": "Team:",
        "start_team": "▶ Run Team",
        "team_output": "Team Output",

        # Feedback
        "feedback_saved_like": "Feedback saved 👍 — Agent is learning!",
        "feedback_saved_dislike": "Feedback saved 👎 — Agent is learning!",

        # Auto debate
        "debate_complete": "Debate complete! Files: data/debates/",
        "debate_stopping": "Stopping debate...",
    },
}


def get_language() -> str:
    """Mevcut dil ayarını oku."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            return settings.get("language", "tr")
    return "tr"


def set_language(lang: str):
    """Dil ayarını kaydet."""
    os.makedirs(DATA_DIR, exist_ok=True)
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
    settings["language"] = lang
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def t(key: str) -> str:
    """Çeviri al. Anahtar bulunamazsa key döner."""
    lang = get_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS["tr"]).get(key, key)


def get_available_languages() -> list[str]:
    return list(TRANSLATIONS.keys())
