#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cihaz Bilgisi Yöneticisi

Bu modül, gerçek cihaz bilgilerini toplama ve sahte bilgilerle değiştirme işlemlerini yönetir.
Çeşitli cihaz bilgilerini (işletim sistemi, donanım, MAC adresi vb.) toplar ve değiştirir.
"""

import os
import sys
import platform
import uuid
import socket
import random
import json
import psutil
import re
import subprocess
from datetime import datetime
import winreg  # Windows Registry işlemleri için
import ctypes  # Sistem API'leri için
from ctypes import wintypes
import time  # İşlem bekletme için


# Windows Registry anahtarları
REG_OS_INFO = r"SYSTEM\CurrentControlSet\Control\SystemInformation"
REG_COMPUTER_NAME = r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName"
REG_NETWORK_INFO = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
REG_HARDWARE_INFO = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"

# Yönetici hakları kontrolü için
def is_admin():
    """Uygulamanın yönetici haklarıyla çalışıp çalışmadığını kontrol et
    
    Returns:
        bool: Yönetici haklarıyla çalışıyorsa True, değilse False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

class DeviceInfoManager:
    """Cihaz bilgilerini yöneten sınıf"""
    
    def __init__(self, config_dir):
        """Cihaz bilgisi yöneticisini başlat
        
        Args:
            config_dir (str): Yapılandırma dosyalarının bulunduğu dizin
        """
        self.config_dir = config_dir
        self.profiles_file = os.path.join(config_dir, "device_profiles.json")
        self.current_profile = None
        self.real_info = self._collect_real_info()
        self.is_admin = is_admin()
        
        # Profilleri yükle veya oluştur
        self._load_profiles()
    
    def _collect_real_info(self):
        """Gerçek cihaz bilgilerini topla
        
        Returns:
            dict: Gerçek cihaz bilgilerini içeren sözlük
        """
        info = {}
        
        # İşletim sistemi bilgileri
        info["os"] = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        
        # Ağ bilgileri
        info["network"] = {
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "mac_address": self._get_mac_address()
        }
        
        # Donanım bilgileri
        info["hardware"] = {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": self._get_cpu_freq(),
            "total_memory": psutil.virtual_memory().total,
            "disk_usage": self._get_disk_usage()
        }
        
        # Kullanıcı bilgileri
        info["user"] = {
            "username": os.getlogin(),
            "home_dir": os.path.expanduser("~")
        }
        
        return info
    
    def _get_mac_address(self):
        """MAC adresini al
        
        Returns:
            str: MAC adresi
        """
        try:
            mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            return mac
        except:
            return "00:00:00:00:00:00"
    
    def _get_cpu_freq(self):
        """CPU frekansını al
        
        Returns:
            dict: CPU frekans bilgileri
        """
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                return {
                    "current": cpu_freq.current,
                    "min": cpu_freq.min,
                    "max": cpu_freq.max
                }
            return {"current": 0, "min": 0, "max": 0}
        except:
            return {"current": 0, "min": 0, "max": 0}
    
    def _get_disk_usage(self):
        """Disk kullanımını al
        
        Returns:
            list: Disk kullanım bilgileri listesi
        """
        try:
            disks = []
            for partition in psutil.disk_partitions():
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            return disks
        except:
            return []
    
    def _load_profiles(self):
        """Profilleri yükle veya varsayılan profilleri oluştur"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
            else:
                # Varsayılan profilleri oluştur
                self.profiles = {
                    "profiles": [
                        self._create_default_profile("Windows 10"),
                        self._create_default_profile("MacOS"),
                        self._create_default_profile("Linux")
                    ]
                }
                self._save_profiles()
        except Exception as e:
            print(f"Profiller yüklenirken hata: {str(e)}")
            # Hata durumunda boş profil listesi oluştur
            self.profiles = {"profiles": []}
    
    def _save_profiles(self):
        """Profilleri kaydet"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Profiller kaydedilirken hata: {str(e)}")
    
    def _create_default_profile(self, os_type):
        """Varsayılan profil oluştur
        
        Args:
            os_type (str): İşletim sistemi türü
            
        Returns:
            dict: Oluşturulan profil
        """
        profile = {
            "name": f"{os_type} Profili",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "os": {}
        }
        
        if os_type == "Windows 10":
            profile["os"] = {
                "system": "Windows",
                "release": "10",
                "version": "10.0.19042",
                "platform": "Windows-10-10.0.19042",
                "machine": "AMD64",
                "processor": "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
            }
            profile["network"] = {
                "hostname": "DESKTOP-" + self._generate_random_id(7),
                "mac_address": self._generate_random_mac()
            }
            profile["hardware"] = {
                "cpu_count": 8,
                "cpu_freq": {"current": 2400, "min": 2400, "max": 4000},
                "total_memory": 16 * 1024 * 1024 * 1024  # 16 GB
            }
            profile["user"] = {
                "username": "User" + self._generate_random_id(3)
            }
            
        elif os_type == "MacOS":
            profile["os"] = {
                "system": "Darwin",
                "release": "20.6.0",
                "version": "Darwin Kernel Version 20.6.0",
                "platform": "macOS-11.6-x86_64-i386-64bit",
                "machine": "x86_64",
                "processor": "i386"
            }
            profile["network"] = {
                "hostname": "MacBook-Pro-" + self._generate_random_id(5),
                "mac_address": self._generate_random_mac()
            }
            profile["hardware"] = {
                "cpu_count": 8,
                "cpu_freq": {"current": 2300, "min": 2300, "max": 3500},
                "total_memory": 16 * 1024 * 1024 * 1024  # 16 GB
            }
            profile["user"] = {
                "username": "user" + self._generate_random_id(3)
            }
            
        elif os_type == "Linux":
            profile["os"] = {
                "system": "Linux",
                "release": "5.15.0-58-generic",
                "version": "#64-Ubuntu SMP",
                "platform": "Linux-5.15.0-58-generic-x86_64-with-glibc2.35",
                "machine": "x86_64",
                "processor": "x86_64"
            }
            profile["network"] = {
                "hostname": "ubuntu-" + self._generate_random_id(5),
                "mac_address": self._generate_random_mac()
            }
            profile["hardware"] = {
                "cpu_count": 4,
                "cpu_freq": {"current": 2200, "min": 2200, "max": 3200},
                "total_memory": 8 * 1024 * 1024 * 1024  # 8 GB
            }
            profile["user"] = {
                "username": "ubuntu" + self._generate_random_id(2)
            }
        
        return profile
    
    def _generate_random_id(self, length=5):
        """Rastgele ID oluştur
        
        Args:
            length (int): ID uzunluğu
            
        Returns:
            str: Rastgele ID
        """
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _generate_random_mac(self):
        """Rastgele MAC adresi oluştur
        
        Returns:
            str: Rastgele MAC adresi
        """
        mac = [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)
        ]
        return ':'.join(map(lambda x: "%02x" % x, mac))
    
    def get_real_info(self):
        """Gerçek cihaz bilgilerini döndür
        
        Returns:
            dict: Gerçek cihaz bilgileri
        """
        return self.real_info
    
    def get_profiles(self):
        """Tüm profilleri döndür
        
        Returns:
            list: Profil listesi
        """
        return self.profiles["profiles"]
    
    def get_profile(self, profile_name):
        """Belirli bir profili döndür
        
        Args:
            profile_name (str): Profil adı
            
        Returns:
            dict: Profil bilgileri veya None
        """
        for profile in self.profiles["profiles"]:
            if profile["name"] == profile_name:
                return profile
        return None
    
    def set_current_profile(self, profile_name):
        """Aktif profili ayarla
        
        Args:
            profile_name (str): Profil adı
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        profile = self.get_profile(profile_name)
        if profile:
            self.current_profile = profile
            return True
        return False
    
    def get_current_profile(self):
        """Aktif profili döndür
        
        Returns:
            dict: Aktif profil veya None
        """
        return self.current_profile
    
    def create_profile(self, profile_data):
        """Yeni profil oluştur
        
        Args:
            profile_data (dict): Profil verileri
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            # Profil adının benzersiz olduğunu kontrol et
            for profile in self.profiles["profiles"]:
                if profile["name"] == profile_data["name"]:
                    return False
            
            # Oluşturma zamanını ekle
            profile_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Profili ekle ve kaydet
            self.profiles["profiles"].append(profile_data)
            self._save_profiles()
            return True
        except Exception as e:
            print(f"Profil oluşturulurken hata: {str(e)}")
            return False
    
    def update_profile(self, profile_name, profile_data):
        """Profili güncelle
        
        Args:
            profile_name (str): Güncellenecek profil adı
            profile_data (dict): Yeni profil verileri
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            # Profili bul
            for i, profile in enumerate(self.profiles["profiles"]):
                if profile["name"] == profile_name:
                    # Oluşturma zamanını koru
                    profile_data["created_at"] = profile["created_at"]
                    
                    # Profili güncelle ve kaydet
                    self.profiles["profiles"][i] = profile_data
                    self._save_profiles()
                    
                    # Aktif profil güncellendiyse onu da güncelle
                    if self.current_profile and self.current_profile["name"] == profile_name:
                        self.current_profile = profile_data
                    
                    return True
            return False
        except Exception as e:
            print(f"Profil güncellenirken hata: {str(e)}")
            return False
    
    def delete_profile(self, profile_name):
        """Profili sil
        
        Args:
            profile_name (str): Silinecek profil adı
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            # Profili bul ve sil
            for i, profile in enumerate(self.profiles["profiles"]):
                if profile["name"] == profile_name:
                    del self.profiles["profiles"][i]
                    self._save_profiles()
                    
                    # Aktif profil silindiyse None yap
                    if self.current_profile and self.current_profile["name"] == profile_name:
                        self.current_profile = None
                    
                    return True
            return False
        except Exception as e:
            print(f"Profil silinirken hata: {str(e)}")
            return False
    
    def generate_random_profile(self, name="Rastgele Profil"):
        """Rastgele profil oluştur
        
        Args:
            name (str): Profil adı
            
        Returns:
            dict: Oluşturulan profil
        """
        # Rastgele işletim sistemi seç
        os_types = ["Windows 10", "MacOS", "Linux"]
        os_type = random.choice(os_types)
        
        # Temel profili oluştur
        profile = self._create_default_profile(os_type)
        
        # Profil adını güncelle
        profile["name"] = name
        
        # Rastgele değerleri güncelle
        profile["network"]["hostname"] = f"HOST-{self._generate_random_id(6)}"
        profile["network"]["mac_address"] = self._generate_random_mac()
        
        # Donanım bilgilerini rastgele güncelle
        cpu_count = random.choice([2, 4, 6, 8, 12, 16])
        cpu_freq_max = random.randint(2000, 5000)
        cpu_freq_min = random.randint(1000, cpu_freq_max - 500)
        cpu_freq_current = random.randint(cpu_freq_min, cpu_freq_max)
        
        profile["hardware"]["cpu_count"] = cpu_count
        profile["hardware"]["cpu_freq"] = {
            "current": cpu_freq_current,
            "min": cpu_freq_min,
            "max": cpu_freq_max
        }
        
        # Rastgele RAM miktarı (4-64 GB)
        ram_gb = random.choice([4, 8, 16, 32, 64])
        profile["hardware"]["total_memory"] = ram_gb * 1024 * 1024 * 1024
        
        return profile
    
    def export_profile(self, profile_name, file_path):
        """Profili dışa aktar
        
        Args:
            profile_name (str): Dışa aktarılacak profil adı
            file_path (str): Kaydedilecek dosya yolu
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            profile = self.get_profile(profile_name)
            if not profile:
                return False
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Profil dışa aktarılırken hata: {str(e)}")
            return False
    
    def import_profile(self, file_path):
        """Profili içe aktar
        
        Args:
            file_path (str): İçe aktarılacak dosya yolu
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            
            # Profil adının benzersiz olduğunu kontrol et
            original_name = profile["name"]
            counter = 1
            
            while self.get_profile(profile["name"]):
                profile["name"] = f"{original_name} ({counter})"
                counter += 1
            
            # Profili ekle
            return self.create_profile(profile)
        except Exception as e:
            print(f"Profil içe aktarılırken hata: {str(e)}")
            return False
            
    def _set_registry_value(self, key_path, value_name, value_data, value_type=winreg.REG_SZ):
        """Registry değerini ayarla
        
        Args:
            key_path (str): Registry anahtar yolu
            value_name (str): Değer adı
            value_data (str/int): Ayarlanacak değer
            value_type (int): Değer tipi (REG_SZ, REG_DWORD, vb.)
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if not self.is_admin:
                return False
                
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.SetValueEx(key, value_name, 0, value_type, value_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Registry değeri ayarlanırken hata: {str(e)}")
            return False
    
    def _change_computer_name(self, new_name):
        """Bilgisayar adını değiştir
        
        Args:
            new_name (str): Yeni bilgisayar adı
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if not self.is_admin:
                return False
                
            # ComputerName anahtarını güncelle
            success1 = self._set_registry_value(REG_COMPUTER_NAME, "ComputerName", new_name)
            
            # ActiveComputerName anahtarını güncelle
            active_key_path = REG_COMPUTER_NAME.replace("ComputerName", "ActiveComputerName")
            success2 = self._set_registry_value(active_key_path, "ComputerName", new_name)
            
            # Hostname anahtarını güncelle
            success3 = self._set_registry_value(REG_NETWORK_INFO, "Hostname", new_name)
            success4 = self._set_registry_value(REG_NETWORK_INFO, "NV Hostname", new_name)
            
            return success1 and success2 and success3 and success4
        except Exception as e:
            print(f"Bilgisayar adı değiştirilirken hata: {str(e)}")
            return False
    
    def _change_os_info(self, os_info):
        """İşletim sistemi bilgilerini değiştir
        
        Args:
            os_info (dict): İşletim sistemi bilgileri
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if not self.is_admin:
                return False
                
            # İşletim sistemi bilgilerini güncelle
            success1 = self._set_registry_value(REG_OS_INFO, "ProductName", os_info["system"] + " " + os_info["release"])
            success2 = self._set_registry_value(REG_OS_INFO, "SystemProductName", os_info["platform"])
            
            return success1 and success2
        except Exception as e:
            print(f"İşletim sistemi bilgileri değiştirilirken hata: {str(e)}")
            return False
            
    def _change_processor_info(self, hardware_info, os_info=None):
        """İşlemci bilgilerini değiştir
        
        Args:
            hardware_info (dict): Donanım bilgileri
            os_info (dict, optional): İşletim sistemi bilgileri
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if not self.is_admin:
                return False
                
            # İşlemci bilgilerini güncelle
            processor_name = ""
            
            # İşlemci adını belirle (os_info veya hardware_info'dan)
            if os_info and "processor" in os_info:
                processor_name = os_info["processor"]
            elif "processor" in hardware_info:
                processor_name = hardware_info["processor"]
            else:
                # Varsayılan bir işlemci adı
                processor_name = "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz"
            
            # Registry değerlerini ayarla
            success1 = self._set_registry_value(REG_HARDWARE_INFO, "ProcessorNameString", processor_name)
            
            # CPU frekansını ayarla
            cpu_freq = 2900  # Varsayılan değer (MHz)
            if "cpu_freq" in hardware_info and "current" in hardware_info["cpu_freq"]:
                cpu_freq = int(hardware_info["cpu_freq"]["current"])
            
            success2 = self._set_registry_value(REG_HARDWARE_INFO, "~MHz", cpu_freq, winreg.REG_DWORD)
            
            # Ek işlemci bilgilerini ayarla
            success3 = self._set_registry_value(REG_HARDWARE_INFO, "VendorIdentifier", "GenuineIntel")
            
            return success1 and success2 and success3
        except Exception as e:
            print(f"İşlemci bilgileri değiştirilirken hata: {str(e)}")
            return False
            
    def apply_profile_changes(self, profile_name):
        """Profil değişikliklerini gerçek sisteme uygula
        
        Args:
            profile_name (str): Uygulanacak profil adı
            
        Returns:
            dict: Sonuç bilgileri
        """
        result = {
            "success": False,
            "admin_rights": self.is_admin,
            "changes": [],
            "errors": []
        }
        
        if not self.is_admin:
            result["errors"].append("Yönetici hakları gerekli. Lütfen uygulamayı yönetici olarak çalıştırın.")
            return result
            
        profile = self.get_profile(profile_name)
        if not profile:
            result["errors"].append(f"{profile_name} profili bulunamadı.")
            return result
            
        # Bilgisayar adını değiştir
        if "network" in profile and "hostname" in profile["network"]:
            hostname_success = self._change_computer_name(profile["network"]["hostname"])
            if hostname_success:
                result["changes"].append("Bilgisayar adı değiştirildi.")
            else:
                result["errors"].append("Bilgisayar adı değiştirilemedi.")
                
        # İşletim sistemi bilgilerini değiştir
        if "os" in profile:
            os_success = self._change_os_info(profile["os"])
            if os_success:
                result["changes"].append("İşletim sistemi bilgileri değiştirildi.")
            else:
                result["errors"].append("İşletim sistemi bilgileri değiştirilemedi.")
                
        # İşlemci bilgilerini değiştir
        if "hardware" in profile:
            # İşlemci bilgilerini değiştirirken hem donanım hem de işletim sistemi bilgilerini kullan
            os_info = profile.get("os", None)
            processor_success = self._change_processor_info(profile["hardware"], os_info)
            if processor_success:
                result["changes"].append("İşlemci bilgileri değiştirildi.")
            else:
                result["errors"].append("İşlemci bilgileri değiştirilemedi.")
                # Hata detaylarını yazdır
                print("İşlemci bilgileri değiştirilirken hata oluştu. Profil bilgileri:")
                if os_info and "processor" in os_info:
                    print(f"OS processor: {os_info['processor']}")
                if "processor" in profile["hardware"]:
                    print(f"Hardware processor: {profile['hardware']['processor']}")
                if "cpu_freq" in profile["hardware"]:
                    print(f"CPU Freq: {profile['hardware']['cpu_freq']}")
                print(f"Registry anahtarı: {REG_HARDWARE_INFO}")
                # Kısa bir bekleme ekle (bazı registry değişiklikleri için gerekebilir)
                time.sleep(1)
                
        # Sonucu güncelle
        result["success"] = len(result["errors"]) == 0
        
        return result
        
    def restore_original_system_info(self):
        """Sistem bilgilerini orijinal haline geri döndür
        
        Returns:
            dict: Sonuç bilgileri
        """
        result = {
            "success": False,
            "admin_rights": self.is_admin,
            "changes": [],
            "errors": []
        }
        
        if not self.is_admin:
            result["errors"].append("Yönetici hakları gerekli. Lütfen uygulamayı yönetici olarak çalıştırın.")
            return result
        
        try:
            # Gerçek sistem bilgilerini al
            real_info = self.get_real_info()
            
            # Bilgisayar adını orijinal haline döndür
            if "network" in real_info and "hostname" in real_info["network"]:
                hostname_success = self._change_computer_name(real_info["network"]["hostname"])
                if hostname_success:
                    result["changes"].append("Bilgisayar adı orijinal haline döndürüldü.")
                else:
                    result["errors"].append("Bilgisayar adı orijinal haline döndürülemedi.")
            
            # İşletim sistemi bilgilerini orijinal haline döndür
            if "os" in real_info:
                os_success = self._change_os_info(real_info["os"])
                if os_success:
                    result["changes"].append("İşletim sistemi bilgileri orijinal haline döndürüldü.")
                else:
                    result["errors"].append("İşletim sistemi bilgileri orijinal haline döndürülemedi.")
            
            # İşlemci bilgilerini orijinal haline döndür
            if "hardware" in real_info:
                processor_success = self._change_processor_info(real_info["hardware"], real_info.get("os", None))
                if processor_success:
                    result["changes"].append("İşlemci bilgileri orijinal haline döndürüldü.")
                else:
                    result["errors"].append("İşlemci bilgileri orijinal haline döndürülemedi.")
                # Kısa bir bekleme ekle (bazı registry değişiklikleri için gerekebilir)
                time.sleep(1)
            
            # Sonucu güncelle
            result["success"] = len(result["errors"]) == 0
            
            return result
            
        except Exception as e:
            result["errors"].append(f"Sistem bilgileri orijinal haline döndürülürken hata: {str(e)}")
            return result