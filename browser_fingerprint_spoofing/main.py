#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from modules.fingerprint_controller import FingerprintController
from modules.error_logger import ErrorLogger

def main():
    # Uygulama örneğini oluştur
    app = QApplication(sys.argv)
    app.setApplicationName("Tarayıcı Parmak İzi Gizleme Aracı")
    
    # Temel dizini belirle
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Hata günlükçüsünü başlat
    logger = ErrorLogger(base_dir)
    logger.log_info("Uygulama başlatılıyor...")
    
    try:
        # Ana pencereyi oluştur ve göster
        window = FingerprintController(base_dir)
        window.show()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec_())
    except Exception as e:
        logger.log_error("Uygulama başlatılırken hata oluştu", e)
        print(f"Hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()