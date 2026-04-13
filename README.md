# HAD3M-EIA

> A fully offline, local AI assistant that learns from your feedback and automates your browser tasks.
> Tamamen yerel, internetsiz, geri bildirimle ogrenen ve tarayici gorevlerini otomatiklestiren bir yapay zeka asistan.

---

## English

### What is HAD3M-EIA?

HAD3M-EIA is a desktop AI assistant that runs entirely on your computer. Unlike ChatGPT or other cloud-based AI tools, **nothing you type or upload ever leaves your machine**. It uses a locally running language model (aya-expanse by Cohere) through Ollama.

### Features

- **RAG Chat** — Upload documents (PDF, Word, TXT, etc.), ask questions, get answers based on your files
- **Feedback Learning** — Rate responses with thumbs up/down, the AI adapts to your preferences over time
- **Custom Personas** — Create AI personalities (CEO, Marketing Consultant, Finance Director, etc.)
- **Debate Mode** — Make two personas argue a topic, get strategy recommendations from a moderator
- **Controlled Browser Agent** — Automate web tasks (e.g., generate shipping labels) with strict security controls
- **File Manager** — Move files, create new files/folders (delete/trash operations are blocked by design)
- **100% Offline** — Everything runs locally after initial setup. No data ever leaves your computer
- **Turkish Optimized** — Powered by Cohere's aya-expanse model, trained for 23 languages including Turkish

### Quick Install (One-Click)

**Download the project, then double-click the installer:**

| Platform | File | What it does |
|----------|------|-------------|
| **Windows** | `INSTALL.bat` | Installs everything automatically, creates desktop shortcut |
| **macOS** | `INSTALL.command` | Installs everything automatically, creates desktop shortcut |

The installer handles: Ollama setup, AI model download (~5GB), Python environment, all dependencies, and a desktop shortcut. First run takes ~10 minutes (mostly model download), after that it's instant.

### Manual Install

```bash
git clone https://github.com/teomanckrsn/mini-ai-agent.git
cd mini-ai-agent

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download AI model
ollama pull aya-expanse:8b

# Setup Python
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Run
python3 app.py
```

### How to Use

#### 1. Chat Mode — Talk to Your Documents
- Click **"Dosya Ekle"** to upload PDF, Word, TXT, or other files
- Type a question and press Enter
- The AI answers based on your documents
- Rate every answer with 👍/👎 — the AI learns!

#### 2. Debate Mode — AI Personas Argue
- Switch to **"Tartisma"** mode
- Pick two personas (e.g., CEO vs Marketing Consultant)
- Type a topic: "Should we invest in social media ads?"
- Watch them debate, get a moderator summary with strategy recommendations

#### 3. Custom Personas
- Click **"Kisilik Ekle"** to create a new personality
- Define name, role, expertise, thinking style, and color
- Saved permanently, available in debate mode

#### 4. Browser Agent — Automate Web Tasks
- Click **"Tarayici"** to open the browser panel
- Add allowed domains (e.g., shipstation.com, yoursite.com)
- The agent can ONLY visit sites you explicitly allow
- Navigate, click, fill forms — critical actions (payment, delete, submit) require your approval
- Password fields are blocked — you must enter passwords yourself
- Runs in a separate Chrome profile, never touches your personal browser

#### 5. File Manager
- Click **"Dosya Yonet"** to open file management
- Move files between folders with undo support
- Create new text files and folders
- **Delete and trash operations are permanently blocked**

### Security

| Rule | Detail |
|------|--------|
| No internet after setup | Everything runs locally via Ollama |
| Domain whitelist | Browser agent can only visit explicitly allowed sites |
| Critical action approval | Payment, delete, submit actions require user confirmation |
| Password protection | Agent cannot type in password fields |
| No file deletion | File manager can only move and create, never delete |
| Trash blocked | Moving files to trash is explicitly prevented |
| Isolated browser profile | Separate Chrome profile, your personal data untouched |
| All actions logged | Browser actions and file moves are logged with timestamps |

### Technical Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Running AI without internet | Ollama runs aya-expanse:8b locally on Apple Silicon/GPU |
| Understanding uploaded documents | RAG pipeline: chunk → embed with sentence-transformers → store in ChromaDB → retrieve on query |
| Learning user preferences | Feedback system: liked/disliked responses stored in JSON, injected into system prompt as examples |
| Good Turkish language support | Cohere's aya-expanse model, specifically trained for 23 languages including Turkish |
| Interactive debates | Turn-based conversation with role-specific system prompts and moderator summary |
| Responsive UI during AI generation | Python threading for all AI calls, keeping GUI interactive |
| Safe browser automation | Domain whitelist + critical action approval + password field blocking + isolated profile |
| Preventing accidental file deletion | Trash/delete paths explicitly blocked, all moves logged with undo support |

### Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM | Ollama + aya-expanse:8b | Best local Turkish language support |
| Vector DB | ChromaDB | Lightweight, local, no server needed |
| Embeddings | sentence-transformers | Fast local embeddings, no API needed |
| Browser Automation | Playwright | Reliable, supports Chrome profiles |
| GUI | CustomTkinter | Modern dark-mode desktop UI |
| Language | Python 3.9+ | Rich AI/ML ecosystem |

### Project Structure

```
HAD3M-EIA/
├── app.py              # Main GUI application
├── rag_engine.py       # RAG engine (document indexing, querying, feedback learning)
├── debate.py           # Debate system + persona management
├── browser_agent.py    # Controlled browser automation
├── file_manager.py     # File move/create manager (no delete)
├── requirements.txt    # Python dependencies
├── INSTALL.bat             # Windows one-click installer
├── INSTALL.command          # macOS one-click installer
├── USER_GUIDE.md # Detailed Turkish user guide
└── data/               # (auto-created) All local data
    ├── chroma_db/      # Vector database
    ├── feedback.json   # User feedback history
    ├── personas.json   # Custom personas
    ├── allowed_domains.json  # Browser whitelist
    ├── browser_history.json  # Browser action logs
    ├── move_history.json     # File move logs
    └── browser_logs/   # Compressed screenshots
```

---

## Turkce

### HAD3M-EIA Nedir?

HAD3M-EIA, tamamen senin bilgisayarinda calisan bir masaustu yapay zeka uygulamasidir. ChatGPT veya diger bulut tabanli AI araclarindan farki, **yazdigin veya yukledign hicbir veri bilgisayarindan cikmaz**.

### Ozellikler

- **RAG Sohbet** — Belgelerini (PDF, Word, TXT vb.) yukle, sorular sor, dosyalarina dayanarak cevap al
- **Geri Bildirimle Ogrenme** — Cevaplari 👍/👎 ile degerlendir, AI zaman icinde sana uyum saglar
- **Ozel Kisilikler** — Kendi AI kisiliklerini olustur (CEO, Pazarlama Danismani, Finans Muduru vb.)
- **Tartisma Modu** — Iki kisiligi bir konu uzerinde tartistir, moderatorden strateji onerileri al
- **Kontrollu Tarayici Agent** — Web gorevlerini otomatiklestir (orn: kargo etiketi al) siki guvenlik kontrolleriyle
- **Dosya Yoneticisi** — Dosya tasi, yeni dosya/klasor olustur (silme ve cop kutusu islemleri engellidir)
- **%100 Cevrimdisi** — Ilk kurulumdan sonra internet gerekmez. Hicbir veri bilgisayarindan cikmaz
- **Turkce Optimize** — Cohere'in aya-expanse modeli, Turkce dahil 23 dil icin egitilmis

### Hizli Kurulum (Tek Tikla)

**Projeyi indir, sonra kurulum dosyasina cift tikla:**

| Platform | Dosya | Ne yapar |
|----------|-------|----------|
| **Windows** | `INSTALL.bat` | Her seyi otomatik kurar, masaustune kisayol olusturur |
| **macOS** | `INSTALL.command` | Her seyi otomatik kurar, masaustune kisayol olusturur |

Kurulum su islemleri halleder: Ollama kurulumu, AI model indirme (~5GB), Python ortami, tum bagimliliklar ve masaustu kisayolu. Ilk calistirmada ~10 dakika surer (cogu model indirme), sonra aninda acilir.

### Manuel Kurulum

```bash
git clone https://github.com/teomanckrsn/mini-ai-agent.git
cd mini-ai-agent

# Ollama kur
curl -fsSL https://ollama.com/install.sh | sh

# AI modelini indir
ollama pull aya-expanse:8b

# Python ortamini kur
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Calistir
python3 app.py
```

### Nasil Kullanilir

#### 1. Sohbet Modu — Belgelerinle Konus
- **"Dosya Ekle"** ile PDF, Word, TXT veya diger dosyalari yukle
- Soruyu yaz ve Enter'a bas
- AI belgelerine dayanarak cevap verir
- Her cevabi 👍/👎 ile degerlendir — AI ogrenir!

#### 2. Tartisma Modu — AI Kisiliklerini Tartistir
- **"Tartisma"** moduna gec
- Iki kisilik sec (orn: Sirket Yoneticisi vs Reklam Danismani)
- Konu yaz: "Sosyal medya reklamlarina yatirim yapmali miyiz?"
- Tartismayi izle, moderator ozetini ve strateji onerilerini al

#### 3. Ozel Kisilik Olustur
- **"Kisilik Ekle"** ile yeni kisilik olustur
- Isim, rol, uzmanlik, dusunme tarzi ve renk tanimla
- Kalici olarak kaydedilir, tartisma modunda kullanilabilir

