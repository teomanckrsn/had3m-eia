"""Zamanlanmış Görevler — AI'lara belirli zamanlarda otomatik görev verme."""

import os
import json
import threading
import time
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule.json")

# Haftanın günleri
DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
DAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class Scheduler:
    """Zamanlanmış görevleri yönetir ve arka planda çalıştırır."""

    def __init__(self, on_trigger=None):
        """
        on_trigger: callback(task_dict) — görev tetiklendiğinde çağrılır
        """
        self.on_trigger = on_trigger or (lambda t: None)
        os.makedirs(DATA_DIR, exist_ok=True)
        self.tasks = self._load()
        self.running = False
        self.thread = None
        self._last_fired = {}  # task_id: last_fire_time

    def _load(self) -> list:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, name: str, ai_name: str, prompt: str,
                 time_str: str, days: list[int], enabled: bool = True):
        """
        name: Görev adı
        ai_name: Hangi AI çalıştıracak
        prompt: AI'a verilecek mesaj
        time_str: "HH:MM" format
        days: [0-6] Pazartesi=0
        """
        task_id = f"task_{int(time.time() * 1000)}"
        self.tasks.append({
            "id": task_id,
            "name": name,
            "ai_name": ai_name,
            "prompt": prompt,
            "time": time_str,
            "days": days,
            "enabled": enabled,
            "created": datetime.now().isoformat(),
        })
        self._save()
        return task_id

    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save()

    def toggle_task(self, task_id: str):
        for t in self.tasks:
            if t["id"] == task_id:
                t["enabled"] = not t.get("enabled", True)
                break
        self._save()

    def get_tasks(self) -> list:
        return list(self.tasks)

    def _check_and_fire(self):
        """Mevcut zamanı kontrol et, tetiklenmesi gereken görevleri çalıştır."""
        now = datetime.now()
        current_day = now.weekday()  # 0=Pzt, 6=Paz
        current_time = now.strftime("%H:%M")

        for task in self.tasks:
            if not task.get("enabled", True):
                continue

            if current_day not in task.get("days", []):
                continue

            if task.get("time") != current_time:
                continue

            # Aynı dakika içinde tetiklenmesin
            last = self._last_fired.get(task["id"])
            if last and (now - last).total_seconds() < 60:
                continue

            self._last_fired[task["id"]] = now
            try:
                self.on_trigger(task)
            except Exception as e:
                print(f"Scheduler error: {e}")

    def _run_loop(self):
        while self.running:
            self._check_and_fire()
            time.sleep(30)  # 30 saniyede bir kontrol

    def start(self):
        """Zamanlayıcıyı arka planda başlat."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False


def format_task(task: dict) -> str:
    """Görevi insan okunabilir formata çevir."""
    days_str = ", ".join(DAYS[d] for d in task.get("days", []))
    status = "🟢" if task.get("enabled", True) else "⚪"
    return (
        f"{status} {task['name']}\n"
        f"   🤖 {task['ai_name']}\n"
        f"   ⏰ {task['time']} — {days_str}"
    )
