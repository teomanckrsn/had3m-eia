# Mini AI Agent - Kullanim Kilavuzu

## Nedir Bu?

Tamamen bilgisayarinda calisan, internete HICBIR sekilde baglanmayan, kisisel yapay zeka asistanin.
Dosyalarini yukle, sorular sor, farkli kisilikler olusturup birbirleriyle tartistir.
Tum verilerin senin bilgisayarinda kalir, hicbir yere gitmez.

---

## Nasil Calistirilir?

Terminal'i ac ve su komutlari yaz:

```bash
cd ~/Desktop/denemeleragain/mini-agent
source venv/bin/activate
python3 app.py
```

NOT: Ollama uygulamasinin acik olmasi gerekiyor. Eger kapaliysa:
```bash
open -a Ollama
```

---

## Ozellikler

### 1. Sohbet Modu (Dosyalarinla Konusma)

**Ne yapar:** Yukledgin dosyalari (PDF, Word, TXT vb.) okur, indeksler ve sorularina cevap verir.

**Nasil kullanilir:**
1. "Dosya Ekle" butonuna tikla
2. PDF, DOCX, TXT, MD, CSV, JSON, PY, JS, HTML dosyalari yukleyebilirsin
3. Soru yaz ve "Gonder" tusuna bas (veya Enter)
4. AI dosyalarindaki bilgilere dayanarak Turkce cevap verir

**Ornekler:**
- "Bu sozlesmedeki odeme kosullari nedir?"
- "Rapordaki ana bulgulari ozetle"
- "Kodda hangi fonksiyonlar kullanilmis?"

**Sinirlar:**
- Dosya ne kadar buyukse indeksleme o kadar uzun surer
- Cok buyuk dosyalarda (100+ sayfa PDF) yavaslik olabilir
- Gorsel icerikleri (resim, grafik) okuyamaz, sadece metin

### 2. Geri Bildirim ile Ogrenme

**Ne yapar:** Begendgin ve begenmedgin cevaplari kaydeder, gelecekte bu tercihlere gore cevap verir.

**Nasil kullanilir:**
- Her AI cevabinin altinda 👍 ve 👎 butonlari var
- 👍: "Bu tarzi cevaplari sevdim, boyle devam et"
- 👎: "Bu tarzi cevaplar isime yaramadi, bundan kacin"

**Sinirlar:**
- Gercek bir fine-tuning degil, prompt muhendisligi ile ogrenme
- Cok fazla geri bildirim biriktikce yavaslik olabilir (ama binlerce cevap lazim bunun icin)
- Geri bildirimleri sifirlamak icin `data/feedback.json` dosyasini sil

### 3. Tartisma Modu (Kisilikler Arasi Fikir Carpismasi)

**Ne yapar:** 2 farkli kisilik secersin, bir konu verirsin, onlar kendi bakis acilarindan tartisir.
Sonunda tarafsiz bir moderator ozet ve strateji onerisi sunar.

**Nasil kullanilir:**
1. "Tartisma" modunu sec (radyo butonu)
2. Kisilik 1 ve Kisilik 2'yi dropdown'dan sec
3. Tartisma konusunu yaz (orne: "Yeni urun lansmani stratejisi")
4. Gonder'e bas ve tartismayi izle

**Hazir Kisilikler:**
- Kisisel Asistan: Senin ihtiyaclarini onceliklendirir
- Sirket Yoneticisi (CEO): Stratejik, buyuk resimci, uzun vadeli
- Reklam Danismani: Pazarlama, marka, kampanya odakli
- Finans Muduru (CFO): Butce, maliyet, karlilik odakli
- Musteri Temsilcisi: Musteri memnuniyeti perspektifi

**Ornek Tartisma Konulari:**
- "Instagram'da reklam mi verelim yoksa Google Ads mi?"
- "Yeni bir sube acmali miyiz?"
- "Fiyat indirim kampanyasi yapmali miyiz?"
- "Calisan memnuniyetini artirmak icin ne yapmaliyiz?"
- "E-ticaret sitesi mi acalim yoksa sadece fiziksel magaza mi?"

### 4. Ozel Kisilik Olusturma

**Ne yapar:** Kendi ihtiyaclarina gore yeni kisilikler olusturabilirsin.

