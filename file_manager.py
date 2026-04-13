"""Dosya Yöneticisi - Sadece dosya taşıma. Silme ve çöp kutusuna taşıma YOK."""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MOVE_LOG_FILE = os.path.join(DATA_DIR, "move_history.json")

# YASAKLI HEDEFLER - bu klasörlere taşıma yapılamaz
BLOCKED_DESTINATIONS = [
    ".Trash",
    ".trash",
    "Trash",
    "trash",
    "$RECYCLE.BIN",
    "$Recycle.Bin",
]


class FileManager:
    """Dosya taşıma yöneticisi. SADECE taşıma — silme YOK."""

    def __init__(self, on_status=None):
        self.on_status = on_status or (lambda msg: None)
        os.makedirs(DATA_DIR, exist_ok=True)
        self.history = self._load_history()

    def _load_history(self) -> list:
        if os.path.exists(MOVE_LOG_FILE):
            with open(MOVE_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_history(self):
        with open(MOVE_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def _is_blocked_destination(self, dest: str) -> bool:
        """Çöp kutusuna veya yasaklı hedeflere taşımayı engelle."""
        dest_parts = Path(dest).parts
        for blocked in BLOCKED_DESTINATIONS:
            if blocked in dest_parts:
                return True
        # macOS çöp kutusu kontrolü
        home = os.path.expanduser("~")
        trash_path = os.path.join(home, ".Trash")
        if os.path.abspath(dest).startswith(trash_path):
            return True
        return False

    def move_file(self, source: str, destination: str) -> dict:
        """
        Dosyayı taşı.

        source: taşınacak dosyanın tam yolu
        destination: hedef klasör veya tam dosya yolu

        Döndürür: {"success": bool, "message": str, "new_path": str}
        """
        source = os.path.abspath(os.path.expanduser(source))
        destination = os.path.abspath(os.path.expanduser(destination))

        # Dosya var mı?
        if not os.path.exists(source):
            return {"success": False, "message": f"Dosya bulunamadı: {source}", "new_path": ""}

        # Çöp kutusu kontrolü
        if self._is_blocked_destination(destination):
            return {
                "success": False,
                "message": "ENGELLENDI: Çöp kutusuna taşıma yetkisi yok! Sadece klasörler arası taşıma yapılabilir.",
                "new_path": "",
            }

        # Hedef bir klasör mü?
        if os.path.isdir(destination):
            file_name = os.path.basename(source)
            dest_path = os.path.join(destination, file_name)
        else:
            dest_path = destination
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

        # Hedefte aynı isimde dosya var mı?
        if os.path.exists(dest_path):
            return {
                "success": False,
                "message": f"Hedefte aynı isimde dosya zaten var: {dest_path}",
                "new_path": "",
            }

        # Taşı
        try:
            shutil.move(source, dest_path)
        except PermissionError:
            return {"success": False, "message": f"İzin hatası: {source} taşınamadı.", "new_path": ""}
        except Exception as e:
            return {"success": False, "message": f"Hata: {e}", "new_path": ""}

        # Geçmişe kaydet
        record = {
            "source": source,
            "destination": dest_path,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(record)
        self._save_history()

        self.on_status(f"Taşındı: {os.path.basename(source)} → {dest_path}")
        return {"success": True, "message": "Dosya başarıyla taşındı.", "new_path": dest_path}

    def undo_last_move(self) -> dict:
        """Son taşımayı geri al."""
        if not self.history:
            return {"success": False, "message": "Geri alınacak işlem yok."}

        last = self.history[-1]
        current = last["destination"]
        original = last["source"]

        if not os.path.exists(current):
            self.history.pop()
            self._save_history()
            return {"success": False, "message": f"Dosya mevcut konumda bulunamadı: {current}"}

        # Orijinal konumun klasörünü oluştur
        original_dir = os.path.dirname(original)
        if not os.path.exists(original_dir):
            os.makedirs(original_dir, exist_ok=True)

        try:
            shutil.move(current, original)
        except Exception as e:
            return {"success": False, "message": f"Geri alma hatası: {e}"}

        self.history.pop()
        self._save_history()

        self.on_status(f"Geri alındı: {os.path.basename(original)} → {original}")
        return {"success": True, "message": f"Geri alındı: {original}"}

    def get_history(self) -> list:
        """Taşıma geçmişini döndür."""
        return list(self.history)

    def create_file(self, file_path: str, content: str = "") -> dict:
        """
        Yeni dosya oluştur.

        file_path: oluşturulacak dosyanın tam yolu
        content: dosya içeriği (varsayılan boş)

        Döndürür: {"success": bool, "message": str}
        """
        file_path = os.path.abspath(os.path.expanduser(file_path))

        # Zaten var mı?
        if os.path.exists(file_path):
            return {"success": False, "message": f"Bu dosya zaten mevcut: {file_path}"}

        # Klasörü oluştur
        parent_dir = os.path.dirname(file_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Sadece metin dosyaları oluşturulabilir
        ext = Path(file_path).suffix.lower()
        allowed_extensions = [".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".css"]
        if ext not in allowed_extensions:
            return {
                "success": False,
                "message": f"Sadece metin dosyaları oluşturulabilir ({', '.join(allowed_extensions)}). '{ext}' desteklenmiyor.",
            }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except PermissionError:
            return {"success": False, "message": f"İzin hatası: {file_path} oluşturulamadı."}
        except Exception as e:
            return {"success": False, "message": f"Hata: {e}"}

        self.on_status(f"Oluşturuldu: {os.path.basename(file_path)}")
        return {"success": True, "message": f"Dosya oluşturuldu: {file_path}"}

    def create_folder(self, folder_path: str) -> dict:
        """Yeni klasör oluştur."""
        folder_path = os.path.abspath(os.path.expanduser(folder_path))

        if os.path.exists(folder_path):
            return {"success": False, "message": f"Bu klasör zaten mevcut: {folder_path}"}

        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            return {"success": False, "message": f"Hata: {e}"}

        self.on_status(f"Klasör oluşturuldu: {os.path.basename(folder_path)}")
        return {"success": True, "message": f"Klasör oluşturuldu: {folder_path}"}

    def list_files(self, directory: str) -> list[str]:
        """Klasördeki dosyaları listele."""
        directory = os.path.abspath(os.path.expanduser(directory))
        if not os.path.isdir(directory):
            return []
        items = []
        for name in sorted(os.listdir(directory)):
            full = os.path.join(directory, name)
            if name.startswith("."):
                continue
            prefix = "📁 " if os.path.isdir(full) else "📄 "
            items.append(prefix + name)
        return items
