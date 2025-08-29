# MAC Adresi Değiştirici

Bu program, ağ adaptörlerinin MAC adreslerini görüntülemeyi ve değiştirmeyi sağlayan kullanıcı dostu bir grafik arayüz sunar.

## Özellikler

- Mevcut MAC adreslerini görüntüleme
- Yeni MAC adresi girişi
- Rastgele MAC adresi oluşturma
- MAC adresini değiştirme
- Kullanıcı dostu modern arayüz

## Gereksinimler

- Python 3.6+
- PyQt5
- netifaces
- psutil

## Kurulum

```
pip install -r requirements.txt
```

## Kullanım

Programı çalıştırmak için:

```
python main.py
```

Not: MAC adresi değişiklikleri için yönetici hakları gereklidir. Programı yönetici olarak çalıştırın.

```
powershell.exe -ExecutionPolicy Bypass -File .\run_as_admin.ps1
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.