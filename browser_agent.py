"""Kontrollü Tarayıcı Agent - Sadece izin verilen sitelerde, onaylı işlemler."""

import os
import io
import json
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, Page, Browser

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DOMAINS_FILE = os.path.join(DATA_DIR, "allowed_domains.json")
TASKS_FILE = os.path.join(DATA_DIR, "task_templates.json")
BROWSER_LOG_FILE = os.path.join(DATA_DIR, "browser_history.json")
SCREENSHOTS_DIR = os.path.join(DATA_DIR, "browser_logs")
PROFILE_DIR = os.path.join(DATA_DIR, "browser_profile")

# Kritik aksiyonlar - bunlar için onay gerekir
CRITICAL_KEYWORDS = [
    "submit", "send", "delete", "remove", "pay", "purchase", "buy",
    "confirm", "approve", "checkout", "order", "gönder", "sil", "onayla",
    "satın", "öde", "sipariş", "kaldır", "iptal",
]


class DomainManager:
    """İzin verilen domain'leri yönetir."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.domains = self._load()

    def _load(self) -> list:
        if os.path.exists(DOMAINS_FILE):
            with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(DOMAINS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.domains, f, ensure_ascii=False, indent=2)

    def add(self, domain: str):
        domain = domain.strip().lower().replace("https://", "").replace("http://", "").rstrip("/")
        if domain and domain not in self.domains:
            self.domains.append(domain)
            self._save()

    def remove(self, domain: str):
        domain = domain.strip().lower()
        if domain in self.domains:
            self.domains.remove(domain)
            self._save()

    def get_all(self) -> list:
        return list(self.domains)

    def is_allowed(self, url: str) -> bool:
        if not self.domains:
            return False
        parsed = urlparse(url)
        host = parsed.hostname or ""
        return any(
            host == d or host.endswith("." + d)
            for d in self.domains
        )


class TaskTemplateManager:
    """Tekrarlayan görev şablonlarını yönetir."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.templates = self._load()

    def _load(self) -> dict:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)

    def add(self, name: str, steps: list[dict], auto_approve: bool = False):
        """
        Görev şablonu ekle.
        steps: [{"action": "goto|click|fill|wait", "target": "...", "value": "..."}]
        auto_approve: True ise kritik olmayan adımlarda onay sorulmaz
        """
        self.templates[name] = {
            "name": name,
            "steps": steps,
            "auto_approve": auto_approve,
            "created": datetime.now().isoformat(),
        }
        self._save()

    def remove(self, name: str):
        if name in self.templates:
            del self.templates[name]
            self._save()

    def get(self, name: str) -> dict:
        return self.templates.get(name, {})

    def get_names(self) -> list[str]:
        return list(self.templates.keys())


