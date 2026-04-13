# Mini AI Agent

> A fully offline, local AI assistant that learns from your feedback.
> Tamamen yerel, internetsiz, geri bildirimle ogrenen bir yapay zeka asistan.

---

## English

### What is Mini AI Agent?

Mini AI Agent is a desktop application that gives you your own personal AI assistant running entirely on your computer. Unlike ChatGPT or other cloud-based AI tools, **nothing you type or upload ever leaves your machine**. It uses a locally running language model (aya-expanse by Cohere) through Ollama.

You can upload your documents, ask questions about them, create custom AI personalities, and even make two AI personas debate a topic to generate ideas — all without an internet connection.

### Why was this project built?

**The Problem:**
- Cloud AI services (ChatGPT, Gemini, etc.) send your data to external servers
- You can't use them offline
- They don't learn from your personal preferences over time
- There's no way to create custom personas that think like your team members

**The Solution:**
Mini AI Agent solves all of these by running everything locally:
- Your documents stay on your computer
- Works without internet after initial setup
- Learns from your thumbs up/down feedback to adapt its response style
- Lets you create custom personas (CEO, Marketing Consultant, etc.) that debate topics from their unique perspectives

### How to Install

**Prerequisites:** macOS (Apple Silicon recommended) or Linux, Python 3.9+, ~8 GB disk space

```bash
# Step 1: Clone the repository
git clone https://github.com/teomanckrsn/mini-ai-agent.git
cd mini-ai-agent

# Step 2: Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
# Open the Ollama app after installation

# Step 3: Download the AI model (~5 GB, one-time download)
ollama pull aya-expanse:8b

# Step 4: Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Step 5: Launch the app
python3 app.py
```

### How to Use

#### 1. Chat Mode — Talk to Your Documents
- Click **"Dosya Ekle"** (Add File) button at the top
- Select PDF, Word, TXT, or other supported files
- Type a question in the text field at the bottom and press Enter
- The AI reads your documents and answers based on their content
- **Rate every answer** with 👍 or 👎 — the AI learns your preferences!

#### 2. Debate Mode — Make AI Personas Argue
- Switch to **"Tartisma"** (Debate) mode using the radio button
- Pick two personas from the dropdown menus (e.g., "CEO" vs "Marketing Consultant")
- Type a topic like "Should we invest in social media ads?"
- Watch the personas argue from their perspectives
- A moderator summarizes with actionable strategy recommendations

#### 3. Create Custom Personas
- Click **"Kisilik Ekle"** (Add Persona)
- Give it a name, role, detailed description of how it thinks, and a color
- It's saved permanently and available in debate mode

### Technical Challenges and Solutions

| Challenge | Solution |
|-----------|----------|
| Running AI without internet | Used Ollama to run aya-expanse:8b model locally on Apple Silicon |
| Making the AI understand uploaded documents | Built a RAG pipeline: documents are split into chunks, embedded with sentence-transformers, stored in ChromaDB, and retrieved on each query |
| Teaching the AI user preferences | Created a feedback system: liked/disliked responses are stored in JSON and injected into the system prompt as examples |
| Making the AI speak good Turkish | Chose Cohere's aya-expanse model, specifically trained for 23 languages including Turkish |
| Creating interactive debates | Built a turn-based conversation system where personas respond to each other with role-specific system prompts |
| Keeping the UI responsive during AI generation | Used Python threading to run all AI calls in the background while keeping the GUI interactive |

### Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM | Ollama + aya-expanse:8b | Best local Turkish language support |
| Vector DB | ChromaDB | Lightweight, local, no server needed |
| Embeddings | sentence-transformers | Fast local embeddings, no API needed |
| GUI | CustomTkinter | Modern dark-mode desktop UI for Python |
| Language | Python 3.9 | Rich AI/ML ecosystem |

---

## Turkce

### Mini AI Agent Nedir?

