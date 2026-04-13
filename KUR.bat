@echo off
chcp 65001 >nul 2>&1
title HAD3M-EIA Kurulum

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║         HAD3M-EIA KURULUM                ║
echo  ║   Yerel AI Asistan - Otomatik Kurulum    ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Bu pencereyi KAPATMAYIN. Kurulum otomatik ilerliyor...
echo.

:: Kurulum klasoru
set "INSTALL_DIR=%~dp0"
cd /d "%INSTALL_DIR%"

:: ============================================
:: ADIM 1: Python kontrolu
:: ============================================
echo [1/5] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ❌ Python bulunamadi!
    echo  Lutfen python.org adresinden Python 3.9+ indirin ve kurun.
    echo  Kurulumda "Add Python to PATH" secenegini isaretleyin!
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
echo  ✅ Python mevcut.

:: ============================================
:: ADIM 2: Ollama kontrolu ve kurulum
:: ============================================
echo [2/5] Ollama kontrol ediliyor...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Ollama bulunamadi, indiriliyor...
    echo  NOT: Ollama kurulumu icin ayri bir pencere acilacak.
    echo  Kurulum tamamlaninca bu pencereye donun.
    echo.
    start /wait https://ollama.com/download/OllamaSetup.exe
    echo  Ollama kurulduktan sonra devam etmek icin bir tusa basin...
    pause >nul
)
echo  ✅ Ollama mevcut.

:: ============================================
:: ADIM 3: Model indirme
:: ============================================
echo [3/5] AI modeli kontrol ediliyor (aya-expanse:8b)...
ollama list 2>nul | findstr "aya-expanse" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Model indiriliyor (~5 GB, bu biraz surecek)...
    ollama pull aya-expanse:8b
    if %errorlevel% neq 0 (
        echo  ❌ Model indirilemedi. Internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
)
echo  ✅ AI modeli hazir.

:: ============================================
:: ADIM 4: Python ortami kurulumu
:: ============================================
echo [4/5] Python ortami kuruluyor...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo  ❌ Bagimliliklar kurulamadi.
    pause
    exit /b 1
)
:: Playwright tarayici kurulumu
playwright install chromium --with-deps >nul 2>&1
echo  ✅ Python ortami hazir.

:: ============================================
:: ADIM 5: Masaustu kisayolu olustur
:: ============================================
echo [5/5] Masaustu kisayolu olusturuluyor...
set "SHORTCUT=%USERPROFILE%\Desktop\HAD3M-EIA.bat"
(
    echo @echo off
    echo cd /d "%INSTALL_DIR%"
    echo call venv\Scripts\activate.bat
    echo start "" ollama serve
    echo timeout /t 3 /nobreak ^>nul
    echo python app.py
) > "%SHORTCUT%"
echo  ✅ Masaustunde "HAD3M-EIA.bat" kisayolu olusturuldu.

:: ============================================
:: TAMAMLANDI
:: ============================================
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║         KURULUM TAMAMLANDI! ✅           ║
echo  ║                                          ║
echo  ║  Masaustundeki HAD3M-EIA.bat dosyasina   ║
echo  ║  cift tiklayarak uygulamayi acabilirsin. ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Simdi uygulamayi acmak ister misiniz? (E/H)
set /p choice="> "
if /i "%choice%"=="E" (
    call venv\Scripts\activate.bat
    start "" ollama serve
    timeout /t 3 /nobreak >nul
    python app.py
)
