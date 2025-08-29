# Cihaz Bilgisi Gizleyici v1.0.0 (Tam Sürüm)

Bu uygulama, cihaz bilgilerini (işletim sistemi, donanım bilgileri, MAC adresi vb.) değiştirerek kullanıcının gerçek cihaz bilgilerini gizlemesini sağlar. Uygulama, Windows Registry'de gerçek değişiklikler yaparak sistem bilgilerini kalıcı olarak değiştirebilir.

## Özellikler

- **Gerçek Cihaz Bilgilerini Görüntüleme**: İşletim sistemi, ağ, donanım ve kullanıcı bilgilerini gerçek zamanlı olarak görüntüler.
- **Sahte Profil Yönetimi**: Özelleştirilebilir sahte cihaz bilgileri için profil oluşturma, düzenleme, silme.
- **Rastgele Profil Oluşturma**: Tek tıklamayla rastgele cihaz bilgileri içeren profiller oluşturabilme.
- **Profil İçe/Dışa Aktarma**: Profilleri JSON formatında dışa aktarma ve içe aktarma.
- **Tema Desteği**: Açık, koyu ve sistem teması seçenekleri.
- **Otomatik Yenileme**: Gerçek cihaz bilgilerini otomatik olarak yenileme özelliği.
- **Gerçek Sistem Değişiklikleri**: Windows Registry'de gerçek değişiklikler yaparak sistem bilgilerini kalıcı olarak değiştirebilme.

## Kurulum

1. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Uygulamayı **yönetici olarak** çalıştırın:
   ```
   python main.py
   ```
   
   **Not**: Gerçek sistem değişiklikleri yapabilmek için uygulamanın yönetici haklarıyla çalıştırılması gerekmektedir.

## Kullanım

1. **Profil Seçimi**: Sol panelden mevcut profilleri seçebilirsiniz.
2. **Yeni Profil**: "Yeni" butonuna tıklayarak yeni bir profil oluşturabilirsiniz.
3. **Rastgele Profil**: "Rastgele Profil Oluştur" butonuyla rastgele bir profil oluşturabilirsiniz.
4. **Profil İçe/Dışa Aktarma**: "İçe Aktar" ve "Dışa Aktar" butonlarıyla profilleri paylaşabilirsiniz.
5. **Değişiklikleri Uygula**: Profil seçtikten sonra "Değişiklikleri Uygula" butonuna tıklayarak seçilen profili etkinleştirebilirsiniz.

## Proje Yapısı

- **main.py**: Ana uygulama başlatma dosyası.
- **modules/**: Uygulama modülleri.
  - **device_info_controller.py**: Ana arayüz ve kontrol sınıfı.
  - **device_info_manager.py**: Cihaz bilgilerini toplama ve değiştirme sınıfı.
  - **error_logger.py**: Hata günlükleme sınıfı.
- **config/**: Yapılandırma dosyaları ve profiller.
- **logs/**: Hata günlükleri.

## Önemli Uyarılar

- Bu uygulama, Windows Registry'de gerçek değişiklikler yapar ve sistem bilgilerini kalıcı olarak değiştirir.
- Değişikliklerin tam olarak etkinleşmesi için bilgisayarınızı yeniden başlatmanız gerekebilir.
- Uygulamayı kullanmadan önce sistem yedeği almanız önerilir.
- Bazı değişiklikler Windows lisansınızı veya diğer yazılımların çalışmasını etkileyebilir.
- Bu uygulama, eğitim ve test amaçlıdır. Gerçek cihaz bilgilerini değiştirmek bazı sistemlerde veya uygulamalarda sorunlara neden olabilir. Kullanım sorumluluğu size aittir.

## Sürüm Bilgisi

- **Sürüm**: 1.0.0
- **Sürüm Türü**: Tam Sürüm (Stable)
- **Son Güncelleme**: Temmuz 2024