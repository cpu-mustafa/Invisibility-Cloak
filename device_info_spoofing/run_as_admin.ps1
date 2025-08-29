# Cihaz Bilgisi Gizleyici uygulamasini yonetici olarak calistiran PowerShell scripti

Write-Host "Cihaz Bilgisi Gizleyici uygulamasi yonetici olarak baslatiliyor..." -ForegroundColor Cyan

# Yonetici haklariyla calistirma fonksiyonu
function Start-ProcessAsAdmin {
    param (
        [string]$FilePath,
        [string]$Arguments = ""
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = $Arguments
    $psi.Verb = "runas"
    $psi.UseShellExecute = $true

    try {
        $process = [System.Diagnostics.Process]::Start($psi)
        return $true
    } catch {
        Write-Host "Hata: Yonetici haklari alinamadi veya islem iptal edildi." -ForegroundColor Red
        return $false
    }
}

# Python uygulamasinin yolunu belirle
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonApp = Join-Path -Path $scriptPath -ChildPath "main.py"

# Python yorumlayicisini bul
$pythonExe = "python"

Write-Host "Uygulama baslatiliyor..." -ForegroundColor Green
$result = Start-ProcessAsAdmin -FilePath $pythonExe -Arguments """$pythonApp"""

if ($result) {
    Write-Host "Uygulama basariyla baslatildi." -ForegroundColor Green
} else {
    Write-Host "Uygulama baslatilirken bir hata olustu." -ForegroundColor Red
}

Write-Host "Cikmak icin bir tusa basin..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")