"""Mini AI Agent - Yerel RAG Asistan (CustomTkinter GUI)"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, colorchooser

import customtkinter as ctk

from rag_engine import RAGEngine
from debate import (debate, get_personality_names, get_persona_color, persona_manager,
                     get_trait_categories, get_all_traits, PERSONALITY_TRAITS,
                     PERMISSION_TYPES, DEFAULT_PERMISSIONS)
from file_manager import FileManager
from browser_agent import BrowserAgent
from auto_debate import AutoDebate
from dev_team import DevProject, dev_team_work, get_team_roles, TEAM_ROLES
from i18n import t, set_language, get_language, get_available_languages
from model_config import detect_models, get_chat_model, get_code_model
from datetime import datetime


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AIChatDialog(ctk.CTkToplevel):
    """Bir AI'a özel sohbet penceresi — geçmiş yüklenir, kayıtlı kalır."""

    def __init__(self, parent, ai_name: str):
        super().__init__(parent)
        self.ai_name = ai_name
        persona = persona_manager.get(ai_name)

        self.title(f"💬 {ai_name}")
        self.geometry("750x650")
        self.transient(parent)

        # Sohbet geçmişi
        from chat_history import ChatHistory
        self.history = ChatHistory(ai_name)

        # Model
        import ollama
        self.ollama = ollama
        self.model_name = get_chat_model()
        self.system_prompt = persona_manager.get_system_prompt(ai_name)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Başlık çubuğu
        header = ctk.CTkFrame(self, fg_color=persona.get("color", "#8e44ad"), corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text=f"💬 {ai_name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            padx=15, pady=10,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text=persona.get("description", "")[:60] + "...",
            font=ctk.CTkFont(size=11),
            text_color="#ddd", padx=15,
        ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        btn_clear = ctk.CTkButton(
            header, text="🗑 Geçmişi Temizle", width=130,
            fg_color="#c0392b", hover_color="#a93226",
            command=self._clear_history,
        )
        btn_clear.grid(row=0, column=1, rowspan=2, padx=10, pady=8)

        # Sohbet alanı
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="Sohbet")
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Giriş alanı
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            input_frame, placeholder_text=f"{ai_name}'a yazın...", height=40,
        )
        self.entry.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="ew")
        self.entry.bind("<Return>", lambda e: self._send())
        self.entry.focus_set()

        self.btn_send = ctk.CTkButton(
            input_frame, text="Gönder", width=80,
            command=self._send, fg_color="#27ae60",
        )
        self.btn_send.grid(row=0, column=1, padx=5, pady=5)

        # Geçmişi yükle
        self._load_history()

    def _add_bubble(self, text: str, is_user: bool):
        color = "#1a73e8" if is_user else "#2b2b2b"
        bubble = ctk.CTkFrame(self.chat_frame, fg_color=color, corner_radius=12)
        bubble.grid(
            sticky="e" if is_user else "w",
            padx=(100, 5) if is_user else (5, 100),
            pady=4,
        )
        if not is_user:
            ctk.CTkLabel(
                bubble, text=f"🤖 {self.ai_name}",
                font=ctk.CTkFont(weight="bold", size=11),
                anchor="w", padx=12, pady=(6, 0),
            ).pack(fill="x")
        ctk.CTkLabel(
            bubble, text=text, wraplength=500, justify="left",
            anchor="w", padx=12, pady=8,
        ).pack(fill="x")
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _load_history(self):
        """Kayıtlı geçmişi göster."""
        for msg in self.history.get_messages():
            self._add_bubble(msg["content"], is_user=(msg["role"] == "user"))

    def _clear_history(self):
        self.history.clear()
        # Sohbet frame'i temizle
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return

        self.entry.delete(0, "end")
        self._add_bubble(text, is_user=True)
        self.history.add_message("user", text)
        self.btn_send.configure(state="disabled")

        def work():
            try:
                messages = [{"role": "system", "content": self.system_prompt}]
                messages.extend(self.history.get_for_llm(max_messages=20))

                response = self.ollama.chat(
                    model=self.model_name,
                    messages=messages,
                )
                answer = response["message"]["content"]
                self.history.add_message("assistant", answer)
                self.after(0, lambda: self._add_bubble(answer, is_user=False))
            except Exception as e:
                err = f"Hata: {e}"
                self.after(0, lambda: self._add_bubble(err, is_user=False))
            finally:
                self.after(0, lambda: self.btn_send.configure(state="normal"))

        threading.Thread(target=work, daemon=True).start()


