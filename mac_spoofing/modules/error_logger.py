#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hata Günlükçüsü Modülü

Bu modül, uygulama çalışırken oluşan hataları kaydetmek için kullanılır.
Hataları tarih ve saat bilgisiyle birlikte logs klasörüne kaydeder.
"""

import os
import datetime
import traceback


class ErrorLogger:
    """Hata günlükleme sınıfı"""
    
    def __init__(self, log_dir):
        """Hata günlükçüsünü başlat
        
        Args:
            log_dir (str): Günlük dosyalarının kaydedileceği dizin
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "error_log.txt")
    
    def log_error(self, error_message, include_traceback=True):
        """Hata mesajını günlüğe kaydet
        
        Args:
            error_message (str): Kaydedilecek hata mesajı
            include_traceback (bool): Hata izini ekleyip eklememe
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Hata izini ekle
            if include_traceback:
                error_message = f"{error_message}\n{traceback.format_exc()}"
            
            # Günlük dosyasına yaz
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {error_message}\n\n")
                
        except Exception as e:
            # Günlükleme sırasında hata oluşursa standart çıktıya yaz
            print(f"Hata günlüklenirken sorun oluştu: {str(e)}")
            print(f"Orijinal hata: {error_message}")