@echo off
setlocal enabledelayedexpansion

echo [🚀] EnfiproV2 Windows Servis Kurulumu Basliyor...

REM === NSSM indirilecek geçici klasör ===
set "NSSM_DIR=%TEMP%\nssm"
set "NSSM_EXE=%NSSM_DIR%\nssm.exe"

REM === Servis ayarları ===
set "SERVICE_NAME=enfipro_service"
set "SERVICE_DESC=Enfipro Django Otomatik Servisi"
set "PROJECT_DIR=%USERPROFILE%\enfiproV2\enfiproV2"
set "PYTHON_PATH=%USERPROFILE%\enfiproV2\venv\Scripts\python.exe"
set "LOG_DIR=%USERPROFILE%\enfiproV2\logs"
set "LOG_OUT=%LOG_DIR%\stdout.log"
set "LOG_ERR=%LOG_DIR%\stderr.log"

REM === Log klasörünü oluştur ===
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

REM === NSSM yoksa indir ===
if not exist "%NSSM_EXE%" (
    echo [⬇️] NSSM indiriliyor...
    powershell -Command "Invoke-WebRequest https://nssm.cc/release/nssm-2.24.zip -OutFile '%TEMP%\nssm.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\nssm.zip' -DestinationPath '%NSSM_DIR%' -Force"
    if exist "%NSSM_DIR%\nssm-2.24\win64\nssm.exe" (
        move /Y "%NSSM_DIR%\nssm-2.24\win64\nssm.exe" "%NSSM_EXE%" >nul
    ) else (
        echo [❌] NSSM indirilemedi veya bulunamadi!
        pause
        exit /b
    )
)

REM === Venv ve manage.py kontrolü ===
if not exist "%PYTHON_PATH%" (
    echo [❌] Python virtualenv bulunamadi: %PYTHON_PATH%
    pause
    exit /b
)

if not exist "%PROJECT_DIR%\manage.py" (
    echo [❌] manage.py bulunamadi: %PROJECT_DIR%\manage.py
    pause
    exit /b
)

REM === Mevcut servis varsa sil ===
"%NSSM_EXE%" stop %SERVICE_NAME% >nul 2>&1
"%NSSM_EXE%" remove %SERVICE_NAME% confirm >nul 2>&1

REM === Servisi kur ===
echo [⚙️] Servis kuruluyor...
"%NSSM_EXE%" install %SERVICE_NAME% "%PYTHON_PATH%" manage.py runserver 0.0.0.0:8000
"%NSSM_EXE%" set %SERVICE_NAME% AppDirectory "%PROJECT_DIR%"
"%NSSM_EXE%" set %SERVICE_NAME% DisplayName "Enfipro Django Servisi"
"%NSSM_EXE%" set %SERVICE_NAME% Description "%SERVICE_DESC%"
"%NSSM_EXE%" set %SERVICE_NAME% Start SERVICE_AUTO_START
"%NSSM_EXE%" set %SERVICE_NAME% AppStdout "%LOG_OUT%"
"%NSSM_EXE%" set %SERVICE_NAME% AppStderr "%LOG_ERR%"
"%NSSM_EXE%" set %SERVICE_NAME% AppStopMethodSkip 6
"%NSSM_EXE%" set %SERVICE_NAME% AppRestartDelay 2000
"%NSSM_EXE%" set %SERVICE_NAME% AppExit Default Restart

REM === Servisi başlat ===
"%NSSM_EXE%" start %SERVICE_NAME%

echo.
echo [✅] Servis kuruldu ve başlatıldı!
echo [🔄] Açılışta otomatik çalışacaktır.
echo [📄] Loglar:
echo      STDOUT: %LOG_OUT%
echo      STDERR: %LOG_ERR%
pause
exit /b
