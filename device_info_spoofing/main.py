#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cihaz Bilgisi Gizleme Programı

Bu program, kullanıcının cihaz bilgilerini (işletim sistemi, donanım bilgileri, MAC adresi vb.)
gizlemek için tasarlanmıştır. Windows Registry'de gerçek değişiklikler yaparak sistem bilgilerini
kalıcı olarak değiştirebilir.
"""

import sys
import os
import traceback
import ctypes
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QDir

# Uygulama sürüm bilgisi
APP_VERSION = "1.0.0"
APP_RELEASE_TYPE = "stable"

# Modülleri içe aktar
from modules.device_info_controller import DeviceInfoController
from modules.error_logger import ErrorLogger


def is_admin():
    """Uygulamanın yönetici haklarıyla çalışıp çalışmadığını kontrol eder"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def main():
    """Ana uygulama başlatma fonksiyonu"""
    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        app.setApplicationName("Cihaz Bilgisi Gizleyici")
        app.setApplicationVersion(APP_VERSION)
        
        # Temel dizini belirle
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Hata günlükçüsünü başlat
        error_logger = ErrorLogger(os.path.join(base_dir, "logs"))
        
        # Yönetici haklarını kontrol et
        admin_status = is_admin()
        if not admin_status:
            QMessageBox.warning(
                None,
                "Yönetici Hakları Gerekli",
                "Sistem bilgilerini değiştirmek için uygulamayı yönetici olarak çalıştırmanız gerekmektedir.\n\n"
                "Uygulama şu anda sınırlı modda çalışacak ve gerçek sistem değişiklikleri yapamayacaktır."
            )
        
        # Ana pencereyi oluştur ve göster
        controller = DeviceInfoController(base_dir)
        controller.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec_())
        
    except Exception as e:
        # Hata durumunda günlüğe kaydet ve kullanıcıya göster
        error_message = f"Uygulama başlatılırken hata oluştu: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        
        # Hata günlükçüsü başlatıldıysa kullan
        try:
            if 'error_logger' in locals():
                error_logger.log_error(error_message)
        except:
            # Günlükçü başlatılamadıysa doğrudan dosyaya yaz
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, "error_log.txt"), "a", encoding="utf-8") as f:
                f.write(f"{error_message}\n\n")


if __name__ == "__main__":
    main()