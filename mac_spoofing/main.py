#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAC Adresi Değiştirici

Bu program, kullanıcıların ağ adaptörlerinin MAC adreslerini görüntülemesine,
değiştirmesine ve rastgele MAC adresi oluşturmasına olanak tanır.

Yönetici hakları gerektirir.
"""

import os
import sys
import ctypes
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

# Modülleri içe aktar
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.mac_controller import MACController
from modules.error_logger import ErrorLogger

# Uygulama versiyonu
APP_VERSION = "1.0.0"

# Yönetici haklarını kontrol et
def is_admin():
    """Uygulamanın yönetici haklarıyla çalışıp çalışmadığını kontrol et"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

# Ana fonksiyon
def main():
    """Ana uygulama fonksiyonu"""
    # Temel dizini al
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Hata günlükleyicisini başlat
    error_logger = ErrorLogger(os.path.join(base_dir, "logs"))
    
    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        app.setApplicationName("MAC Adresi Değiştirici")
        app.setApplicationVersion(APP_VERSION)
        
        # Uygulama simgesini ayarla
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # Yönetici haklarını kontrol et
        if not is_admin():
            # Yönetici hakları uyarısı
            QMessageBox.warning(
                None,
                "Yönetici Hakları Gerekli",
                "MAC adresi değiştirmek için yönetici hakları gereklidir.\n\n"
                "Bazı özellikler sınırlı olabilir. Tam işlevsellik için uygulamayı yönetici olarak çalıştırın."
            )
        
        # MAC kontrolcüsünü oluştur ve göster
        controller = MACController(base_dir)
        controller.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec_())
        
    except Exception as e:
        # Hata mesajını göster
        error_message = f"Beklenmeyen bir hata oluştu: {str(e)}"
        QMessageBox.critical(None, "Hata", error_message)
        
        # Hatayı günlüğe kaydet
        error_logger.log_error(error_message, traceback.format_exc())
        
        # Uygulamadan çık
        sys.exit(1)

# Uygulamayı başlat
if __name__ == "__main__":
    main()