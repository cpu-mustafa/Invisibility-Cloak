#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cihaz Bilgisi Kontrolcüsü

Bu modül, cihaz bilgilerini gizleme uygulamasının ana arayüzünü ve kontrolcüsünü içerir.
Kullanıcı arayüzü, profil yönetimi ve cihaz bilgisi değiştirme işlemlerini yönetir.
"""

import os
import sys
import json
import random
from datetime import datetime

# Ana modülden sürüm bilgisini içe aktar
try:
    from main import APP_VERSION, APP_RELEASE_TYPE
except ImportError:
    APP_VERSION = "1.0.0"
    APP_RELEASE_TYPE = "stable"
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QGroupBox,
    QFormLayout, QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QFrame,
    QCheckBox, QRadioButton, QButtonGroup, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPalette

from .device_info_manager import DeviceInfoManager
from .error_logger import ErrorLogger


class DeviceInfoController(QMainWindow):
    """Cihaz bilgisi kontrolcüsü ana penceresi"""
    
    def __init__(self, base_dir):
        """Kontrolcüyü başlat
        
        Args:
            base_dir (str): Uygulama temel dizini
        """
        super().__init__()
        
        # Temel dizin ve yapılandırma
        self.base_dir = base_dir
        self.config_dir = os.path.join(base_dir, "config")
        self.settings = QSettings(os.path.join(self.config_dir, "settings.ini"), QSettings.IniFormat)
        
        # Cihaz bilgisi yöneticisini başlat
        self.device_manager = DeviceInfoManager(self.config_dir)
        
        # Hata günlükçüsünü başlat
        self.error_logger = ErrorLogger(os.path.join(base_dir, "logs"))
        
        # Otomatik yenileme zamanlayıcısı
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_real_info)
        
        # Arayüzü oluştur
        self._init_ui()
        
        # Profilleri yükle
        self._load_profiles()
        
        # Pencere başlığını ayarla
        self.setWindowTitle(f"Cihaz Bilgisi Gizleyici v{APP_VERSION} ({APP_RELEASE_TYPE})")
        self.statusBar().showMessage(f"Sürüm {APP_VERSION} - Tam Sürüm")
        
        # Zamanlayıcıyı başlat
        self.refresh_timer.start(5000)  # 5 saniyede bir yenile
    
    def _init_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana pencere ayarları
        self.setWindowTitle("Cihaz Bilgisi Gizleyici")
        self.setMinimumSize(900, 700)
        
        # Tema ayarlarını yükle
        self._load_theme()
        
        # Ana widget ve düzen
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Üst bilgi çubuğu
        info_bar = QWidget()
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(10, 5, 10, 5)
        
        # Logo ve başlık
        logo_label = QLabel()
        # Logo eklenecek: logo_label.setPixmap(QPixmap("path/to/logo.png").scaled(32, 32, Qt.KeepAspectRatio))
        title_label = QLabel("Cihaz Bilgisi Gizleyici")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Durum bilgisi
        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("color: green;")
        
        # Bilgi çubuğu düzeni
        info_layout.addWidget(logo_label)
        info_layout.addWidget(title_label)
        info_layout.addStretch()
        info_layout.addWidget(QLabel("Durum:"))
        info_layout.addWidget(self.status_label)
        
        # Ana içerik bölgesi
        content_area = QSplitter(Qt.Horizontal)
        
        # Sol panel - Profil yönetimi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Profil seçimi
        profile_group = QGroupBox("Profil Yönetimi")
        profile_layout = QVBoxLayout(profile_group)
        
        # Profil seçici
        profile_form = QFormLayout()
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(200)
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        profile_form.addRow("Aktif Profil:", self.profile_combo)
        profile_layout.addLayout(profile_form)
        
        # Profil butonları
        profile_buttons = QHBoxLayout()
        self.new_profile_btn = QPushButton("Yeni")
        self.new_profile_btn.clicked.connect(self._create_new_profile)
        self.edit_profile_btn = QPushButton("Düzenle")
        self.edit_profile_btn.clicked.connect(self._edit_current_profile)
        self.delete_profile_btn = QPushButton("Sil")
        self.delete_profile_btn.clicked.connect(self._delete_current_profile)
        
        profile_buttons.addWidget(self.new_profile_btn)
        profile_buttons.addWidget(self.edit_profile_btn)
        profile_buttons.addWidget(self.delete_profile_btn)
        profile_layout.addLayout(profile_buttons)
        
        # İçe/Dışa aktarma butonları
        export_buttons = QHBoxLayout()
        self.import_btn = QPushButton("İçe Aktar")
        self.import_btn.clicked.connect(self._import_profile)
        self.export_btn = QPushButton("Dışa Aktar")
        self.export_btn.clicked.connect(self._export_profile)
        
        export_buttons.addWidget(self.import_btn)
        export_buttons.addWidget(self.export_btn)
        profile_layout.addLayout(export_buttons)
        
        # Rastgele profil oluşturma
        random_group = QGroupBox("Rastgele Profil")
        random_layout = QVBoxLayout(random_group)
        
        random_desc = QLabel("Rastgele cihaz bilgileri ile yeni bir profil oluşturun.")
        random_desc.setWordWrap(True)
        random_layout.addWidget(random_desc)
        
        self.random_name = QLineEdit("Rastgele Profil")
        random_layout.addWidget(self.random_name)
        
        self.random_btn = QPushButton("Rastgele Profil Oluştur")
        self.random_btn.clicked.connect(self._create_random_profile)
        random_layout.addWidget(self.random_btn)
        
        # Sol panel düzeni
        left_layout.addWidget(profile_group)
        left_layout.addWidget(random_group)
        left_layout.addStretch()
        
        # Sağ panel - Bilgi görüntüleme
        right_panel = QTabWidget()
        
        # Gerçek bilgiler sekmesi
        real_info_tab = QWidget()
        real_layout = QVBoxLayout(real_info_tab)
        
        real_scroll = QScrollArea()
        real_scroll.setWidgetResizable(True)
        real_content = QWidget()
        real_content_layout = QVBoxLayout(real_content)
        
        # İşletim sistemi bilgileri
        os_group = QGroupBox("İşletim Sistemi Bilgileri")
        os_layout = QFormLayout(os_group)
        self.real_os_system = QLabel("")
        self.real_os_release = QLabel("")
        self.real_os_version = QLabel("")
        self.real_os_platform = QLabel("")
        self.real_os_machine = QLabel("")
        self.real_os_processor = QLabel("")
        
        os_layout.addRow("Sistem:", self.real_os_system)
        os_layout.addRow("Sürüm:", self.real_os_release)
        os_layout.addRow("Versiyon:", self.real_os_version)
        os_layout.addRow("Platform:", self.real_os_platform)
        os_layout.addRow("Makine:", self.real_os_machine)
        os_layout.addRow("İşlemci:", self.real_os_processor)
        
        # Ağ bilgileri
        network_group = QGroupBox("Ağ Bilgileri")
        network_layout = QFormLayout(network_group)
        self.real_network_hostname = QLabel("")
        self.real_network_ip = QLabel("")
        self.real_network_mac = QLabel("")
        
        network_layout.addRow("Bilgisayar Adı:", self.real_network_hostname)
        network_layout.addRow("IP Adresi:", self.real_network_ip)
        network_layout.addRow("MAC Adresi:", self.real_network_mac)
        
        # Donanım bilgileri
        hardware_group = QGroupBox("Donanım Bilgileri")
        hardware_layout = QFormLayout(hardware_group)
        self.real_hw_cpu_count = QLabel("")
        self.real_hw_cpu_freq = QLabel("")
        self.real_hw_memory = QLabel("")
        
        hardware_layout.addRow("CPU Sayısı:", self.real_hw_cpu_count)
        hardware_layout.addRow("CPU Frekansı:", self.real_hw_cpu_freq)
        hardware_layout.addRow("Toplam Bellek:", self.real_hw_memory)
        
        # Kullanıcı bilgileri
        user_group = QGroupBox("Kullanıcı Bilgileri")
        user_layout = QFormLayout(user_group)
        self.real_user_name = QLabel("")
        self.real_user_home = QLabel("")
        
        user_layout.addRow("Kullanıcı Adı:", self.real_user_name)
        user_layout.addRow("Kullanıcı Dizini:", self.real_user_home)
        
        # Gerçek bilgiler düzeni
        real_content_layout.addWidget(os_group)
        real_content_layout.addWidget(network_group)
        real_content_layout.addWidget(hardware_group)
        real_content_layout.addWidget(user_group)
        real_content_layout.addStretch()
        
        real_scroll.setWidget(real_content)
        real_layout.addWidget(real_scroll)
        
        # Sahte bilgiler sekmesi
        fake_info_tab = QWidget()
        fake_layout = QVBoxLayout(fake_info_tab)
        
        fake_scroll = QScrollArea()
        fake_scroll.setWidgetResizable(True)
        fake_content = QWidget()
        fake_content_layout = QVBoxLayout(fake_content)
        
        # İşletim sistemi bilgileri
        fake_os_group = QGroupBox("İşletim Sistemi Bilgileri")
        fake_os_layout = QFormLayout(fake_os_group)
        self.fake_os_system = QLabel("")
        self.fake_os_release = QLabel("")
        self.fake_os_version = QLabel("")
        self.fake_os_platform = QLabel("")
        self.fake_os_machine = QLabel("")
        self.fake_os_processor = QLabel("")
        
        fake_os_layout.addRow("Sistem:", self.fake_os_system)
        fake_os_layout.addRow("Sürüm:", self.fake_os_release)
        fake_os_layout.addRow("Versiyon:", self.fake_os_version)
        fake_os_layout.addRow("Platform:", self.fake_os_platform)
        fake_os_layout.addRow("Makine:", self.fake_os_machine)
        fake_os_layout.addRow("İşlemci:", self.fake_os_processor)
        
        # Ağ bilgileri
        fake_network_group = QGroupBox("Ağ Bilgileri")
        fake_network_layout = QFormLayout(fake_network_group)
        self.fake_network_hostname = QLabel("")
        self.fake_network_ip = QLabel("")
        self.fake_network_mac = QLabel("")
        
        fake_network_layout.addRow("Bilgisayar Adı:", self.fake_network_hostname)
        fake_network_layout.addRow("IP Adresi:", self.fake_network_ip)
        fake_network_layout.addRow("MAC Adresi:", self.fake_network_mac)
        
        # Donanım bilgileri
        fake_hardware_group = QGroupBox("Donanım Bilgileri")
        fake_hardware_layout = QFormLayout(fake_hardware_group)
        self.fake_hw_cpu_count = QLabel("")
        self.fake_hw_cpu_freq = QLabel("")
        self.fake_hw_memory = QLabel("")
        
        fake_hardware_layout.addRow("CPU Sayısı:", self.fake_hw_cpu_count)
        fake_hardware_layout.addRow("CPU Frekansı:", self.fake_hw_cpu_freq)
        fake_hardware_layout.addRow("Toplam Bellek:", self.fake_hw_memory)
        
        # Kullanıcı bilgileri
        fake_user_group = QGroupBox("Kullanıcı Bilgileri")
        fake_user_layout = QFormLayout(fake_user_group)
        self.fake_user_name = QLabel("")
        
        fake_user_layout.addRow("Kullanıcı Adı:", self.fake_user_name)
        
        # Sahte bilgiler düzeni
        fake_content_layout.addWidget(fake_os_group)
        fake_content_layout.addWidget(fake_network_group)
        fake_content_layout.addWidget(fake_hardware_group)
        fake_content_layout.addWidget(fake_user_group)
        fake_content_layout.addStretch()
        
        fake_scroll.setWidget(fake_content)
        fake_layout.addWidget(fake_scroll)
        
        # Ayarlar sekmesi
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Tema ayarları
        theme_group = QGroupBox("Tema Ayarları")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık Tema", "Koyu Tema", "Sistem Teması"])
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        
        # Otomatik yenileme ayarları
        refresh_group = QGroupBox("Otomatik Yenileme")
        refresh_layout = QVBoxLayout(refresh_group)
        
        self.refresh_check = QCheckBox("Gerçek bilgileri otomatik yenile")
        self.refresh_check.setChecked(True)
        self.refresh_check.stateChanged.connect(self._on_refresh_changed)
        refresh_layout.addWidget(self.refresh_check)
        
        refresh_interval_layout = QHBoxLayout()
        refresh_interval_layout.addWidget(QLabel("Yenileme aralığı (saniye):"))
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 60)
        self.refresh_spin.setValue(5)
        self.refresh_spin.valueChanged.connect(self._on_refresh_interval_changed)
        refresh_interval_layout.addWidget(self.refresh_spin)
        refresh_interval_layout.addStretch()
        refresh_layout.addLayout(refresh_interval_layout)
        
        # Ayarlar düzeni
        settings_layout.addWidget(theme_group)
        settings_layout.addWidget(refresh_group)
        settings_layout.addStretch()
        
        # Sekmeleri ekle
        right_panel.addTab(real_info_tab, "Gerçek Bilgiler")
        right_panel.addTab(fake_info_tab, "Sahte Bilgiler")
        right_panel.addTab(settings_tab, "Ayarlar")
        
        # İçerik bölgesine panelleri ekle
        content_area.addWidget(left_panel)
        content_area.addWidget(right_panel)
        content_area.setStretchFactor(0, 1)  # Sol panel
        content_area.setStretchFactor(1, 2)  # Sağ panel
        
        # Alt bilgi çubuğu
        footer_bar = QWidget()
        footer_layout = QHBoxLayout(footer_bar)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Versiyon bilgisi
        version_label = QLabel("v1.0.0")
        
        # Uygula butonu
        self.apply_btn = QPushButton("Değişiklikleri Uygula")
        self.apply_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.clicked.connect(self._apply_changes)
        
        # Sistemi sıfırla butonu
        self.restore_btn = QPushButton("Sistemi Orijinal Haline Döndür")
        self.restore_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        self.restore_btn.setMinimumHeight(40)
        self.restore_btn.clicked.connect(self._reset_to_original)
        
        # Alt bilgi çubuğu düzeni
        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.restore_btn)
        footer_layout.addWidget(self.apply_btn)
        
        # Ana düzene ekle
        main_layout.addWidget(info_bar)
        main_layout.addWidget(content_area)
        main_layout.addWidget(footer_bar)
        
        # Ana pencereye ekle
        self.setCentralWidget(central_widget)
        
        # Tema ayarını yükle
        theme_index = self.settings.value("theme", 0, type=int)
        self.theme_combo.setCurrentIndex(theme_index)
        
        # Yenileme ayarlarını yükle
        refresh_enabled = self.settings.value("refresh_enabled", True, type=bool)
        self.refresh_check.setChecked(refresh_enabled)
        
        refresh_interval = self.settings.value("refresh_interval", 5, type=int)
        self.refresh_spin.setValue(refresh_interval)
        
        # Yenileme zamanlayıcısını ayarla
        self._on_refresh_changed()
    
    def _load_theme(self):
        """Tema ayarlarını yükle"""
        theme_index = self.settings.value("theme", 0, type=int)
        
        if theme_index == 0:  # Açık tema
            self._set_light_theme()
        elif theme_index == 1:  # Koyu tema
            self._set_dark_theme()
        else:  # Sistem teması
            self._set_system_theme()
    
    def _set_light_theme(self):
        """Açık temayı uygula"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px 10px;
            }
            QTabBar::tab:selected {
                background-color: #f5f5f5;
                border-bottom-color: #f5f5f5;
            }
            QScrollArea, QScrollBar {
                background-color: #f5f5f5;
                border: none;
            }
        """)
    
    def _set_dark_theme(self):
        """Koyu temayı uygula"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
                background-color: #3d3d3d;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px 10px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom-color: #2d2d2d;
            }
            QScrollArea, QScrollBar {
                background-color: #2d2d2d;
                border: none;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
    
    def _set_system_theme(self):
        """Sistem temasını uygula"""
        self.setStyleSheet("")
    
    def _on_theme_changed(self):
        """Tema değiştiğinde çağrılır"""
        theme_index = self.theme_combo.currentIndex()
        self.settings.setValue("theme", theme_index)
        
        if theme_index == 0:  # Açık tema
            self._set_light_theme()
        elif theme_index == 1:  # Koyu tema
            self._set_dark_theme()
        else:  # Sistem teması
            self._set_system_theme()
    
    def _on_refresh_changed(self):
        """Otomatik yenileme değiştiğinde çağrılır"""
        enabled = self.refresh_check.isChecked()
        self.settings.setValue("refresh_enabled", enabled)
        self.refresh_spin.setEnabled(enabled)
        
        if hasattr(self, 'refresh_timer'):
            if enabled:
                interval = self.refresh_spin.value() * 1000  # ms cinsinden
                self.refresh_timer.start(interval)
            else:
                self.refresh_timer.stop()
    
    def _on_refresh_interval_changed(self):
        """Yenileme aralığı değiştiğinde çağrılır"""
        interval = self.refresh_spin.value()
        self.settings.setValue("refresh_interval", interval)
        
        if hasattr(self, 'refresh_timer') and self.refresh_check.isChecked():
            self.refresh_timer.start(interval * 1000)  # ms cinsinden
    
    def _load_profiles(self):
        """Profilleri yükle"""
        try:
            # Profil listesini temizle
            self.profile_combo.clear()
            
            # Profilleri al ve ekle
            profiles = self.device_manager.get_profiles()
            for profile in profiles:
                self.profile_combo.addItem(profile["name"])
            
            # Son seçilen profili yükle
            last_profile = self.settings.value("last_profile", "")
            if last_profile:
                index = self.profile_combo.findText(last_profile)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
            
            # Profil varsa ilkini seç
            if self.profile_combo.count() > 0 and self.profile_combo.currentIndex() < 0:
                self.profile_combo.setCurrentIndex(0)
        except Exception as e:
            error_msg = f"Profiller yüklenirken hata: {str(e)}"
            self.error_logger.log_error(error_msg)
            self.status_label.setText("Hata: Profiller yüklenemedi")
            self.status_label.setStyleSheet("color: red;")
    
    def _on_profile_changed(self):
        """Profil değiştiğinde çağrılır"""
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        
        # Profili ayarla
        success = self.device_manager.set_current_profile(profile_name)
        if success:
            self.settings.setValue("last_profile", profile_name)
            self._update_fake_info_display()
            self.status_label.setText(f"Profil yüklendi: {profile_name}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Hata: Profil yüklenemedi")
            self.status_label.setStyleSheet("color: red;")
    
    def _refresh_real_info(self):
        """Gerçek cihaz bilgilerini yenile"""
        try:
            # Gerçek bilgileri al
            real_info = self.device_manager.get_real_info()
            
            # İşletim sistemi bilgilerini güncelle
            self.real_os_system.setText(real_info["os"]["system"])
            self.real_os_release.setText(real_info["os"]["release"])
            self.real_os_version.setText(real_info["os"]["version"])
            self.real_os_platform.setText(real_info["os"]["platform"])
            self.real_os_machine.setText(real_info["os"]["machine"])
            self.real_os_processor.setText(real_info["os"]["processor"])
            
            # Ağ bilgilerini güncelle
            self.real_network_hostname.setText(real_info["network"]["hostname"])
            self.real_network_ip.setText(real_info["network"]["ip_address"])
            self.real_network_mac.setText(real_info["network"]["mac_address"])
            
            # Donanım bilgilerini güncelle
            self.real_hw_cpu_count.setText(str(real_info["hardware"]["cpu_count"]))
            
            cpu_freq = real_info["hardware"]["cpu_freq"]
            if cpu_freq["current"] > 0:
                freq_text = f"{cpu_freq['current']:.2f} MHz (Min: {cpu_freq['min']:.2f} MHz, Max: {cpu_freq['max']:.2f} MHz)"
            else:
                freq_text = "Bilinmiyor"
            self.real_hw_cpu_freq.setText(freq_text)
            
            memory_gb = real_info["hardware"]["total_memory"] / (1024 * 1024 * 1024)
            self.real_hw_memory.setText(f"{memory_gb:.2f} GB")
            
            # Kullanıcı bilgilerini güncelle
            self.real_user_name.setText(real_info["user"]["username"])
            self.real_user_home.setText(real_info["user"]["home_dir"])
            
        except Exception as e:
            error_msg = f"Gerçek bilgiler yenilenirken hata: {str(e)}"
            self.error_logger.log_error(error_msg)
            self.status_label.setText("Hata: Gerçek bilgiler yenilenemedi")
            self.status_label.setStyleSheet("color: red;")
    
    def _update_fake_info_display(self):
        """Sahte bilgileri görüntüle"""
        try:
            # Aktif profili al
            profile = self.device_manager.get_current_profile()
            if not profile:
                return
            
            # İşletim sistemi bilgilerini güncelle
            self.fake_os_system.setText(profile["os"]["system"])
            self.fake_os_release.setText(profile["os"]["release"])
            self.fake_os_version.setText(profile["os"]["version"])
            self.fake_os_platform.setText(profile["os"]["platform"])
            self.fake_os_machine.setText(profile["os"]["machine"])
            self.fake_os_processor.setText(profile["os"]["processor"])
            
            # Ağ bilgilerini güncelle
            self.fake_network_hostname.setText(profile["network"]["hostname"])
            self.fake_network_ip.setText(profile["network"].get("ip_address", "Değiştirilmedi"))
            self.fake_network_mac.setText(profile["network"]["mac_address"])
            
            # Donanım bilgilerini güncelle
            self.fake_hw_cpu_count.setText(str(profile["hardware"]["cpu_count"]))
            
            cpu_freq = profile["hardware"]["cpu_freq"]
            freq_text = f"{cpu_freq['current']:.2f} MHz (Min: {cpu_freq['min']:.2f} MHz, Max: {cpu_freq['max']:.2f} MHz)"
            self.fake_hw_cpu_freq.setText(freq_text)
            
            memory_gb = profile["hardware"]["total_memory"] / (1024 * 1024 * 1024)
            self.fake_hw_memory.setText(f"{memory_gb:.2f} GB")
            
            # Kullanıcı bilgilerini güncelle
            self.fake_user_name.setText(profile["user"]["username"])
            
        except Exception as e:
            error_msg = f"Sahte bilgiler görüntülenirken hata: {str(e)}"
            self.error_logger.log_error(error_msg)
            self.status_label.setText("Hata: Sahte bilgiler görüntülenemedi")
            self.status_label.setStyleSheet("color: red;")
    
    def _create_new_profile(self):
        """Yeni profil oluştur"""
        # Profil adını al
        profile_name, ok = QInputDialog.getText(self, "Yeni Profil", "Profil Adı:")
        if not ok or not profile_name:
            return
        
        # Profil adının benzersiz olduğunu kontrol et
        if self.device_manager.get_profile(profile_name):
            QMessageBox.warning(self, "Hata", "Bu isimde bir profil zaten var.")
            return
        
        # Yeni profil oluştur (Windows 10 temel alınarak)
        profile = self.device_manager.generate_random_profile(profile_name)
        
        # Profili kaydet
        success = self.device_manager.create_profile(profile)
        if success:
            # Profil listesini güncelle
            self._load_profiles()
            
            # Yeni profili seç
            index = self.profile_combo.findText(profile_name)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
            
            self.status_label.setText(f"Yeni profil oluşturuldu: {profile_name}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Hata: Profil oluşturulamadı")
            self.status_label.setStyleSheet("color: red;")
    
    def _edit_current_profile(self):
        """Mevcut profili düzenle"""
        # TODO: Profil düzenleme penceresi eklenecek
        QMessageBox.information(self, "Bilgi", "Profil düzenleme özelliği yakında eklenecek.")
    
    def _delete_current_profile(self):
        """Mevcut profili sil"""
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        
        # Onay al
        reply = QMessageBox.question(
            self, "Profil Sil",
            f"{profile_name} profilini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Profili sil
        success = self.device_manager.delete_profile(profile_name)
        if success:
            # Profil listesini güncelle
            self._load_profiles()
            
            self.status_label.setText(f"Profil silindi: {profile_name}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Hata: Profil silinemedi")
            self.status_label.setStyleSheet("color: red;")
    
    def _import_profile(self):
        """Profil içe aktar"""
        # Dosya seç
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Profil İçe Aktar", "", "JSON Dosyaları (*.json);;Tüm Dosyalar (*)"
        )
        
        if not file_path:
            return
        
        # Profili içe aktar
        success = self.device_manager.import_profile(file_path)
        if success:
            # Profil listesini güncelle
            self._load_profiles()
            
            self.status_label.setText("Profil içe aktarıldı")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Hata: Profil içe aktarılamadı")
            self.status_label.setStyleSheet("color: red;")
    
    def _export_profile(self):
        """Profil dışa aktar"""
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return
        
        # Dosya seç
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Profil Dışa Aktar", f"{profile_name}.json", "JSON Dosyaları (*.json);;Tüm Dosyalar (*)"
        )
        
        if not file_path:
            return
        
        # Profili dışa aktar
        success = self.device_manager.export_profile(profile_name, file_path)
        if success:
            self.status_label.setText(f"Profil dışa aktarıldı: {file_path}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Hata: Profil dışa aktarılamadı")
            self.status_label.setStyleSheet("color: red;")
    
    def _create_random_profile(self):
        """Rastgele profil oluştur"""
        profile_name = self.random_name.text()
        if not profile_name:
            profile_name = "Rastgele Profil"
        
        # Profil adının benzersiz olduğunu kontrol et
        if self.device_manager.get_profile(profile_name):
            # Benzersiz ad oluştur
            original_name = profile_name
            counter = 1
            while self.device_manager.get_profile(profile_name):
                profile_name = f"{original_name} ({counter})"
                counter += 1
        
        # Rastgele profil oluştur
        profile = self.device_manager.generate_random_profile(profile_name)
        
        # Profili kaydet
        success = self.device_manager.create_profile(profile)
        if success:
            # Profil listesini güncelle
            self._load_profiles()
            
            # Yeni profili seç
            index = self.profile_combo.findText(profile_name)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
            
            self.status_label.setText(f"Rastgele profil oluşturuldu: {profile_name}")
            self.status_label.setStyleSheet("color: green;")
            
            # Profil adını sıfırla
            self.random_name.setText("Rastgele Profil")
        else:
            self.status_label.setText("Hata: Rastgele profil oluşturulamadı")
            self.status_label.setStyleSheet("color: red;")
    
    def _apply_changes(self):
        """Değişiklikleri uygula"""
        # Aktif profili al
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            QMessageBox.warning(self, "Hata", "Lütfen bir profil seçin.")
            return
        
        # Gerçek değişiklikleri uygula
        result = self.device_manager.apply_profile_changes(profile_name)
        
        if not result["admin_rights"]:
            QMessageBox.warning(
                self, "Yönetici Hakları Gerekli",
                "Sistem bilgilerini değiştirmek için uygulamayı yönetici olarak çalıştırmanız gerekmektedir."
            )
            return
        
        if result["success"]:
            changes_text = "\n- " + "\n- ".join(result["changes"])
            QMessageBox.information(
                self, "Başarılı",
                f"{profile_name} profili başarıyla uygulandı.\n\n"
                f"Yapılan değişiklikler:{changes_text}\n\n"
                "Değişikliklerin tam olarak etkinleşmesi için bilgisayarınızı yeniden başlatmanız gerekebilir."
            )
            self.status_label.setText(f"Profil uygulandı: {profile_name}")
            self.status_label.setStyleSheet("color: green;")
        else:
            errors_text = "\n- " + "\n- ".join(result["errors"])
            if result["changes"]:
                changes_text = "\n- " + "\n- ".join(result["changes"])
                errors_text += f"\n\nBaşarılı değişiklikler:{changes_text}"
            
            QMessageBox.warning(
                self, "Hata",
                f"{profile_name} profili uygulanırken bazı hatalar oluştu.\n\n"
                f"Hatalar:{errors_text}"
            )
            self.status_label.setText(f"Profil kısmen uygulandı: {profile_name}")
            self.status_label.setStyleSheet("color: orange;")
    
    def _reset_to_original(self):
        """Sistem bilgilerini orijinal haline döndür"""
        # Kullanıcıya onay sor
        reply = QMessageBox.question(
            self, "Sistemi Sıfırla",
            "Bu işlem, tüm sistem bilgilerini orijinal haline döndürecektir. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Orijinal sistem bilgilerine dönüş işlemini başlat
        result = self.device_manager.restore_original_system_info()
        
        if not result["admin_rights"]:
            QMessageBox.warning(
                self, "Yönetici Hakları Gerekli",
                "Sistem bilgilerini orijinal haline döndürmek için uygulamayı yönetici olarak çalıştırmanız gerekmektedir."
            )
            return
        
        if result["success"]:
            changes_text = "\n- " + "\n- ".join(result["changes"])
            QMessageBox.information(
                self, "Başarılı",
                f"Sistem bilgileri başarıyla orijinal haline döndürüldü.\n\n"
                f"Yapılan değişiklikler:{changes_text}\n\n"
                "Değişikliklerin tam olarak etkinleşmesi için bilgisayarınızı yeniden başlatmanız gerekebilir."
            )
            self.status_label.setText("Sistem bilgileri orijinal haline döndürüldü")
            self.status_label.setStyleSheet("color: green;")
            
            # Gerçek bilgileri yenile
            self._refresh_real_info()
        else:
            errors_text = "\n- " + "\n- ".join(result["errors"])
            if result["changes"]:
                changes_text = "\n- " + "\n- ".join(result["changes"])
                errors_text += f"\n\nBaşarılı değişiklikler:{changes_text}"
            
            QMessageBox.warning(
                self, "Hata",
                f"Sistem bilgileri orijinal haline döndürülürken bazı hatalar oluştu.\n\n"
                f"Hatalar:{errors_text}"
            )
            self.status_label.setText("Sistem bilgileri kısmen orijinal haline döndürüldü")
            self.status_label.setStyleSheet("color: orange;")
    
    def closeEvent(self, event):
        """Pencere kapatıldığında çağrılır"""
        # Ayarları kaydet
        self.settings.sync()
        event.accept()