class BrowserAgent:
    """
    Kontrollü tarayıcı agent.
    - Sadece izin verilen domain'lere gidebilir
    - Kritik aksiyonlarda onay ister
    - Ayrı profilde çalışır
    - Tüm aksiyonları loglar
    """

    def __init__(self, on_status=None, on_confirm=None, on_screenshot=None):
        """
        on_status: callback(str) - durum mesajları
        on_confirm: callback(str) -> bool - onay isteme (True=onayla, False=reddet)
        on_screenshot: callback(bytes) - screenshot gösterme
        """
        self.on_status = on_status or (lambda msg: None)
        self.on_confirm = on_confirm or (lambda msg: True)
        self.on_screenshot = on_screenshot or (lambda img: None)

        self.domains = DomainManager()
        self.templates = TaskTemplateManager()
        self.browser = None
        self.page = None
        self.playwright = None
        self.log = []

        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(PROFILE_DIR, exist_ok=True)

    def _log_action(self, action: str, target: str = "", result: str = ""):
        entry = {
            "action": action,
            "target": target,
            "result": result,
            "url": self.page.url if self.page else "",
            "timestamp": datetime.now().isoformat(),
        }
        self.log.append(entry)
        self._save_log()

    def _save_log(self):
        # Mevcut log'a ekle
        existing = []
        if os.path.exists(BROWSER_LOG_FILE):
            with open(BROWSER_LOG_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.extend(self.log)
        # Son 500 kaydı tut
        existing = existing[-500:]
        with open(BROWSER_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        self.log.clear()

    def _is_critical_action(self, action: str, target: str = "") -> bool:
        """Aksiyonun kritik olup olmadığını kontrol et."""
        text = (action + " " + target).lower()
        return any(kw in text for kw in CRITICAL_KEYWORDS)

    def _take_screenshot(self) -> bytes:
        """Screenshot al, sıkıştırılmış JPEG olarak kaydet ve döndür."""
        if not self.page:
            return b""
        screenshot = self.page.screenshot(type="jpeg", quality=50)

        # Dosyaya kaydet
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOTS_DIR, f"ss_{ts}.jpg")
        with open(path, "wb") as f:
            f.write(screenshot)

        # Eski screenshot'ları temizle (son 50 tane tut)
        files = sorted(Path(SCREENSHOTS_DIR).glob("ss_*.jpg"))
        for old in files[:-50]:
            old.unlink()

        return screenshot

    def start(self):
        """Tarayıcıyı başlat."""
        if self.browser:
            return

        self.on_status("Tarayıcı başlatılıyor...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            locale="tr-TR",
        )
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        self.on_status("Tarayıcı hazır.")
        self._log_action("start", "Tarayıcı başlatıldı")

    def stop(self):
        """Tarayıcıyı kapat."""
        if self.browser:
            self._log_action("stop", "Tarayıcı kapatıldı")
            self.browser.close()
            self.browser = None
            self.page = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        self.on_status("Tarayıcı kapatıldı.")

    def goto(self, url: str) -> dict:
        """URL'ye git. Sadece izin verilen domain'ler."""
        if not url.startswith("http"):
            url = "https://" + url

        if not self.domains.is_allowed(url):
            domain = urlparse(url).hostname
            msg = f"ENGELLENDI: '{domain}' izin verilen domainler arasında değil!"
            self.on_status(msg)
            self._log_action("goto_blocked", url, msg)
            return {"success": False, "message": msg}

        if not self.page:
            self.start()

        self.on_status(f"Gidiliyor: {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            msg = f"Sayfa yüklenemedi: {e}"
            self._log_action("goto_error", url, msg)
            return {"success": False, "message": msg}

        screenshot = self._take_screenshot()
        self.on_screenshot(screenshot)
        self._log_action("goto", url, "OK")
        self.on_status(f"Sayfa yüklendi: {self.page.title()}")
        return {"success": True, "message": "OK", "title": self.page.title()}

    def click(self, selector: str, description: str = "") -> dict:
        """Elemente tıkla. Kritik aksiyonlarda onay ister."""
        if not self.page:
            return {"success": False, "message": "Tarayıcı açık değil"}

        if self._is_critical_action("click", description or selector):
            approved = self.on_confirm(
                f"Kritik aksiyon: '{description or selector}' tıklanacak. Onaylıyor musun?"
            )
            if not approved:
                self._log_action("click_rejected", selector, "Kullanıcı reddetti")
                return {"success": False, "message": "Kullanıcı tarafından reddedildi"}

        try:
            self.page.click(selector, timeout=10000)
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception as e:
            msg = f"Tıklama hatası: {e}"
            self._log_action("click_error", selector, msg)
            return {"success": False, "message": msg}

        screenshot = self._take_screenshot()
        self.on_screenshot(screenshot)
        self._log_action("click", selector, description)
        return {"success": True, "message": "OK"}

    def fill(self, selector: str, value: str, description: str = "") -> dict:
        """Input alanını doldur. Şifre alanlarına yazamaz."""
        if not self.page:
            return {"success": False, "message": "Tarayıcı açık değil"}

        # Şifre alanı kontrolü
        try:
            input_type = self.page.get_attribute(selector, "type") or ""
            if input_type.lower() == "password":
                msg = "GÜVENLİK: Şifre alanlarına agent yazamaz. Lütfen kendin gir."
                self.on_status(msg)
                self._log_action("fill_blocked", selector, "Şifre alanı")
                return {"success": False, "message": msg}
        except Exception:
            pass

        if self._is_critical_action("fill", description):
            approved = self.on_confirm(
                f"'{description or selector}' alanına '{value}' yazılacak. Onaylıyor musun?"
            )
            if not approved:
                self._log_action("fill_rejected", selector, "Kullanıcı reddetti")
                return {"success": False, "message": "Kullanıcı tarafından reddedildi"}

        try:
            self.page.fill(selector, value, timeout=10000)
        except Exception as e:
            msg = f"Doldurma hatası: {e}"
            self._log_action("fill_error", selector, msg)
            return {"success": False, "message": msg}

        self._log_action("fill", selector, f"{description}: {value}")
        return {"success": True, "message": "OK"}

    def get_page_text(self) -> str:
        """Sayfanın metin içeriğini al."""
        if not self.page:
            return ""
        try:
            return self.page.inner_text("body")[:5000]
        except Exception:
            return ""

    def get_page_title(self) -> str:
        if not self.page:
            return ""
        return self.page.title()

    def get_current_url(self) -> str:
        if not self.page:
            return ""
        return self.page.url

    def wait(self, seconds: float = 2):
        """Bekle."""
        time.sleep(seconds)

    def screenshot(self) -> bytes:
        """Manuel screenshot al."""
        return self._take_screenshot()

    def execute_task(self, task_name: str, variables: dict = None) -> list[dict]:
        """Kaydedilmiş görev şablonunu çalıştır."""
        template = self.templates.get(task_name)
        if not template:
            return [{"success": False, "message": f"Görev bulunamadı: {task_name}"}]

        results = []
        variables = variables or {}

        for step in template.get("steps", []):
            action = step.get("action", "")
            target = step.get("target", "")
            value = step.get("value", "")
            desc = step.get("description", "")

            # Değişkenleri yerleştir
            for k, v in variables.items():
                target = target.replace(f"{{{{{k}}}}}", v)
                value = value.replace(f"{{{{{k}}}}}", v)

            if action == "goto":
                r = self.goto(target)
            elif action == "click":
                r = self.click(target, desc)
            elif action == "fill":
                r = self.fill(target, value, desc)
            elif action == "wait":
                self.wait(float(value or 2))
                r = {"success": True, "message": "Beklendi"}
            elif action == "screenshot":
                self.screenshot()
                r = {"success": True, "message": "Screenshot alındı"}
            else:
                r = {"success": False, "message": f"Bilinmeyen aksiyon: {action}"}

            results.append(r)

            if not r.get("success"):
                self.on_status(f"Görev durdu: {r.get('message')}")
                break

        self._log_action("task_complete", task_name, f"{len(results)} adım")
        return results
