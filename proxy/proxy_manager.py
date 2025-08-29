import os
import sys
import json
import time
import socket
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import requests
import winreg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import customtkinter as ctk
from PIL import Image, ImageTk
import darkdetect
import webbrowser

# Sabitler
APP_NAME = "Proxy Manager"
APP_VERSION = "1.0.0"
CONFIG_FILE = "config.json"
PROXY_FILE = "proxy.txt"
PROXY_DETAILS_FILE = "proxy_details.txt"
TIMEOUT = 5  # Saniye cinsinden proxy test zaman aşımı
MAX_WORKERS = 20  # Eşzamanlı test iş parçacığı sayısı
TEST_URLS = [
    "http://www.google.com",
    "http://www.youtube.com",
    "http://www.facebook.com",
    "http://www.amazon.com",
    "http://www.twitter.com"
]

# Tema renkleri
COLORS = {
    "light": {
        "bg": "#f5f5f5",
        "fg": "#333333",
        "accent": "#007bff",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "card": "#ffffff",
        "border": "#e0e0e0"
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#f5f5f5",
        "accent": "#0d6efd",
        "success": "#198754",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "card": "#252525",
        "border": "#333333"
    }
}


class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.fast_proxies = []
        self.current_proxy = None
        self.config = self.load_config()
        self.load_proxies()

    def load_config(self):
        """Yapılandırma dosyasını yükler veya varsayılan yapılandırmayı oluşturur"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Yapılandırma dosyası yüklenirken hata oluştu: {e}")

        # Varsayılan yapılandırma
        default_config = {
            "theme": "system",  # system, light, dark
            "auto_test": True,
            "fast_proxy_threshold": 5.0,  # 5 saniyeden hızlı proxy'ler
            "auto_apply": True,
            "startup_test": True,
            "last_proxy": None
        }

        # Varsayılan yapılandırmayı kaydet
        self.save_config(default_config)
        return default_config

    def save_config(self, config=None):
        """Yapılandırmayı dosyaya kaydeder"""
        if config is None:
            config = self.config

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Yapılandırma kaydedilirken hata oluştu: {e}")

    def load_proxies(self):
        """Proxy listesini dosyadan yükler"""
        self.proxies = []
        if os.path.exists(PROXY_FILE):
            try:
                with open(PROXY_FILE, "r") as f:
                    for line in f:
                        proxy = line.strip()
                        if proxy and not proxy.startswith("#"):
                            self.proxies.append(proxy)
                print(f"{len(self.proxies)} proxy yüklendi.")
            except Exception as e:
                print(f"Proxy listesi yüklenirken hata oluştu: {e}")

    def save_proxies(self):
        """Proxy listesini dosyaya kaydeder"""
        try:
            with open(PROXY_FILE, "w") as f:
                for proxy in self.proxies:
                    f.write(f"{proxy}\n")
            print(f"{len(self.proxies)} proxy kaydedildi.")
        except Exception as e:
            print(f"Proxy listesi kaydedilirken hata oluştu: {e}")

    def add_proxy(self, proxy):
        """Listeye yeni bir proxy ekler"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.save_proxies()
            return True
        return False

    def remove_proxy(self, proxy):
        """Listeden bir proxy'yi kaldırır"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies()
            return True
        return False

    def test_proxy(self, proxy, protocol="http"):
        """Belirtilen proxy'yi test eder"""
        proxies = {
            "http": f"{protocol}://{proxy}",
            "https": f"{protocol}://{proxy}"
        }

        for url in TEST_URLS:
            try:
                start_time = time.time()
                response = requests.get(url, proxies=proxies, timeout=TIMEOUT)
                elapsed_time = time.time() - start_time

                if response.status_code == 200:
                    return {"status": "success", "protocol": protocol, "time": elapsed_time}
            except Exception:
                pass

        return {"status": "failed", "protocol": protocol, "time": None}

    def test_all_protocols(self, proxy):
        """Tüm protokollerle proxy'yi test eder"""
        protocols = ["http", "https", "socks4", "socks5"]
        for protocol in protocols:
            result = self.test_proxy(proxy, protocol)
            if result["status"] == "success":
                return result
        return {"status": "failed", "protocol": None, "time": None}

    def test_all_proxies(self, callback=None):
        """Tüm proxy'leri test eder"""
        self.working_proxies = []
        self.fast_proxies = []
        total = len(self.proxies)
        tested = 0

        # Proxy listesini yedekle
        if os.path.exists(PROXY_FILE):
            backup_file = f"{PROXY_FILE}_backup"
            try:
                with open(PROXY_FILE, "r") as src, open(backup_file, "w") as dst:
                    dst.write(src.read())
                print(f"Proxy listesi yedeklendi: {backup_file}")
            except Exception as e:
                print(f"Proxy listesi yedeklenirken hata oluştu: {e}")

        # ThreadPoolExecutor ile eşzamanlı test
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_proxy = {executor.submit(self.test_all_protocols, proxy): proxy for proxy in self.proxies}

            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                tested += 1
                try:
                    result = future.result()
                    if result["status"] == "success":
                        proxy_info = {
                            "address": proxy,
                            "protocol": result["protocol"],
                            "response_time": result["time"]
                        }
                        self.working_proxies.append(proxy_info)

                        # Hızlı proxy kontrolü
                        if result["time"] < self.config["fast_proxy_threshold"]:
                            self.fast_proxies.append(proxy_info)

                    # İlerleme geri çağrısı
                    if callback:
                        progress = (tested / total) * 100
                        callback(progress, tested, total, result["status"] == "success")

                except Exception as e:
                    print(f"Proxy test edilirken hata oluştu ({proxy}): {e}")

        # Çalışan proxy'leri kaydet
        self.save_working_proxies()
        return self.working_proxies

    def save_working_proxies(self):
        """Çalışan proxy'leri dosyaya kaydeder"""
        # Tüm çalışan proxy'leri proxy_details.txt dosyasına kaydet
        try:
            with open(PROXY_DETAILS_FILE, "w") as f:
                for proxy in self.working_proxies:
                    f.write(f"{proxy['address']} | {proxy['protocol']} | {proxy['response_time']:.2f}s\n")
            print(f"{len(self.working_proxies)} çalışan proxy kaydedildi.")
        except Exception as e:
            print(f"Çalışan proxy'ler kaydedilirken hata oluştu: {e}")

        # Hızlı proxy'leri proxy.txt dosyasına kaydet
        try:
            with open(PROXY_FILE, "w") as f:
                for proxy in self.fast_proxies:
                    f.write(f"{proxy['address']}\n")
            print(f"{len(self.fast_proxies)} hızlı proxy kaydedildi.")
        except Exception as e:
            print(f"Hızlı proxy'ler kaydedilirken hata oluştu: {e}")

    def set_system_proxy(self, proxy=None, enable=True):
        """Windows sistem proxy ayarlarını yapılandırır"""
        try:
            internet_settings = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                0, winreg.KEY_ALL_ACCESS
            )

            if enable and proxy:
                # Proxy'yi etkinleştir
                winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(internet_settings, 'ProxyServer', 0, winreg.REG_SZ, proxy)
                self.current_proxy = proxy
            else:
                # Proxy'yi devre dışı bırak
                winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
                self.current_proxy = None

            # Internet Explorer'ı yenileme (değişiklikleri uygulamak için)
            try:
                import ctypes
                INTERNET_OPTION_REFRESH = 37
                INTERNET_OPTION_SETTINGS_CHANGED = 39
                ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
                ctypes.windll.Wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
            except:
                pass

            winreg.CloseKey(internet_settings)
            return True
        except Exception as e:
            print(f"Sistem proxy ayarları yapılandırılırken hata oluştu: {e}")
            return False

    def get_current_system_proxy(self):
        """Mevcut sistem proxy ayarlarını alır"""
        try:
            internet_settings = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                0, winreg.KEY_READ
            )

            try:
                proxy_enable = winreg.QueryValueEx(internet_settings, 'ProxyEnable')[0]
                if proxy_enable:
                    proxy_server = winreg.QueryValueEx(internet_settings, 'ProxyServer')[0]
                    winreg.CloseKey(internet_settings)
                    return proxy_server
            except:
                pass

            winreg.CloseKey(internet_settings)
        except Exception as e:
            print(f"Sistem proxy ayarları alınırken hata oluştu: {e}")

        return None


class ProxyManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.proxy_manager = ProxyManager()
        self.setup_ui()
        self.load_proxy_list()
        
        # Başlangıçta otomatik test
        if self.proxy_manager.config["startup_test"]:
            self.after(1000, self.test_proxies)
            
        # Son kullanılan proxy'yi uygula
        if self.proxy_manager.config["auto_apply"] and self.proxy_manager.config["last_proxy"]:
            self.after(1500, lambda: self.apply_proxy(self.proxy_manager.config["last_proxy"]))

    def setup_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        # Ana pencere ayarları
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Tema ayarları
        self.setup_theme()
        
        # Ana çerçeve
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst panel (araç çubuğu)
        self.create_toolbar()
        
        # Sol panel (proxy listesi)
        self.create_proxy_list_panel()
        
        # Sağ panel (detaylar ve ayarlar)
        self.create_details_panel()
        
        # Alt panel (durum çubuğu)
        self.create_status_bar()

    def setup_theme(self):
        """Tema ayarlarını yapılandırır"""
        theme = self.proxy_manager.config["theme"]
        
        if theme == "system":
            theme = darkdetect.theme().lower()
            if theme not in ["light", "dark"]:
                theme = "light"
        
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        self.theme = theme
        self.colors = COLORS[theme]

    def create_toolbar(self):
        """Üst araç çubuğunu oluşturur"""
        toolbar = ctk.CTkFrame(self.main_frame, height=50)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        title_label = ctk.CTkLabel(
            toolbar, 
            text=APP_NAME, 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Tema değiştirme düğmesi
        theme_btn = ctk.CTkButton(
            toolbar,
            text="🌙" if self.theme == "light" else "☀️",
            width=40,
            command=self.toggle_theme
        )
        theme_btn.pack(side=tk.RIGHT, padx=10)
        
        # Ayarlar düğmesi
        settings_btn = ctk.CTkButton(
            toolbar,
            text="⚙️ Ayarlar",
            command=self.open_settings
        )
        settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # Test düğmesi
        test_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Tüm Proxy'leri Test Et",
            command=self.test_proxies
        )
        test_btn.pack(side=tk.RIGHT, padx=5)

    def create_proxy_list_panel(self):
        """Sol panel - Proxy listesi"""
        # Ana çerçeve
        left_frame = ctk.CTkFrame(self.main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Başlık
        header_frame = ctk.CTkFrame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Proxy Listesi", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Arama kutusu
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_proxy_list())
        
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Proxy ara...",
            textvariable=self.search_var
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        # Proxy listesi
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("proxy", "protocol", "speed")
        self.proxy_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Sütun başlıkları
        self.proxy_tree.heading("proxy", text="Proxy Adresi")
        self.proxy_tree.heading("protocol", text="Protokol")
        self.proxy_tree.heading("speed", text="Hız (s)")
        
        # Sütun genişlikleri
        self.proxy_tree.column("proxy", width=150)
        self.proxy_tree.column("protocol", width=70)
        self.proxy_tree.column("speed", width=70)
        
        # Kaydırma çubukları
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.proxy_tree.yview)
        self.proxy_tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.proxy_tree.xview)
        self.proxy_tree.configure(xscrollcommand=scrollbar_x.set)
        
        # Yerleştirme
        self.proxy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Olay işleyicileri
        self.proxy_tree.bind("<Double-1>", self.on_proxy_double_click)
        self.proxy_tree.bind("<Button-3>", self.show_proxy_context_menu)
        
        # Düğmeler
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Ekle",
            command=self.add_proxy_dialog
        )
        add_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        remove_btn = ctk.CTkButton(
            button_frame,
            text="Sil",
            command=self.remove_selected_proxy
        )
        remove_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        import_btn = ctk.CTkButton(
            button_frame,
            text="İçe Aktar",
            command=self.import_proxies
        )
        import_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="Dışa Aktar",
            command=self.export_proxies
        )
        export_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def create_details_panel(self):
        """Sağ panel - Detaylar ve ayarlar"""
        # Ana çerçeve
        right_frame = ctk.CTkFrame(self.main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=0)
        
        # Aktif proxy bilgisi
        active_frame = ctk.CTkFrame(right_frame)
        active_frame.pack(fill=tk.X, padx=10, pady=10)
        
        active_label = ctk.CTkLabel(
            active_frame, 
            text="Aktif Proxy", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        active_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.active_proxy_var = tk.StringVar(value="Proxy kullanılmıyor")
        active_proxy_label = ctk.CTkLabel(
            active_frame,
            textvariable=self.active_proxy_var,
            font=ctk.CTkFont(size=14)
        )
        active_proxy_label.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        # Proxy kontrol düğmeleri
        control_frame = ctk.CTkFrame(active_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        apply_btn = ctk.CTkButton(
            control_frame,
            text="Uygula",
            command=lambda: self.apply_selected_proxy()
        )
        apply_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        disable_btn = ctk.CTkButton(
            control_frame,
            text="Devre Dışı Bırak",
            command=self.disable_proxy
        )
        disable_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        test_btn = ctk.CTkButton(
            control_frame,
            text="Test Et",
            command=self.test_selected_proxy
        )
        test_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Test sonuçları
        results_frame = ctk.CTkFrame(right_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        results_label = ctk.CTkLabel(
            results_frame, 
            text="Test Sonuçları", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.results_text = ScrolledText(results_frame, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.results_text.config(state=tk.DISABLED)

    def create_status_bar(self):
        """Alt durum çubuğu"""
        status_bar = ctk.CTkFrame(self, height=25)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Hazır")
        status_label = ctk.CTkLabel(
            status_bar,
            textvariable=self.status_var
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_bar, 
            variable=self.progress_var,
            length=200,
            mode="determinate"
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=10, pady=5)

    def load_proxy_list(self):
        """Proxy listesini yükler ve görüntüler"""
        # Mevcut listeyi temizle
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
        
        # Proxy'leri ekle
        for proxy in self.proxy_manager.proxies:
            self.proxy_tree.insert("", tk.END, values=(proxy, "", ""))
        
        # Çalışan proxy'leri güncelle
        self.update_working_proxies()
        
        # Mevcut sistem proxy'sini kontrol et
        self.check_current_system_proxy()

    def update_working_proxies(self):
        """Çalışan proxy'leri listede günceller"""
        # Proxy_details.txt dosyasını kontrol et
        if os.path.exists(PROXY_DETAILS_FILE):
            try:
                with open(PROXY_DETAILS_FILE, "r") as f:
                    for line in f:
                        parts = line.strip().split(" | ")
                        if len(parts) >= 3:
                            proxy = parts[0]
                            protocol = parts[1]
                            speed = float(parts[2].replace("s", ""))
                            
                            # Ağaçta proxy'yi bul ve güncelle
                            for item in self.proxy_tree.get_children():
                                if self.proxy_tree.item(item, "values")[0] == proxy:
                                    self.proxy_tree.item(item, values=(proxy, protocol, f"{speed:.2f}"))
                                    break
            except Exception as e:
                print(f"Çalışan proxy'ler güncellenirken hata oluştu: {e}")

    def check_current_system_proxy(self):
        """Mevcut sistem proxy ayarını kontrol eder"""
        current_proxy = self.proxy_manager.get_current_system_proxy()
        if current_proxy:
            self.active_proxy_var.set(f"Aktif: {current_proxy}")
            self.proxy_manager.current_proxy = current_proxy
            self.proxy_manager.config["last_proxy"] = current_proxy
            self.proxy_manager.save_config()
        else:
            self.active_proxy_var.set("Proxy kullanılmıyor")

    def filter_proxy_list(self):
        """Proxy listesini arama terimlerine göre filtreler"""
        search_term = self.search_var.get().lower()
        
        # Mevcut listeyi temizle
        for item in self.proxy_tree.get_children():
            self.proxy_tree.delete(item)
        
        # Filtrelenmiş proxy'leri ekle
        for proxy in self.proxy_manager.proxies:
            if search_term in proxy.lower():
                self.proxy_tree.insert("", tk.END, values=(proxy, "", ""))
        
        # Çalışan proxy'leri güncelle
        self.update_working_proxies()

    def toggle_theme(self):
        """Temayı değiştirir"""
        new_theme = "dark" if self.theme == "light" else "light"
        self.proxy_manager.config["theme"] = new_theme
        self.proxy_manager.save_config()
        
        # Uygulamayı yeniden başlat
        self.destroy()
        app = ProxyManagerApp()
        app.mainloop()

    def open_settings(self):
        """Ayarlar penceresini açar"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Ayarlar")
        settings_window.geometry("500x400")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Tema ayarları
        theme_frame = ctk.CTkFrame(settings_window)
        theme_frame.pack(fill=tk.X, padx=20, pady=10)
        
        theme_label = ctk.CTkLabel(
            theme_frame, 
            text="Tema", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        theme_label.pack(anchor=tk.W, padx=10, pady=5)
        
        theme_var = tk.StringVar(value=self.proxy_manager.config["theme"])
        
        theme_system = ctk.CTkRadioButton(
            theme_frame, 
            text="Sistem", 
            variable=theme_var, 
            value="system"
        )
        theme_system.pack(anchor=tk.W, padx=20, pady=2)
        
        theme_light = ctk.CTkRadioButton(
            theme_frame, 
            text="Açık", 
            variable=theme_var, 
            value="light"
        )
        theme_light.pack(anchor=tk.W, padx=20, pady=2)
        
        theme_dark = ctk.CTkRadioButton(
            theme_frame, 
            text="Koyu", 
            variable=theme_var, 
            value="dark"
        )
        theme_dark.pack(anchor=tk.W, padx=20, pady=2)
        
        # Proxy ayarları
        proxy_frame = ctk.CTkFrame(settings_window)
        proxy_frame.pack(fill=tk.X, padx=20, pady=10)
        
        proxy_label = ctk.CTkLabel(
            proxy_frame, 
            text="Proxy Ayarları", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        proxy_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Otomatik test
        auto_test_var = tk.BooleanVar(value=self.proxy_manager.config["auto_test"])
        auto_test_cb = ctk.CTkCheckBox(
            proxy_frame, 
            text="Proxy eklendiğinde otomatik test et", 
            variable=auto_test_var
        )
        auto_test_cb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Başlangıçta test
        startup_test_var = tk.BooleanVar(value=self.proxy_manager.config["startup_test"])
        startup_test_cb = ctk.CTkCheckBox(
            proxy_frame, 
            text="Başlangıçta proxy'leri test et", 
            variable=startup_test_var
        )
        startup_test_cb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Otomatik uygula
        auto_apply_var = tk.BooleanVar(value=self.proxy_manager.config["auto_apply"])
        auto_apply_cb = ctk.CTkCheckBox(
            proxy_frame, 
            text="Son kullanılan proxy'yi başlangıçta uygula", 
            variable=auto_apply_var
        )
        auto_apply_cb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Hızlı proxy eşiği
        threshold_frame = ctk.CTkFrame(proxy_frame)
        threshold_frame.pack(fill=tk.X, padx=20, pady=5)
        
        threshold_label = ctk.CTkLabel(
            threshold_frame, 
            text="Hızlı proxy eşiği (saniye):"
        )
        threshold_label.pack(side=tk.LEFT, padx=5)
        
        threshold_var = tk.DoubleVar(value=self.proxy_manager.config["fast_proxy_threshold"])
        threshold_entry = ctk.CTkEntry(
            threshold_frame, 
            width=60,
            textvariable=threshold_var
        )
        threshold_entry.pack(side=tk.LEFT, padx=5)
        
        # Kaydet düğmesi
        save_btn = ctk.CTkButton(
            settings_window,
            text="Kaydet",
            command=lambda: self.save_settings(
                theme_var.get(),
                auto_test_var.get(),
                startup_test_var.get(),
                auto_apply_var.get(),
                threshold_var.get(),
                settings_window
            )
        )
        save_btn.pack(pady=20)

    def save_settings(self, theme, auto_test, startup_test, auto_apply, threshold, window):
        """Ayarları kaydeder"""
        try:
            # Ayarları güncelle
            self.proxy_manager.config["theme"] = theme
            self.proxy_manager.config["auto_test"] = auto_test
            self.proxy_manager.config["startup_test"] = startup_test
            self.proxy_manager.config["auto_apply"] = auto_apply
            self.proxy_manager.config["fast_proxy_threshold"] = float(threshold)
            
            # Ayarları kaydet
            self.proxy_manager.save_config()
            
            # Pencereyi kapat
            window.destroy()
            
            # Tema değiştiyse uygulamayı yeniden başlat
            if theme != self.theme:
                self.destroy()
                app = ProxyManagerApp()
                app.mainloop()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken hata oluştu: {e}")

    def add_proxy_dialog(self):
        """Yeni proxy ekleme iletişim kutusu"""
        dialog = ctk.CTkInputDialog(text="Proxy adresini girin (örn. 192.168.1.1:8080):", title="Proxy Ekle")
        proxy = dialog.get_input()
        
        if proxy:
            # Proxy formatını kontrol et
            if ":" not in proxy:
                messagebox.showerror("Hata", "Geçersiz proxy formatı. Doğru format: IP:PORT")
                return
                
            # Proxy'yi ekle
            if self.proxy_manager.add_proxy(proxy):
                self.proxy_tree.insert("", tk.END, values=(proxy, "", ""))
                
                # Otomatik test
                if self.proxy_manager.config["auto_test"]:
                    self.test_proxy(proxy)
            else:
                messagebox.showinfo("Bilgi", "Bu proxy zaten listede mevcut.")

    def remove_selected_proxy(self):
        """Seçili proxy'yi listeden kaldırır"""
        selected = self.proxy_tree.selection()
        if not selected:
            messagebox.showinfo("Bilgi", "Lütfen silmek için bir proxy seçin.")
            return
            
        proxy = self.proxy_tree.item(selected, "values")[0]
        
        if messagebox.askyesno("Onay", f"{proxy} proxy'sini silmek istediğinizden emin misiniz?"):
            if self.proxy_manager.remove_proxy(proxy):
                self.proxy_tree.delete(selected)
                
                # Aktif proxy ise devre dışı bırak
                if self.proxy_manager.current_proxy == proxy:
                    self.disable_proxy()

    def import_proxies(self):
        """Proxy listesini dosyadan içe aktarır"""
        file_path = filedialog.askopenfilename(
            title="Proxy Listesi Seç",
            filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "r") as f:
                imported = 0
                for line in f:
                    proxy = line.strip()
                    if proxy and not proxy.startswith("#"):
                        if self.proxy_manager.add_proxy(proxy):
                            self.proxy_tree.insert("", tk.END, values=(proxy, "", ""))
                            imported += 1
                            
            messagebox.showinfo("Başarılı", f"{imported} proxy içe aktarıldı.")
            
            # Otomatik test
            if imported > 0 and messagebox.askyesno("Test", "İçe aktarılan proxy'leri test etmek ister misiniz?"):
                self.test_proxies()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Proxy'ler içe aktarılırken hata oluştu: {e}")

    def export_proxies(self):
        """Proxy listesini dosyaya dışa aktarır"""
        file_path = filedialog.asksaveasfilename(
            title="Proxy Listesini Kaydet",
            defaultextension=".txt",
            filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "w") as f:
                for proxy in self.proxy_manager.proxies:
                    f.write(f"{proxy}\n")
                    
            messagebox.showinfo("Başarılı", f"{len(self.proxy_manager.proxies)} proxy dışa aktarıldı.")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Proxy'ler dışa aktarılırken hata oluştu: {e}")

    def on_proxy_double_click(self, event):
        """Proxy'ye çift tıklandığında çalışır"""
        selected = self.proxy_tree.selection()
        if selected:
            proxy = self.proxy_tree.item(selected, "values")[0]
            self.apply_proxy(proxy)

    def show_proxy_context_menu(self, event):
        """Proxy listesinde sağ tıklama menüsünü gösterir"""
        item = self.proxy_tree.identify_row(event.y)
        if not item:
            return
            
        # Öğeyi seç
        self.proxy_tree.selection_set(item)
        proxy = self.proxy_tree.item(item, "values")[0]
        
        # Menüyü oluştur
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Uygula", command=lambda: self.apply_proxy(proxy))
        menu.add_command(label="Test Et", command=lambda: self.test_proxy(proxy))
        menu.add_separator()
        menu.add_command(label="Düzenle", command=lambda: self.edit_proxy(item, proxy))
        menu.add_command(label="Sil", command=self.remove_selected_proxy)
        
        # Menüyü göster
        menu.post(event.x_root, event.y_root)

    def edit_proxy(self, item, old_proxy):
        """Proxy'yi düzenler"""
        dialog = ctk.CTkInputDialog(text="Yeni proxy adresini girin:", title="Proxy Düzenle")
        dialog.set_placeholder_text(old_proxy)
        new_proxy = dialog.get_input()
        
        if new_proxy and new_proxy != old_proxy:
            # Proxy formatını kontrol et
            if ":" not in new_proxy:
                messagebox.showerror("Hata", "Geçersiz proxy formatı. Doğru format: IP:PORT")
                return
                
            # Eski proxy'yi kaldır
            self.proxy_manager.remove_proxy(old_proxy)
            
            # Yeni proxy'yi ekle
            if self.proxy_manager.add_proxy(new_proxy):
                self.proxy_tree.item(item, values=(new_proxy, "", ""))
                
                # Aktif proxy ise güncelle
                if self.proxy_manager.current_proxy == old_proxy:
                    self.apply_proxy(new_proxy)
                    
                # Otomatik test
                if self.proxy_manager.config["auto_test"]:
                    self.test_proxy(new_proxy)
            else:
                # Ekleme başarısız olursa eski proxy'yi geri ekle
                self.proxy_manager.add_proxy(old_proxy)
                messagebox.showinfo("Bilgi", "Bu proxy zaten listede mevcut.")

    def apply_selected_proxy(self):
        """Seçili proxy'yi uygular"""
        selected = self.proxy_tree.selection()
        if not selected:
            messagebox.showinfo("Bilgi", "Lütfen uygulamak için bir proxy seçin.")
            return
            
        proxy = self.proxy_tree.item(selected, "values")[0]
        self.apply_proxy(proxy)

    def apply_proxy(self, proxy):
        """Belirtilen proxy'yi sistem ayarlarına uygular"""
        self.status_var.set(f"Proxy uygulanıyor: {proxy}...")
        self.update_idletasks()
        
        if self.proxy_manager.set_system_proxy(proxy, True):
            self.active_proxy_var.set(f"Aktif: {proxy}")
            self.proxy_manager.config["last_proxy"] = proxy
            self.proxy_manager.save_config()
            self.status_var.set(f"Proxy başarıyla uygulandı: {proxy}")
            
            # Sonuç ekranına ekle
            self.add_to_results(f"✅ Proxy uygulandı: {proxy}")
        else:
            self.status_var.set("Proxy uygulanırken hata oluştu!")
            messagebox.showerror("Hata", "Proxy ayarları uygulanırken bir hata oluştu.")

    def disable_proxy(self):
        """Sistem proxy ayarlarını devre dışı bırakır"""
        self.status_var.set("Proxy devre dışı bırakılıyor...")
        self.update_idletasks()
        
        if self.proxy_manager.set_system_proxy(None, False):
            self.active_proxy_var.set("Proxy kullanılmıyor")
            self.status_var.set("Proxy devre dışı bırakıldı")
            
            # Sonuç ekranına ekle
            self.add_to_results("❌ Proxy devre dışı bırakıldı")
        else:
            self.status_var.set("Proxy devre dışı bırakılırken hata oluştu!")
            messagebox.showerror("Hata", "Proxy ayarları devre dışı bırakılırken bir hata oluştu.")

    def test_selected_proxy(self):
        """Seçili proxy'yi test eder"""
        selected = self.proxy_tree.selection()
        if not selected:
            messagebox.showinfo("Bilgi", "Lütfen test etmek için bir proxy seçin.")
            return
            
        proxy = self.proxy_tree.item(selected, "values")[0]
        self.test_proxy(proxy)

    def test_proxy(self, proxy):
        """Belirtilen proxy'yi test eder"""
        self.status_var.set(f"Proxy test ediliyor: {proxy}...")
        self.update_idletasks()
        
        # Test işlemini ayrı bir iş parçacığında çalıştır
        threading.Thread(target=self._test_proxy_thread, args=(proxy,), daemon=True).start()

    def _test_proxy_thread(self, proxy):
        """Proxy test iş parçacığı"""
        try:
            result = self.proxy_manager.test_all_protocols(proxy)
            
            # Ana iş parçacığında UI güncellemesi
            self.after(0, lambda: self._update_proxy_test_result(proxy, result))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Proxy test edilirken hata oluştu: {e}"))

    def _update_proxy_test_result(self, proxy, result):
        """Proxy test sonucunu günceller"""
        if result["status"] == "success":
            # Ağaçta proxy'yi bul ve güncelle
            for item in self.proxy_tree.get_children():
                if self.proxy_tree.item(item, "values")[0] == proxy:
                    self.proxy_tree.item(item, values=(proxy, result["protocol"], f"{result['time']:.2f}"))
                    break
                    
            # Sonuç ekranına ekle
            self.add_to_results(f"✅ {proxy} ({result['protocol']}) - {result['time']:.2f}s")
            self.status_var.set(f"Proxy test edildi: {proxy} - Çalışıyor ({result['protocol']})")
        else:
            # Sonuç ekranına ekle
            self.add_to_results(f"❌ {proxy} - Çalışmıyor")
            self.status_var.set(f"Proxy test edildi: {proxy} - Çalışmıyor")

    def test_proxies(self):
        """Tüm proxy'leri test eder"""
        if not self.proxy_manager.proxies:
            messagebox.showinfo("Bilgi", "Test edilecek proxy bulunamadı.")
            return
            
        if messagebox.askyesno("Onay", f"{len(self.proxy_manager.proxies)} proxy'yi test etmek istediğinizden emin misiniz? Bu işlem biraz zaman alabilir."):
            # Test işlemini ayrı bir iş parçacığında çalıştır
            threading.Thread(target=self._test_proxies_thread, daemon=True).start()

    def _test_proxies_thread(self):
        """Tüm proxy'leri test etme iş parçacığı"""
        try:
            # Test başlangıcı
            self.after(0, lambda: self.status_var.set("Proxy'ler test ediliyor..."))
            self.after(0, lambda: self.add_to_results("🔄 Proxy testi başlatıldı..."))
            self.after(0, lambda: self.progress_var.set(0))
            
            # Test işlemi
            self.proxy_manager.test_all_proxies(self.update_test_progress)
            
            # Test sonucu
            self.after(0, lambda: self.load_proxy_list())
            self.after(0, lambda: self.status_var.set(f"Test tamamlandı. {len(self.proxy_manager.working_proxies)} çalışan proxy bulundu."))
            self.after(0, lambda: self.add_to_results(f"✅ Test tamamlandı. {len(self.proxy_manager.working_proxies)} çalışan proxy, {len(self.proxy_manager.fast_proxies)} hızlı proxy bulundu."))
            
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Proxy'ler test edilirken hata oluştu: {e}"))
            self.after(0, lambda: self.add_to_results(f"❌ Hata: {e}"))

    def update_test_progress(self, progress, tested, total, success):
        """Test ilerleme durumunu günceller"""
        self.after(0, lambda: self.progress_var.set(progress))
        self.after(0, lambda: self.status_var.set(f"Test ediliyor... {tested}/{total} ({progress:.1f}%)"))

    def add_to_results(self, message):
        """Sonuç ekranına mesaj ekler"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    try:
        # CustomTkinter ayarları
        ctk.set_appearance_mode("system")  # system, light, dark
        ctk.set_default_color_theme("blue")
        
        app = ProxyManagerApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Hata", f"Uygulama başlatılırken bir hata oluştu:\n{e}")