#### 4. Tarayici Agent — Web Gorevlerini Otomatiklestir
- **"Tarayici"** butonuna tikla
- Izin verilen siteleri ekle (orn: shipstation.com, seninsiten.com)
- Agent SADECE senin izin verdign sitelere gidebilir
- Gezinme, tiklama, form doldurma — kritik aksiyonlar (odeme, silme, gonderme) icin onay ister
- Sifre alanlari engellenmistir — sifreleri kendin girmelisin
- Ayri Chrome profilinde calisir, kisisel tarayicina dokunmaz

#### 5. Dosya Yoneticisi
- **"Dosya Yonet"** butonuna tikla
- Dosyalari klasorler arasi tasi (geri alma destegi ile)
- Yeni metin dosyalari ve klasorler olustur
- **Silme ve cop kutusuna tasima kalici olarak engellidir**

### Hazir Gelen Kisilikler

| Kisilik | Rol | Nasil Dusunur |
|---------|-----|---------------|
| Kisisel Asistan | Asistan | Senin ihtiyaclarini onceliklendirir, pratik cozumler sunar |
| Sirket Yoneticisi | CEO | Stratejik dusunur, buyuk resmi gorur, uzun vadeli planlar yapar |
| Reklam Danismani | Pazarlama Uzmani | Yaratici, trend takipcisi, marka bilinirligine odaklanir |
| Finans Muduru | CFO | Butce, maliyet, karlilik ve yatirim getirisi acisindan degerlendirir |
| Musteri Temsilcisi | CX Uzmani | Her karari musterinin gozunden degerlendirir |

### Guvenlik

| Kural | Detay |
|-------|-------|
| Kurulum sonrasi internet yok | Her sey Ollama ile yerel calisir |
| Domain beyaz listesi | Tarayici agent sadece izin verilen sitelere gidebilir |
| Kritik aksiyon onayi | Odeme, silme, gonderme islemleri kullanici onayi gerektirir |
| Sifre korumasi | Agent sifre alanlarina yazamaz |
| Dosya silme yok | Dosya yoneticisi sadece tasima ve olusturma yapabilir, silme yok |
| Cop kutusu engelli | Dosyalari cop kutusuna tasima acikca engellenmistir |
| Izole tarayici profili | Ayri Chrome profili, kisisel verilerine dokunulmaz |
| Tum aksiyonlar loglaniyor | Tarayici aksiyonlari ve dosya tasimalari zaman damgasiyla kaydedilir |

### Karsilasilan Teknik Zorluklar ve Cozumleri

| Zorluk | Cozum |
|--------|-------|
| AI'yi internetsiz calistirmak | Ollama ile aya-expanse:8b modelini Apple Silicon/GPU uzerinde yerel calistirdik |
| AI'nin yuklenen belgeleri anlamasi | RAG pipeline: parcala → sentence-transformers ile vektorlestir → ChromaDB'de sakla → soruda getir |
| AI'ya kullanici tercihlerini ogretmek | Geri bildirim sistemi: begenilen/begenilmeyen cevaplar JSON'da saklanir, sistem promptuna ornek olarak eklenir |
| AI'nin iyi Turkce konusmasi | Cohere'in aya-expanse modelini sectik — Turkce dahil 23 dil icin ozel egitilmis |
| Interaktif tartismalar olusturmak | Sira tabanli konusma sistemi: kisilikler role ozgu sistem promptlariyla birbirlerine cevap verir |
| AI cevap uretirken arayuzun donmamasi | Python threading ile tum AI cagrilarini arka planda calistirdik |
| Guvenli tarayici otomasyonu | Domain beyaz listesi + kritik aksiyon onayi + sifre alani engeli + izole profil |
| Kazara dosya silmeyi onlemek | Cop kutusu/silme yollari engellendi, tum tasimalar geri alma destegi ile loglaniyor |

### Kullanilan Teknolojiler

| Bilesen | Teknoloji | Neden |
|---------|-----------|-------|
| Dil Modeli | Ollama + aya-expanse:8b | En iyi yerel Turkce dil destegi |
| Vektor Veritabani | ChromaDB | Hafif, yerel, sunucu gerektirmez |
| Embedding | sentence-transformers | Hizli yerel embedding, API gerektirmez |
| Tarayici Otomasyon | Playwright | Guvenilir, Chrome profili destegi |
| Arayuz | CustomTkinter | Modern karanlik tema masaustu arayuzu |
| Dil | Python 3.9+ | Zengin AI/ML ekosistemi |

### Veri Guvenligi

- Tum veriler `data/` klasorunde yerel olarak saklanir
- Kurulum sonrasi internet gerekmez
- Telemetri yok, takip yok, bulut yok
- `data/` klasorunu silersen tum veriler silinir
- Uygulamayi tamamen kaldirmak icin proje klasorunu sil

---

## License

MIT License — feel free to use, modify, and share.

## Contributing

Pull requests are welcome! Feel free to open issues for bugs or feature requests.

---

*Built with Ollama, ChromaDB, sentence-transformers, Playwright, and CustomTkinter.*
