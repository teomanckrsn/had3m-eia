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

        # Create AI (form)
        "create_ai_title": "🤖 Yeni AI Oluştur",
        "create_ai_subtitle": "Kendi yapay zekanı oluştur. İsim ver, görev tanımını yaz.",
        "ai_name_label": "İsim",
        "ai_name_placeholder": "örn: Halime, Ayşe, Pazarlama Asistanı",
        "ai_task_label": "Görev Tanımı (Prompt)",
        "ai_task_hint": "Nasıl biri olmalı? Ne iş yapacak? Karakteri nasıl olsun?",
        "ai_task_default": "Sen benim kişisel asistanımsın. Günlük işlerimde bana yardım ediyorsun. Organize, pratik ve çözüm odaklısın. Kısa ve net cevaplar verirsin.",
        "create_btn": "✨ Oluştur",

        # AI list sidebar
        "ai_list_title": "🤖 Yapay Zekalar",
        "new_ai_btn": "+ Yeni AI Oluştur",
        "no_ai_msg": "Henüz AI yok.\n\n'+ Yeni AI Oluştur'\nbutonuna bas.",

        # Chat window
        "clear_history": "🗑 Geçmişi Temizle",
        "search_history": "🔍 Geçmişte ara...",
        "write_to": "'a yazın...",
        "permissions_label": "Yetkiler:",

        # Telegram
        "telegram_title": "📱 Telegram Botu",
        "telegram_desc": "AI'na telefondan Telegram üzerinden eriş.\nMesajlar internet üzerinden gider ama AI modeli yerelde kalır.",
        "telegram_token_label": "Bot Token:",
        "telegram_token_hint": "@BotFather'dan al (t.me/BotFather). /newbot komutu ile yeni bot oluştur.",
        "telegram_start": "▶ Botu Başlat",
        "telegram_stop": "⏹ Botu Durdur",
        "telegram_btn": "📱 Telegram",
        "telegram_running": "🟢 Bot çalışıyor",
        "telegram_stopped": "⚫ Bot durdu",

        # Settings
        "settings_lang_section": "🌐 Dil",
        "settings_model_section": "🧠 Model Yönetimi",
        "settings_chat_model": "Sohbet:",
        "settings_code_model": "Kod:",
        "settings_installed_models": "Kurulu Modeller:",
        "settings_downloadable": "⬇️ İndirilebilir Modeller",
        "settings_download": "⬇️ İndir",
        "settings_installed_badge": "✓ Kurulu",

        # FileManager
        "fm_title": "Dosya Yöneticisi",
        "fm_move_section": "📦 Dosya Taşı",
        "fm_source": "Kaynak:",
        "fm_destination": "Hedef:",
        "fm_select": "Seç",
        "fm_move": "Taşı",
        "fm_undo": "↩ Geri Al",
        "fm_create_section": "📝 Yeni Dosya / Klasör Oluştur",
        "fm_path": "Yol:",
        "fm_create_file": "📄 Dosya Oluştur",
        "fm_create_folder": "📁 Klasör Oluştur",
        "fm_history": "Taşıma Geçmişi:",
        "fm_no_history": "Henüz taşıma yapılmadı.",

        # Browser
        "br_title": "HAD3M-EIA — Tarayıcı Agent",
        "br_allowed_sites": "🔒 İzin Verilen Siteler",
        "br_add": "Ekle",
        "br_remove": "Çıkar",
        "br_no_domains": "Henüz site eklenmedi. Önce izin verilen siteleri ekleyin.",
        "br_allowed_list": "İzinli:",
        "br_task_section": "🎯 Görev",
        "br_go": "Git",
        "br_screenshot": "Screenshot",
        "br_start": "▶ Tarayıcı Aç",
        "br_stop": "⏹ Tarayıcı Kapat",
        "br_page_text": "📄 Sayfa Metni",
        "br_selector": "Selector:",
        "br_click": "Tıkla",
        "br_value": "Değer:",
        "br_fill": "Doldur",
        "br_status_off": "Tarayıcı kapalı. Önce site ekle, sonra tarayıcıyı aç.",

        # DevTeam
        "dt_title": "HAD3M-EIA — Geliştirme Ekibi",
        "dt_project_section": "🏗 Proje",
        "dt_name": "Ad:",
        "dt_desc": "Açıklama:",
        "dt_task_section": "🎯 Görev",
        "dt_team": "Ekip:",
        "dt_start": "▶ Ekibi Çalıştır",
        "dt_output": "Ekip Çıktısı",
        "dt_status_ready": "Proje adı ve görev girin, ekibi seçin, çalıştırın.",

        # Relationships
        "rel_title": "Kişilik İlişkileri",
        "rel_define": "🔗 İlişki Tanımla",
        "rel_who": "Kim:",
        "rel_to_whom": "→ Kime:",
        "rel_opinion": "Düşüncesi:",
        "rel_save": "İlişki Kaydet",
        "rel_list_title": "Mevcut İlişkiler:",
        "rel_no_relations": "Henüz ilişki tanımlanmamış.",

        # Scheduling
        "sched_title": "⏰ Zamanlanmış Görevler",
        "sched_new": "+ Yeni Görev",
        "sched_name": "Görev Adı:",
        "sched_ai": "AI Seç:",
        "sched_prompt": "Prompt:",
        "sched_time": "Zaman (HH:MM):",
        "sched_days": "Günler:",
        "sched_add": "Ekle",
        "sched_enabled": "Aktif",
        "sched_disabled": "Kapalı",
        "sched_no_tasks": "Henüz zamanlanmış görev yok.",
        "sched_btn": "⏰ Zamanla",

        # Multi-AI Team
        "team_title": "👥 AI Takım Çalışması",
        "team_select": "AI'ları Seç:",
        "team_task": "Ortak Görev:",
        "team_start": "▶ Takımı Başlat",
        "team_btn": "👥 Takım",
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

        # Create AI (form)
        "create_ai_title": "🤖 Create New AI",
        "create_ai_subtitle": "Create your own AI. Give it a name and task.",
        "ai_name_label": "Name",
        "ai_name_placeholder": "e.g. Helen, Marketing Assistant",
        "ai_task_label": "Task Description (Prompt)",
        "ai_task_hint": "Who should it be? What should it do? How should it behave?",
        "ai_task_default": "You are my personal assistant. You help me with daily tasks. You are organized, practical, and solution-focused. You give short and clear answers.",
        "create_btn": "✨ Create",

        # AI list sidebar
        "ai_list_title": "🤖 AI Personas",
        "new_ai_btn": "+ Create New AI",
        "no_ai_msg": "No AI yet.\n\nClick '+ Create New AI'\nto start.",

        # Chat window
        "clear_history": "🗑 Clear History",
        "search_history": "🔍 Search history...",
        "write_to": "Write to ",
        "permissions_label": "Permissions:",

        # Telegram
        "telegram_title": "📱 Telegram Bot",
        "telegram_desc": "Access your AI from your phone via Telegram.\nMessages go through internet but the AI model stays local.",
        "telegram_token_label": "Bot Token:",
        "telegram_token_hint": "Get from @BotFather (t.me/BotFather). Use /newbot to create.",
        "telegram_start": "▶ Start Bot",
        "telegram_stop": "⏹ Stop Bot",
        "telegram_btn": "📱 Telegram",
        "telegram_running": "🟢 Bot is running",
        "telegram_stopped": "⚫ Bot stopped",

        # Settings
        "settings_lang_section": "🌐 Language",
        "settings_model_section": "🧠 Model Management",
        "settings_chat_model": "Chat:",
        "settings_code_model": "Code:",
        "settings_installed_models": "Installed Models:",
        "settings_downloadable": "⬇️ Downloadable Models",
        "settings_download": "⬇️ Download",
        "settings_installed_badge": "✓ Installed",

        # FileManager
        "fm_title": "File Manager",
        "fm_move_section": "📦 Move File",
        "fm_source": "Source:",
        "fm_destination": "Destination:",
        "fm_select": "Select",
        "fm_move": "Move",
        "fm_undo": "↩ Undo",
        "fm_create_section": "📝 Create New File / Folder",
        "fm_path": "Path:",
        "fm_create_file": "📄 Create File",
        "fm_create_folder": "📁 Create Folder",
        "fm_history": "Move History:",
        "fm_no_history": "No moves yet.",

        # Browser
        "br_title": "HAD3M-EIA — Browser Agent",
        "br_allowed_sites": "🔒 Allowed Sites",
        "br_add": "Add",
        "br_remove": "Remove",
        "br_no_domains": "No sites added. Add allowed sites first.",
        "br_allowed_list": "Allowed:",
        "br_task_section": "🎯 Task",
        "br_go": "Go",
        "br_screenshot": "Screenshot",
        "br_start": "▶ Open Browser",
        "br_stop": "⏹ Close Browser",
        "br_page_text": "📄 Page Text",
        "br_selector": "Selector:",
        "br_click": "Click",
        "br_value": "Value:",
        "br_fill": "Fill",
        "br_status_off": "Browser closed. Add sites first, then open browser.",

        # DevTeam
        "dt_title": "HAD3M-EIA — Dev Team",
        "dt_project_section": "🏗 Project",
        "dt_name": "Name:",
        "dt_desc": "Description:",
        "dt_task_section": "🎯 Task",
        "dt_team": "Team:",
        "dt_start": "▶ Run Team",
        "dt_output": "Team Output",
        "dt_status_ready": "Enter project name and task, select team, run.",

        # Relationships
        "rel_title": "Persona Relationships",
        "rel_define": "🔗 Define Relationship",
        "rel_who": "From:",
        "rel_to_whom": "→ To:",
        "rel_opinion": "Opinion:",
        "rel_save": "Save Relationship",
        "rel_list_title": "Current Relationships:",
        "rel_no_relations": "No relationships defined yet.",

        # Scheduling
        "sched_title": "⏰ Scheduled Tasks",
        "sched_new": "+ New Task",
        "sched_name": "Task Name:",
        "sched_ai": "Select AI:",
        "sched_prompt": "Prompt:",
        "sched_time": "Time (HH:MM):",
        "sched_days": "Days:",
        "sched_add": "Add",
        "sched_enabled": "Active",
        "sched_disabled": "Disabled",
        "sched_no_tasks": "No scheduled tasks yet.",
        "sched_btn": "⏰ Schedule",

        # Multi-AI Team
        "team_title": "👥 AI Team Collaboration",
        "team_select": "Select AIs:",
        "team_task": "Shared Task:",
        "team_start": "▶ Start Team",
        "team_btn": "👥 Team",
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
