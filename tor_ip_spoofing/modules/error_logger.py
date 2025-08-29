import os
import time
import logging
from logging.handlers import RotatingFileHandler

class ErrorLogger:
    def __init__(self, log_dir="logs", max_size=1024*1024, backup_count=5):
        """
        Hata loglama sistemi
        
        Args:
            log_dir: Log dosyalarının kaydedileceği dizin
            max_size: Maksimum log dosyası boyutu (byte cinsinden)
            backup_count: Saklanacak yedek log dosyası sayısı
        """
        self.log_dir = log_dir
        self.max_size = max_size
        self.backup_count = backup_count
        
        # Log dizinini oluştur
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Ana logger'ı yapılandır
        self.logger = logging.getLogger("TorPrivacy")
        self.logger.setLevel(logging.DEBUG)
        
        # Formatı ayarla
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Dosya handler'ı
        log_file = os.path.join(log_dir, "tor_privacy.log")
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_size, 
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Konsol handler'ı
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler'ları logger'a ekle
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Özel hata log dosyası
        self.error_log_path = os.path.join(log_dir, "error_log.txt")
    
    def log_info(self, message):
        """Bilgi mesajı logla"""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Uyarı mesajı logla"""
        self.logger.warning(message)
    
    def log_error(self, message, exception=None):
        """Hata mesajı logla"""
        if exception:
            error_details = f"{message}: {str(exception)}"
            self.logger.error(error_details, exc_info=True)
            
            # Özel hata log dosyasına da yaz
            with open(self.error_log_path, "a", encoding="utf-8") as error_file:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(f"[{timestamp}] {error_details}\n")
        else:
            self.logger.error(message)
            
            # Özel hata log dosyasına da yaz
            with open(self.error_log_path, "a", encoding="utf-8") as error_file:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(f"[{timestamp}] {message}\n")
    
    def log_critical(self, message, exception=None):
        """Kritik hata mesajı logla"""
        if exception:
            error_details = f"{message}: {str(exception)}"
            self.logger.critical(error_details, exc_info=True)
            
            # Özel hata log dosyasına da yaz
            with open(self.error_log_path, "a", encoding="utf-8") as error_file:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(f"[KRİTİK] [{timestamp}] {error_details}\n")
        else:
            self.logger.critical(message)
            
            # Özel hata log dosyasına da yaz
            with open(self.error_log_path, "a", encoding="utf-8") as error_file:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(f"[KRİTİK] [{timestamp}] {message}\n")
    
    def get_error_log_content(self, max_lines=50):
        """Hata log dosyasının içeriğini döndür"""
        if os.path.exists(self.error_log_path):
            with open(self.error_log_path, "r", encoding="utf-8") as error_file:
                lines = error_file.readlines()
                return lines[-max_lines:] if len(lines) > max_lines else lines
        return []
    
    def clear_error_log(self):
        """Hata log dosyasını temizle"""
        if os.path.exists(self.error_log_path):
            with open(self.error_log_path, "w", encoding="utf-8") as error_file:
                error_file.write("")
            return True
        return False