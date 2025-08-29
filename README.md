# Invisibility Cloak - Gizlilik ve Anonimlik Araçları

Bu proje, çevrimiçi gizliliğinizi ve anonimliğinizi artırmak için tasarlanmış çeşitli araçlar içerir. Her bir araç, dijital kimliğinizin farklı yönlerini korumak ve değiştirmek için özel olarak geliştirilmiştir.

## İçindekiler

1. [MAC Adresi Değiştirme](#mac-spoofing)
2. [Proxy Yöneticisi](#proxy-manager)
3. [Tarayıcı Parmak İzi Gizleme](#browser-fingerprint-spoofing)
4. [Cihaz Bilgisi Değiştirme](#device-info-spoofing)
5. [Tor IP Değiştirme](#tor-ip-spoofing)

## Araçlar

### MAC Spoofing
<a name="mac-spoofing"></a>

MAC adresi değiştirme aracı, ağ adaptörlerinizin MAC adreslerini kolayca değiştirmenizi sağlar.

**Özellikler:**
- Tüm ağ adaptörlerini otomatik tespit etme
- Rastgele veya özel MAC adresleri atama
- Kullanıcı dostu grafik arayüz
- Orijinal MAC adreslerini yedekleme ve geri yükleme

**Kullanım:**
```
cd mac_spoofing
python main.py
```

> **Not:** Bu aracın çalışması için yönetici hakları gereklidir. Yönetici olarak çalıştırmak için `auto_admin.bat` dosyasını kullanabilirsiniz.

### Proxy Yöneticisi
<a name="proxy-manager"></a>

Proxy Yöneticisi, proxy sunucularını test etmenizi, yönetmenizi ve sistem proxy ayarlarını kolayca değiştirmenizi sağlar.

**Özellikler:**
- Kullanıcı dostu ve profesyonel grafik arayüz (GUI)
- Proxy listesi ekleme/düzenleme/silme özellikleri
- Otomatik proxy test fonksiyonu
- Hızlı proxy geçiş seçenekleri
- Sistem proxy ayarlarını otomatik yapılandırma
- Temiz ve modern tasarım
- Karanlık/açık tema seçenekleri

**Kullanım:**
```
cd proxy
pip install -r requirements.txt
python proxy_manager.py
```

### Tarayıcı Parmak İzi Gizleme
<a name="browser-fingerprint-spoofing"></a>

Tarayıcı parmak izi gizleme aracı, tarayıcınızın benzersiz parmak izini değiştirerek çevrimiçi izlenmeyi zorlaştırır.

**Özellikler:**
- User-Agent değiştirme
- Canvas parmak izi gizleme
- WebRTC IP sızıntısı engelleme
- Tarayıcı eklentileri ve özellikleri gizleme
- Ekran çözünürlüğü ve renk derinliği değiştirme

**Kullanım:**
```
cd browser_fingerprint_spoofing
pip install -r requirements.txt
python main.py
```

### Cihaz Bilgisi Değiştirme
<a name="device-info-spoofing"></a>

Cihaz bilgisi değiştirme aracı, bilgisayarınızın sistem bilgilerini değiştirerek tanımlanmasını zorlaştırır.

**Özellikler:**
- Bilgisayar adı değiştirme
- Donanım kimliklerini değiştirme
- İşletim sistemi bilgilerini gizleme
- Seri numaralarını değiştirme
- Önceden tanımlanmış profiller arasında geçiş yapma

**Kullanım:**
```
cd device_info_spoofing
pip install -r requirements.txt
python main.py
```

> **Not:** Bu aracın çalışması için yönetici hakları gereklidir. Yönetici olarak çalıştırmak için `run_as_admin.bat` dosyasını kullanabilirsiniz.

### Tor IP Değiştirme
<a name="tor-ip-spoofing"></a>

Tor IP değiştirme aracı, Tor ağı üzerinden internet bağlantınızı yönlendirerek IP adresinizi gizler ve değiştirir.

**Özellikler:**
- Tor ağına otomatik bağlanma
- Belirli aralıklarla IP değiştirme
- Ülke bazlı çıkış düğümü seçimi
- Tor bağlantı durumu izleme
- Sistem genelinde veya uygulama bazlı proxy ayarları

**Kullanım:**
```
cd tor_ip_spoofing
pip install -r requirements.txt
python main.py
```

## Gereksinimler

Her bir araç kendi klasöründe bulunan `requirements.txt` dosyasında belirtilen bağımlılıklara sahiptir. Genel olarak aşağıdaki gereksinimlere ihtiyaç duyulur:

- Python 3.6 veya üzeri
- Windows işletim sistemi (bazı araçlar için)
- Yönetici hakları (bazı araçlar için)

## Kurulum

1. Bu depoyu klonlayın veya indirin:
```
git clone https://github.com/kullanici/invisibility-cloak.git
```

2. İlgilendiğiniz aracın klasörüne gidin ve gerekli bağımlılıkları yükleyin:
```
cd [araç-klasörü]
pip install -r requirements.txt
```

3. Aracı çalıştırın:
```
python main.py
```

## Güvenlik Uyarısı

Bu araçlar eğitim ve yasal kullanım amaçları için tasarlanmıştır. Kötü niyetli amaçlarla kullanılmamalıdır. Bu araçların kullanımından doğabilecek sonuçlardan kullanıcı sorumludur.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için her bir araç klasöründeki lisans dosyalarına bakın.