Mini AI Agent, tamamen senin bilgisayarinda calisan bir masaustu yapay zeka uygulamasidir. ChatGPT veya diger bulut tabanli AI araclarindan farki, **yazdigin veya yukledign hicbir veri bilgisayarindan cikmaz**. Ollama uzerinden yerel olarak calisan bir dil modeli (Cohere'in aya-expanse modeli) kullanir.

Belgelerini yukleyebilir, onlar hakkinda sorular sorabilir, ozel AI kisilikleri olusturabilir ve hatta iki AI kisiligini bir konu uzerinde tartistirarak yeni fikirler uretebilirsin — hepsi internet baglantisi olmadan.

### Bu Proje Neden Yapildi?

**Problem:**
- Bulut tabanli AI servisleri (ChatGPT, Gemini vb.) verilerini dis sunuculara gonderiyor
- Internet olmadan kullanilamiyor
- Zaman icinde senin kisisel tercihlerinden ogrenmiyorlar
- Ekip uyelerine benzer dusunecek ozel kisilikler olusturamiyorsun

**Cozum:**
Mini AI Agent her seyi yerel calistirarak bu sorunlarin hepsini cozer:
- Belgelerin bilgisayarinda kalir
- Ilk kurulumdan sonra internet gerekmez
- 👍/👎 geri bildirimlerinden ogrenerek cevap tarzini sana uyarlar
- Ozel kisilikler olusturup (CEO, Pazarlama Danismani vb.) konulari kendi bakis acilarindan tartistirabilirsin

### Nasil Kurulur

**Gereksinimler:** macOS (Apple Silicon onerilir) veya Linux, Python 3.9+, ~8 GB bos disk alani

```bash
# Adim 1: Repoyu klonla
git clone https://github.com/teomanckrsn/mini-ai-agent.git
cd mini-ai-agent

# Adim 2: Ollama'yi kur
curl -fsSL https://ollama.com/install.sh | sh
# Kurulumdan sonra Ollama uygulamasini ac

# Adim 3: AI modelini indir (~5 GB, bir kere indirilir)
ollama pull aya-expanse:8b

# Adim 4: Python ortamini kur
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Adim 5: Uygulamayi calistir
python3 app.py
```

### Nasil Kullanilir

#### 1. Sohbet Modu — Belgelerinle Konus
- Ust taraftaki **"Dosya Ekle"** butonuna tikla
- PDF, Word, TXT veya desteklenen diger dosyalari sec
- Alt taraftaki metin alanina soruyu yaz ve Enter'a bas
- AI belgelerini okur ve iceriklerine dayanarak cevap verir
- **Her cevabi degerlendir** 👍 veya 👎 ile — AI tercihlerini ogrenir!

#### 2. Tartisma Modu — AI Kisiliklerini Tartistir
- Radyo butonu ile **"Tartisma"** moduna gec
- Dropdown menulardan iki kisilik sec (orn: "Sirket Yoneticisi" vs "Reklam Danismani")
- Bir konu yaz, mesela "Sosyal medya reklamlarina yatirim yapmali miyiz?"
- Kisiliklerin kendi bakis acilarindan tartismasini izle
- Moderator tartismayi ozetler ve uygulanabilir strateji onerileri sunar

#### 3. Ozel Kisilik Olustur
- **"Kisilik Ekle"** butonuna tikla
- Isim, rol, nasil dusundugune dair detayli tanim ve renk ver
- Kalici olarak kaydedilir ve tartisma modunda kullanilabilir

### Hazir Gelen Kisilikler

| Kisilik | Rol | Nasil Dusunur |
|---------|-----|---------------|
| Kisisel Asistan | Asistan | Senin ihtiyaclarini onceliklendirir, pratik cozumler sunar |
| Sirket Yoneticisi | CEO | Stratejik dusunur, buyuk resmi gorur, uzun vadeli planlar yapar |
| Reklam Danismani | Pazarlama Uzmani | Yaratici, trend takipcisi, marka bilinirligine odaklanir |
| Finans Muduru | CFO | Butce, maliyet, karlilik ve yatirim getirisi acisindan degerlendirir |
| Musteri Temsilcisi | CX Uzmani | Her karari musterinin gozunden degerlendirir |

### Karsilasilan Teknik Zorluklar ve Cozumleri

| Zorluk | Cozum |
|--------|-------|
| AI'yi internetsiz calistirmak | Ollama ile aya-expanse:8b modelini Apple Silicon uzerinde yerel calistirdik |
| AI'nin yuklenen belgeleri anlamasi | RAG pipeline kurduk: belgeler parcalara ayrilir, sentence-transformers ile vektorlere donusturulur, ChromaDB'de saklanir ve her soruda ilgili parcalar getirilir |
| AI'ya kullanici tercihlerini ogretmek | Geri bildirim sistemi: begenilen/begenilmeyen cevaplar JSON'da saklanir ve sistem promptuna ornek olarak eklenir |
| AI'nin iyi Turkce konusmasi | Cohere'in aya-expanse modelini sectik — Turkce dahil 23 dil icin ozel egitilmis |
| Interaktif tartismalar olusturmak | Sira tabanli konusma sistemi kurduk: kisilikler role ozgu sistem promptlariyla birbirlerine cevap verir |
| AI cevap uretirken arayuzun donmamasi | Python threading ile tum AI cagrilarini arka planda calistirarak GUI'yi akici tuttuk |

### Kullanilan Teknolojiler

| Bilesen | Teknoloji | Neden |
|---------|-----------|-------|
| Dil Modeli | Ollama + aya-expanse:8b | En iyi yerel Turkce dil destegi |
| Vektor Veritabani | ChromaDB | Hafif, yerel, sunucu gerektirmez |
| Embedding | sentence-transformers | Hizli yerel embedding, API gerektirmez |
| Arayuz | CustomTkinter | Python icin modern karanlik tema masaustu arayuzu |
| Dil | Python 3.9 | Zengin AI/ML ekosistemi |

### Veri Guvenligi

- Tum veriler `data/` klasorunde yerel olarak saklanir
- Kurulum sonrasi internet baglantisi gerekmez
- Telemetri yok, takip yok, bulut yok
- `data/` klasorunu silersen tum veriler silinir
- Uygulamayi tamamen kaldirmak icin `mini-ai-agent/` klasorunu sil

---

## License

MIT License — feel free to use, modify, and share.

## Contributing

Pull requests are welcome! Feel free to open issues for bugs or feature requests.

---

*Built with Ollama, ChromaDB, sentence-transformers, and CustomTkinter.*
