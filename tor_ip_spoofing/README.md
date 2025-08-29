# Tor Gizlilik Kontrolcüsü

Bu uygulama, Tor ağı üzerinden güvenli ve gizli internet erişimi sağlamak için geliştirilmiş bir araçtır. Tor Bundle kullanarak IP adresinizi gizleyebilir, gizlilik seviyenizi ayarlayabilir ve internet trafiğinizi güvenli bir şekilde yönlendirebilirsiniz.

## Özellikler

- **Tor Bağlantı Kontrolü**: Tor ağına bağlanma ve bağlantıyı kesme
- **IP Değişim İzleme**: Mevcut IP adresinizi görüntüleme ve değişimleri takip etme
- **Otomatik IP Değiştirme**: Belirli aralıklarla otomatik olarak IP adresinizi değiştirme
- **Gizlilik Seviyeleri**: Düşük, Orta, Yüksek ve Özel gizlilik seviyeleri
- **Gelişmiş Gizlilik Ayarları**: Çerezleri temizleme, scriptleri engelleme, köprü kullanma gibi özellikler
- **Hata Takip ve Loglama**: Detaylı hata günlükleri ve durum bilgileri
- **Tema Seçenekleri**: Açık ve koyu tema desteği

## Kurulum

1. Tor Bundle'ı indirin ve `tor.exe` dosyasını projenin ana dizinine yerleştirin
2. Gerekli Python paketlerini yükleyin:

```
pip install stem requests PyQt5
```

3. Uygulamayı başlatın:

```
python main.py
```

## Kullanım

1. Uygulamayı başlattıktan sonra "Tor'a Bağlan" düğmesine tıklayarak Tor ağına bağlanın
2. Bağlantı kurulduktan sonra mevcut IP adresiniz ekranda görüntülenecektir
3. "Çıkış Düğümünü Değiştir" düğmesine tıklayarak yeni bir IP adresi alabilirsiniz
4. Otomatik IP değiştirme özelliğini etkinleştirerek belirli aralıklarla IP adresinizin otomatik olarak değişmesini sağlayabilirsiniz
5. Gizlilik seviyesini ihtiyaçlarınıza göre ayarlayabilirsiniz

## Gizlilik Seviyeleri

- **Düşük**: Temel gizlilik koruması, daha hızlı bağlantı
- **Orta**: Dengeli gizlilik ve performans (varsayılan)
- **Yüksek**: Maksimum gizlilik koruması, daha yavaş bağlantı
- **Özel**: Kendi gizlilik ayarlarınızı yapılandırma

## Proje Yapısı

```
Invisibilty-Cloak/
├── main.py                  # Ana uygulama başlatıcı
├── modules/                 # Modüller dizini
│   ├── tor.exe              # Tor çalıştırılabilir dosyası
│   ├── tor_controller.py    # Tor kontrol arayüzü
│   ├── privacy_settings.py  # Gizlilik ayarları yöneticisi
│   ├── error_logger.py      # Hata loglama sistemi
│   └── tor_data/            # Tor veri dizini
├── logs/                    # Log dosyaları
└── config/                  # Yapılandırma dosyaları
```

## Güvenlik Notları

- Bu uygulama, Tor ağının sağladığı gizlilik özelliklerini kullanır, ancak %100 anonimlik garanti edilemez
- Tarayıcı parmak izi, çerezler ve diğer izleme yöntemleri hala sizi tanımlayabilir
- Kritik güvenlik gerektiren işlemler için ek güvenlik önlemleri almanız önerilir

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.