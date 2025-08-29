#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from modules.error_logger import ErrorLogger

class FingerprintSettings:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.logger = ErrorLogger(base_dir)
        self.config_dir = os.path.join(base_dir, 'config')
        self.settings_path = os.path.join(self.config_dir, 'fingerprint_settings.json')
        
        # Yapılandırma dizini yoksa oluştur
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        # Varsayılan ayarları yükle veya oluştur
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """Ayarları dosyadan yükle veya varsayılan ayarları oluştur"""
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.log_error("Ayarlar yüklenirken hata oluştu", e)
                return self._create_default_settings()
        else:
            return self._create_default_settings()
            
    def _create_default_settings(self):
        """Varsayılan ayarları oluştur"""
        default_settings = {
            "profiles": {
                "default": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "platform": "Win32",
                    "vendor": "Google Inc.",
                    "languages": ["tr-TR", "tr", "en-US", "en"],
                    "do_not_track": False,
                    "hardware_concurrency": 4,
                    "device_memory": 8,
                    "screen_resolution": {
                        "width": 1920,
                        "height": 1080
                    },
                    "color_depth": 24,
                    "timezone_offset": -180,
                    "session_storage": True,
                    "local_storage": True,
                    "indexed_db": True,
                    "cookies": True,
                    "canvas_fingerprint": True,
                    "audio_fingerprint": True,
                    "webgl_fingerprint": True,
                    "fonts": ["Arial", "Courier New", "Georgia", "Times New Roman", "Verdana"]
                },
                "privacy": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                    "platform": "Win32",
                    "vendor": "",
                    "languages": ["en-US", "en"],
                    "do_not_track": True,
                    "hardware_concurrency": 2,
                    "device_memory": 4,
                    "screen_resolution": {
                        "width": 1366,
                        "height": 768
                    },
                    "color_depth": 24,
                    "timezone_offset": 0,
                    "session_storage": False,
                    "local_storage": False,
                    "indexed_db": False,
                    "cookies": False,
                    "canvas_fingerprint": False,
                    "audio_fingerprint": False,
                    "webgl_fingerprint": False,
                    "fonts": ["Arial", "Times New Roman"]
                }
            },
            "settings": {
                "active_profile": "default",
                "auto_change_interval": 0,
                "startup_profile": "default",
                "theme": "light"
            }
        }
        
        # Varsayılan ayarları kaydet
        self.save_settings(default_settings)
        return default_settings
        
    def save_settings(self, settings=None):
        """Ayarları dosyaya kaydet"""
        if settings is None:
            settings = self.settings
            
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            self.logger.log_info("Ayarlar başarıyla kaydedildi")
            return True
        except Exception as e:
            self.logger.log_error("Ayarlar kaydedilirken hata oluştu", e)
            return False
            
    def get_profile(self, profile_name=None):
        """Belirtilen profili getir, belirtilmemişse aktif profili getir"""
        if profile_name is None:
            profile_name = self.settings["settings"]["active_profile"]
            
        if profile_name in self.settings["profiles"]:
            return self.settings["profiles"][profile_name]
        else:
            self.logger.log_error(f"Profil bulunamadı: {profile_name}")
            return self.settings["profiles"]["default"]
            
    def set_active_profile(self, profile_name):
        """Aktif profili değiştir"""
        if profile_name in self.settings["profiles"]:
            self.settings["settings"]["active_profile"] = profile_name
            self.save_settings()
            self.logger.log_info(f"Aktif profil değiştirildi: {profile_name}")
            return True
        else:
            self.logger.log_error(f"Profil bulunamadı: {profile_name}")
            return False
            
    def create_profile(self, profile_name, profile_data):
        """Yeni profil oluştur"""
        if profile_name in self.settings["profiles"]:
            self.logger.log_error(f"Bu isimde bir profil zaten var: {profile_name}")
            return False
            
        self.settings["profiles"][profile_name] = profile_data
        self.save_settings()
        self.logger.log_info(f"Yeni profil oluşturuldu: {profile_name}")
        return True
        
    def update_profile(self, profile_name, profile_data):
        """Mevcut profili güncelle"""
        if profile_name not in self.settings["profiles"]:
            self.logger.log_error(f"Profil bulunamadı: {profile_name}")
            return False
            
        self.settings["profiles"][profile_name] = profile_data
        self.save_settings()
        self.logger.log_info(f"Profil güncellendi: {profile_name}")
        return True
        
    def delete_profile(self, profile_name):
        """Profili sil"""
        if profile_name not in self.settings["profiles"]:
            self.logger.log_error(f"Profil bulunamadı: {profile_name}")
            return False
            
        if profile_name == "default":
            self.logger.log_error("Varsayılan profil silinemez")
            return False
            
        # Aktif profil siliniyorsa, varsayılan profile geç
        if self.settings["settings"]["active_profile"] == profile_name:
            self.settings["settings"]["active_profile"] = "default"
            
        # Başlangıç profili siliniyorsa, varsayılan profile geç
        if self.settings["settings"]["startup_profile"] == profile_name:
            self.settings["settings"]["startup_profile"] = "default"
            
        del self.settings["profiles"][profile_name]
        self.save_settings()
        self.logger.log_info(f"Profil silindi: {profile_name}")
        return True
        
    def get_all_profiles(self):
        """Tüm profilleri getir"""
        return self.settings["profiles"]
        
    def get_setting(self, setting_name):
        """Belirli bir ayarı getir"""
        if setting_name in self.settings["settings"]:
            return self.settings["settings"][setting_name]
        else:
            self.logger.log_error(f"Ayar bulunamadı: {setting_name}")
            return None
            
    def update_setting(self, setting_name, value):
        """Belirli bir ayarı güncelle"""
        if setting_name in self.settings["settings"]:
            self.settings["settings"][setting_name] = value
            self.save_settings()
            self.logger.log_info(f"Ayar güncellendi: {setting_name} = {value}")
            return True
        else:
            self.logger.log_error(f"Ayar bulunamadı: {setting_name}")
            return False