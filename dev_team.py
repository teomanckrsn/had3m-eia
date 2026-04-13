"""Geliştirme Ekibi - Kodcu, Tasarımcı, Tester AI kişilikleri birlikte proje geliştirir."""

import os
import json
import base64
from pathlib import Path
from datetime import datetime

import ollama

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROJECTS_DIR = os.path.join(DATA_DIR, "projects")

from model_config import get_code_model, get_vision_model, has_vision

CODE_MODEL = get_code_model()
VISION_MODEL = get_vision_model()


def _check_model_exists(model_name: str) -> bool:
    """Modelin kurulu olup olmadığını kontrol et."""
    try:
        result = ollama.list()
        return any(model_name in m.model for m in result.models)
    except Exception:
        return False


# Ekip rolleri
TEAM_ROLES = {
    "Kodcu": {
        "name": "Kodcu",
        "emoji": "👨‍💻",
        "color": "#2ecc71",
        "system": (
            "Sen deneyimli bir yazılım geliştiricisisin. Temiz, okunabilir ve çalışan kod yazarsın. "
            "Kod yazarken:\n"
            "- Dosya adını ve içeriğini açıkça belirt\n"
            "- Her dosyayı ```dosya_adi.uzanti şeklinde işaretle\n"
            "- Hata yönetimi ve edge case'leri düşün\n"
            "- Kısa ve öz yorumlar ekle\n"
            "Her zaman Türkçe açıklama yap ama kod İngilizce olsun."
        ),
    },
    "Tasarımcı": {
        "name": "Tasarımcı",
        "emoji": "🎨",
        "color": "#e74c3c",
        "system": (
            "Sen UI/UX tasarımcısısın. Kullanıcı deneyimi, görsel tasarım ve erişilebilirlik konusunda uzmansın. "
            "Görevlerin:\n"
            "- HTML/CSS tasarımı yap\n"
            "- Renk paleti, tipografi ve layout öner\n"
            "- Responsive tasarım düşün\n"
            "- Kullanıcı akışını planla\n"
            "Eğer bir görsel/mockup gösterilirse, onu analiz edip HTML/CSS'e çevir.\n"
            "Her zaman Türkçe açıklama yap ama kod İngilizce olsun."
        ),
    },
    "Tester": {
        "name": "Tester",
        "emoji": "🧪",
        "color": "#3498db",
        "system": (
            "Sen QA mühendisisin. Kod kalitesi, bug tespiti ve test yazma konusunda uzmansın. "
            "Görevlerin:\n"
            "- Verilen kodu incele ve hataları bul\n"
            "- Test senaryoları yaz\n"
            "- Güvenlik açıklarını kontrol et\n"
            "- Performans önerilerinde bulun\n"
            "- Düzeltme önerileri sun\n"
            "Her zaman Türkçe açıklama yap ama kod İngilizce olsun."
        ),
    },
    "Mimar": {
        "name": "Mimar",
        "emoji": "🏗",
        "color": "#9b59b6",
        "system": (
            "Sen yazılım mimarısın. Sistem tasarımı, dosya yapısı ve teknoloji seçimi konusunda uzmansın. "
            "Görevlerin:\n"
            "- Proje yapısını planla\n"
            "- Hangi teknolojilerin kullanılacağına karar ver\n"
            "- Modüller arası ilişkileri tasarla\n"
            "- Ölçeklenebilirlik ve sürdürülebilirlik düşün\n"
            "Her zaman Türkçe açıklama yap."
        ),
    },
}


def get_team_roles() -> list[str]:
    return list(TEAM_ROLES.keys())


