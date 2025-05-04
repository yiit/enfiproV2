@echo off
setlocal enabledelayedexpansion

REM 🚀 EnfiproV2 Windows Kurulumu Başlıyor...
echo.
pause

REM 1. Gerekli Uygulama Kontrolleri
where git >nul 2>nul || (
    echo [❌] Git yüklü değil. https://git-scm.com adresinden kurun.
    pause
    exit /b
)

where python >nul 2>nul || (
    echo [❌] Python yüklü değil. https://python.org adresinden indirip PATH'e ekleyin.
    pause
    exit /b
)

REM 2. Proje Klasörünü Klonla
cd /d %USERPROFILE%
if exist enfiproV2 (
    echo [⚠️] enfiproV2 klasoru zaten var, silmek istemiyorsan devam edebilirsin.
) else (
    echo [📥] GitHub reposu klonlaniyor...
    git clone https://github.com/yiit/enfiproV2.git || (
        echo [❌] GitHub repo klonlanamadi! Baglanti veya yetki sorununu kontrol edin.
        pause
        exit /b
    )
)
cd enfiproV2 || (
    echo [❌] enfiproV2 klasorune girilemedi!
    pause
    exit /b
)

REM 3. Sanal Ortam (venv) Kurulumu
if not exist venv (
    echo [🛠] Sanal ortam olusturuluyor...
    python -m venv venv
)
call venv\Scripts\activate.bat || (
    echo [❌] venv aktif edilemedi!
    pause
    exit /b
)

REM 4. pip Güncelleme ve Python Paketleri
echo [📦] pip güncelleniyor...
python -m pip install --upgrade pip

if exist requirements.txt (
    echo [📦] Python gereksinimleri yukleniyor...
    pip install -r %cd%\requirements.txt || (
        echo [❌] requirements.txt yüklenemedi!
        pause
        exit /b
    )
) else (
    echo [❌] requirements.txt bulunamadi!
    pause
    exit /b
)

REM 5. Node.js Paket Kurulumu
where npm >nul 2>nul || (
    echo [❌] Node.js veya npm yüklü değil. https://nodejs.org adresinden kurun.
    pause
    exit /b
)

if exist package.json (
    echo [📦] Node paketleri yukleniyor...
    npm install
) else (
    echo [⚠️] package.json yok! Elle gerekli paketler kuruluyor...
    npm install express serialport @serialport/parser-readline cors
)

REM 6. PostgreSQL Kullanıcı ve Veritabanı Bilgilendirmesi
echo.
echo [📝] PostgreSQL veritabanını manuel oluşturmalısınız:
echo      Kullanıcı: django_user
echo      Veritabanı: django_db
echo      Şifre: 1
pause

REM 7. Django Migration İşlemleri
echo [🔧] Django migration islemleri basliyor...
python manage.py makemigrations
python manage.py migrate

REM 8. (İsteğe Bağlı) Superuser Oluştur
REM echo [👤] Admin kullanıcı oluşturuluyor...
REM python manage.py createsuperuser --username admin --email admin@example.com

REM 9. Django ve Node.js Sunucularını Başlat
echo [🚀] Sunucular başlatılıyor...
start cmd /k "cd /d %cd% && call venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

if exist serial.js (
    start cmd /k "cd /d %cd% && node serial.js"
) else (
    echo [⚠️] serial.js bulunamadi. Node.js backend baslatilamadi.
)

REM 10. TAMAMLANDI
echo.
echo [✅] Kurulum ve başlatma işlemi tamamlandı!
echo [🌐] Tarayıcıdan http://localhost:8000 adresine gidebilirsiniz.
pause
