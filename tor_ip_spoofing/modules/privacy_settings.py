import os
import json
from enum import Enum

class PrivacyLevel(Enum):
    LOW = 1      # Temel gizlilik
    MEDIUM = 2   # Orta seviye gizlilik
    HIGH = 3     # Yüksek seviye gizlilik
    CUSTOM = 4   # Özel ayarlar

class PrivacySettings:
    def __init__(self, config_dir="config"):
        """
        Gizlilik ayarları yöneticisi
        
        Args:
            config_dir: Yapılandırma dosyalarının kaydedileceği dizin
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "privacy_settings.json")
        
        # Varsayılan ayarlar
        self.default_settings = {
            "privacy_level": PrivacyLevel.MEDIUM.name,
            "auto_switch_ip": True,
            "auto_switch_interval": 60,  # saniye
            "clear_cookies": True,
            "block_scripts": True,
            "block_webrtc": True,
            "use_bridges": False,
            "custom_settings": {
                "entry_nodes": [],
                "exit_nodes": [],
                "excluded_nodes": [],
                "strict_nodes": False,
                "use_pluggable_transports": False,
                "transport_type": "obfs4"
            }
        }
        
        # Gizlilik seviyelerine göre ayarlar
        self.level_settings = {
            PrivacyLevel.LOW.name: {
                "auto_switch_ip": False,
                "auto_switch_interval": 300,
                "clear_cookies": False,
                "block_scripts": False,
                "block_webrtc": True,
                "use_bridges": False
            },
            PrivacyLevel.MEDIUM.name: {
                "auto_switch_ip": True,
                "auto_switch_interval": 60,
                "clear_cookies": True,
                "block_scripts": True,
                "block_webrtc": True,
                "use_bridges": False
            },
            PrivacyLevel.HIGH.name: {
                "auto_switch_ip": True,
                "auto_switch_interval": 30,
                "clear_cookies": True,
                "block_scripts": True,
                "block_webrtc": True,
                "use_bridges": True
            }
        }
        
        # Yapılandırma dizinini oluştur
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Ayarları yükle veya varsayılanları oluştur
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Ayarları yapılandırma dosyasından yükle"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ayarlar yüklenirken hata oluştu: {str(e)}")
                return self.default_settings.copy()
        else:
            # Varsayılan ayarları kaydet ve döndür
            self.save_settings(self.default_settings)
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Ayarları yapılandırma dosyasına kaydet"""
        if settings is None:
            settings = self.settings
            
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata oluştu: {str(e)}")
            return False
    
    def get_privacy_level(self):
        """Mevcut gizlilik seviyesini döndür"""
        return self.settings.get("privacy_level", PrivacyLevel.MEDIUM.name)
    
    def set_privacy_level(self, level):
        """Gizlilik seviyesini ayarla ve ilgili ayarları güncelle"""
        if isinstance(level, PrivacyLevel):
            level = level.name
            
        if level in [l.name for l in PrivacyLevel] and level != PrivacyLevel.CUSTOM.name:
            self.settings["privacy_level"] = level
            
            # Seviyeye göre ayarları güncelle
            for key, value in self.level_settings[level].items():
                self.settings[key] = value
                
            self.save_settings()
            return True
        return False
    
    def get_setting(self, key, default=None):
        """Belirli bir ayarı döndür"""
        if default is None:
            return self.settings.get(key, self.default_settings.get(key))
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Belirli bir ayarı güncelle"""
        if key in self.default_settings:
            self.settings[key] = value
            
            # Özel ayarlar yapıldığında seviyeyi CUSTOM olarak işaretle
            if key not in ["privacy_level", "custom_settings"]:
                self.settings["privacy_level"] = PrivacyLevel.CUSTOM.name
                
            self.save_settings()
            return True
        return False
    
    def get_custom_setting(self, key):
        """Özel ayarlardan belirli bir ayarı döndür"""
        return self.settings.get("custom_settings", {}).get(
            key, 
            self.default_settings["custom_settings"].get(key)
        )
    
    def set_custom_setting(self, key, value):
        """Özel ayarlardan belirli bir ayarı güncelle"""
        if key in self.default_settings["custom_settings"]:
            if "custom_settings" not in self.settings:
                self.settings["custom_settings"] = {}
                
            self.settings["custom_settings"][key] = value
            self.settings["privacy_level"] = PrivacyLevel.CUSTOM.name
            self.save_settings()
            return True
        return False
    
    def reset_to_defaults(self):
        """Tüm ayarları varsayılanlara sıfırla"""
        self.settings = self.default_settings.copy()
        self.save_settings()
        return True
    
    def get_tor_config(self):
        """Mevcut ayarlara göre Tor yapılandırmasını döndür"""
        # Tor data dizinini oluştur
        tor_data_dir = os.path.join(os.getcwd(), "modules", "tor_data")
        os.makedirs(tor_data_dir, exist_ok=True)
        
        config = {
            'SocksPort': '9090',
            'ControlPort': '9091',
            'DataDirectory': tor_data_dir
        }
        
        # Köprü kullanımı
        if self.get_setting("use_bridges"):
            config['UseBridges'] = '1'
            config['ClientTransportPlugin'] = 'obfs4 exec PluggableTransports\\obfs4proxy'
            
            # Varsayılan köprüler (gerçek uygulamada güncel köprüler kullanılmalı)
            config['Bridge'] = [
                'obfs4 154.35.22.10:15937 8FB9F4319E89E5C6223052AA525A192AFBC85D55 cert=GGGS1TX4R81m3r0HBl79wKy1OtPPNR2CZUIrHjkRg65Vc2VR8fOyo64f9kmT1UAFG7j0HQ iat-mode=0',
                'obfs4 198.98.51.90:80 7F82D2B9B3C21E89FBC9A32ECBFBF59A8BFEC179 cert=JZMfHBQaRo4XNz1eXrvwXlzW/b+CzIZ+3qlmJN2UjzlQFzfOTNzB0hSJNrZR5QQFuA+Vdw iat-mode=1',
                'obfs4 192.95.36.142:443 CDF2E852BF539B82BD10E27E9115A31734E378C2 cert=qUVQ0srL1JI/vO6V6m/24anYXiJD3QP2HgzUKQtQ7GRqqUvs7P+tG43RtAqdhLOALP7DJQ iat-mode=1'
            ]
        
        # Özel düğüm ayarları
        custom_settings = self.settings.get("custom_settings", {})
        
        if custom_settings.get("entry_nodes"):
            config['EntryNodes'] = ','.join(custom_settings["entry_nodes"])
            
        if custom_settings.get("exit_nodes"):
            config['ExitNodes'] = ','.join(custom_settings["exit_nodes"])
            
        if custom_settings.get("excluded_nodes"):
            config['ExcludeNodes'] = ','.join(custom_settings["excluded_nodes"])
            
        if custom_settings.get("strict_nodes"):
            config['StrictNodes'] = '1'
            
        return config