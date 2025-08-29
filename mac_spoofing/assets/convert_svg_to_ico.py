#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SVG'yi ICO'ya Dönüştürme Betiği

Bu betik, SVG simgesini ICO formatına dönüştürür.
Gerekli kütüphaneler: cairosvg, pillow

Kurulum:
    pip install cairosvg pillow
"""

import os
import sys
from io import BytesIO

try:
    import cairosvg
    from PIL import Image
except ImportError:
    print("Gerekli kütüphaneler eksik. Lütfen şu komutu çalıştırın:")
    print("pip install cairosvg pillow")
    sys.exit(1)

def convert_svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """SVG dosyasını ICO formatına dönüştür
    
    Args:
        svg_path (str): SVG dosyasının yolu
        ico_path (str): Oluşturulacak ICO dosyasının yolu
        sizes (list): ICO dosyasına eklenecek boyutlar
    """
    if not os.path.exists(svg_path):
        print(f"Hata: {svg_path} bulunamadı.")
        return False
    
    try:
        # Farklı boyutlarda PNG'ler oluştur
        images = []
        for size in sizes:
            png_data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
            img = Image.open(BytesIO(png_data))
            images.append(img)
        
        # ICO dosyasını kaydet
        images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in images])
        print(f"ICO dosyası başarıyla oluşturuldu: {ico_path}")
        return True
    except Exception as e:
        print(f"Dönüştürme hatası: {str(e)}")
        return False

def main():
    # Betik dizinini al
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # SVG ve ICO dosya yolları
    svg_path = os.path.join(script_dir, "icon.svg")
    ico_path = os.path.join(script_dir, "icon.ico")
    
    # Dönüştürme işlemini gerçekleştir
    convert_svg_to_ico(svg_path, ico_path)

if __name__ == "__main__":
    main()