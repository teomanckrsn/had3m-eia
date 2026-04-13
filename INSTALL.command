#!/bin/bash
# HAD3M-EIA - macOS Otomatik Kurulum
# Bu dosyaya cift tiklayin, gerisi otomatik.

clear
echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║         HAD3M-EIA KURULUM                ║"
echo "  ║   Yerel AI Asistan - Otomatik Kurulum    ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""
echo "  Bu pencereyi KAPATMAYIN. Kurulum otomatik ilerliyor..."
echo ""

# Kurulum klasorune git
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================
# ADIM 1: Python kontrolu
# ============================================
echo "[1/5] Python kontrol ediliyor..."
if ! command -v python3 &>/dev/null; then
    echo "  ❌ Python bulunamadi!"
    echo "  Xcode Command Line Tools kuruluyor..."
    xcode-select --install 2>/dev/null
    echo "  Kurulum tamamlaninca bu scripti tekrar calistirin."
    read -p "  Devam etmek icin Enter'a basin..."
    exit 1
fi
echo "  ✅ Python mevcut: $(python3 --version)"

# ============================================
# ADIM 2: Ollama kontrolu ve kurulum
# ============================================
echo "[2/5] Ollama kontrol ediliyor..."
if ! command -v ollama &>/dev/null; then
    # Uygulama olarak kurulu mu?
    if [ -f "/Applications/Ollama.app/Contents/Resources/ollama" ]; then
        mkdir -p ~/bin
        ln -sf /Applications/Ollama.app/Contents/Resources/ollama ~/bin/ollama
        export PATH="$HOME/bin:$PATH"
    else
        echo "  Ollama indiriliyor ve kuruluyor..."
        curl -fsSL https://ollama.com/install.sh | sh
        if [ -f "/Applications/Ollama.app/Contents/Resources/ollama" ]; then
            mkdir -p ~/bin
            ln -sf /Applications/Ollama.app/Contents/Resources/ollama ~/bin/ollama
            export PATH="$HOME/bin:$PATH"
        fi
    fi
fi
echo "  ✅ Ollama mevcut."

# Ollama servisini baslat
echo "  Ollama servisi baslatiliyor..."
open -a Ollama 2>/dev/null || true
sleep 5
# Alternatif: Resources'dan serve
if ! curl -s http://localhost:11434/ &>/dev/null; then
    if [ -f "/Applications/Ollama.app/Contents/Resources/ollama" ]; then
        /Applications/Ollama.app/Contents/Resources/ollama serve &>/dev/null &
        sleep 5
    fi
fi

# ============================================
# ADIM 3: Model indirme
# ============================================
echo "[3/5] AI modeli kontrol ediliyor (aya-expanse:8b)..."
if ! ollama list 2>/dev/null | grep -q "aya-expanse"; then
    echo "  Model indiriliyor (~5 GB, bu biraz surecek)..."
    ollama pull aya-expanse:8b
    if [ $? -ne 0 ]; then
        echo "  ❌ Model indirilemedi. Internet baglantinizi kontrol edin."
        read -p "  Devam etmek icin Enter'a basin..."
        exit 1
    fi
fi
echo "  ✅ AI modeli hazir."

# ============================================
# ADIM 4: Python ortami kurulumu
# ============================================
echo "[4/5] Python ortami kuruluyor..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
# Playwright tarayici kurulumu
playwright install chromium 2>/dev/null
echo "  ✅ Python ortami hazir."

# ============================================
# ADIM 5: Masaustu kisayolu olustur
# ============================================
echo "[5/5] Masaustu kisayolu olusturuluyor..."
SHORTCUT="$HOME/Desktop/HAD3M-EIA.command"
cat > "$SHORTCUT" << 'SHORTCUT_EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Projenin gercek konumunu bul
SHORTCUT_EOF

# Gercek yolu ekle
echo "cd \"$SCRIPT_DIR\"" >> "$SHORTCUT"
cat >> "$SHORTCUT" << 'SHORTCUT_EOF'
source venv/bin/activate
# Ollama'yi baslat
open -a Ollama 2>/dev/null || true
if [ -f "/Applications/Ollama.app/Contents/Resources/ollama" ]; then
    /Applications/Ollama.app/Contents/Resources/ollama serve &>/dev/null &
fi
sleep 3
python3 app.py
SHORTCUT_EOF

chmod +x "$SHORTCUT"
echo "  ✅ Masaustunde 'HAD3M-EIA.command' kisayolu olusturuldu."

# ============================================
# TAMAMLANDI
# ============================================
echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║         KURULUM TAMAMLANDI! ✅           ║"
echo "  ║                                          ║"
echo "  ║  Masaustundeki HAD3M-EIA.command          ║"
echo "  ║  dosyasina cift tiklayarak                ║"
echo "  ║  uygulamayi acabilirsin.                  ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""
read -p "  Simdi uygulamayi acmak ister misin? (e/h): " choice
if [ "$choice" = "e" ] || [ "$choice" = "E" ]; then
    source venv/bin/activate
    python3 app.py
fi
