import sys
import os
import time
import requests
import stem.process
import winreg
import ctypes
from stem.control import Controller
from stem import Signal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QLabel, QComboBox, QListWidget,
                           QSlider, QGroupBox, QTextEdit, QCheckBox, QMessageBox)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer, Qt

# Doğrudan çalıştırma durumunda modül yolunu ayarla
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.error_logger import ErrorLogger
from modules.privacy_settings import PrivacySettings, PrivacyLevel

class TorController(QMainWindow):
    def __init__(self):
        super().__init__()

        # Başlangıçta çalışan tor.exe süreçlerini sonlandır
        try:
            os.system("taskkill /F /IM tor.exe")
        except Exception as e:
            print(f"Tor süreçlerini sonlandırma hatası: {str(e)}")

        self.setWindowTitle("Tor Gizlilik Kontrolcüsü")
        self.setGeometry(100, 100, 800, 600)
        
        # Hata loglama ve gizlilik ayarları modüllerini başlat
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logger = ErrorLogger(log_dir=os.path.join(base_dir, "logs"))
        self.privacy_settings = PrivacySettings(config_dir=os.path.join(base_dir, "config"))

        self.tor_process = None
        self.ip_list = []
        self.auto_switch_enabled = self.privacy_settings.get_setting("auto_switch_ip")
        self.auto_switch_interval = self.privacy_settings.get_setting("auto_switch_interval")
        
        # Proxy port bilgisini privacy_settings'ten al
        self.proxy_port = int(self.privacy_settings.get_tor_config().get('SocksPort', 9090))

        self.initUI()
        self.set_light_theme()
        
        # Dizinleri oluştur (UI oluşturulduktan sonra çağrılmalı)
        self.create_directories()
        
    def create_directories(self):
        """Gerekli dizinleri oluştur"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dirs = ["logs", "config", "modules/tor_data"]
        for dir_path in dirs:
            full_path = os.path.join(base_dir, dir_path)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                self.log_message(f"{dir_path} dizini oluşturuldu")

    def initUI(self):
        main_layout = QVBoxLayout()

        # Durum bilgisi
        self.status_label = QLabel("Tor Bağlantısı: Kapalı")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(self.status_label)

        # IP Listesi ve Kontrol Paneli
        content_layout = QHBoxLayout()

        # Sol Panel - IP Listesi
        left_panel = QGroupBox("IP Değişim Geçmişi")
        left_layout = QVBoxLayout()
        
        self.current_ip_label = QLabel("Mevcut IP: -")
        left_layout.addWidget(self.current_ip_label)
        
        self.ip_list_widget = QListWidget()
        left_layout.addWidget(self.ip_list_widget)
        
        left_panel.setLayout(left_layout)
        content_layout.addWidget(left_panel)

        # Sağ Panel - Kontroller
        right_panel = QGroupBox("Kontroller")
        right_layout = QVBoxLayout()

        # Bağlantı kontrolleri
        connection_group = QGroupBox("Bağlantı")
        connection_layout = QVBoxLayout()
        
        self.connect_button = QPushButton("Tor'a Bağlan")
        self.connect_button.clicked.connect(self.connect_to_tor)
        connection_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("Bağlantıyı Kes")
        self.disconnect_button.clicked.connect(self.disconnect_from_tor)
        connection_layout.addWidget(self.disconnect_button)
        
        self.switch_node_button = QPushButton("Çıkış Düğümünü Değiştir")
        self.switch_node_button.clicked.connect(self.switch_exit_node)
        connection_layout.addWidget(self.switch_node_button)
        
        connection_group.setLayout(connection_layout)
        right_layout.addWidget(connection_group)

        # Gizlilik ayarları
        privacy_group = QGroupBox("Gizlilik Ayarları")
        privacy_layout = QVBoxLayout()
        
        # Gizlilik seviyesi seçimi
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Gizlilik Seviyesi:"))
        
        self.privacy_level_selector = QComboBox()
        self.privacy_level_selector.addItems(["Düşük", "Orta", "Yüksek", "Özel"])
        current_level = self.privacy_settings.get_privacy_level()
        if current_level == "LOW":
            self.privacy_level_selector.setCurrentIndex(0)
        elif current_level == "MEDIUM":
            self.privacy_level_selector.setCurrentIndex(1)
        elif current_level == "HIGH":
            self.privacy_level_selector.setCurrentIndex(2)
        else:  # CUSTOM
            self.privacy_level_selector.setCurrentIndex(3)
            
        self.privacy_level_selector.currentIndexChanged.connect(self.change_privacy_level)
        level_layout.addWidget(self.privacy_level_selector)
        privacy_layout.addLayout(level_layout)
        
        # Otomatik IP değiştirme
        self.auto_switch_checkbox = QCheckBox("Otomatik IP Değiştirme")
        self.auto_switch_checkbox.setChecked(self.auto_switch_enabled)
        self.auto_switch_checkbox.toggled.connect(self.toggle_auto_switch)
        privacy_layout.addWidget(self.auto_switch_checkbox)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Değişim Aralığı:"))
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(30)
        self.interval_slider.setMaximum(300)
        self.interval_slider.setValue(self.auto_switch_interval)
        self.interval_slider.setTickPosition(QSlider.TicksBelow)
        self.interval_slider.setTickInterval(30)
        self.interval_slider.valueChanged.connect(self.update_interval)
        interval_layout.addWidget(self.interval_slider)
        
        self.interval_label = QLabel(f"{self.auto_switch_interval} saniye")
        interval_layout.addWidget(self.interval_label)
        
        privacy_layout.addLayout(interval_layout)
        
        # Ek gizlilik seçenekleri
        self.system_proxy_checkbox = QCheckBox("Sistem Genelinde Proxy Kullan (Tüm Windows IP'sini Değiştir)")
        self.system_proxy_checkbox.setChecked(self.privacy_settings.get_setting("use_system_proxy", False))
        self.system_proxy_checkbox.toggled.connect(self.toggle_system_proxy)
        privacy_layout.addWidget(self.system_proxy_checkbox)
        
        self.clear_cookies_checkbox = QCheckBox("Çerezleri Temizle")
        self.clear_cookies_checkbox.setChecked(self.privacy_settings.get_setting("clear_cookies"))
        self.clear_cookies_checkbox.toggled.connect(lambda state: self.update_privacy_setting("clear_cookies", state))
        privacy_layout.addWidget(self.clear_cookies_checkbox)
        
        # Tarayıcı yapılandırma butonu
        self.browser_config_button = QPushButton("Tarayıcı Ayarlarını Yapılandır")
        self.browser_config_button.clicked.connect(self.show_browser_config)
        privacy_layout.addWidget(self.browser_config_button)
        
        self.block_scripts_checkbox = QCheckBox("Scriptleri Engelle")
        self.block_scripts_checkbox.setChecked(self.privacy_settings.get_setting("block_scripts"))
        self.block_scripts_checkbox.toggled.connect(lambda state: self.update_privacy_setting("block_scripts", state))
        privacy_layout.addWidget(self.block_scripts_checkbox)
        
        self.use_bridges_checkbox = QCheckBox("Köprü Kullan (Sansür Atlatma)")
        self.use_bridges_checkbox.setChecked(self.privacy_settings.get_setting("use_bridges"))
        self.use_bridges_checkbox.toggled.connect(lambda state: self.update_privacy_setting("use_bridges", state))
        privacy_layout.addWidget(self.use_bridges_checkbox)
        
        privacy_group.setLayout(privacy_layout)
        right_layout.addWidget(privacy_group)

        # Tema seçimi
        theme_group = QGroupBox("Görünüm")
        theme_layout = QHBoxLayout()
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Açık Tema", "Koyu Tema"])
        self.theme_selector.currentIndexChanged.connect(self.change_theme)
        theme_layout.addWidget(QLabel("Tema:"))
        theme_layout.addWidget(self.theme_selector)
        
        theme_group.setLayout(theme_layout)
        right_layout.addWidget(theme_group)

        # Log alanı
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        right_panel.setLayout(right_layout)
        content_layout.addWidget(right_panel)

        main_layout.addLayout(content_layout)

        # Ana widget'a layout'u ekle
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Timer'lar
        self.ip_timer = QTimer(self)
        self.ip_timer.timeout.connect(self.update_ip_list)
        
        self.auto_switch_timer = QTimer(self)
        self.auto_switch_timer.timeout.connect(self.switch_exit_node)

    def connect_to_tor(self):
        try:
            self.log_message("Tor'a bağlanılıyor...")
            self.status_label.setText("Tor Bağlantısı: Bağlanıyor...")
            
            # Tor veri dizini oluştur
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tor_data")
            os.makedirs(data_dir, exist_ok=True)
            
            # Gizlilik ayarlarından Tor yapılandırmasını al
            tor_config = self.privacy_settings.get_tor_config()
            
            # Tor'u başlat
            tor_exe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modules", "tor.exe")
            # Eğer tor.exe bulunamazsa, modules dizinindeki tor.exe'yi kullan
            if not os.path.exists(tor_exe_path):
                tor_exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tor.exe")
            
            self.tor_process = stem.process.launch_tor_with_config(
                tor_cmd=tor_exe_path,
                config=tor_config,
                init_msg_handler=lambda line: self.log_message(line)
            )
            
            self.status_label.setText("Tor Bağlantısı: Açık")
            self.log_message("Tor'a başarıyla bağlanıldı!")
            
            # IP güncelleme zamanlayıcısını başlat
            self.ip_timer.start(5000)  # 5 saniyede bir IP kontrolü
            self.update_ip_list()
            
            # Otomatik değiştirme etkinse zamanlayıcıyı başlat
            if self.auto_switch_enabled:
                self.auto_switch_timer.start(self.auto_switch_interval * 1000)
                
            # Sistem genelinde proxy kullanımı etkinse, sistem proxy ayarlarını güncelle
            if self.privacy_settings.get_setting("use_system_proxy", False):
                self.set_system_proxy()
                self.log_message("Sistem genelinde proxy ayarları etkinleştirildi")
                
        except Exception as e:
            error_msg = f"Bağlantı hatası: {str(e)}"
            self.status_label.setText("Tor Bağlantısı: Hata")
            self.log_message(error_msg, is_error=True)
            self.logger.log_error("Tor bağlantı hatası", e)

    def disconnect_from_tor(self):
        try:
            # Her durumda sistem proxy ayarlarını sıfırla (checkbox durumuna bakmaksızın)
            # Bu, proxy ayarlarının kesinlikle kapatılmasını sağlar
            self.reset_system_proxy()
            self.log_message("Sistem genelinde proxy ayarları devre dışı bırakıldı")
            
            # Proxy ayarlarını sıfırladıktan sonra privacy_settings'i güncelle
            self.privacy_settings.set_setting("use_system_proxy", False)
                
            if self.tor_process:
                self.tor_process.kill()
                self.tor_process = None
                self.log_message("Tor bağlantısı kapatıldı")
            else:
                # Eğer process kontrolü yoksa, tor.exe'yi zorla sonlandır
                os.system("taskkill /IM tor.exe /F")
                self.log_message("Tor.exe zorla sonlandırıldı")
                
            self.status_label.setText("Tor Bağlantısı: Kapalı")
            
            # Zamanlayıcıları durdur
            self.ip_timer.stop()
            self.auto_switch_timer.stop()
            
            # Sistem proxy checkbox'ını güncelle
            self.system_proxy_checkbox.setChecked(False)
            
            # Proxy ayarlarının gerçekten kapatıldığından emin olmak için ikinci bir kontrol
            try:
                # Internet Settings kayıt defteri anahtarını kontrol et
                internet_settings = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 
                                                0, winreg.KEY_READ)
                proxy_enabled, _ = winreg.QueryValueEx(internet_settings, "ProxyEnable")
                winreg.CloseKey(internet_settings)
                
                if proxy_enabled == 1:
                    # Eğer hala etkinse, tekrar sıfırlamayı dene
                    self.log_message("Proxy hala etkin, tekrar sıfırlanıyor...", is_error=True)
                    self.reset_system_proxy()
            except Exception as registry_error:
                self.log_message(f"Proxy durumu kontrol edilemedi: {str(registry_error)}", is_error=True)
            
        except Exception as e:
            error_msg = f"Bağlantı kesme hatası: {str(e)}"
            self.log_message(error_msg, is_error=True)
            # Hata durumunda da proxy'yi sıfırlamaya çalış
            try:
                self.reset_system_proxy()
            except:
                pass

    def switch_exit_node(self):
        try:
            if not self.tor_process:
                self.log_message("Tor bağlantısı yok, önce bağlanın", is_error=True)
                return
                
            # ControlPort değerini privacy_settings'ten al
            control_port = int(self.privacy_settings.get_tor_config().get('ControlPort', 9091))
                
            with Controller.from_port(port=control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                self.log_message("Yeni Tor çıkış düğümüne geçildi")
                
                # Sistem genelinde proxy kullanımı etkinse, sistem proxy ayarlarını yenile
                if self.privacy_settings.get_setting("use_system_proxy", False):
                    # Proxy ayarlarını yenilemek için önce devre dışı bırakıp sonra tekrar etkinleştir
                    self.reset_system_proxy()
                    self.set_system_proxy()
                    self.log_message("Sistem genelinde proxy ayarları yenilendi")
                
                # 5 saniye sonra IP'yi güncelle
                QTimer.singleShot(5000, self.update_ip_list)
                
        except Exception as e:
            error_msg = f"Çıkış düğümü değiştirme hatası: {str(e)}"
            self.log_message(error_msg, is_error=True)

    def get_current_ip(self):
        try:
            if not self.tor_process:
                return "Bağlantı yok"
                
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.proxy_port}',
                'https': f'socks5h://127.0.0.1:{self.proxy_port}'
            }
            
            # Birden fazla API deneyerek daha güvenilir IP alma
            api_endpoints = [
                "https://ifconfig.me/ip",
                "https://api.ipify.org",
                "https://icanhazip.com",
                "https://ident.me",
                "https://ipecho.net/plain"
            ]
            
            for endpoint in api_endpoints:
                try:
                    ip = requests.get(endpoint, proxies=proxies, timeout=10).text.strip()
                    if ip and not ip.startswith('{') and not "error" in ip.lower():
                        return ip
                except Exception as e:
                    self.log_message(f"{endpoint} API hatası: {str(e)}", is_error=True)
                    continue
            
            return "IP alınamadı"
            
        except Exception as e:
            error_msg = f"IP alma hatası: {str(e)}"
            self.log_message(error_msg, is_error=True)
            return "Hata"

    def update_ip_list(self):
        if not self.tor_process:
            return
            
        new_ip = self.get_current_ip()
        self.current_ip_label.setText(f"Mevcut IP: {new_ip}")
        
        if new_ip and new_ip != "Hata" and new_ip != "Bağlantı yok" and new_ip not in self.ip_list:
            self.ip_list.insert(0, new_ip)
            self.ip_list_widget.clear()
            self.ip_list_widget.addItems([f"{i+1}. {ip}" for i, ip in enumerate(self.ip_list)])
            self.log_message(f"Yeni IP tespit edildi: {new_ip}")

    def toggle_auto_switch(self, enabled):
        self.auto_switch_enabled = enabled
        
        if enabled and self.tor_process:
            self.auto_switch_timer.start(self.auto_switch_interval * 1000)
            self.log_message(f"Otomatik IP değiştirme etkinleştirildi ({self.auto_switch_interval} saniye)")
        else:
            self.auto_switch_timer.stop()
            self.log_message("Otomatik IP değiştirme devre dışı bırakıldı")

    def update_interval(self, value):
        self.auto_switch_interval = value
        self.interval_label.setText(f"{value} saniye")
        
    def show_browser_config(self):
        """Tarayıcı yapılandırma talimatlarını göster"""
        msg = QMessageBox()
        msg.setWindowTitle("Tarayıcı Yapılandırması")
        msg.setIcon(QMessageBox.Information)
        
        instructions = f"""Tor proxy'sini kullanmak için iki seçeneğiniz var:

1. SİSTEM GENELİNDE PROXY (Tüm Windows IP'nizi değiştirir):
   - Gizlilik Ayarları bölümünde "Sistem Genelinde Proxy Kullan" seçeneğini işaretleyin
   - Bu seçenek, tüm Windows uygulamalarının Tor üzerinden bağlanmasını sağlar
   - Windows'un kendi proxy ayarlarını otomatik olarak değiştirir
   - Tüm uygulamalarınız Tor üzerinden bağlanacak ve IP adresiniz gizlenecektir

2. SADECE TARAYICI İÇİN PROXY:
   - Tarayıcı ayarlarınızı açın
   - Proxy ayarlarını bulun
   - Manuel proxy yapılandırması seçin
   - SOCKS proxy için aşağıdaki bilgileri girin:
     - Adres: 127.0.0.1
     - Port: {self.proxy_port}
     - SOCKS v5 seçin
   - 'DNS isteklerini proxy üzerinden yönlendir' seçeneğini işaretleyin
   - Ayarları kaydedin

Not: Tor bağlantısını kapattığınızda, sistem genelinde proxy ayarları otomatik olarak devre dışı bırakılacaktır. Tarayıcı ayarlarını ise manuel olarak geri almanız gerekecektir."""
        
        msg.setText(instructions)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def change_theme(self, index):
        if index == 0:
            self.set_light_theme()
        else:
            self.set_dark_theme()

    def set_light_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #f0f0f0; color: #333333; }
            QGroupBox { border: 1px solid #cccccc; border-radius: 5px; margin-top: 1ex; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QPushButton { background-color: #e0e0e0; border: 1px solid #b0b0b0; border-radius: 3px; padding: 5px; }
            QPushButton:hover { background-color: #d0d0d0; }
            QTextEdit, QListWidget { background-color: white; border: 1px solid #cccccc; }
        """)
        self.log_message("Açık tema uygulandı")

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2d2d2d; color: #e0e0e0; }
            QGroupBox { border: 1px solid #555555; border-radius: 5px; margin-top: 1ex; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QPushButton { background-color: #444444; border: 1px solid #666666; border-radius: 3px; padding: 5px; color: #e0e0e0; }
            QPushButton:hover { background-color: #555555; }
            QTextEdit, QListWidget { background-color: #333333; border: 1px solid #555555; color: #e0e0e0; }
            QLabel { color: #e0e0e0; }
            QComboBox { background-color: #444444; color: #e0e0e0; border: 1px solid #666666; }
            QComboBox QAbstractItemView { background-color: #444444; color: #e0e0e0; }
        """)
        self.log_message("Koyu tema uygulandı")

    def log_message(self, message, is_error=False):
        timestamp = time.strftime("%H:%M:%S")
        prefix = "[HATA]" if is_error else "[BİLGİ]"
        log_entry = f"[{timestamp}] {prefix} {message}"
        
        # Metin rengini ayarla
        if is_error:
            self.log_text.setTextColor(QColor("red"))
            # Hata loglama sistemine de kaydet
            self.logger.log_error(message)
        else:
            self.log_text.setTextColor(QColor("green"))
            # Bilgi loglama sistemine de kaydet
            self.logger.log_info(message)
            
        self.log_text.append(log_entry)
        self.log_text.setTextColor(QColor("black"))  # Rengi sıfırla

        # Otomatik kaydırma
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def change_privacy_level(self, index):
        """Gizlilik seviyesini değiştir"""
        level_map = {
            0: PrivacyLevel.LOW,
            1: PrivacyLevel.MEDIUM,
            2: PrivacyLevel.HIGH,
            3: PrivacyLevel.CUSTOM
        }
        
        level = level_map.get(index)
        if level:
            self.privacy_settings.set_privacy_level(level)
            self.log_message(f"Gizlilik seviyesi değiştirildi: {level.name}")
            
            # Arayüz elemanlarını güncelle
            if level != PrivacyLevel.CUSTOM:
                self.auto_switch_enabled = self.privacy_settings.get_setting("auto_switch_ip")
                self.auto_switch_checkbox.setChecked(self.auto_switch_enabled)
                
                self.auto_switch_interval = self.privacy_settings.get_setting("auto_switch_interval")
                self.interval_slider.setValue(self.auto_switch_interval)
                self.interval_label.setText(f"{self.auto_switch_interval} saniye")
                
                self.clear_cookies_checkbox.setChecked(self.privacy_settings.get_setting("clear_cookies"))
                self.block_scripts_checkbox.setChecked(self.privacy_settings.get_setting("block_scripts"))
                self.use_bridges_checkbox.setChecked(self.privacy_settings.get_setting("use_bridges"))
                
            # Eğer Tor bağlantısı açıksa, yeniden bağlanmak isteyip istemediğini sor
            if self.tor_process:
                reply = QMessageBox.question(self, "Yeniden Bağlan", 
                                           "Gizlilik ayarları değiştirildi. Tor'a yeniden bağlanmak ister misiniz?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.disconnect_from_tor()
                    QTimer.singleShot(1000, self.connect_to_tor)  # 1 saniye bekle, sonra bağlan
    
    def update_privacy_setting(self, key, value):
        """Gizlilik ayarını güncelle"""
        self.privacy_settings.set_setting(key, value)
        self.log_message(f"Gizlilik ayarı güncellendi: {key} = {value}")
        
        # Otomatik IP değiştirme ayarını güncelle
        if key == "auto_switch_ip":
            self.auto_switch_enabled = value
            self.toggle_auto_switch(value)
            
    def toggle_system_proxy(self, enabled):
        """Sistem genelinde proxy kullanımını aç/kapat"""
        self.update_privacy_setting("use_system_proxy", enabled)
        
        if enabled:
            # Proxy'yi etkinleştirmek istiyorsa, Tor bağlantısı olmalı
            if not self.tor_process:
                self.log_message("Tor bağlantısı yok, önce bağlanın", is_error=True)
                # Checkbox'ı işaretsiz yap ve ayarı güncelle
                self.system_proxy_checkbox.setChecked(False)
                self.privacy_settings.set_setting("use_system_proxy", False)
                return
            # Tor bağlantısı varsa proxy'yi etkinleştir
            self.set_system_proxy()
        else:
            # Proxy'yi kapatmak istiyorsa, her durumda kapat
            # Tor bağlantısı olup olmadığına bakılmaksızın proxy'yi devre dışı bırak
            self.reset_system_proxy()
            # Ayarı güncelle
            self.privacy_settings.set_setting("use_system_proxy", False)
            
    def set_system_proxy(self):
        """Windows sistem proxy ayarlarını Tor proxy'sine yönlendir"""
        try:
            proxy_server = f"socks=127.0.0.1:{self.proxy_port}"
            
            # Internet Settings kayıt defteri anahtarını aç
            internet_settings = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                             r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 
                                             0, winreg.KEY_WRITE)
            
            # Proxy ayarlarını güncelle
            winreg.SetValueEx(internet_settings, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(internet_settings, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
            # Yerel adresler için proxy kullanma
            winreg.SetValueEx(internet_settings, "ProxyOverride", 0, winreg.REG_SZ, "<local>")
            
            # Kayıt defteri anahtarını kapat
            winreg.CloseKey(internet_settings)
            
            # Değişiklikleri uygula - birkaç kez dene
            success = False
            for _ in range(3):  # 3 kez deneme yap
                result1 = ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
                result2 = ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)  # INTERNET_OPTION_REFRESH
                if result1 and result2:
                    success = True
                    break
                time.sleep(0.5)  # Kısa bir bekleme
            
            if success:
                self.log_message("Sistem genelinde proxy ayarları etkinleştirildi")
            else:
                self.log_message("Sistem proxy ayarları değiştirildi ancak uygulanamadı", is_error=True)
                # Başarısız olursa proxy'yi sıfırla
                self.reset_system_proxy()
                return
            
        except Exception as e:
            error_msg = f"Sistem proxy ayarları hatası: {str(e)}"
            self.log_message(error_msg, is_error=True)
            self.system_proxy_checkbox.setChecked(False)
            
    def reset_system_proxy(self):
        """Windows sistem proxy ayarlarını sıfırla"""
        try:
            # Internet Settings kayıt defteri anahtarını aç
            internet_settings = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                             r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 
                                             0, winreg.KEY_WRITE)
            
            # Proxy ayarlarını devre dışı bırak
            winreg.SetValueEx(internet_settings, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            # ProxyServer değerini temizle
            winreg.SetValueEx(internet_settings, "ProxyServer", 0, winreg.REG_SZ, "")
            # ProxyOverride değerini temizle
            winreg.SetValueEx(internet_settings, "ProxyOverride", 0, winreg.REG_SZ, "")
            
            # Kayıt defteri anahtarını kapat
            winreg.CloseKey(internet_settings)
            
            # Değişiklikleri uygula - birkaç kez dene
            for _ in range(3):  # 3 kez deneme yap
                result1 = ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
                result2 = ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)  # INTERNET_OPTION_REFRESH
                if result1 and result2:
                    break
                time.sleep(0.5)  # Kısa bir bekleme
            
            self.log_message(f"Sistem genelinde proxy ayarları devre dışı bırakıldı (Sonuç: {result1 and result2})")
            
            # Sistem proxy checkbox'ını güncelle
            self.system_proxy_checkbox.setChecked(False)
            
        except Exception as e:
            error_msg = f"Sistem proxy ayarlarını sıfırlama hatası: {str(e)}"
            self.log_message(error_msg, is_error=True)
            # Hata durumunda da checkbox'ı güncelle
            self.system_proxy_checkbox.setChecked(False)

def main():
    app = QApplication(sys.argv)
    window = TorController()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()