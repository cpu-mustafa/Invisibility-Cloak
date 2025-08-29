# Proxy Manager

Modern ve şık bir arayüze sahip proxy değiştirme programı. Bu uygulama, Windows sistemlerde proxy ayarlarını kolayca yönetmenizi sağlar.

## Özellikler

- Kullanıcı dostu ve profesyonel bir grafik arayüz (GUI)
- Proxy listesi ekleme/düzenleme/silme özellikleri
- Otomatik proxy test fonksiyonu
- Hızlı proxy geçiş seçenekleri
- Sistem proxy ayarlarını otomatik yapılandırma
- Temiz ve modern bir tasarım
- Karanlık/açık tema seçenekleri

## Kurulum

1. Gerekli bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

2. Programı çalıştırın:

```bash
python proxy_manager.py
```

## Kullanım

### Proxy Ekleme

- "Ekle" düğmesine tıklayarak yeni bir proxy ekleyebilirsiniz.
- Proxy formatı: `IP:PORT` şeklinde olmalıdır (örn. 192.168.1.1:8080).

### Proxy Test Etme

- Tek bir proxy'yi test etmek için, proxy'yi seçin ve "Test Et" düğmesine tıklayın.
- Tüm proxy'leri test etmek için, üst araç çubuğundaki "Tüm Proxy'leri Test Et" düğmesine tıklayın.

### Proxy Uygulama

- Bir proxy'yi sistem ayarlarına uygulamak için, proxy'yi seçin ve "Uygula" düğmesine tıklayın.
- Proxy'yi devre dışı bırakmak için "Devre Dışı Bırak" düğmesine tıklayın.

### Ayarlar

- Üst araç çubuğundaki "Ayarlar" düğmesine tıklayarak program ayarlarını değiştirebilirsiniz.
- Tema, otomatik test, başlangıçta test, otomatik uygulama ve hızlı proxy eşiği gibi ayarları yapılandırabilirsiniz.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.