class CreateAIDialog(ctk.CTkToplevel):
    """Yeni AI oluştur — basit form: isim + görev tanımı."""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("🤖 Yeni AI Oluştur")
        self.geometry("520x480")
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Başlık
        ctk.CTkLabel(
            self, text="🤖 Yeni AI Oluştur",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        ctk.CTkLabel(
            self, text="Kendi yapay zekanı oluştur. İsim ver, görev tanımını yaz.",
            text_color="gray",
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Form frame
        form = ctk.CTkFrame(self)
        form.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        form.grid_columnconfigure(0, weight=1)

        # İsim
        ctk.CTkLabel(
            form, text="İsim", font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 3), sticky="w")

        self.name_entry = ctk.CTkEntry(
            form, placeholder_text="örn: Halime, Ayşe, Pazarlama Asistanı",
            height=38,
        )
        self.name_entry.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.name_entry.focus_set()

        # Görev tanımı
        ctk.CTkLabel(
            form, text="Görev Tanımı (Prompt)",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=2, column=0, padx=15, pady=(10, 3), sticky="w")

        ctk.CTkLabel(
            form, text="Nasıl biri olmalı? Ne iş yapacak? Karakteri nasıl olsun?",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).grid(row=3, column=0, padx=15, pady=0, sticky="w")

        self.task_text = ctk.CTkTextbox(form, height=140)
        self.task_text.grid(row=4, column=0, padx=15, pady=(5, 15), sticky="ew")
        self.task_text.insert(
            "1.0",
            "Sen benim kişisel asistanımsın. Günlük işlerimde bana yardım ediyorsun. "
            "Organize, pratik ve çözüm odaklısın. Kısa ve net cevaplar verirsin.",
        )

        # Oluştur butonu
        self.btn_create = ctk.CTkButton(
            self, text="✨ Oluştur", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8e44ad", hover_color="#7d3c98",
            command=self._create,
        )
        self.btn_create.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

    def _create(self):
        name = self.name_entry.get().strip()
        task = self.task_text.get("1.0", "end").strip()

        if not name:
            self.name_entry.configure(border_color="red")
            return
        if not task:
            return

        # İsim çakışması
        base = name
        final_name = base
        counter = 2
        while final_name in persona_manager.get_names():
            final_name = f"{base} ({counter})"
            counter += 1

        persona_manager.add(
            name=final_name,
            role=name,
            description=task,
            color="#8e44ad",
            traits=[],
            permissions=dict(DEFAULT_PERMISSIONS),
        )

        if self.on_save:
            self.on_save(final_name)
        self.destroy()


class PersonaDialog(ctk.CTkToplevel):
    """Yapay Zeka oluştur / düzenle — isim, rol, özellikler, izinler."""

    def __init__(self, parent, on_save=None, edit_name: str = None):
        super().__init__(parent)
        self.edit_name = edit_name
        self.editing = edit_name is not None
        self.title("Yapay Zeka Düzenle" if self.editing else "Yapay Zeka Oluştur")
        self.geometry("620x750")
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save
        self.selected_color = "#2b2b2b"

        # Düzenleme modunda mevcut veriyi yükle
        existing = persona_manager.get(edit_name) if self.editing else {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)

        row = 0
        ctk.CTkLabel(self, text="İsim:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="ör: Pazarlama Müdürü")
        self.name_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        if self.editing:
            self.name_entry.insert(0, existing.get("name", ""))

        row += 1
        ctk.CTkLabel(self, text="Rol:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.role_entry = ctk.CTkEntry(self, placeholder_text="ör: Dijital pazarlama uzmanı")
        self.role_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        if self.editing:
            self.role_entry.insert(0, existing.get("role", ""))

        row += 1
        ctk.CTkLabel(self, text="Tanım:").grid(row=row, column=0, padx=10, pady=5, sticky="nw")
        self.desc_text = ctk.CTkTextbox(self, height=60)
        self.desc_text.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        if self.editing and existing.get("description"):
            self.desc_text.insert("1.0", existing["description"])
        else:
            self.desc_text.insert("1.0", "Uzmanlık alanını tanımlayın (opsiyonel)...")

        row += 1
        ctk.CTkLabel(self, text="Renk:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        if self.editing:
            self.selected_color = existing.get("color", "#2b2b2b")
        self.color_btn = ctk.CTkButton(
            self, text="Renk Seç", fg_color=self.selected_color,
            command=self._pick_color, width=100,
        )
        self.color_btn.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        # === İzinler ===
        row += 1
        ctk.CTkLabel(
            self, text="İzinler:", font=ctk.CTkFont(weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(8, 3), sticky="w")

        row += 1
        perm_frame = ctk.CTkFrame(self, fg_color="transparent")
        perm_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=3)

        existing_perms = existing.get("permissions", DEFAULT_PERMISSIONS) if self.editing else DEFAULT_PERMISSIONS
        self.perm_vars = {}
        for perm_key, perm_label in PERMISSION_TYPES.items():
            var = tk.BooleanVar(value=existing_perms.get(perm_key, False))
            self.perm_vars[perm_key] = var
            ctk.CTkCheckBox(perm_frame, text=perm_label, variable=var).pack(
                side="left", padx=8, pady=3
            )

        # === Karakter Özellikleri ===
        row += 1
        ctk.CTkLabel(
            self, text="Karakter Özellikleri:", font=ctk.CTkFont(weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(8, 3), sticky="w")

        row += 1
        traits_frame = ctk.CTkScrollableFrame(self, height=220)
        traits_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=10, pady=3)

        existing_traits = existing.get("traits", []) if self.editing else []
        self.trait_vars = {}
        categories = get_trait_categories()

        for cat_name, trait_list in categories.items():
            ctk.CTkLabel(
                traits_frame, text=f"  {cat_name}",
                font=ctk.CTkFont(weight="bold", size=12),
            ).pack(anchor="w", padx=5, pady=(6, 1))

            cat_frame = ctk.CTkFrame(traits_frame, fg_color="transparent")
            cat_frame.pack(fill="x", padx=10, pady=1)

            for trait_name in trait_list:
                var = tk.BooleanVar(value=trait_name in existing_traits)
                self.trait_vars[trait_name] = var
                ctk.CTkCheckBox(
                    cat_frame, text=trait_name, variable=var, width=130,
                ).pack(side="left", padx=4, pady=1)

        # Kaydet butonu
        row += 1
        self.btn_save = ctk.CTkButton(
            self, text="Güncelle" if self.editing else "Oluştur",
            command=self._save, height=35, fg_color="#27ae60",
        )
        self.btn_save.grid(row=row, column=0, columnspan=2, padx=10, pady=10)

    def _pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.selected_color)
        if color[1]:
            self.selected_color = color[1]
            self.color_btn.configure(fg_color=self.selected_color)

    def _save(self):
        name = self.name_entry.get().strip()
        role = self.role_entry.get().strip()
        desc = self.desc_text.get("1.0", "end").strip()
        if desc == "Uzmanlık alanını tanımlayın (opsiyonel)...":
            desc = ""
        if not name or not role:
            return

        selected_traits = [t for t, v in self.trait_vars.items() if v.get()]
        selected_perms = {k: v.get() for k, v in self.perm_vars.items()}

        if self.editing:
            # Düzenleme: eski kişiliği güncelle
            persona_manager.update(
                self.edit_name,
                name=name, role=role, description=desc,
                color=self.selected_color, traits=selected_traits,
                permissions=selected_perms,
            )
        else:
            # Yeni oluştur
            persona_manager.add(
                name, role, desc, self.selected_color,
                traits=selected_traits, permissions=selected_perms,
            )

        if self.on_save:
            self.on_save()
        self.destroy()


class RelationshipDialog(ctk.CTkToplevel):
    """Kişilikler arası ilişki yönetimi penceresi."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Kişilik İlişkileri")
        self.geometry("600x500")
        self.transient(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # === İlişki ekleme ===
        add_frame = ctk.CTkFrame(self)
        add_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        add_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(add_frame, text="🔗 İlişki Tanımla", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=10, pady=(5, 2), sticky="w"
        )

        names = get_personality_names()

        ctk.CTkLabel(add_frame, text="Kim:").grid(row=1, column=0, padx=10, pady=5)
        self.from_var = tk.StringVar(value=names[0] if names else "")
        self.from_combo = ctk.CTkComboBox(add_frame, values=names, variable=self.from_var, width=160)
        self.from_combo.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(add_frame, text="→ Kime:").grid(row=1, column=2, padx=5, pady=5)
        self.to_var = tk.StringVar(value=names[1] if len(names) > 1 else "")
        self.to_combo = ctk.CTkComboBox(add_frame, values=names, variable=self.to_var, width=160)
        self.to_combo.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(add_frame, text="Düşüncesi:").grid(row=2, column=0, padx=10, pady=5)
        self.opinion_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="ör: Çok temkinli buluyorum, bazen fırsat kaçırıyoruz yüzünden",
        )
        self.opinion_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(
            add_frame, text="İlişki Kaydet", fg_color="#27ae60", command=self._save_relationship
        ).grid(row=3, column=0, columnspan=4, pady=10)

        # === Durum ===
        self.status_label = ctk.CTkLabel(self, text="", anchor="w")
        self.status_label.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        # === Mevcut ilişkiler ===
        ctk.CTkLabel(self, text="Mevcut İlişkiler:", font=ctk.CTkFont(weight="bold")).grid(
            row=2, column=0, sticky="w", padx=15, pady=(10, 0)
        )
        self.rel_text = ctk.CTkTextbox(self, height=200)
        self.rel_text.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5, 10))

        self._refresh_list()

    def _save_relationship(self):
        from_name = self.from_var.get().strip()
        to_name = self.to_var.get().strip()
        opinion = self.opinion_entry.get().strip()

        if not from_name or not to_name or not opinion:
            self.status_label.configure(text="❌ Tüm alanları doldur!")
            return
        if from_name == to_name:
            self.status_label.configure(text="❌ Aynı kişilik seçilemez!")
            return

        persona_manager.set_relationship(from_name, to_name, opinion)
        self.opinion_entry.delete(0, "end")
        self.status_label.configure(text=f"✅ {from_name} → {to_name} ilişkisi kaydedildi!")
        self._refresh_list()

    def _refresh_list(self):
        self.rel_text.delete("1.0", "end")
        names = get_personality_names()
        has_any = False
        for name in names:
            rels = persona_manager.get_all_relationships(name)
            if rels:
                has_any = True
                self.rel_text.insert("end", f"🔹 {name}:\n")
                for to_name, opinion in rels.items():
                    self.rel_text.insert("end", f"   → {to_name}: \"{opinion}\"\n")
                self.rel_text.insert("end", "\n")
        if not has_any:
            self.rel_text.insert("1.0", "Henüz ilişki tanımlanmamış.\n\nÖrnek:\nŞirket Yöneticisi → Finans Müdürü: \"Çok temkinli, bazen fırsatları kaçırıyoruz\"\nFinans Müdürü → Şirket Yöneticisi: \"Çok hırslı, riskleri görmezden geliyor\"")


class FileManagerDialog(ctk.CTkToplevel):
    """Dosya yönetimi penceresi — taşıma, oluşturma, geri alma."""

    def __init__(self, parent, file_mgr: FileManager):
        super().__init__(parent)
        self.title("Dosya Yöneticisi")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        self.fm = file_mgr

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # === Taşıma bölümü ===
        move_frame = ctk.CTkFrame(self)
        move_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        move_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(move_frame, text="📦 Dosya Taşı", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=10, pady=(5, 2), sticky="w"
        )

        ctk.CTkLabel(move_frame, text="Kaynak:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.source_entry = ctk.CTkEntry(move_frame, placeholder_text="Taşınacak dosyanın yolu")
        self.source_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(move_frame, text="Seç", width=50, command=self._pick_source).grid(
            row=1, column=2, padx=5, pady=5
        )

        ctk.CTkLabel(move_frame, text="Hedef:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.dest_entry = ctk.CTkEntry(move_frame, placeholder_text="Hedef klasör yolu")
        self.dest_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(move_frame, text="Seç", width=50, command=self._pick_dest).grid(
            row=2, column=2, padx=5, pady=5
        )

        btn_frame = ctk.CTkFrame(move_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=3, pady=5)

        ctk.CTkButton(btn_frame, text="Taşı", width=100, command=self._do_move).pack(side="left", padx=5)
        ctk.CTkButton(
            btn_frame, text="↩ Geri Al", width=100, fg_color="#e67e22", command=self._do_undo
        ).pack(side="left", padx=5)

        # === Dosya oluşturma bölümü ===
        create_frame = ctk.CTkFrame(self)
        create_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        create_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(create_frame, text="📝 Yeni Dosya / Klasör Oluştur", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=10, pady=(5, 2), sticky="w"
        )

        ctk.CTkLabel(create_frame, text="Yol:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.create_path_entry = ctk.CTkEntry(
            create_frame, placeholder_text="ör: ~/Desktop/notlar/yeni_dosya.txt"
        )
        self.create_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        create_btn_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        create_btn_frame.grid(row=2, column=0, columnspan=2, pady=5)

        ctk.CTkButton(
            create_btn_frame, text="📄 Dosya Oluştur", width=130, fg_color="#27ae60",
            command=self._do_create_file
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            create_btn_frame, text="📁 Klasör Oluştur", width=130, fg_color="#2980b9",
            command=self._do_create_folder
        ).pack(side="left", padx=5)

        # === Durum ===
        self.result_label = ctk.CTkLabel(self, text="", anchor="w", wraplength=550)
        self.result_label.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        # === Taşıma geçmişi ===
        ctk.CTkLabel(self, text="Taşıma Geçmişi:", font=ctk.CTkFont(weight="bold")).grid(
            row=3, column=0, sticky="nw", padx=15, pady=(5, 0)
        )
        self.history_text = ctk.CTkTextbox(self, height=120)
        self.history_text.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._refresh_history()

    def _pick_source(self):
        path = filedialog.askopenfilename(title="Taşınacak dosyayı seç")
        if path:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, path)

    def _pick_dest(self):
        path = filedialog.askdirectory(title="Hedef klasörü seç")
        if path:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, path)

    def _show_result(self, result: dict):
        icon = "✅" if result["success"] else "❌"
        self.result_label.configure(text=f"{icon} {result['message']}")
        self._refresh_history()

    def _do_move(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        if not source or not dest:
            self.result_label.configure(text="❌ Kaynak ve hedef belirtilmeli!")
            return
        result = self.fm.move_file(source, dest)
        self._show_result(result)

    def _do_undo(self):
        result = self.fm.undo_last_move()
        self._show_result(result)

    def _do_create_file(self):
        path = self.create_path_entry.get().strip()
        if not path:
            self.result_label.configure(text="❌ Dosya yolu belirtilmeli!")
            return
        result = self.fm.create_file(path)
        self._show_result(result)

    def _do_create_folder(self):
        path = self.create_path_entry.get().strip()
        if not path:
            self.result_label.configure(text="❌ Klasör yolu belirtilmeli!")
            return
        result = self.fm.create_folder(path)
        self._show_result(result)

    def _refresh_history(self):
        self.history_text.delete("1.0", "end")
        history = self.fm.get_history()
        if not history:
            self.history_text.insert("1.0", "Henüz taşıma yapılmadı.")
            return
        for i, h in enumerate(reversed(history[-10:]), 1):
            src = os.path.basename(h["source"])
            dest = h["destination"]
            ts = h["timestamp"][:16].replace("T", " ")
            self.history_text.insert("end", f"{i}. {src} → {dest}\n   ({ts})\n\n")


class BrowserDialog(ctk.CTkToplevel):
    """Kontrollü tarayıcı penceresi."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("HAD3M-EIA — Tarayıcı Agent")
        self.geometry("750x650")
        self.transient(parent)

        self.agent = BrowserAgent(
            on_status=self._update_status,
            on_confirm=self._ask_confirm,
            on_screenshot=self._show_screenshot,
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # === Domain yönetimi ===
        domain_frame = ctk.CTkFrame(self)
        domain_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        domain_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(domain_frame, text="🔒 İzin Verilen Siteler", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=10, pady=(5, 2), sticky="w"
        )

        self.domain_entry = ctk.CTkEntry(domain_frame, placeholder_text="ör: shipstation.com")
        self.domain_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(domain_frame, text="Ekle", width=60, fg_color="#27ae60",
                       command=self._add_domain).grid(row=1, column=2, padx=5, pady=5)
        ctk.CTkButton(domain_frame, text="Çıkar", width=60, fg_color="#c0392b",
                       command=self._remove_domain).grid(row=1, column=3, padx=5, pady=5)

        self.domain_label = ctk.CTkLabel(domain_frame, text="", anchor="w", wraplength=650)
        self.domain_label.grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="w")
        self._refresh_domains()

        # === Görev alanı ===
        task_frame = ctk.CTkFrame(self)
        task_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        task_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(task_frame, text="🎯 Görev", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=10, pady=(5, 2), sticky="w"
        )

        self.url_entry = ctk.CTkEntry(task_frame, placeholder_text="URL: https://shipstation.com/orders")
        self.url_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(task_frame, text="Git", width=60, command=self._do_goto).grid(
            row=1, column=1, padx=5, pady=5
        )
        ctk.CTkButton(task_frame, text="Screenshot", width=90, fg_color="#2980b9",
                       command=self._do_screenshot).grid(row=1, column=2, padx=5, pady=5)

        # Tarayıcı kontrol butonları
        ctrl_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        ctrl_frame.grid(row=2, column=0, columnspan=3, pady=5)

        ctk.CTkButton(ctrl_frame, text="▶ Tarayıcı Aç", width=120, fg_color="#27ae60",
                       command=self._start_browser).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frame, text="⏹ Tarayıcı Kapat", width=120, fg_color="#c0392b",
                       command=self._stop_browser).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frame, text="📄 Sayfa Metni", width=110, fg_color="#7f8c8d",
                       command=self._get_text).pack(side="left", padx=5)

        # === Tıklama / Form doldurma ===
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        action_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(action_frame, text="Selector:").grid(row=0, column=0, padx=10, pady=5)
        self.selector_entry = ctk.CTkEntry(action_frame, placeholder_text="CSS selector (ör: #login-btn, .submit)")
        self.selector_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(action_frame, text="Tıkla", width=60, command=self._do_click).grid(
            row=0, column=2, padx=5, pady=5
        )

        ctk.CTkLabel(action_frame, text="Değer:").grid(row=1, column=0, padx=10, pady=5)
        self.value_entry = ctk.CTkEntry(action_frame, placeholder_text="Doldurmak için değer")
        self.value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkButton(action_frame, text="Doldur", width=60, command=self._do_fill).grid(
            row=1, column=2, padx=5, pady=5
        )

        # === Durum ===
        self.status_label = ctk.CTkLabel(self, text="Tarayıcı kapalı. Önce site ekle, sonra tarayıcıyı aç.", anchor="w")
        self.status_label.grid(row=3, column=0, sticky="ew", padx=15, pady=5)

        # === Log alanı ===
        self.log_text = ctk.CTkTextbox(self, height=150)
        self.log_text.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Pencere kapanınca tarayıcıyı kapat
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _update_status(self, msg: str):
        self.after(0, lambda: self.status_label.configure(text=msg))
        self.after(0, lambda: self._append_log(msg))

    def _append_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n")
        self.log_text.see("end")

    def _ask_confirm(self, msg: str) -> bool:
        """Kritik aksiyon onay penceresi."""
        from tkinter import messagebox
        return messagebox.askyesno("Onay Gerekli", msg, parent=self)

    def _show_screenshot(self, img_bytes: bytes):
        """Screenshot'ı log'a not olarak ekle (görsel gösterim ileride eklenebilir)."""
        self._append_log("📸 Screenshot alındı ve kaydedildi.")

    def _refresh_domains(self):
        domains = self.agent.domains.get_all()
        if domains:
            self.domain_label.configure(text=f"İzinli: {', '.join(domains)}")
        else:
            self.domain_label.configure(text="Henüz site eklenmedi. Önce izin verilen siteleri ekleyin.")

    def _add_domain(self):
        d = self.domain_entry.get().strip()
        if d:
            self.agent.domains.add(d)
            self.domain_entry.delete(0, "end")
            self._refresh_domains()
            self._update_status(f"'{d}' eklendi.")

    def _remove_domain(self):
        d = self.domain_entry.get().strip()
        if d:
            self.agent.domains.remove(d)
            self.domain_entry.delete(0, "end")
            self._refresh_domains()
            self._update_status(f"'{d}' çıkarıldı.")

    def _start_browser(self):
        def work():
            try:
                self.agent.start()
            except Exception as e:
                self._update_status(f"Hata: {e}")
        threading.Thread(target=work, daemon=True).start()

    def _stop_browser(self):
        def work():
            self.agent.stop()
        threading.Thread(target=work, daemon=True).start()

    def _do_goto(self):
        url = self.url_entry.get().strip()
        if not url:
            return
        def work():
            self.agent.goto(url)
        threading.Thread(target=work, daemon=True).start()

    def _do_click(self):
        sel = self.selector_entry.get().strip()
        if not sel:
            return
        def work():
            r = self.agent.click(sel)
            if not r["success"]:
                self._update_status(r["message"])
        threading.Thread(target=work, daemon=True).start()

    def _do_fill(self):
        sel = self.selector_entry.get().strip()
        val = self.value_entry.get().strip()
        if not sel or not val:
            return
        def work():
            r = self.agent.fill(sel, val)
            if not r["success"]:
                self._update_status(r["message"])
        threading.Thread(target=work, daemon=True).start()

    def _do_screenshot(self):
        def work():
            self.agent.screenshot()
            self._update_status("Screenshot alındı.")
        threading.Thread(target=work, daemon=True).start()

    def _get_text(self):
        def work():
            text = self.agent.get_page_text()
            self.after(0, lambda: self._append_log(f"Sayfa metni:\n{text[:500]}..."))
        threading.Thread(target=work, daemon=True).start()

    def _on_close(self):
        self.agent.stop()
        self.destroy()


class DevTeamDialog(ctk.CTkToplevel):
    """Geliştirme ekibi penceresi — kodcu, tasarımcı, tester birlikte çalışır."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("HAD3M-EIA — Geliştirme Ekibi")
        self.geometry("850x700")
        self.transient(parent)

        self.project = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # === Proje bilgileri ===
        proj_frame = ctk.CTkFrame(self)
        proj_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        proj_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(proj_frame, text="🏗 Proje", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=10, pady=(5, 2), sticky="w"
        )

        ctk.CTkLabel(proj_frame, text="Ad:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.proj_name = ctk.CTkEntry(proj_frame, placeholder_text="ör: e-ticaret-sitesi")
        self.proj_name.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(proj_frame, text="Açıklama:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.proj_desc = ctk.CTkEntry(proj_frame, placeholder_text="ör: Basit bir ürün listeleme ve sepet sistemi")
        self.proj_desc.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # === Görev ve ekip seçimi ===
        task_frame = ctk.CTkFrame(self)
        task_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        task_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(task_frame, text="🎯 Görev", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(5, 2), sticky="w"
        )

        self.task_entry = ctk.CTkEntry(
            task_frame, placeholder_text="ör: Login sayfası oluştur, responsive olsun", height=40
        )
        self.task_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Ekip üyeleri seçimi
        team_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        team_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(team_frame, text="Ekip:").pack(side="left", padx=(0, 10))

        self.team_vars = {}
        for role_name, role_info in TEAM_ROLES.items():
            var = tk.BooleanVar(value=True)
            self.team_vars[role_name] = var
            ctk.CTkCheckBox(
                team_frame, text=f"{role_info['emoji']} {role_name}",
                variable=var
            ).pack(side="left", padx=5)

        # Başlat butonu
        self.btn_start = ctk.CTkButton(
            task_frame, text="▶ Ekibi Çalıştır", height=35, fg_color="#27ae60",
            command=self._start_work
        )
        self.btn_start.grid(row=3, column=0, padx=10, pady=10)

        # === Durum ===
        self.status_label = ctk.CTkLabel(self, text="Proje adı ve görev girin, ekibi seçin, çalıştırın.", anchor="w")
        self.status_label.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        # === Çıktı alanı ===
        self.output_frame = ctk.CTkScrollableFrame(self, label_text="Ekip Çıktısı")
        self.output_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.output_frame.grid_columnconfigure(0, weight=1)

    def _add_output(self, role: str, emoji: str, text: str, color: str):
        frame = ctk.CTkFrame(self.output_frame, fg_color=color, corner_radius=10)
        frame.grid(sticky="ew", padx=5, pady=3)

        header = ctk.CTkLabel(
            frame, text=f"{emoji} {role}",
            font=ctk.CTkFont(weight="bold"), anchor="w", padx=10, pady=(5, 0),
        )
        header.pack(fill="x")

        body = ctk.CTkLabel(
            frame, text=text, wraplength=700, justify="left",
            anchor="w", padx=10, pady=(2, 8),
        )
        body.pack(fill="x")

        self.output_frame._parent_canvas.yview_moveto(1.0)

    def _start_work(self):
        name = self.proj_name.get().strip()
        desc = self.proj_desc.get().strip()
        task = self.task_entry.get().strip()

        if not name or not task:
            self.status_label.configure(text="❌ Proje adı ve görev gerekli!")
            return

        selected_team = [r for r, v in self.team_vars.items() if v.get()]
        if not selected_team:
            self.status_label.configure(text="❌ En az bir ekip üyesi seçin!")
            return

        self.project = DevProject(name, desc or task)
        self.btn_start.configure(state="disabled")
        self.status_label.configure(text="Ekip çalışıyor...")

        def on_message(role, emoji, text, color):
            self.after(0, lambda r=role, e=emoji, t=text, c=color: self._add_output(r, e, t, c))
            self.after(0, lambda: self.status_label.configure(text=f"{emoji} {role} çalışıyor..."))

        def work():
            try:
                dev_team_work(
                    self.project, task, selected_team,
                    on_message=on_message,
                )
                self.after(0, lambda: self.status_label.configure(
                    text=f"✅ Tamamlandı! Dosyalar: {self.project.project_dir}"
                ))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ Hata: {e}"))
            finally:
                self.after(0, lambda: self.btn_start.configure(state="normal"))

        threading.Thread(target=work, daemon=True).start()


class SettingsDialog(ctk.CTkToplevel):
    """Ayarlar penceresi — dil değiştirme ve diğer ayarlar."""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title(t("settings"))
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save

        self.grid_columnconfigure(1, weight=1)

        # Dil seçimi
        ctk.CTkLabel(self, text=t("language") + ":", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=15, pady=15, sticky="w"
        )

        lang_names = {"tr": "Türkçe", "en": "English"}
        current = get_language()
        self.lang_var = tk.StringVar(value=current)

        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        for lang_code in get_available_languages():
            ctk.CTkRadioButton(
                lang_frame, text=lang_names.get(lang_code, lang_code),
                variable=self.lang_var, value=lang_code,
            ).pack(side="left", padx=10)

        # Bilgi
        ctk.CTkLabel(
            self, text="Dil değişikliği uygulamayı yeniden başlattığında aktif olur.",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="w")

        ctk.CTkLabel(
            self, text="Language change takes effect after restarting the app.",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).grid(row=2, column=0, columnspan=2, padx=15, pady=0, sticky="w")

        # Kaydet
        ctk.CTkButton(
            self, text=t("save"), fg_color="#27ae60", command=self._save
        ).grid(row=3, column=0, columnspan=2, padx=15, pady=20)

    def _save(self):
        set_language(self.lang_var.get())
        if self.on_save:
            self.on_save()
        self.destroy()


class MiniAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HAD3M-EIA")
        self.geometry("1000x800")
        self.minsize(800, 600)

        self.engine = None
        self.file_mgr = FileManager()
        self.current_answer = ""
        self.current_question = ""

        self._build_ui()
        self._init_engine()

    def _build_ui(self):
        # İki sütun: sol sidebar (AI listesi), sağ ana içerik
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === Sol sidebar: AI listesi ===
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.sidebar, text="🤖 Yapay Zekalar",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        btn_new_ai = ctk.CTkButton(
            self.sidebar, text="+ Yeni AI Oluştur",
            fg_color="#8e44ad", hover_color="#7d3c98",
            command=self._open_persona_dialog,
        )
        btn_new_ai.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.ai_list_frame = ctk.CTkScrollableFrame(self.sidebar, label_text="")
        self.ai_list_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.ai_list_frame.grid_columnconfigure(0, weight=1)

        # === Üst bar ===
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 5))
        top_frame.grid_columnconfigure(8, weight=1)

        self.btn_add = ctk.CTkButton(
            top_frame, text=t("add_file"), width=110, command=self._add_files
        )
        self.btn_add.grid(row=0, column=0, padx=3, pady=5)

        self.btn_clear = ctk.CTkButton(
            top_frame, text=t("clear"), width=70, fg_color="gray",
            command=self._clear_files
        )
        self.btn_clear.grid(row=0, column=1, padx=3, pady=5)

        self.btn_new_persona = ctk.CTkButton(
            top_frame, text=t("create_ai"), width=100, fg_color="#8e44ad",
            command=self._open_persona_dialog
        )
        self.btn_new_persona.grid(row=0, column=2, padx=3, pady=5)

        self.btn_relationships = ctk.CTkButton(
            top_frame, text=t("relationships"), width=90, fg_color="#e67e22",
            command=self._open_relationships
        )
        self.btn_relationships.grid(row=0, column=3, padx=3, pady=5)

        self.btn_file_mgr = ctk.CTkButton(
            top_frame, text=t("file_manager"), width=70, fg_color="#d35400",
            command=self._open_file_manager
        )
        self.btn_file_mgr.grid(row=0, column=4, padx=3, pady=5)

        self.btn_browser = ctk.CTkButton(
            top_frame, text=t("browser"), width=85, fg_color="#2c3e50",
            command=self._open_browser
        )
        self.btn_browser.grid(row=0, column=5, padx=3, pady=5)

        self.btn_dev_team = ctk.CTkButton(
            top_frame, text=t("dev_team"), width=70, fg_color="#2ecc71",
            command=self._open_dev_team
        )
        self.btn_dev_team.grid(row=0, column=6, padx=3, pady=5)

        self.btn_settings = ctk.CTkButton(
            top_frame, text=t("settings_btn"), width=70, fg_color="#7f8c8d",
            command=self._open_settings
        )
        self.btn_settings.grid(row=0, column=7, padx=3, pady=5)

        self.file_label = ctk.CTkLabel(top_frame, text=t("no_files"), anchor="w")
        self.file_label.grid(row=0, column=8, padx=10, pady=5, sticky="w")

        # === Mod seçimi + kişilik seçiciler ===
        mode_frame = ctk.CTkFrame(self)
        mode_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 5))
        mode_frame.grid_columnconfigure(7, weight=1)

        self.mode_var = tk.StringVar(value="chat")

        self.radio_chat = ctk.CTkRadioButton(
            mode_frame, text=t("chat_mode"), variable=self.mode_var, value="chat",
            command=self._on_mode_change
        )
        self.radio_chat.grid(row=0, column=0, padx=10, pady=5)

        self.radio_debate = ctk.CTkRadioButton(
            mode_frame, text=t("debate_mode"), variable=self.mode_var, value="debate",
            command=self._on_mode_change
        )
        self.radio_debate.grid(row=0, column=1, padx=10, pady=5)

        names = get_personality_names()

        ctk.CTkLabel(mode_frame, text="Kişilik 1:").grid(row=0, column=2, padx=(20, 5))
        self.persona1_var = tk.StringVar(value=names[0] if names else "")
        self.combo_p1 = ctk.CTkComboBox(
            mode_frame, values=names, variable=self.persona1_var, width=150
        )
        self.combo_p1.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(mode_frame, text="vs").grid(row=0, column=4, padx=5)

        self.persona2_var = tk.StringVar(value=names[1] if len(names) > 1 else "")
        self.combo_p2 = ctk.CTkComboBox(
            mode_frame, values=names, variable=self.persona2_var, width=150
        )
        self.combo_p2.grid(row=0, column=5, padx=5, pady=5)

        self.btn_edit_persona = ctk.CTkButton(
            mode_frame, text="✏️", width=35, fg_color="#2980b9",
            command=self._edit_persona
        )
        self.btn_edit_persona.grid(row=0, column=6, padx=2, pady=5)

        self.btn_del_persona = ctk.CTkButton(
            mode_frame, text="🗑", width=35, fg_color="#c0392b",
            command=self._delete_persona
        )
        self.btn_del_persona.grid(row=0, column=7, padx=2, pady=5)

        # Otonom tartışma ayarları
        ctk.CTkLabel(mode_frame, text="Tur:").grid(row=0, column=8, padx=(10, 2))
        self.rounds_var = tk.StringVar(value="20")
        self.rounds_entry = ctk.CTkEntry(mode_frame, textvariable=self.rounds_var, width=50)
        self.rounds_entry.grid(row=0, column=9, padx=2, pady=5)

        self.btn_auto_debate = ctk.CTkButton(
            mode_frame, text="🔄 Otonom", width=80, fg_color="#e67e22",
            command=self._start_auto_debate
        )
        self.btn_auto_debate.grid(row=0, column=10, padx=5, pady=5)

        self.btn_stop_debate = ctk.CTkButton(
            mode_frame, text="⏹", width=35, fg_color="#c0392b",
            command=self._stop_auto_debate
        )
        self.btn_stop_debate.grid(row=0, column=11, padx=2, pady=5)

        self.auto_debate = None

        self._on_mode_change()

        # === Sohbet alanı ===
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text=t("chat_label"))
        self.chat_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_widgets = []

        # === Giriş alanı ===
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=3, column=1, sticky="ew", padx=10, pady=(5, 10))
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            bottom_frame, placeholder_text=t("type_question"), height=40
        )
        self.input_entry.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="ew")
        self.input_entry.bind("<Return>", self._on_enter)

        self.btn_send = ctk.CTkButton(
            bottom_frame, text=t("send"), width=80, command=self._send_question
        )
        self.btn_send.grid(row=0, column=1, padx=5, pady=5)

        # === Durum çubuğu ===
        self.status_label = ctk.CTkLabel(self, text="Başlatılıyor...", anchor="w")
        self.status_label.grid(row=4, column=1, sticky="ew", padx=15, pady=(0, 5))

        # AI listesini başlangıçta doldur
        self._refresh_ai_list()

    def _open_file_manager(self):
        FileManagerDialog(self, self.file_mgr)

    def _start_auto_debate(self):
        p1 = self.persona1_var.get()
        p2 = self.persona2_var.get()
        topic = self.input_entry.get().strip()

        if not p1 or not p2 or p1 == p2:
            self._update_status("Farklı 2 kişilik seçin!")
            return
        if not topic:
            self._update_status("Tartışma konusu yazın!")
            return

        self.input_entry.delete(0, "end")

        try:
            rounds = int(self.rounds_var.get())
        except ValueError:
            rounds = 20

        self._add_chat_bubble(f"Otonom tartışma: {p1} vs {p2} — {rounds} tur\nKonu: {topic}", is_user=True)

        self.auto_debate = AutoDebate(
            topic=topic,
            personas=[p1, p2],
            rounds=rounds,
            on_message=lambda p, m, r: self.after(0, lambda: self._add_chat_bubble(
                f"[Tur {r}] {m}", persona=p
            )),
            on_status=lambda s: self._update_status(s),
        )

        self.btn_auto_debate.configure(state="disabled")

        def work():
            self.auto_debate.run()
            self.after(0, lambda: self.btn_auto_debate.configure(state="normal"))
            self.after(0, lambda: self._update_status(
                f"Tartışma bitti! Dosyalar: data/debates/"
            ))

        threading.Thread(target=work, daemon=True).start()

    def _stop_auto_debate(self):
        if self.auto_debate:
            self.auto_debate.stop()
            self._update_status("Tartışma durduruluyor...")

    def _open_settings(self):
        SettingsDialog(self)

    def _open_relationships(self):
        RelationshipDialog(self)

    def _open_browser(self):
        BrowserDialog(self)

    def _open_dev_team(self):
        DevTeamDialog(self)

    def _refresh_persona_combos(self):
        names = get_personality_names()
        self.combo_p1.configure(values=names)
        self.combo_p2.configure(values=names)
        if names and not self.persona1_var.get():
            self.persona1_var.set(names[0])
        if len(names) > 1 and not self.persona2_var.get():
            self.persona2_var.set(names[1])

    def _open_persona_dialog(self):
        # Form ile yeni AI oluştur (isim + görev)
        def on_created(name=None):
            self._refresh_persona_combos()
            self._refresh_ai_list()
            # Oluşturulan AI'ın sohbet penceresini direkt aç
            if name:
                AIChatDialog(self, name)
        CreateAIDialog(self, on_save=on_created)

    def _refresh_ai_list(self):
        """Sol sidebar'daki AI butonlarını yenile."""
        # Önceki butonları temizle
        for widget in self.ai_list_frame.winfo_children():
            widget.destroy()

        names = persona_manager.get_names()
        if not names:
            ctk.CTkLabel(
                self.ai_list_frame,
                text="Henüz AI yok.\n\n'+ Yeni AI Oluştur'\nbutonuna bas.",
                text_color="gray", justify="center",
            ).pack(pady=20)
            return

        for name in names:
            persona = persona_manager.get(name)
            color = persona.get("color", "#8e44ad")
            btn = ctk.CTkButton(
                self.ai_list_frame,
                text=f"🤖 {name}",
                fg_color=color,
                hover_color=color,
                anchor="w",
                height=40,
                command=lambda n=name: self._open_ai_chat(n),
            )
            btn.pack(fill="x", padx=5, pady=3)

    def _open_ai_chat(self, name: str):
        """AI'ın kendi sohbet penceresini aç."""
        AIChatDialog(self, name)

    def _edit_persona(self):
        name = self.persona1_var.get()
        if name and name in persona_manager.get_names():
            PersonaDialog(self, on_save=self._refresh_persona_combos, edit_name=name)

    def _delete_persona(self):
        name = self.persona1_var.get()
        if name:
            persona_manager.remove(name)
            self._refresh_persona_combos()
            names = get_personality_names()
            if names:
                self.persona1_var.set(names[0])
            self._update_status(f"'{name}' kişiliği silindi.")

    def _on_mode_change(self):
        is_debate = self.mode_var.get() == "debate"
        state = "normal" if is_debate else "disabled"
        self.combo_p1.configure(state=state)
        self.combo_p2.configure(state=state)
        self.btn_edit_persona.configure(state=state)
        self.btn_del_persona.configure(state=state)
        self.rounds_entry.configure(state=state)
        self.btn_auto_debate.configure(state=state)
        self.btn_stop_debate.configure(state=state)
        if is_debate:
            self.input_entry.configure(placeholder_text=t("type_debate_topic"))
        else:
            self.input_entry.configure(placeholder_text=t("type_question"))

    def _init_engine(self):
        def init():
            try:
                # Modelleri algıla
                self._update_status("Modeller algılanıyor...")
                config = detect_models()
                chat = config.get("chat_model", "?")
                code = config.get("code_model", "?")
                self._update_status(f"Modeller: Sohbet={chat} | Kod={code}")

                self.engine = RAGEngine(on_status=self._update_status)
                self._update_status(f"Hazır! (Model: {chat})")
                self._update_file_label()
            except Exception as e:
                self._update_status(f"Hata: {e}")
        threading.Thread(target=init, daemon=True).start()

    def _update_status(self, msg: str):
        self.after(0, lambda: self.status_label.configure(text=msg))

    def _update_file_label(self):
        if self.engine is None:
            return
        files = self.engine.get_indexed_files()
        text = f"Yüklü: {', '.join(files)} ({len(files)})" if files else "Henüz dosya yüklenmedi"
        self.after(0, lambda: self.file_label.configure(text=text))

    def _add_files(self):
        if self.engine is None:
            return
        paths = filedialog.askopenfilenames(
            title="Dosya Seç",
            filetypes=[
                ("Tüm desteklenen", "*.pdf *.docx *.txt *.md *.csv *.json *.py *.js *.html"),
                ("PDF", "*.pdf"), ("Word", "*.docx"), ("Metin", "*.txt *.md *.csv"),
                ("Tümü", "*.*"),
            ],
        )
        if not paths:
            return

        def process():
            for p in paths:
                try:
                    self.engine.add_document(p)
                except Exception as e:
                    self._update_status(f"Hata ({os.path.basename(p)}): {e}")
            self._update_file_label()
        threading.Thread(target=process, daemon=True).start()

    def _clear_files(self):
        if self.engine is None:
            return
        for f in self.engine.get_indexed_files():
            self.engine.remove_document(f)
        self._update_file_label()
        self._update_status("Tüm dosyalar temizlendi.")

    def _add_chat_bubble(self, text: str, is_user: bool = False,
                         show_feedback: bool = False, persona: str = None):
        if persona:
            color = get_persona_color(persona) if persona != "🏛 Moderatör" else "#7f8c8d"
        elif is_user:
            color = "#1a73e8"
        else:
            color = "#2b2b2b"

        bubble_frame = ctk.CTkFrame(
            self.chat_frame, fg_color=color, corner_radius=12,
        )
        bubble_frame.grid(
            sticky="e" if is_user else "w",
            padx=(120 if is_user else 5, 5 if is_user else 120),
            pady=3,
        )

        if persona:
            name_label = ctk.CTkLabel(
                bubble_frame, text=persona, font=ctk.CTkFont(weight="bold"),
                anchor="w", padx=12, pady=(6, 0),
            )
            name_label.pack(fill="x")

        label = ctk.CTkLabel(
            bubble_frame, text=text, wraplength=550, justify="left",
            anchor="w", padx=12, pady=8,
        )
        label.pack(fill="x")

        if show_feedback:
            fb_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
            fb_frame.pack(fill="x", padx=5, pady=(0, 5))

            question = self.current_question
            answer = text

            btn_like = ctk.CTkButton(
                fb_frame, text="👍", width=40, height=28, fg_color="#2d8a4e",
                command=lambda q=question, a=answer: self._give_feedback(q, a, True),
            )
            btn_like.pack(side="left", padx=2)

            btn_dislike = ctk.CTkButton(
                fb_frame, text="👎", width=40, height=28, fg_color="#c0392b",
                command=lambda q=question, a=answer: self._give_feedback(q, a, False),
            )
            btn_dislike.pack(side="left", padx=2)

        self.chat_widgets.append(bubble_frame)
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _give_feedback(self, question: str, answer: str, liked: bool):
        if self.engine:
            self.engine.feedback.add(question, answer, liked)
            emoji = "👍" if liked else "👎"
            self._update_status(f"Geri bildirim kaydedildi {emoji} — Agent öğreniyor!")

    def _on_enter(self, event):
        self._send_question()

    def _send_question(self):
        if self.engine is None:
            self._update_status("Engine henüz hazır değil...")
            return

        text = self.input_entry.get().strip()
        if not text:
            return

        self.input_entry.delete(0, "end")
        self.current_question = text
        self._add_chat_bubble(text, is_user=True)
        self.btn_send.configure(state="disabled")

        if self.mode_var.get() == "debate":
            self._run_debate(text)
        else:
            self._run_chat(text)

    def _run_chat(self, question: str):
        def work():
            try:
                answer = self.engine.ask(question)
                self.current_answer = answer
                self.after(0, lambda: self._add_chat_bubble(
                    answer, is_user=False, show_feedback=True
                ))
            except Exception as e:
                self.after(0, lambda: self._add_chat_bubble(f"Hata: {e}"))
                self._update_status(f"Hata: {e}")
            finally:
                self.after(0, lambda: self.btn_send.configure(state="normal"))
        threading.Thread(target=work, daemon=True).start()

    def _run_debate(self, topic: str):
        p1 = self.persona1_var.get()
        p2 = self.persona2_var.get()

        if not p1 or not p2:
            self._update_status("Lütfen 2 kişilik seçin!")
            self.btn_send.configure(state="normal")
            return

        if p1 == p2:
            self._update_status("Farklı 2 kişilik seçin!")
            self.btn_send.configure(state="normal")
            return

        def on_message(persona, msg):
            self.after(0, lambda p=persona, m=msg: self._add_chat_bubble(m, persona=p))
            self._update_status(f"{persona} konuşuyor...")

        def work():
            try:
                self._update_status(f"Tartışma: {p1} vs {p2}")
                debate(topic, p1, p2, rounds=2, on_message=on_message)
                self._update_status("Tartışma tamamlandı!")
            except Exception as e:
                self.after(0, lambda: self._add_chat_bubble(f"Hata: {e}"))
                self._update_status(f"Hata: {e}")
            finally:
                self.after(0, lambda: self.btn_send.configure(state="normal"))
        threading.Thread(target=work, daemon=True).start()


def main():
    app = MiniAgentApp()
    app.mainloop()


if __name__ == "__main__":
    main()