**Nasil kullanilir:**
1. "Kisilik Ekle" butonuna tikla
2. Isim: orne "IT Muduru"
3. Rol: orne "Bilgi teknolojileri direktoru"
4. Tanim: Bu kisiligin nasil dusunecegini, neye oncelik verecegini yaz
5. Renk: Sohbette kolayca ayirt etmek icin renk sec
6. Kaydet

**Silme:** Tartisma modunda Kisilik 1'de silmek istedigini sec, kirmizi cop kutusu butonuna tikla.

**Kisilik Tanimlama Ipuclari:**
- Ne kadar detayli yazarsan o kadar iyi sonuc alirsin
- Uzmanlik alanini belirt
- Karar verme tarzini acikla
- Oncelikleri ve bakis acisini yaz

**Ornek Kisilik Tanimi:**
```
Isim: Dijital Pazarlama Uzmani
Rol: Sosyal medya ve dijital pazarlama stratejisti
Tanim: Sosyal medya trendlerini takip eden, icerik stratejileri gelistiren,
influencer pazarlama ve topluluk yonetimi konusunda deneyimli bir uzman.
ROI odakli dusunur ama yaraticiliga da onem verir. Gen Z ve milenyallarin
tuketim aliskanliklarini iyi bilir.
```

---

## Teknik Bilgiler

### Kullanilan Teknolojiler
- **Ollama + aya-expanse:8b**: Yerel LLM (Cohere'in Turkce destekli modeli)
- **ChromaDB**: Yerel vektor veritabani (dosya indeksleme)
- **sentence-transformers**: Yerel embedding modeli
- **CustomTkinter**: Modern masaustu arayuzu

### Dosya Yapisi
```
mini-agent/
├── app.py              # Ana uygulama (GUI)
├── rag_engine.py       # RAG motoru (dosya indeksleme + sorgulama)
├── debate.py           # Tartisma sistemi + kisilik yonetimi
├── requirements.txt    # Python bagimliliklari
├── venv/               # Python sanal ortami
└── data/               # Tum veriler burada
    ├── chroma_db/      # Indekslenmis dosya verileri
    ├── feedback.json   # Geri bildirimler
    └── personas.json   # Ozel kisilikler
```

### Sinirlar ve Kisitlamalar

| Ozellik | Sinir | Neden |
|---------|-------|-------|
| Model zekasi | Orta-iyi | 8B parametre, GPT-4 seviyesinde degil ama pratik isler icin yeterli |
| Turkce | Iyi | aya-expanse Turkce icin ozel egitilmis |
| Dosya boyutu | ~50MB tek dosya | Cok buyuk dosyalar RAM sorununa yol acabilir |
| Cevap suresi | 5-30 saniye | M2 MacBook'ta, konunun karmasikligina bagli |
| Tartisma suresi | 1-3 dakika | Her kisilik sirasi ile cevap verdigi icin |
| Gorsel icerik | Desteklenmiyor | Sadece metin tabanli dosyalar okunur |
| Internet | YOK | Tamamen offline, hicbir veri disari cikmaz |
| Ogrenme | Geri bildirim bazli | Gercek fine-tuning degil, prompt bazli ogrenme |

### Veri Guvenligi
- Tum veriler `data/` klasorunde YEREL olarak saklanir
- Hicbir veri internete gonderilmez
- Ollama modeli tamamen bilgisayarinda calisir
- Silmek icin `data/` klasorunu silmen yeterli
- Uygulamayi tamamen kaldirmak icin `mini-agent/` klasorunu sil

---

## Sik Sorulan Sorular

**S: Uygulama acilmiyor?**
C: Ollama'nin calistiginden emin ol: `open -a Ollama` ve birkaç saniye bekle.

**S: "Model bulunamadi" hatasi aliyorum?**
C: Modeli indir: `ollama pull aya-expanse:8b`

**S: Cevaplar cok yavas?**
C: M2 MacBook'ta normal sartlarda 5-30 saniye. Diger uygulamalari kapatmak hizlandirir.

**S: Geri bildirimleri sifirlamak istiyorum?**
C: `data/feedback.json` dosyasini sil. Agent sifirdan ogrenir.

**S: Tum verileri silmek istiyorum?**
C: `data/` klasorunu tamamen sil. Temiz baslangic.

**S: Baska model kullanabilir miyim?**
C: Evet! `rag_engine.py` ve `debate.py` dosyalarinda MODEL_NAME'i degistir.
Ornekler: `llama3.2`, `gemma2`, `mistral`
