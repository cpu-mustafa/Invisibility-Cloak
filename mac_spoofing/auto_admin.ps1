# MAC Adresi Değiştirici - Otomatik Yönetici Olarak Çalıştırma Betiği

# Yönetici haklarını kontrol et
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Yönetici hakları yoksa, yönetici olarak yeniden başlat
if (-not $isAdmin) {
    Write-Host "Yönetici hakları alınıyor..."
    
    # Mevcut betiğin yolunu al
    $scriptPath = $MyInvocation.MyCommand.Path
    
    # Yönetici olarak yeniden başlat
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    exit
}

# Betik dizinini al
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Ana uygulamayı çalıştır
Write-Host "MAC Adresi Değiştirici başlatılıyor..."

# Python yürütülebilir dosyasını bul
$pythonExe = "python.exe"

# Ana uygulamayı çalıştır
$mainScript = Join-Path $scriptDir "main.py"
if (Test-Path $mainScript) {
    try {
        # Uygulamayı çalıştır
        Start-Process -FilePath $pythonExe -ArgumentList """$mainScript""" -Wait -NoNewWindow
        
        # Başarılı çıkış
        Write-Host "Uygulama başarıyla tamamlandı." -ForegroundColor Green
    }
    catch {
        # Hata durumu
        Write-Host "Hata: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Çıkmak için bir tuşa basın..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}
else {
    # Ana dosya bulunamadı
    Write-Host "Hata: $mainScript bulunamadı." -ForegroundColor Red
    Write-Host "Çıkmak için bir tuşa basın..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}