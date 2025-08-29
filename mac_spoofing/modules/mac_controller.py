#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAC Adresi Kontrolcüsü

Bu modül, MAC adresi değiştirme işlemlerini yöneten kullanıcı arayüzünü sağlar.
Kullanıcıların MAC adreslerini görüntülemesine, değiştirmesine ve rastgele MAC adresi oluşturmasına olanak tanır.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QComboBox, QLineEdit, QPushButton, QGroupBox, 
    QMessageBox, QSplitter, QFrame, QStatusBar, QApplication
)
from PyQt5.QtCore import Qt, QSettings, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from .mac_manager import MACManager


class MACController(QMainWindow):
    """MAC adresi kontrolcüsü sınıfı"""
    
    def __init__(self, base_dir):
        """MAC adresi kontrolcüsünü başlat
        
        Args:
            base_dir (str): Uygulamanın temel dizini
        """
        super().__init__()
        
        # Temel dizini ayarla
        self.base_dir = base_dir
        
        # MAC yöneticisini başlat
        self.mac_manager = MACManager()
        
        # Ayarları yükle
        self.settings = QSettings(os.path.join(base_dir, "config", "settings.ini"), QSettings.IniFormat)
        
        # Arayüzü oluştur
        self._init_ui()
        
        # Ağ adaptörlerini yükle
        self._load_network_adapters()
        
        # Otomatik yenileme zamanlayıcısını başlat
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._load_network_adapters)
        self.refresh_timer.start(10000)  # 10 saniyede bir yenile
    
    def _init_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana pencere ayarları
        self.setWindowTitle("MAC Adresi Değiştirici")
        self.setMinimumSize(800, 500)
        
        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana düzen
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Başlık çubuğu
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Başlık etiketi
        title_label = QLabel("MAC Adresi Değiştirici")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        # Yönetici durumu etiketi
        admin_status = "Yönetici: Evet" if self.mac_manager.is_admin else "Yönetici: Hayır (Sınırlı Mod)"
        admin_color = "green" if self.mac_manager.is_admin else "red"
        self.admin_label = QLabel(admin_status)
        self.admin_label.setStyleSheet(f"color: {admin_color}; font-weight: bold;")
        title_layout.addWidget(self.admin_label, alignment=Qt.AlignRight)
        
        # Ana içerik alanı
        content_area = QSplitter(Qt.Horizontal)
        
        # Sol panel - Adaptör seçimi ve bilgileri
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Adaptör seçimi
        adapter_group = QGroupBox("Ağ Adaptörü Seçimi")
        adapter_layout = QVBoxLayout(adapter_group)
        
        # Adaptör açıklaması
        adapter_info = QLabel("Lütfen MAC adresini değiştirmek istediğiniz ağ adaptörünü seçin:")
        adapter_info.setWordWrap(True)
        adapter_layout.addWidget(adapter_info)
        
        # Adaptör seçim kutusu
        self.adapter_combo = QComboBox()
        self.adapter_combo.setMinimumHeight(30)
        self.adapter_combo.currentIndexChanged.connect(self._on_adapter_changed)
        adapter_layout.addWidget(self.adapter_combo)
        
        # Yenile butonu
        refresh_btn = QPushButton("Adaptörleri Yenile")
        refresh_btn.setMinimumHeight(30)
        refresh_btn.clicked.connect(self._load_network_adapters)
        adapter_layout.addWidget(refresh_btn)
        
        # Adaptör bilgileri
        adapter_info_group = QGroupBox("Adaptör Bilgileri")
        adapter_info_layout = QFormLayout(adapter_info_group)
        
        self.adapter_name_label = QLabel("")
        self.adapter_desc_label = QLabel("")
        self.adapter_mac_label = QLabel("")
        self.adapter_status_label = QLabel("")
        
        adapter_info_layout.addRow("Adaptör Adı:", self.adapter_name_label)
        adapter_info_layout.addRow("Açıklama:", self.adapter_desc_label)
        adapter_info_layout.addRow("MAC Adresi:", self.adapter_mac_label)
        adapter_info_layout.addRow("Durum:", self.adapter_status_label)
        
        # Sol panel düzeni
        left_layout.addWidget(adapter_group)
        left_layout.addWidget(adapter_info_group)
        left_layout.addStretch()
        
        # Sağ panel - MAC adresi değiştirme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # MAC adresi değiştirme grubu
        mac_change_group = QGroupBox("MAC Adresi Değiştirme")
        mac_change_layout = QVBoxLayout(mac_change_group)
        
        # MAC adresi giriş alanı
        mac_input_layout = QHBoxLayout()
        mac_input_layout.addWidget(QLabel("Yeni MAC Adresi:"))
        
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("XX:XX:XX:XX:XX:XX")
        self.mac_input.setMinimumHeight(30)
        mac_input_layout.addWidget(self.mac_input)
        
        # Rastgele MAC oluştur butonu
        random_mac_btn = QPushButton("Rastgele MAC")
        random_mac_btn.setMinimumHeight(30)
        random_mac_btn.clicked.connect(self._generate_random_mac)
        mac_input_layout.addWidget(random_mac_btn)
        
        mac_change_layout.addLayout(mac_input_layout)
        
        # MAC adresi değiştirme butonları
        mac_buttons_layout = QHBoxLayout()
        
        # MAC değiştir butonu
        change_mac_btn = QPushButton("MAC Adresini Değiştir")
        change_mac_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        change_mac_btn.setMinimumHeight(40)
        change_mac_btn.clicked.connect(self._change_mac_address)
        mac_buttons_layout.addWidget(change_mac_btn)
        
        # MAC sıfırla butonu
        reset_mac_btn = QPushButton("Orijinal MAC'e Döndür")
        reset_mac_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
        reset_mac_btn.setMinimumHeight(40)
        reset_mac_btn.clicked.connect(self._reset_mac_address)
        mac_buttons_layout.addWidget(reset_mac_btn)
        
        mac_change_layout.addLayout(mac_buttons_layout)
        
        # MAC formatı bilgisi
        mac_format_info = QLabel(
            "MAC adresi formatı: XX:XX:XX:XX:XX:XX (örn. 00:1A:2B:3C:4D:5E)\n"
            "Not: MAC adresi değişiklikleri için yönetici hakları gereklidir."
        )
        mac_format_info.setWordWrap(True)
        mac_format_info.setStyleSheet("color: #666; font-style: italic;")
        mac_change_layout.addWidget(mac_format_info)
        
        # MAC adresi hakkında bilgi
        mac_info_group = QGroupBox("MAC Adresi Hakkında")
        mac_info_layout = QVBoxLayout(mac_info_group)
        
        mac_info_text = QLabel(
            "MAC (Media Access Control) adresi, ağ donanımlarını benzersiz şekilde tanımlayan "
            "fiziksel bir adrestir. Bu adres, üreticiler tarafından donanıma atanır ve genellikle "
            "değiştirilemez olarak kabul edilir.\n\n"
            "Ancak, bazı durumlarda MAC adresini değiştirmek gerekebilir:\n"
            "- Gizlilik ve güvenlik için\n"
            "- Ağ erişim kontrollerini aşmak için\n"
            "- Ağ sorunlarını gidermek için\n\n"
            "Not: MAC adresini değiştirmek bazı ülkelerde yasal kısıtlamalara tabi olabilir. "
            "Lütfen bu aracı yalnızca yasal amaçlar için kullanın."
        )
        mac_info_text.setWordWrap(True)
        mac_info_layout.addWidget(mac_info_text)
        
        # Sağ panel düzeni
        right_layout.addWidget(mac_change_group)
        right_layout.addWidget(mac_info_group)
        right_layout.addStretch()
        
        # İçerik alanına panelleri ekle
        content_area.addWidget(left_panel)
        content_area.addWidget(right_panel)
        content_area.setStretchFactor(0, 1)  # Sol panel
        content_area.setStretchFactor(1, 2)  # Sağ panel
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("font-weight: bold;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # Ana düzene ekle
        main_layout.addWidget(title_bar)
        main_layout.addWidget(content_area)
    
    def _load_network_adapters(self):
        """Ağ adaptörlerini yükle"""
        try:
            # Mevcut seçimi hatırla
            current_adapter = self.adapter_combo.currentText() if self.adapter_combo.count() > 0 else ""
            
            # Adaptörleri temizle
            self.adapter_combo.clear()
            
            # Adaptörleri al
            adapters = self.mac_manager.get_network_adapters()
            
            # Adaptörleri ekle
            for adapter in adapters:
                self.adapter_combo.addItem(adapter["name"])
            
            # Önceki seçimi geri yükle
            if current_adapter:
                index = self.adapter_combo.findText(current_adapter)
                if index >= 0:
                    self.adapter_combo.setCurrentIndex(index)
            
            # Durum çubuğunu güncelle
            self.status_bar.showMessage(f"{len(adapters)} ağ adaptörü bulundu")
            
        except Exception as e:
            self.status_bar.showMessage(f"Hata: {str(e)}")
    
    def _on_adapter_changed(self):
        """Adaptör değiştiğinde çağrılır"""
        adapter_name = self.adapter_combo.currentText()
        if not adapter_name:
            return
        
        # Adaptör bilgilerini al
        adapters = self.mac_manager.get_network_adapters()
        for adapter in adapters:
            if adapter["name"] == adapter_name:
                # Adaptör bilgilerini göster
                self.adapter_name_label.setText(adapter["name"])
                self.adapter_desc_label.setText(adapter["description"])
                self.adapter_mac_label.setText(adapter["mac_address"])
                
                status_text = "Aktif" if adapter["is_up"] else "Devre Dışı"
                status_color = "green" if adapter["is_up"] else "red"
                self.adapter_status_label.setText(status_text)
                self.adapter_status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
                
                # MAC giriş alanını mevcut MAC ile doldur
                self.mac_input.setText(adapter["mac_address"])
                break
    
    def _generate_random_mac(self):
        """Rastgele MAC adresi oluştur"""
        random_mac = self.mac_manager.generate_random_mac()
        self.mac_input.setText(random_mac)
        self.status_bar.showMessage(f"Rastgele MAC adresi oluşturuldu: {random_mac}")
    
    def _change_mac_address(self):
        """MAC adresini değiştir"""
        adapter_name = self.adapter_combo.currentText()
        new_mac = self.mac_input.text().strip()
        
        if not adapter_name:
            QMessageBox.warning(self, "Hata", "Lütfen bir ağ adaptörü seçin.")
            return
        
        if not new_mac:
            QMessageBox.warning(self, "Hata", "Lütfen yeni MAC adresini girin.")
            return
        
        # Kullanıcıya onay sor
        reply = QMessageBox.question(
            self, "MAC Adresini Değiştir",
            f"{adapter_name} adaptörünün MAC adresini {new_mac} olarak değiştirmek istiyor musunuz?\n\n"
            "Not: Bu işlem ağ bağlantınızı geçici olarak kesecektir.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # MAC adresini değiştir
        result = self.mac_manager.change_mac_address(adapter_name, new_mac)
        
        if not result["admin_rights"]:
            QMessageBox.warning(
                self, "Yönetici Hakları Gerekli",
                "MAC adresini değiştirmek için uygulamayı yönetici olarak çalıştırmanız gerekmektedir."
            )
            return
        
        if result["success"]:
            QMessageBox.information(self, "Başarılı", result["message"])
            self.status_bar.showMessage(result["message"])
            
            # Adaptör bilgilerini yenile
            QTimer.singleShot(2000, self._load_network_adapters)  # 2 saniye sonra yenile
        else:
            QMessageBox.warning(self, "Hata", result["message"])
            self.status_bar.showMessage(f"Hata: {result['message']}")
    
    def _reset_mac_address(self):
        """MAC adresini sıfırla"""
        adapter_name = self.adapter_combo.currentText()
        
        if not adapter_name:
            QMessageBox.warning(self, "Hata", "Lütfen bir ağ adaptörü seçin.")
            return
        
        # Kullanıcıya onay sor
        reply = QMessageBox.question(
            self, "MAC Adresini Sıfırla",
            f"{adapter_name} adaptörünün MAC adresini orijinal değerine döndürmek istiyor musunuz?\n\n"
            "Not: Bu işlem ağ bağlantınızı geçici olarak kesecektir.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # MAC adresini sıfırla
        result = self.mac_manager.reset_mac_address(adapter_name)
        
        if not result["admin_rights"]:
            QMessageBox.warning(
                self, "Yönetici Hakları Gerekli",
                "MAC adresini sıfırlamak için uygulamayı yönetici olarak çalıştırmanız gerekmektedir."
            )
            return
        
        if result["success"]:
            QMessageBox.information(self, "Başarılı", result["message"])
            self.status_bar.showMessage(result["message"])
            
            # Adaptör bilgilerini yenile
            QTimer.singleShot(2000, self._load_network_adapters)  # 2 saniye sonra yenile
        else:
            QMessageBox.warning(self, "Hata", result["message"])
            self.status_bar.showMessage(f"Hata: {result['message']}")
    
    def closeEvent(self, event):
        """Pencere kapatıldığında çağrılır"""
        # Ayarları kaydet
        self.settings.sync()
        event.accept()