class DevProject:
    """Bir geliştirme projesini temsil eder."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.project_dir = os.path.join(PROJECTS_DIR, name.replace(" ", "_").lower())
        os.makedirs(self.project_dir, exist_ok=True)

        self.history = []  # Ekip konuşma geçmişi
        self.files = {}  # Oluşturulan dosyalar

    def save_file(self, filename: str, content: str):
        """Proje dosyası oluştur/güncelle."""
        filepath = os.path.join(self.project_dir, filename)
        # Alt klasör varsa oluştur
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) != self.project_dir else None
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        self.files[filename] = content

    def get_file(self, filename: str) -> str:
        filepath = os.path.join(self.project_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def list_files(self) -> list[str]:
        files = []
        for root, dirs, filenames in os.walk(self.project_dir):
            for fn in filenames:
                rel = os.path.relpath(os.path.join(root, fn), self.project_dir)
                files.append(rel)
        return sorted(files)


def _extract_code_blocks(text: str) -> list[dict]:
    """AI çıktısından kod bloklarını çıkar."""
    blocks = []
    lines = text.split("\n")
    in_block = False
    current_file = ""
    current_lines = []

    for line in lines:
        if line.startswith("```") and not in_block:
            in_block = True
            # Dosya adı var mı?
            lang_or_file = line[3:].strip()
            if "." in lang_or_file and "/" not in lang_or_file[:1]:
                current_file = lang_or_file
            else:
                current_file = ""
            current_lines = []
        elif line.startswith("```") and in_block:
            in_block = False
            if current_lines:
                blocks.append({
                    "filename": current_file,
                    "content": "\n".join(current_lines),
                })
        elif in_block:
            current_lines.append(line)

    return blocks


def analyze_image(image_path: str) -> str:
    """Görseli analiz et (multimodal model gerekir)."""
    if not VISION_MODEL or not _check_model_exists(VISION_MODEL):
        return (
            f"Görsel model ({VISION_MODEL}) kurulu değil. "
            f"Kurmak için: ollama pull {VISION_MODEL}\n"
            f"Görsel analiz bu model olmadan yapılamaz."
        )

    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": (
                "Bu görseli analiz et. Eğer bir UI/web tasarımı ise, "
                "detaylı olarak şunları belirt:\n"
                "1. Layout yapısı (header, sidebar, content, footer)\n"
                "2. Renk paleti\n"
                "3. Kullanılan bileşenler (butonlar, formlar, kartlar vb.)\n"
                "4. Tipografi\n"
                "5. Bu tasarımı HTML/CSS ile nasıl implement edersin\n"
                "Türkçe cevap ver."
            ),
            "images": [img_data],
        }],
    )
    return response["message"]["content"]


def dev_team_work(project: DevProject, task: str, team_members: list[str],
                  on_message=None, image_path: str = None):
    """
    Geliştirme ekibini bir görev üzerinde çalıştır.

    project: DevProject instance
    task: Yapılacak görev açıklaması
    team_members: Çalışacak ekip üyeleri listesi (ör: ["Mimar", "Kodcu", "Tester"])
    on_message: callback(role_name, emoji, message, color)
    image_path: Opsiyonel görsel dosya yolu (tasarım referansı)
    """
    on_message = on_message or (lambda *a: None)

    # Görsel analizi
    image_analysis = ""
    if image_path and os.path.exists(image_path):
        on_message("Sistem", "🖼", "Görsel analiz ediliyor...", "#7f8c8d")
        image_analysis = analyze_image(image_path)
        on_message("Sistem", "🖼", f"Görsel analiz tamamlandı:\n{image_analysis}", "#7f8c8d")

    # Mevcut dosyaları context olarak hazırla
    existing_files = project.list_files()
    files_context = ""
    if existing_files:
        files_context = "\n\nMevcut proje dosyaları:\n"
        for f in existing_files[:10]:  # Max 10 dosya
            content = project.get_file(f)
            if len(content) < 2000:
                files_context += f"\n--- {f} ---\n{content}\n"
            else:
                files_context += f"\n--- {f} --- (ilk 500 karakter)\n{content[:500]}...\n"

    accumulated_work = ""

    for i, role_name in enumerate(team_members):
        role = TEAM_ROLES.get(role_name)
        if not role:
            continue

        # Önceki ekip üyelerinin çıktılarını dahil et
        context = (
            f"Proje: {project.name}\n"
            f"Açıklama: {project.description}\n"
            f"Görev: {task}\n"
        )

        if image_analysis:
            context += f"\nTasarım referansı analizi:\n{image_analysis}\n"

        if files_context:
            context += files_context

        if accumulated_work:
            context += f"\n\nÖnceki ekip üyelerinin çalışması:\n{accumulated_work}"

        if i == 0:
            prompt = f"{context}\n\nBu görev için çalışmaya başla. Rolün: {role_name}"
        else:
            prompt = (
                f"{context}\n\n"
                f"Önceki ekip üyeleri yukarıdaki çalışmayı yaptı. "
                f"Senin rolün {role_name}. Kendi uzmanlık alanından katkıda bulun."
            )

        on_message(role_name, role["emoji"], "Çalışıyor...", role["color"])

        response = ollama.chat(
            model=CODE_MODEL,
            messages=[
                {"role": "system", "content": role["system"]},
                {"role": "user", "content": prompt},
            ],
        )

        output = response["message"]["content"]
        on_message(role_name, role["emoji"], output, role["color"])
        accumulated_work += f"\n\n--- {role['emoji']} {role_name} ---\n{output}"

        # Kod bloklarını çıkar ve dosyaları kaydet
        code_blocks = _extract_code_blocks(output)
        for block in code_blocks:
            if block["filename"]:
                project.save_file(block["filename"], block["content"])
                on_message(
                    "Sistem", "💾",
                    f"Dosya kaydedildi: {block['filename']}",
                    "#7f8c8d",
                )

    # Son özet
    saved_files = project.list_files()
    if saved_files:
        file_list = "\n".join(f"  - {f}" for f in saved_files)
        on_message(
            "Sistem", "✅",
            f"Proje tamamlandı! Dosyalar:\n{file_list}\n\nKonum: {project.project_dir}",
            "#27ae60",
        )

    return project
