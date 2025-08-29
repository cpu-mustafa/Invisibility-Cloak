# MAC Adresi Değiştirici - Yönetici Olarak Çalıştırma Betiği

# Yönetici olarak çalıştırma fonksiyonu
function Start-ProcessAsAdmin {
    param (
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        
        [Parameter(Mandatory=$false)]
        [string]$Arguments = ""
    )
    
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $FilePath
        $psi.Arguments = $Arguments
        $psi.Verb = "runas" # Yönetici olarak çalıştır
        $psi.UseShellExecute = $true
        
        Write-Host "Uygulama yönetici olarak başlatılıyor..."
        [System.Diagnostics.Process]::Start($psi) | Out-Null
        Write-Host "Uygulama başlatıldı."
        
        return $true
    }
    catch [System.ComponentModel.Win32Exception] {
        # Kullanıcı UAC iletişim kutusunu iptal ettiğinde
        if ($_.Exception.NativeErrorCode -eq 1223) {
            Write-Host "Yönetici hakları reddedildi. Uygulama sınırlı modda çalışacak."
        }
        else {
            Write-Host "Hata: $($_.Exception.Message)"
        }
        return $false
    }
    catch {
        Write-Host "Beklenmeyen hata: $($_.Exception.Message)"
        return $false
    }
}

# Betik dizinini al
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Python yürütülebilir dosyasını bul
$pythonExe = "python.exe"

# Ana uygulamayı yönetici olarak çalıştır
$mainScript = Join-Path $scriptDir "main.py"
if (Test-Path $mainScript) {
    $result = Start-ProcessAsAdmin -FilePath $pythonExe -Arguments """$mainScript"""
    
    if (-not $result) {
        Write-Host "Uygulama normal modda başlatılıyor..."
        Start-Process -FilePath $pythonExe -ArgumentList """$mainScript"""
    }
}
else {
    Write-Host "Hata: $mainScript bulunamadı."
}

# Çıkmak için bir tuşa basın
Write-Host "`nÇıkmak için bir tuşa basın..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")