#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import random
import base64
import platform
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QTabWidget, 
                             QLineEdit, QCheckBox, QSpinBox, QSlider, QGroupBox, 
                             QFormLayout, QMessageBox, QFileDialog, QTextEdit, 
                             QScrollArea, QSizePolicy, QFrame, QListWidget, 
                             QListWidgetItem, QMenu, QAction, QToolBar, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings

from modules.error_logger import ErrorLogger
from modules.fingerprint_settings import FingerprintSettings

class FingerprintController(QMainWindow):
    def __init__(self, base_dir=None):
        super().__init__()
        
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.base_dir = base_dir
        self.logger = ErrorLogger(base_dir)
        self.settings = FingerprintSettings(base_dir)
        
        # Aktif profili yükle
        self.active_profile = self.settings.get_profile()
        
        # Arayüz öğelerini başlat
        self.init_ui()
        
        # Önizleme tarayıcısını başlat
        self.init_preview_browser()
        
        # Otomatik değiştirme zamanlayıcısını başlat
        self.change_timer = QTimer()
        self.change_timer.timeout.connect(self.auto_change_fingerprint)
        self.set_auto_change_interval()
        
        self.logger.log_info("Parmak İzi Kontrolcüsü başlatıldı")
        
    def init_ui(self):
        """Ana kullanıcı arayüzünü oluştur"""
        self.setWindowTitle("Tarayıcı Parmak İzi Gizleme Aracı")
        self.setMinimumSize(1000, 700)
        
        # Ana widget ve düzen
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Sol panel (kontrol paneli)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_panel.setMaximumWidth(400)
        
        # Profil seçici
        self.profile_group = QGroupBox("Profil Yönetimi")
        self.profile_layout = QVBoxLayout()
        
        self.profile_selector_layout = QHBoxLayout()
        self.profile_label = QLabel("Aktif Profil:")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.settings.get_all_profiles().keys())
        self.profile_combo.setCurrentText(self.settings.get_setting("active_profile"))
        self.profile_combo.currentTextChanged.connect(self.change_profile)
        
        self.profile_selector_layout.addWidget(self.profile_label)
        self.profile_selector_layout.addWidget(self.profile_combo)
        
        self.profile_buttons_layout = QHBoxLayout()
        self.new_profile_btn = QPushButton("Yeni")
        self.new_profile_btn.clicked.connect(self.create_new_profile)
        self.save_profile_btn = QPushButton("Kaydet")
        self.save_profile_btn.clicked.connect(self.save_current_profile)
        self.delete_profile_btn = QPushButton("Sil")
        self.delete_profile_btn.clicked.connect(self.delete_current_profile)
        
        self.profile_buttons_layout.addWidget(self.new_profile_btn)
        self.profile_buttons_layout.addWidget(self.save_profile_btn)
        self.profile_buttons_layout.addWidget(self.delete_profile_btn)
        
        self.profile_layout.addLayout(self.profile_selector_layout)
        self.profile_layout.addLayout(self.profile_buttons_layout)
        self.profile_group.setLayout(self.profile_layout)
        
        # Parmak izi ayarları sekmesi
        self.settings_tabs = QTabWidget()
        
        # Temel ayarlar sekmesi
        self.basic_tab = QWidget()
        self.basic_layout = QFormLayout(self.basic_tab)
        
        # User Agent
        self.user_agent_label = QLabel("User Agent:")
        self.user_agent_input = QLineEdit(self.active_profile["user_agent"])
        self.user_agent_input.textChanged.connect(lambda: self.update_profile_setting("user_agent"))
        self.basic_layout.addRow(self.user_agent_label, self.user_agent_input)
        
        # Platform
        self.platform_label = QLabel("Platform:")
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Win32", "MacIntel", "Linux x86_64", "Linux i686", "iPhone", "iPad", "Android"])
        self.platform_combo.setCurrentText(self.active_profile["platform"])
        self.platform_combo.currentTextChanged.connect(lambda: self.update_profile_setting("platform"))
        self.basic_layout.addRow(self.platform_label, self.platform_combo)
        
        # Vendor
        self.vendor_label = QLabel("Vendor:")
        self.vendor_input = QLineEdit(self.active_profile["vendor"])
        self.vendor_input.textChanged.connect(lambda: self.update_profile_setting("vendor"))
        self.basic_layout.addRow(self.vendor_label, self.vendor_input)
        
        # Do Not Track
        self.dnt_checkbox = QCheckBox("Do Not Track")
        self.dnt_checkbox.setChecked(self.active_profile["do_not_track"])
        self.dnt_checkbox.stateChanged.connect(lambda: self.update_profile_setting("do_not_track"))
        self.basic_layout.addRow("", self.dnt_checkbox)
        
        # Hardware Concurrency
        self.concurrency_label = QLabel("CPU Çekirdek Sayısı:")
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 32)
        self.concurrency_spin.setValue(self.active_profile["hardware_concurrency"])
        self.concurrency_spin.valueChanged.connect(lambda: self.update_profile_setting("hardware_concurrency"))
        self.basic_layout.addRow(self.concurrency_label, self.concurrency_spin)
        
        # Device Memory
        self.memory_label = QLabel("Cihaz Belleği (GB):")
        self.memory_combo = QComboBox()
        self.memory_combo.addItems(["0.25", "0.5", "1", "2", "4", "8", "16", "32"])
        self.memory_combo.setCurrentText(str(self.active_profile["device_memory"]))
        self.memory_combo.currentTextChanged.connect(lambda: self.update_profile_setting("device_memory"))
        self.basic_layout.addRow(self.memory_label, self.memory_combo)
        
        # Ekran çözünürlüğü
        self.resolution_label = QLabel("Ekran Çözünürlüğü:")
        self.resolution_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 3840)
        self.width_spin.setValue(self.active_profile["screen_resolution"]["width"])
        self.width_spin.valueChanged.connect(lambda: self.update_resolution())
        
        self.resolution_x_label = QLabel("x")
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 2160)
        self.height_spin.setValue(self.active_profile["screen_resolution"]["height"])
        self.height_spin.valueChanged.connect(lambda: self.update_resolution())
        
        self.resolution_layout.addWidget(self.width_spin)
        self.resolution_layout.addWidget(self.resolution_x_label)
        self.resolution_layout.addWidget(self.height_spin)
        
        self.resolution_widget = QWidget()
        self.resolution_widget.setLayout(self.resolution_layout)
        self.basic_layout.addRow(self.resolution_label, self.resolution_widget)
        
        # Renk derinliği
        self.color_depth_label = QLabel("Renk Derinliği:")
        self.color_depth_combo = QComboBox()
        self.color_depth_combo.addItems(["16", "24", "32", "48"])
        self.color_depth_combo.setCurrentText(str(self.active_profile["color_depth"]))
        self.color_depth_combo.currentTextChanged.connect(lambda: self.update_profile_setting("color_depth"))
        self.basic_layout.addRow(self.color_depth_label, self.color_depth_combo)
        
        # Saat dilimi
        self.timezone_label = QLabel("Saat Dilimi Ofseti:")
        self.timezone_spin = QSpinBox()
        self.timezone_spin.setRange(-720, 720)
        self.timezone_spin.setValue(self.active_profile["timezone_offset"])
        self.timezone_spin.valueChanged.connect(lambda: self.update_profile_setting("timezone_offset"))
        self.basic_layout.addRow(self.timezone_label, self.timezone_spin)
        
        # Gelişmiş ayarlar sekmesi
        self.advanced_tab = QWidget()
        self.advanced_layout = QFormLayout(self.advanced_tab)
        
        # Depolama ayarları
        self.storage_group = QGroupBox("Depolama Ayarları")
        self.storage_layout = QVBoxLayout()
        
        self.session_storage_check = QCheckBox("Session Storage")
        self.session_storage_check.setChecked(self.active_profile["session_storage"])
        self.session_storage_check.stateChanged.connect(lambda: self.update_profile_setting("session_storage"))
        
        self.local_storage_check = QCheckBox("Local Storage")
        self.local_storage_check.setChecked(self.active_profile["local_storage"])
        self.local_storage_check.stateChanged.connect(lambda: self.update_profile_setting("local_storage"))
        
        self.indexed_db_check = QCheckBox("IndexedDB")
        self.indexed_db_check.setChecked(self.active_profile["indexed_db"])
        self.indexed_db_check.stateChanged.connect(lambda: self.update_profile_setting("indexed_db"))
        
        self.cookies_check = QCheckBox("Çerezler")
        self.cookies_check.setChecked(self.active_profile["cookies"])
        self.cookies_check.stateChanged.connect(lambda: self.update_profile_setting("cookies"))
        
        self.storage_layout.addWidget(self.session_storage_check)
        self.storage_layout.addWidget(self.local_storage_check)
        self.storage_layout.addWidget(self.indexed_db_check)
        self.storage_layout.addWidget(self.cookies_check)
        self.storage_group.setLayout(self.storage_layout)
        
        self.advanced_layout.addRow(self.storage_group)
        
        # Parmak izi koruması
        self.fingerprint_group = QGroupBox("Parmak İzi Koruması")
        self.fingerprint_layout = QVBoxLayout()
        
        self.canvas_check = QCheckBox("Canvas Parmak İzi")
        self.canvas_check.setChecked(self.active_profile["canvas_fingerprint"])
        self.canvas_check.stateChanged.connect(lambda: self.update_profile_setting("canvas_fingerprint"))
        
        self.audio_check = QCheckBox("Ses Parmak İzi")
        self.audio_check.setChecked(self.active_profile["audio_fingerprint"])
        self.audio_check.stateChanged.connect(lambda: self.update_profile_setting("audio_fingerprint"))
        
        self.webgl_check = QCheckBox("WebGL Parmak İzi")
        self.webgl_check.setChecked(self.active_profile["webgl_fingerprint"])
        self.webgl_check.stateChanged.connect(lambda: self.update_profile_setting("webgl_fingerprint"))
        
        self.fingerprint_layout.addWidget(self.canvas_check)
        self.fingerprint_layout.addWidget(self.audio_check)
        self.fingerprint_layout.addWidget(self.webgl_check)
        self.fingerprint_group.setLayout(self.fingerprint_layout)
        
        self.advanced_layout.addRow(self.fingerprint_group)
        
        # Fontlar
        self.fonts_group = QGroupBox("Fontlar")
        self.fonts_layout = QVBoxLayout()
        
        self.fonts_list = QListWidget()
        for font in self.active_profile["fonts"]:
            self.fonts_list.addItem(font)
        
        self.fonts_buttons_layout = QHBoxLayout()
        self.add_font_btn = QPushButton("Ekle")
        self.add_font_btn.clicked.connect(self.add_font)
        self.remove_font_btn = QPushButton("Kaldır")
        self.remove_font_btn.clicked.connect(self.remove_font)
        
        self.fonts_buttons_layout.addWidget(self.add_font_btn)
        self.fonts_buttons_layout.addWidget(self.remove_font_btn)
        
        self.fonts_layout.addWidget(self.fonts_list)
        self.fonts_layout.addLayout(self.fonts_buttons_layout)
        self.fonts_group.setLayout(self.fonts_layout)
        
        self.advanced_layout.addRow(self.fonts_group)
        
        # Ayarlar sekmesi
        self.config_tab = QWidget()
        self.config_layout = QFormLayout(self.config_tab)
        
        # Otomatik değiştirme aralığı
        self.auto_change_label = QLabel("Otomatik Değiştirme Aralığı (dakika):")
        self.auto_change_spin = QSpinBox()
        self.auto_change_spin.setRange(0, 1440)  # 0 - 24 saat
        self.auto_change_spin.setValue(self.settings.get_setting("auto_change_interval"))
        self.auto_change_spin.valueChanged.connect(self.set_auto_change_interval)
        self.config_layout.addRow(self.auto_change_label, self.auto_change_spin)
        
        # Başlangıç profili
        self.startup_profile_label = QLabel("Başlangıç Profili:")
        self.startup_profile_combo = QComboBox()
        self.startup_profile_combo.addItems(self.settings.get_all_profiles().keys())
        self.startup_profile_combo.setCurrentText(self.settings.get_setting("startup_profile"))
        self.startup_profile_combo.currentTextChanged.connect(lambda text: self.settings.update_setting("startup_profile", text))
        self.config_layout.addRow(self.startup_profile_label, self.startup_profile_combo)
        
        # Tema
        self.theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.settings.get_setting("theme"))
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.config_layout.addRow(self.theme_label, self.theme_combo)
        
        # Sekmeleri ekle
        self.settings_tabs.addTab(self.basic_tab, "Temel Ayarlar")
        self.settings_tabs.addTab(self.advanced_tab, "Gelişmiş Ayarlar")
        self.settings_tabs.addTab(self.config_tab, "Uygulama Ayarları")
        
        # Butonlar
        self.buttons_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Uygula")
        self.apply_btn.clicked.connect(self.apply_fingerprint)
        
        self.random_btn = QPushButton("Rastgele")
        self.random_btn.clicked.connect(self.randomize_fingerprint)
        
        self.export_btn = QPushButton("Dışa Aktar")
        self.export_btn.clicked.connect(self.export_profile)
        
        self.import_btn = QPushButton("İçe Aktar")
        self.import_btn.clicked.connect(self.import_profile)
        
        self.buttons_layout.addWidget(self.apply_btn)
        self.buttons_layout.addWidget(self.random_btn)
        self.buttons_layout.addWidget(self.export_btn)
        self.buttons_layout.addWidget(self.import_btn)
        
        # Sol paneli tamamla
        self.left_layout.addWidget(self.profile_group)
        self.left_layout.addWidget(self.settings_tabs)
        self.left_layout.addLayout(self.buttons_layout)
        
        # Sağ panel (önizleme)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.preview_label = QLabel("Parmak İzi Önizleme")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.preview_url_layout = QHBoxLayout()
        self.preview_url_label = QLabel("URL:")
        self.preview_url_input = QLineEdit("https://amiunique.org/fp")
        self.preview_url_btn = QPushButton("Git")
        self.preview_url_btn.clicked.connect(self.navigate_preview)
        
        self.preview_url_layout.addWidget(self.preview_url_label)
        self.preview_url_layout.addWidget(self.preview_url_input)
        self.preview_url_layout.addWidget(self.preview_url_btn)
        
        self.preview_url_widget = QWidget()
        self.preview_url_widget.setLayout(self.preview_url_layout)
        
        self.preview_browser_container = QWidget()
        self.preview_browser_layout = QVBoxLayout(self.preview_browser_container)
        
        # Sağ paneli tamamla
        self.right_layout.addWidget(self.preview_label)
        self.right_layout.addWidget(self.preview_url_widget)
        self.right_layout.addWidget(self.preview_browser_container)
        
        # Ana düzeni tamamla
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.right_panel)
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # Temayı uygula
        self.apply_theme()
        
    def init_preview_browser(self):
        """Önizleme tarayıcısını başlat"""
        # Tarayıcı profilini oluştur
        self.browser_profile = QWebEngineProfile("FingerprintPreview", self)
        
        # Tarayıcı sayfasını oluştur
        self.browser_page = QWebEnginePage(self.browser_profile, self)
        
        # JavaScript'i etkinleştir
        self.browser_page.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        
        # Tarayıcı görünümünü oluştur
        self.preview_browser = QWebEngineView()
        self.preview_browser.setPage(self.browser_page)
        
        # Tarayıcıyı düzene ekle
        self.preview_browser_layout.addWidget(self.preview_browser)
        
        # Varsayılan URL'ye git
        self.navigate_preview()
        
    def navigate_preview(self):
        """Önizleme tarayıcısında belirtilen URL'ye git"""
        url = self.preview_url_input.text()
        if not url.startswith("http"):
            url = "https://" + url
            self.preview_url_input.setText(url)
            
        self.preview_browser.load(QUrl(url))
        self.status_bar.showMessage(f"Yükleniyor: {url}")
        
    def change_profile(self, profile_name):
        """Aktif profili değiştir"""
        self.active_profile = self.settings.get_profile(profile_name)
        self.settings.set_active_profile(profile_name)
        self.update_ui_from_profile()
        self.status_bar.showMessage(f"Profil değiştirildi: {profile_name}")
        
    def update_ui_from_profile(self):
        """UI öğelerini aktif profile göre güncelle"""
        # Temel ayarlar
        self.user_agent_input.setText(self.active_profile["user_agent"])
        self.platform_combo.setCurrentText(self.active_profile["platform"])
        self.vendor_input.setText(self.active_profile["vendor"])
        self.dnt_checkbox.setChecked(self.active_profile["do_not_track"])
        self.concurrency_spin.setValue(self.active_profile["hardware_concurrency"])
        self.memory_combo.setCurrentText(str(self.active_profile["device_memory"]))
        self.width_spin.setValue(self.active_profile["screen_resolution"]["width"])
        self.height_spin.setValue(self.active_profile["screen_resolution"]["height"])
        self.color_depth_combo.setCurrentText(str(self.active_profile["color_depth"]))
        self.timezone_spin.setValue(self.active_profile["timezone_offset"])
        
        # Gelişmiş ayarlar
        self.session_storage_check.setChecked(self.active_profile["session_storage"])
        self.local_storage_check.setChecked(self.active_profile["local_storage"])
        self.indexed_db_check.setChecked(self.active_profile["indexed_db"])
        self.cookies_check.setChecked(self.active_profile["cookies"])
        self.canvas_check.setChecked(self.active_profile["canvas_fingerprint"])
        self.audio_check.setChecked(self.active_profile["audio_fingerprint"])
        self.webgl_check.setChecked(self.active_profile["webgl_fingerprint"])
        
        # Fontlar
        self.fonts_list.clear()
        for font in self.active_profile["fonts"]:
            self.fonts_list.addItem(font)
            
    def update_profile_setting(self, setting_name):
        """Profil ayarını güncelle"""
        if setting_name == "user_agent":
            self.active_profile[setting_name] = self.user_agent_input.text()
        elif setting_name == "platform":
            self.active_profile[setting_name] = self.platform_combo.currentText()
        elif setting_name == "vendor":
            self.active_profile[setting_name] = self.vendor_input.text()
        elif setting_name == "do_not_track":
            self.active_profile[setting_name] = self.dnt_checkbox.isChecked()
        elif setting_name == "hardware_concurrency":
            self.active_profile[setting_name] = self.concurrency_spin.value()
        elif setting_name == "device_memory":
            self.active_profile[setting_name] = float(self.memory_combo.currentText())
        elif setting_name == "color_depth":
            self.active_profile[setting_name] = int(self.color_depth_combo.currentText())
        elif setting_name == "timezone_offset":
            self.active_profile[setting_name] = self.timezone_spin.value()
        elif setting_name == "session_storage":
            self.active_profile[setting_name] = self.session_storage_check.isChecked()
        elif setting_name == "local_storage":
            self.active_profile[setting_name] = self.local_storage_check.isChecked()
        elif setting_name == "indexed_db":
            self.active_profile[setting_name] = self.indexed_db_check.isChecked()
        elif setting_name == "cookies":
            self.active_profile[setting_name] = self.cookies_check.isChecked()
        elif setting_name == "canvas_fingerprint":
            self.active_profile[setting_name] = self.canvas_check.isChecked()
        elif setting_name == "audio_fingerprint":
            self.active_profile[setting_name] = self.audio_check.isChecked()
        elif setting_name == "webgl_fingerprint":
            self.active_profile[setting_name] = self.webgl_check.isChecked()
            
    def update_resolution(self):
        """Ekran çözünürlüğü ayarını güncelle"""
        self.active_profile["screen_resolution"]["width"] = self.width_spin.value()
        self.active_profile["screen_resolution"]["height"] = self.height_spin.value()
        
    def create_new_profile(self):
        """Yeni profil oluştur"""
        profile_name, ok = QInputDialog.getText(self, "Yeni Profil", "Profil Adı:")
        
        if ok and profile_name:
            if profile_name in self.settings.get_all_profiles():
                QMessageBox.warning(self, "Hata", f"'{profile_name}' adında bir profil zaten var.")
                return
                
            # Mevcut profili kopyala
            new_profile = self.active_profile.copy()
            
            # Yeni profili oluştur
            if self.settings.create_profile(profile_name, new_profile):
                self.profile_combo.addItem(profile_name)
                self.profile_combo.setCurrentText(profile_name)
                self.startup_profile_combo.addItem(profile_name)
                self.status_bar.showMessage(f"Yeni profil oluşturuldu: {profile_name}")
            else:
                QMessageBox.warning(self, "Hata", "Profil oluşturulurken bir hata oluştu.")
                
    def save_current_profile(self):
        """Mevcut profili kaydet"""
        profile_name = self.profile_combo.currentText()
        
        if self.settings.update_profile(profile_name, self.active_profile):
            self.status_bar.showMessage(f"Profil kaydedildi: {profile_name}")
        else:
            QMessageBox.warning(self, "Hata", "Profil kaydedilirken bir hata oluştu.")
            
    def delete_current_profile(self):
        """Mevcut profili sil"""
        profile_name = self.profile_combo.currentText()
        
        if profile_name == "default":
            QMessageBox.warning(self, "Hata", "Varsayılan profil silinemez.")
            return
            
        reply = QMessageBox.question(self, "Profil Sil", 
                                    f"'{profile_name}' profilini silmek istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    
        if reply == QMessageBox.Yes:
            if self.settings.delete_profile(profile_name):
                current_index = self.profile_combo.currentIndex()
                self.profile_combo.removeItem(current_index)
                
                startup_index = self.startup_profile_combo.findText(profile_name)
                if startup_index >= 0:
                    self.startup_profile_combo.removeItem(startup_index)
                    
                self.status_bar.showMessage(f"Profil silindi: {profile_name}")
            else:
                QMessageBox.warning(self, "Hata", "Profil silinirken bir hata oluştu.")
                
    def add_font(self):
        """Font listesine yeni font ekle"""
        font_name, ok = QInputDialog.getText(self, "Font Ekle", "Font Adı:")
        
        if ok and font_name:
            if font_name not in self.active_profile["fonts"]:
                self.active_profile["fonts"].append(font_name)
                self.fonts_list.addItem(font_name)
                self.status_bar.showMessage(f"Font eklendi: {font_name}")
                
    def remove_font(self):
        """Seçili fontu listeden kaldır"""
        selected_items = self.fonts_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Hata", "Lütfen kaldırılacak bir font seçin.")
            return
            
        for item in selected_items:
            font_name = item.text()
            if font_name in self.active_profile["fonts"]:
                self.active_profile["fonts"].remove(font_name)
                self.fonts_list.takeItem(self.fonts_list.row(item))
                self.status_bar.showMessage(f"Font kaldırıldı: {font_name}")
                
    def set_auto_change_interval(self):
        """Otomatik değiştirme aralığını ayarla"""
        interval = self.auto_change_spin.value()
        self.settings.update_setting("auto_change_interval", interval)
        
        # Zamanlayıcıyı durdur
        self.change_timer.stop()
        
        # Eğer aralık 0'dan büyükse zamanlayıcıyı başlat
        if interval > 0:
            # Dakikayı milisaniyeye çevir
            ms_interval = interval * 60 * 1000
            self.change_timer.start(ms_interval)
            self.status_bar.showMessage(f"Otomatik değiştirme etkinleştirildi: {interval} dakika")
        else:
            self.status_bar.showMessage("Otomatik değiştirme devre dışı")
            
    def auto_change_fingerprint(self):
        """Otomatik olarak parmak izini değiştir"""
        self.randomize_fingerprint()
        self.apply_fingerprint()
        
    def change_theme(self, theme_name):
        """Uygulama temasını değiştir"""
        self.settings.update_setting("theme", theme_name)
        self.apply_theme()
        
    def apply_theme(self):
        """Seçili temayı uygula"""
        theme = self.settings.get_setting("theme")
        
        if theme == "dark":
            # Koyu tema
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)
        else:
            # Açık tema (varsayılan)
            self.setPalette(self.style().standardPalette())
            
        self.status_bar.showMessage(f"Tema değiştirildi: {theme}")
        
    def apply_fingerprint(self):
        """Parmak izi ayarlarını uygula ve önizlemeyi güncelle"""
        # Mevcut profili kaydet
        self.save_current_profile()
        
        # JavaScript kodunu oluştur
        js_code = self.generate_fingerprint_js()
        
        # JavaScript kodunu tarayıcıda çalıştır
        self.preview_browser.page().runJavaScript(js_code, self.on_js_executed)
        
        # Sayfayı yenile
        self.preview_browser.reload()
        
        self.status_bar.showMessage("Parmak izi ayarları uygulandı")
        
    def randomize_fingerprint(self):
        """Rastgele parmak izi oluştur"""
        # Rastgele user agent seç
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        ]
        self.user_agent_input.setText(random.choice(user_agents))
        
        # Rastgele platform seç
        platforms = ["Win32", "MacIntel", "Linux x86_64", "Linux i686"]
        self.platform_combo.setCurrentText(random.choice(platforms))
        
        # Rastgele vendor seç
        vendors = ["Google Inc.", "Apple Computer, Inc.", "Mozilla Foundation"]
        self.vendor_input.setText(random.choice(vendors))
        
        # Rastgele DNT seç
        self.dnt_checkbox.setChecked(random.choice([True, False]))
        
        # Rastgele CPU çekirdek sayısı
        self.concurrency_spin.setValue(random.choice([2, 4, 8, 16]))
        
        # Rastgele bellek
        memories = ["0.5", "1", "2", "4", "8"]
        self.memory_combo.setCurrentText(random.choice(memories))
        
        # Rastgele çözünürlük
        resolutions = [(1366, 768), (1920, 1080), (2560, 1440), (1440, 900)]
        width, height = random.choice(resolutions)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        
        # Rastgele renk derinliği
        self.color_depth_combo.setCurrentText(random.choice(["24", "32"]))
        
        # Rastgele saat dilimi
        self.timezone_spin.setValue(random.randint(-720, 720))
        
        # Rastgele depolama ayarları
        self.session_storage_check.setChecked(random.choice([True, False]))
        self.local_storage_check.setChecked(random.choice([True, False]))
        self.indexed_db_check.setChecked(random.choice([True, False]))
        self.cookies_check.setChecked(random.choice([True, False]))
        
        # Rastgele parmak izi koruması
        self.canvas_check.setChecked(random.choice([True, False]))
        self.audio_check.setChecked(random.choice([True, False]))
        self.webgl_check.setChecked(random.choice([True, False]))
        
        # Tüm ayarları profile güncelle
        self.update_profile_setting("user_agent")
        self.update_profile_setting("platform")
        self.update_profile_setting("vendor")
        self.update_profile_setting("do_not_track")
        self.update_profile_setting("hardware_concurrency")
        self.update_profile_setting("device_memory")
        self.update_resolution()
        self.update_profile_setting("color_depth")
        self.update_profile_setting("timezone_offset")
        self.update_profile_setting("session_storage")
        self.update_profile_setting("local_storage")
        self.update_profile_setting("indexed_db")
        self.update_profile_setting("cookies")
        self.update_profile_setting("canvas_fingerprint")
        self.update_profile_setting("audio_fingerprint")
        self.update_profile_setting("webgl_fingerprint")
        
        self.status_bar.showMessage("Rastgele parmak izi oluşturuldu")
        
    def on_js_executed(self, result):
        """JavaScript kodu çalıştırıldıktan sonra çağrılır"""
        if result:
            self.logger.log_info(f"JavaScript kodu çalıştırıldı: {result}")
        
    def export_profile(self):
        """Aktif profili dışa aktar"""
        import json
        import os
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Profili Dışa Aktar", 
            os.path.expanduser("~") + "/profile.json", 
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                # Profili JSON olarak kaydet
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.active_profile, f, ensure_ascii=False, indent=4)
                self.logger.log_info(f"Profil dışa aktarıldı: {file_path}")
                self.status_bar.showMessage(f"Profil başarıyla dışa aktarıldı: {file_path}")
            except Exception as e:
                self.logger.log_error(f"Profil dışa aktarma hatası: {str(e)}")
                self.status_bar.showMessage("Profil dışa aktarma hatası!")
                
    def import_profile(self):
        """Profil içe aktar"""
        import json
        import os
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Profil İçe Aktar", 
            os.path.expanduser("~"), 
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                # JSON dosyasını oku
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                # Gerekli alanları kontrol et
                required_fields = ["name", "user_agent", "platform", "vendor"]
                for field in required_fields:
                    if field not in profile_data:
                        raise ValueError(f"Geçersiz profil dosyası: {field} alanı eksik")
                
                # Profil adını kontrol et ve gerekirse değiştir
                original_name = profile_data["name"]
                profile_name = original_name
                counter = 1
                
                while profile_name in self.settings.get_profile_names():
                    profile_name = f"{original_name} ({counter})"
                    counter += 1
                
                if profile_name != original_name:
                    profile_data["name"] = profile_name
                    QMessageBox.information(
                        self, "Profil Adı Değiştirildi",
                        f"Bu isimde bir profil zaten var. Yeni profil adı: {profile_name}"
                    )
                
                # Profili kaydet ve uygula
                self.settings.create_profile(profile_data)
                self.settings.set_active_profile(profile_name)
                self.active_profile = profile_data
                self.load_profile_to_ui()
                self.apply_fingerprint()
                
                self.logger.log_info(f"Profil içe aktarıldı: {profile_name}")
                self.status_bar.showMessage(f"Profil başarıyla içe aktarıldı: {profile_name}")
                
            except Exception as e:
                self.logger.log_error(f"Profil içe aktarma hatası: {str(e)}")
                self.status_bar.showMessage("Profil içe aktarma hatası!")
                QMessageBox.critical(self, "İçe Aktarma Hatası", f"Profil içe aktarılamadı: {str(e)}")
        
    def generate_fingerprint_js(self):
        """Parmak izi değiştirme için JavaScript kodu oluştur"""
        profile = self.active_profile
        
        js_code = "(function() {\n"
        js_code += "    // Tarayıcı parmak izi değiştirme\n"
        js_code += "    try {\n"
        js_code += "        // Navigator özellikleri\n"
        js_code += f"        Object.defineProperty(navigator, 'userAgent', {{value: '{profile['user_agent']}', writable: false}});\n"
        js_code += f"        Object.defineProperty(navigator, 'platform', {{value: '{profile['platform']}', writable: false}});\n"
        js_code += f"        Object.defineProperty(navigator, 'vendor', {{value: '{profile['vendor']}', writable: false}});\n"
        js_code += f"        Object.defineProperty(navigator, 'doNotTrack', {{value: '{'1' if profile['do_not_track'] else '0'}', writable: false}});\n"
        js_code += f"        Object.defineProperty(navigator, 'hardwareConcurrency', {{value: {profile['hardware_concurrency']}, writable: false}});\n"
        js_code += f"        Object.defineProperty(navigator, 'deviceMemory', {{value: {profile['device_memory']}, writable: false}});\n\n"
        
        js_code += "        // Dil ayarları\n"
        js_code += f"        Object.defineProperty(navigator, 'languages', {{value: {json.dumps(profile['languages'])}, writable: false}});\n\n"
        
        js_code += "        // Ekran özellikleri\n"
        js_code += "        if (window.screen) {\n"
        js_code += f"            Object.defineProperty(screen, 'width', {{value: {profile['screen_resolution']['width']}, writable: false}});\n"
        js_code += f"            Object.defineProperty(screen, 'height', {{value: {profile['screen_resolution']['height']}, writable: false}});\n"
        js_code += f"            Object.defineProperty(screen, 'colorDepth', {{value: {profile['color_depth']}, writable: false}});\n"
        js_code += f"            Object.defineProperty(screen, 'pixelDepth', {{value: {profile['color_depth']}, writable: false}});\n"
        js_code += "        }\n\n"
        
        js_code += "        // Saat dilimi\n"
        js_code += f"        Date.prototype.getTimezoneOffset = function() {{ return {profile['timezone_offset']}; }};\n\n"
        
        js_code += "        // Depolama özellikleri\n"
        js_code += f"        if (!{'true' if profile['session_storage'] else 'false'}) {{\n"
        js_code += "            Object.defineProperty(window, 'sessionStorage', {value: undefined, writable: false});\n"
        js_code += "        }\n"
        js_code += f"        if (!{'true' if profile['local_storage'] else 'false'}) {{\n"
        js_code += "            Object.defineProperty(window, 'localStorage', {value: undefined, writable: false});\n"
        js_code += "        }\n"
        js_code += f"        if (!{'true' if profile['indexed_db'] else 'false'}) {{\n"
        js_code += "            Object.defineProperty(window, 'indexedDB', {value: undefined, writable: false});\n"
        js_code += "        }\n\n"
        
        js_code += "        // Canvas parmak izi koruması\n"
        js_code += f"        if (!{'true' if profile['canvas_fingerprint'] else 'false'}) {{\n"
        js_code += "            const originalGetContext = HTMLCanvasElement.prototype.getContext;\n"
        js_code += "            HTMLCanvasElement.prototype.getContext = function(type, attributes) {\n"
        js_code += "                const context = originalGetContext.call(this, type, attributes);\n"
        js_code += "                if (context && (type === '2d' || type === 'webgl' || type === 'experimental-webgl')) {\n"
        js_code += "                    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;\n"
        js_code += "                    this.toDataURL = function() {\n"
        js_code += "                        return originalToDataURL.apply(this, arguments);\n"
        js_code += "                    };\n"
        js_code += "                    if (type === '2d') {\n"
        js_code += "                        const originalGetImageData = context.getImageData;\n"
        js_code += "                        context.getImageData = function() {\n"
        js_code += "                            return originalGetImageData.apply(this, arguments);\n"
        js_code += "                        };\n"
        js_code += "                    }\n"
        js_code += "                }\n"
        js_code += "                return context;\n"
        js_code += "            };\n"
        js_code += "        }\n\n"
        
        js_code += "        // Audio parmak izi koruması\n"
        js_code += f"        if (!{'true' if profile['audio_fingerprint'] else 'false'} && window.AudioContext) {{\n"
        js_code += "            const originalGetChannelData = AudioBuffer.prototype.getChannelData;\n"
        js_code += "            AudioBuffer.prototype.getChannelData = function(channel) {\n"
        js_code += "                const data = originalGetChannelData.call(this, channel);\n"
        js_code += "                return data;\n"
        js_code += "            };\n"
        js_code += "        }\n\n"
        
        js_code += "        // WebGL parmak izi koruması\n"
        js_code += f"        if (!{'true' if profile['webgl_fingerprint'] else 'false'} && window.WebGLRenderingContext) {{\n"
        js_code += "            const getParameterProxied = WebGLRenderingContext.prototype.getParameter;\n"
        js_code += "            WebGLRenderingContext.prototype.getParameter = function(parameter) {\n"
        js_code += "                return getParameterProxied.call(this, parameter);\n"
        js_code += "            };\n"
        js_code += "        }\n\n"
        
        js_code += "        // Font listesi\n"
        js_code += "        if (document.fonts && document.fonts.check) {\n"
        js_code += "            const originalCheck = document.fonts.check;\n"
        js_code += "            document.fonts.check = function(font) {\n"
        js_code += "                const fontFamily = font.split(' ').pop().replace(/['\",]/g, '');\n"
        js_code += f"                const allowedFonts = {json.dumps(profile['fonts'])};\n"
        js_code += "                return allowedFonts.includes(fontFamily) ? originalCheck.apply(this, arguments) : false;\n"
        js_code += "            };\n"
        js_code += "        }\n\n"
        
        js_code += "        console.log('Tarayıcı parmak izi değiştirildi');\n"
        js_code += "        return 'Parmak izi değiştirildi';\n"
        js_code += "    } catch (e) {\n"
        js_code += "        console.error('Parmak izi değiştirme hatası:', e);\n"
        js_code += "        return 'Hata: ' + e.message;\n"
        js_code += "    }\n"
        js_code += "})();"
        
        return js_code