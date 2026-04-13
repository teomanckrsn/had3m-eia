"""Mini AI Agent - Yerel RAG Asistan (CustomTkinter GUI)"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, colorchooser

import customtkinter as ctk

from rag_engine import RAGEngine
from debate import debate, get_personality_names, get_persona_color, persona_manager


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PersonaDialog(ctk.CTkToplevel):
    """Yeni kişilik oluşturma penceresi."""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Yeni Kişilik Oluştur")
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save
        self.selected_color = "#2b2b2b"

        self.grid_columnconfigure(1, weight=1)

        row = 0
        ctk.CTkLabel(self, text="İsim:").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="ör: Pazarlama Müdürü")
        self.name_entry.grid(row=row, column=1, padx=10, pady=8, sticky="ew")

        row += 1
        ctk.CTkLabel(self, text="Rol:").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.role_entry = ctk.CTkEntry(self, placeholder_text="ör: Dijital pazarlama uzmanı")
        self.role_entry.grid(row=row, column=1, padx=10, pady=8, sticky="ew")

        row += 1
        ctk.CTkLabel(self, text="Tanım:").grid(row=row, column=0, padx=10, pady=8, sticky="nw")
        self.desc_text = ctk.CTkTextbox(self, height=120)
        self.desc_text.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
        self.desc_text.insert("1.0", "Bu kişiliğin uzmanlık alanını ve bakış açısını tanımlayın...")

        row += 1
        ctk.CTkLabel(self, text="Renk:").grid(row=row, column=0, padx=10, pady=8, sticky="w")
        self.color_btn = ctk.CTkButton(
            self, text="Renk Seç", fg_color=self.selected_color,
            command=self._pick_color, width=100,
        )
        self.color_btn.grid(row=row, column=1, padx=10, pady=8, sticky="w")

        row += 1
        self.btn_save = ctk.CTkButton(self, text="Kaydet", command=self._save)
        self.btn_save.grid(row=row, column=0, columnspan=2, padx=10, pady=15)

    def _pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.selected_color)
        if color[1]:
            self.selected_color = color[1]
            self.color_btn.configure(fg_color=self.selected_color)

    def _save(self):
        name = self.name_entry.get().strip()
        role = self.role_entry.get().strip()
        desc = self.desc_text.get("1.0", "end").strip()
        if not name or not role:
            return

        persona_manager.add(name, role, desc, self.selected_color)
        if self.on_save:
            self.on_save()
        self.destroy()


class MiniAgentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mini AI Agent - Yerel Asistan")
        self.geometry("1000x800")
        self.minsize(800, 600)

        self.engine = None
        self.current_answer = ""
        self.current_question = ""

        self._build_ui()
        self._init_engine()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === Üst bar: dosya + kişilik yönetimi ===
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_frame.grid_columnconfigure(3, weight=1)

        self.btn_add = ctk.CTkButton(
            top_frame, text="📂 Dosya Ekle", width=110, command=self._add_files
        )
        self.btn_add.grid(row=0, column=0, padx=5, pady=5)

        self.btn_clear = ctk.CTkButton(
            top_frame, text="🗑 Temizle", width=80, fg_color="gray",
            command=self._clear_files
        )
        self.btn_clear.grid(row=0, column=1, padx=5, pady=5)

        self.btn_new_persona = ctk.CTkButton(
            top_frame, text="👤 Kişilik Ekle", width=120, fg_color="#8e44ad",
            command=self._open_persona_dialog
        )
        self.btn_new_persona.grid(row=0, column=2, padx=5, pady=5)

        self.file_label = ctk.CTkLabel(top_frame, text="Henüz dosya yüklenmedi", anchor="w")
        self.file_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # === Mod seçimi + kişilik seçiciler ===
        mode_frame = ctk.CTkFrame(self)
        mode_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        mode_frame.grid_columnconfigure(7, weight=1)

        self.mode_var = tk.StringVar(value="chat")

        self.radio_chat = ctk.CTkRadioButton(
            mode_frame, text="💬 Sohbet", variable=self.mode_var, value="chat",
            command=self._on_mode_change
        )
        self.radio_chat.grid(row=0, column=0, padx=10, pady=5)

        self.radio_debate = ctk.CTkRadioButton(
            mode_frame, text="⚔️ Tartışma", variable=self.mode_var, value="debate",
            command=self._on_mode_change
        )
        self.radio_debate.grid(row=0, column=1, padx=10, pady=5)

        # Kişilik seçiciler
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

        self.btn_del_persona = ctk.CTkButton(
            mode_frame, text="🗑", width=35, fg_color="#c0392b",
            command=self._delete_persona
        )
        self.btn_del_persona.grid(row=0, column=6, padx=5, pady=5)

        self._on_mode_change()

        # === Sohbet alanı ===
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="Sohbet")
        self.chat_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_widgets = []

        # === Giriş alanı ===
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            bottom_frame, placeholder_text="Sorunuzu yazın...", height=40
        )
        self.input_entry.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="ew")
        self.input_entry.bind("<Return>", self._on_enter)

        self.btn_send = ctk.CTkButton(
            bottom_frame, text="Gönder", width=80, command=self._send_question
        )
        self.btn_send.grid(row=0, column=1, padx=5, pady=5)

        # === Durum çubuğu ===
        self.status_label = ctk.CTkLabel(self, text="Başlatılıyor...", anchor="w")
        self.status_label.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 5))

    def _refresh_persona_combos(self):
        names = get_personality_names()
        self.combo_p1.configure(values=names)
        self.combo_p2.configure(values=names)
        if names and not self.persona1_var.get():
            self.persona1_var.set(names[0])
        if len(names) > 1 and not self.persona2_var.get():
            self.persona2_var.set(names[1])

    def _open_persona_dialog(self):
        PersonaDialog(self, on_save=self._refresh_persona_combos)

    def _delete_persona(self):
        # Seçili olan kişilik 1'i sil
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
        self.btn_del_persona.configure(state=state)
        if is_debate:
            self.input_entry.configure(placeholder_text="Tartışma konusunu yazın (ör: Yeni ürün lansmanı stratejisi)...")
        else:
            self.input_entry.configure(placeholder_text="Sorunuzu yazın...")

    def _init_engine(self):
        def init():
            try:
                self.engine = RAGEngine(on_status=self._update_status)
                self._update_status("Hazır! Dosya yükleyin ve soru sorun, veya tartışma başlatın.")
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
