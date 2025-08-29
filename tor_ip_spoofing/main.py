import sys
import os
from PyQt5.QtWidgets import QApplication
from modules.tor_controller import TorController

def main():
    # Gerekli dizinlerin varlığını kontrol et
    modules_dir = os.path.join(os.getcwd(), "modules")
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
        print(f"'{modules_dir}' dizini oluşturuldu.")
    
    # Tor.exe'nin varlığını kontrol et
    tor_exe_path = os.path.join(modules_dir, "tor.exe")
    if not os.path.exists(tor_exe_path):
        # Ana dizindeki tor.exe'yi modules dizinine kopyala
        main_tor_exe = os.path.join(os.getcwd(), "tor.exe")
        if os.path.exists(main_tor_exe):
            import shutil
            shutil.copy2(main_tor_exe, tor_exe_path)
            print(f"tor.exe '{tor_exe_path}' konumuna kopyalandı.")
        else:
            print("HATA: tor.exe bulunamadı. Lütfen tor.exe dosyasını ana dizine yerleştirin.")
            return
    
    # Uygulamayı başlat
    app = QApplication(sys.argv)
    window = TorController()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()