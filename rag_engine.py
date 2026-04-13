"""RAG Engine - Yerel dosyaları indeksler ve sorgular."""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama

# PDF ve DOCX okuma
from PyPDF2 import PdfReader
from docx import Document


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")

from model_config import get_chat_model

MODEL_NAME = get_chat_model()
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class FeedbackStore:
    """Kullanıcı geri bildirimlerini saklar ve öğrenir."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.feedback_file = FEEDBACK_FILE
        self.feedback = self._load()

    def _load(self) -> list:
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.feedback_file, "w", encoding="utf-8") as f:
            json.dump(self.feedback, f, ensure_ascii=False, indent=2)

    def add(self, question: str, answer: str, liked: bool):
        self.feedback.append({
            "question": question,
            "answer": answer,
            "liked": liked,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def get_good_examples(self, limit: int = 5) -> list:
        """Beğenilen cevaplardan en son N tanesini döndür."""
        good = [f for f in self.feedback if f["liked"]]
        return good[-limit:]

    def get_bad_examples(self, limit: int = 3) -> list:
        """Beğenilmeyen cevaplardan en son N tanesini döndür."""
        bad = [f for f in self.feedback if not f["liked"]]
        return bad[-limit:]


class RAGEngine:
    def __init__(self, on_status=None):
        """
        on_status: callback(str) - durum mesajları için
        """
        self.on_status = on_status or (lambda msg: None)
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(CHROMA_DIR, exist_ok=True)

        self.on_status("Embedding modeli yükleniyor...")
        self.embed_model = SentenceTransformer(EMBED_MODEL_NAME)

        self.on_status("Veritabanı başlatılıyor...")
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )

        self.feedback = FeedbackStore()
        self.on_status("Hazır!")

    def _extract_text(self, file_path: str) -> str:
        """Dosyadan metin çıkar."""
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        elif ext in (".txt", ".md", ".csv", ".json", ".py", ".js", ".html"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            raise ValueError(f"Desteklenmeyen dosya türü: {ext}")

    def _chunk_text(self, text: str) -> list[str]:
        """Metni parçalara ayır."""
        chunks = []
        words = text.split()
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = " ".join(words[i : i + CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def _file_hash(self, file_path: str) -> str:
        h = hashlib.md5()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(8192), b""):
                h.update(block)
        return h.hexdigest()

    def add_document(self, file_path: str) -> int:
        """Dosyayı indeksle. Eklenen chunk sayısını döndürür."""
        file_path = os.path.abspath(file_path)
        file_hash = self._file_hash(file_path)
        file_name = os.path.basename(file_path)

        # Aynı dosya zaten varsa atla
        existing = self.collection.get(where={"file_hash": file_hash})
        if existing and existing["ids"]:
            self.on_status(f"'{file_name}' zaten indekslenmiş.")
            return 0

        self.on_status(f"'{file_name}' okunuyor...")
        text = self._extract_text(file_path)

        self.on_status(f"'{file_name}' parçalanıyor...")
        chunks = self._chunk_text(text)
        if not chunks:
            self.on_status(f"'{file_name}' boş veya okunamadı.")
            return 0

        self.on_status(f"'{file_name}' indeksleniyor ({len(chunks)} parça)...")
        embeddings = self.embed_model.encode(chunks).tolist()
        ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"file_name": file_name, "file_path": file_path, "file_hash": file_hash, "chunk_index": i}
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

        self.on_status(f"'{file_name}' eklendi ({len(chunks)} parça).")
        return len(chunks)

    def get_indexed_files(self) -> list[str]:
        """İndekslenmiş dosya isimlerini döndür."""
        all_meta = self.collection.get()
        if not all_meta or not all_meta["metadatas"]:
            return []
        names = set()
        for m in all_meta["metadatas"]:
            names.add(m.get("file_name", "?"))
        return sorted(names)

    def remove_document(self, file_name: str):
        """Dosyayı indeksten kaldır."""
        all_data = self.collection.get()
        ids_to_remove = []
        for i, meta in enumerate(all_data["metadatas"]):
            if meta.get("file_name") == file_name:
                ids_to_remove.append(all_data["ids"][i])
        if ids_to_remove:
            self.collection.delete(ids=ids_to_remove)
            self.on_status(f"'{file_name}' indeksten kaldırıldı.")

    def query(self, question: str, n_results: int = 3) -> list[dict]:
        """Soruya en yakın parçaları bul."""
        if self.collection.count() == 0:
            return []

        q_embedding = self.embed_model.encode([question]).tolist()
        results = self.collection.query(
            query_embeddings=q_embedding,
            n_results=min(n_results, self.collection.count()),
        )

        docs = []
        for i in range(len(results["ids"][0])):
            docs.append({
                "text": results["documents"][0][i],
                "file_name": results["metadatas"][0][i].get("file_name", "?"),
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
        return docs

    def _build_feedback_prompt(self) -> str:
        """Geri bildirimlerden öğrenme promptu oluştur."""
        good = self.feedback.get_good_examples()
        bad = self.feedback.get_bad_examples()
        if not good and not bad:
            return ""

        parts = ["\n--- ÖĞRENİLMİŞ TERCİHLER ---"]
        if good:
            parts.append("Kullanıcının beğendiği cevap tarzları:")
            for ex in good:
                parts.append(f"  Soru: {ex['question'][:100]}")
                parts.append(f"  Beğenilen cevap: {ex['answer'][:200]}")
                parts.append("")
        if bad:
            parts.append("Kullanıcının beğenmediği cevap tarzları (BUNLARDAN KAÇIN):")
            for ex in bad:
                parts.append(f"  Soru: {ex['question'][:100]}")
                parts.append(f"  Beğenilmeyen cevap: {ex['answer'][:200]}")
                parts.append("")

        parts.append("Yukarıdaki örneklerden öğrenerek cevap ver. Beğenilen tarza yakın, beğenilmeyen tarzdan uzak dur.")
        return "\n".join(parts)

    def ask(self, question: str) -> str:
        """Soruyu cevapla (RAG + geri bildirim öğrenme)."""
        # Benzer dokümanları bul
        context_docs = self.query(question)

        # Sistem promptu
        system = (
            "Sen yardımcı bir Türkçe asistansın. "
            "Kullanıcının yüklediği belgelerden bilgi alarak sorularını yanıtlıyorsun. "
            "Her zaman Türkçe cevap ver. Bilmiyorsan bilmediğini söyle."
        )

        # Geri bildirim öğrenme
        feedback_prompt = self._build_feedback_prompt()
        if feedback_prompt:
            system += feedback_prompt

        # Bağlam
        if context_docs:
            context_text = "\n\n".join(
                f"[{d['file_name']}]: {d['text']}" for d in context_docs
            )
            user_msg = (
                f"Aşağıdaki belgelerden yararlanarak soruyu yanıtla:\n\n"
                f"--- BELGELER ---\n{context_text}\n\n"
                f"--- SORU ---\n{question}"
            )
        else:
            user_msg = question

        self.on_status("Düşünüyor...")
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
        )

        answer = response["message"]["content"]
        self.on_status("Hazır!")
        return answer
