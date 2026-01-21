
"""
Yardımcı fonksiyonlar ve araçlar
"""

import os
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import url2pathname
from typing import Tuple


def dosya_adi_temizle(url: str) -> str:
    """
    URL'den güvenli dosya adı oluştur
    
    Args:
        url: Dosyanın tam URL'si
        
    Returns:
        Güvenli, temizlenmiş dosya adı (max 100 karakter)
    """
    ayrilmis_url = urlparse(url)
    dosya_adi = os.path.basename(unquote(ayrilmis_url.path))
    
    if not dosya_adi or '.' not in dosya_adi:
        # URL'den dosya adı oluştur
        yol_parcalari = [p for p in ayrilmis_url.path.split('/') if p]
        if yol_parcalari:
            dosya_adi = yol_parcalari[-1] + dosya_uzantisi_al(url)
        else:
            dosya_adi = f"dosya_{hash(url) % 10000}" + dosya_uzantisi_al(url)
    
    # Güvensiz karakterleri temizle
    dosya_adi = "".join(c for c in dosya_adi if c.isalnum() or c in ('.', '-', '_'))
    
    # Uzunluk sınırlaması
    if len(dosya_adi) > 100:
        ad, uzanti = os.path.splitext(dosya_adi)
        dosya_adi = ad[:95 - len(uzanti)] + uzanti
    
    return dosya_adi


def dosya_uzantisi_al(url: str) -> str:
    """
    URL'den dosya uzantısını çıkar
    
    Args:
        url: Dosyanın tam URL'si
        
    Returns:
        Dosya uzantısı (örn: '.html') veya '.html' (uzantı yoksa)
    """
    ayrilmis_url = urlparse(url)
    return os.path.splitext(ayrilmis_url.path)[1].lower() or '.html'


def klasor_yapisi_olustur(temel_yol: str, url: str) -> str:
    """
    Web sitesi yapısını yansıtan klasör yapısı oluştur
    
    Args:
        temel_yol: Ana indirme klasörü yolu
        url: Web sayfasının URL'si
        
    Returns:
        Oluşturulan klasörün tam yolu
    """
    ayrilmis_url = urlparse(url)
    
    # Alan adına ve yola göre klasör oluştur
    alan_klasoru = ayrilmis_url.netloc.replace(':', '_').replace('/', '_')
    yol_parcalari = [p for p in ayrilmis_url.path.split('/') if p][:-1]  # Dosya adı hariç
    
    # Güvenli klasör adları oluştur
    guvenli_yol_parcalari = []
    for parca in yol_parcalari:
        guvenli_parca = "".join(c for c in parca if c.isalnum() or c in ('-', '_'))
        if guvenli_parca:
            guvenli_yol_parcalari.append(guvenli_parca)
    
    klasor_yolu = os.path.join(temel_yol, alan_klasoru, *guvenli_yol_parcalari)
    os.makedirs(klasor_yolu, exist_ok=True)
    
    return klasor_yolu


def url_gecerli_mi(url: str) -> bool:
    """
    URL'nin geçerli olup olmadığını kontrol et
    
    Args:
        url: Kontrol edilecek URL
        
    Returns:
        URL geçerli ise True, değilse False
    """
    try:
        ayrilmis_url = urlparse(url)
        return all([ayrilmis_url.scheme, ayrilmis_url.netloc])
    except Exception:
        return False


def boyut_formatla(boyut_bayt: int) -> str:
    """
    Bayt cinsinden boyutu okunabilir formata dönüştür
    
    Args:
        boyut_bayt: Boyut bayt cinsinden
        
    Returns:
        Okunabilir boyut string'i (örn: "2.5 MB")
    """
    for birim in ['B', 'KB', 'MB', 'GB']:
        if boyut_bayt < 1024.0:
            return f"{boyut_bayt:.1f} {birim}"
        boyut_bayt /= 1024.0
    return f"{boyut_bayt:.1f} TB"