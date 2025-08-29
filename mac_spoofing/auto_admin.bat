@echo off
REM MAC Adresi Değiştirici - Otomatik Yönetici Olarak Çalıştırma Betiği

REM Yönetici haklarını kontrol et
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM Yönetici hakları yoksa, yönetici olarak yeniden başlat
if '%errorlevel%' NEQ '0' (
    echo Yönetici hakları alınıyor...
    goto UACPrompt
) else (
    goto GotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:GotAdmin
    if exist "%temp%\getadmin.vbs" (
        del "%temp%\getadmin.vbs"
    )
    pushd "%CD%"
    CD /D "%~dp0"

REM Ana uygulamayı çalıştır
echo MAC Adresi Değiştirici başlatılıyor...
python main.py

REM Hata durumunda bekle
if %errorlevel% NEQ 0 (
    echo.
    echo Bir hata oluştu. Çıkmak için bir tuşa basın...
    pause > nul
)