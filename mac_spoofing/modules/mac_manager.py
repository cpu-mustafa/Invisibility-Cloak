#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAC Adresi Yöneticisi

Bu modül, ağ adaptörlerinin MAC adreslerini görüntüleme ve değiştirme işlemlerini yönetir.
Sistem düzeyinde MAC adresi değişiklikleri yapabilir.
"""

import os
import re
import random
import subprocess
import ctypes
import netifaces
import psutil
import winreg


def is_admin():
    """Uygulamanın yönetici haklarıyla çalışıp çalışmadığını kontrol eder
    
    Returns:
        bool: Yönetici haklarıyla çalışıyorsa True, değilse False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


class MACManager:
    """MAC adresi yönetim sınıfı"""
    
    def __init__(self):
        """MAC adresi yöneticisini başlat"""
        self.is_admin = is_admin()
        
    def get_network_adapters(self):
        """Sistemdeki ağ adaptörlerini listele
        
        Returns:
            list: Ağ adaptörlerinin listesi (ad, açıklama, MAC adresi)
        """
        adapters = []
        
        try:
            # Ağ adaptörlerini al
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, interface_addresses in net_if_addrs.items():
                # Sadece fiziksel adaptörleri al (MAC adresi olanlar)
                for addr in interface_addresses:
                    if addr.family == psutil.AF_LINK and interface_name in net_if_stats:
                        # Adaptör bilgilerini ekle
                        adapters.append({
                            "name": interface_name,
                            "description": self._get_adapter_description(interface_name),
                            "mac_address": addr.address,
                            "is_up": net_if_stats[interface_name].isup
                        })
                        break
        except Exception as e:
            print(f"Ağ adaptörleri listelenirken hata: {str(e)}")
        
        return adapters
    
    def _get_adapter_description(self, adapter_name):
        """Ağ adaptörünün açıklamasını al
        
        Args:
            adapter_name (str): Adaptör adı
            
        Returns:
            str: Adaptör açıklaması
        """
        try:
            # Registry'den adaptör açıklamasını al
            key_path = r"SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                subkeys = []
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkeys.append(subkey_name)
                        i += 1
                    except WindowsError:
                        break
                
                for subkey_name in subkeys:
                    try:
                        connection_key_path = f"{key_path}\\{subkey_name}\\Connection"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, connection_key_path) as connection_key:
                            name = winreg.QueryValueEx(connection_key, "Name")[0]
                            if name == adapter_name:
                                return self._get_adapter_friendly_name(subkey_name)
                    except WindowsError:
                        continue
        except Exception as e:
            print(f"Adaptör açıklaması alınırken hata: {str(e)}")
        
        return adapter_name
    
    def _get_adapter_friendly_name(self, adapter_guid):
        """Ağ adaptörünün kullanıcı dostu adını al
        
        Args:
            adapter_guid (str): Adaptör GUID'i
            
        Returns:
            str: Adaptörün kullanıcı dostu adı
        """
        try:
            key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                subkeys = []
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name not in ["Properties"]:
                            subkeys.append(subkey_name)
                        i += 1
                    except WindowsError:
                        break
                
                for subkey_name in subkeys:
                    try:
                        subkey_path = f"{key_path}\\{subkey_name}"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
                            try:
                                net_cfg_instance_id = winreg.QueryValueEx(subkey, "NetCfgInstanceId")[0]
                                if net_cfg_instance_id.lower() == adapter_guid.lower():
                                    return winreg.QueryValueEx(subkey, "DriverDesc")[0]
                            except WindowsError:
                                continue
                    except WindowsError:
                        continue
        except Exception as e:
            print(f"Adaptör kullanıcı dostu adı alınırken hata: {str(e)}")
        
        return "Bilinmeyen Adaptör"
    
    def generate_random_mac(self):
        """Rastgele bir MAC adresi oluştur
        
        Returns:
            str: Rastgele MAC adresi
        """
        # İlk bayt çift olmalı (yerel yönetimli adres)
        first_byte = random.randint(0, 127) * 2  # 0-254 arasında çift sayı
        
        # Diğer baytlar rastgele
        mac_bytes = [first_byte] + [random.randint(0, 255) for _ in range(5)]
        
        # MAC adresini formatla
        mac_address = ':'.join([f"{b:02x}" for b in mac_bytes])
        return mac_address
    
    def is_valid_mac(self, mac_address):
        """MAC adresinin geçerli olup olmadığını kontrol et
        
        Args:
            mac_address (str): Kontrol edilecek MAC adresi
            
        Returns:
            bool: Geçerli ise True, değilse False
        """
        # MAC adresi formatını kontrol et (XX:XX:XX:XX:XX:XX veya XX-XX-XX-XX-XX-XX)
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac_address))
    
    def change_mac_address(self, adapter_name, new_mac):
        """MAC adresini değiştir
        
        Args:
            adapter_name (str): Ağ adaptörünün adı
            new_mac (str): Yeni MAC adresi
            
        Returns:
            dict: İşlem sonucu
        """
        result = {
            "success": False,
            "admin_rights": self.is_admin,
            "message": ""
        }
        
        if not self.is_admin:
            result["message"] = "Yönetici hakları gerekli. Lütfen uygulamayı yönetici olarak çalıştırın."
            return result
        
        if not self.is_valid_mac(new_mac):
            result["message"] = "Geçersiz MAC adresi formatı. XX:XX:XX:XX:XX:XX formatında olmalıdır."
            return result
        
        try:
            # Adaptör GUID'ini bul
            adapter_guid = self._find_adapter_guid(adapter_name)
            if not adapter_guid:
                result["message"] = f"{adapter_name} adaptörü bulunamadı."
                return result
            
            # Adaptörü devre dışı bırak
            disable_cmd = f'netsh interface set interface "{adapter_name}" admin=disable'
            subprocess.run(disable_cmd, shell=True, check=True)
            
            # MAC adresini değiştir
            new_mac_formatted = new_mac.replace(':', '')
            registry_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{adapter_guid}"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, new_mac_formatted)
            
            # Adaptörü tekrar etkinleştir
            enable_cmd = f'netsh interface set interface "{adapter_name}" admin=enable'
            subprocess.run(enable_cmd, shell=True, check=True)
            
            result["success"] = True
            result["message"] = f"{adapter_name} adaptörünün MAC adresi başarıyla değiştirildi."
            
        except Exception as e:
            result["message"] = f"MAC adresi değiştirilirken hata: {str(e)}"
            
            # Hata durumunda adaptörü etkinleştirmeyi dene
            try:
                enable_cmd = f'netsh interface set interface "{adapter_name}" admin=enable'
                subprocess.run(enable_cmd, shell=True)
            except:
                pass
        
        return result
    
    def _find_adapter_guid(self, adapter_name):
        """Ağ adaptörünün GUID'ini bul
        
        Args:
            adapter_name (str): Adaptör adı
            
        Returns:
            str: Adaptör GUID'i veya None
        """
        try:
            key_path = r"SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                subkeys = []
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkeys.append(subkey_name)
                        i += 1
                    except WindowsError:
                        break
                
                for subkey_name in subkeys:
                    try:
                        connection_key_path = f"{key_path}\\{subkey_name}\\Connection"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, connection_key_path) as connection_key:
                            name = winreg.QueryValueEx(connection_key, "Name")[0]
                            if name == adapter_name:
                                # Adaptör GUID'ini bul
                                class_key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
                                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, class_key_path) as class_key:
                                    class_subkeys = []
                                    j = 0
                                    while True:
                                        try:
                                            class_subkey_name = winreg.EnumKey(class_key, j)
                                            if class_subkey_name not in ["Properties"]:
                                                class_subkeys.append(class_subkey_name)
                                            j += 1
                                        except WindowsError:
                                            break
                                    
                                    for class_subkey_name in class_subkeys:
                                        try:
                                            class_subkey_path = f"{class_key_path}\\{class_subkey_name}"
                                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, class_subkey_path) as class_subkey:
                                                try:
                                                    net_cfg_instance_id = winreg.QueryValueEx(class_subkey, "NetCfgInstanceId")[0]
                                                    if net_cfg_instance_id.lower() == subkey_name.lower():
                                                        return class_subkey_name
                                                except WindowsError:
                                                    continue
                                        except WindowsError:
                                            continue
                    except WindowsError:
                        continue
        except Exception as e:
            print(f"Adaptör GUID'i bulunurken hata: {str(e)}")
        
        return None
    
    def reset_mac_address(self, adapter_name):
        """MAC adresini sıfırla (NetworkAddress değerini kaldır)
        
        Args:
            adapter_name (str): Ağ adaptörünün adı
            
        Returns:
            dict: İşlem sonucu
        """
        result = {
            "success": False,
            "admin_rights": self.is_admin,
            "message": ""
        }
        
        if not self.is_admin:
            result["message"] = "Yönetici hakları gerekli. Lütfen uygulamayı yönetici olarak çalıştırın."
            return result
        
        try:
            # Adaptör GUID'ini bul
            adapter_guid = self._find_adapter_guid(adapter_name)
            if not adapter_guid:
                result["message"] = f"{adapter_name} adaptörü bulunamadı."
                return result
            
            # Adaptörü devre dışı bırak
            disable_cmd = f'netsh interface set interface "{adapter_name}" admin=disable'
            subprocess.run(disable_cmd, shell=True, check=True)
            
            # NetworkAddress değerini kaldır
            registry_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{adapter_guid}"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_ALL_ACCESS) as key:
                try:
                    winreg.DeleteValue(key, "NetworkAddress")
                except WindowsError:
                    # Değer zaten yoksa sorun değil
                    pass
            
            # Adaptörü tekrar etkinleştir
            enable_cmd = f'netsh interface set interface "{adapter_name}" admin=enable'
            subprocess.run(enable_cmd, shell=True, check=True)
            
            result["success"] = True
            result["message"] = f"{adapter_name} adaptörünün MAC adresi başarıyla sıfırlandı."
            
        except Exception as e:
            result["message"] = f"MAC adresi sıfırlanırken hata: {str(e)}"
            
            # Hata durumunda adaptörü etkinleştirmeyi dene
            try:
                enable_cmd = f'netsh interface set interface "{adapter_name}" admin=enable'
                subprocess.run(enable_cmd, shell=True)
            except:
                pass
        
        return result