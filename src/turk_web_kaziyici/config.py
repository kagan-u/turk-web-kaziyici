"""
Yapılandırma sınıfları ve ayarlar
"""

from dataclasses import dataclass


@dataclass
class WebKaziyiciYapilandirma:
    """
    Web Kazıyıcı için yapılandırma sınıfı
    
    Attributes:
        maks_calisanlar: Aynı anda çalışacak maksimum iş parçacığı sayısı
        istekler_arasi_gecikme: İstekler arası bekleme süresi (saniye)
        zaman_asimi: HTTP istekleri için zaman aşımı süresi (saniye)
        maks_tekrar: Başarısız istekler için maksimum yeniden deneme sayısı
        geri_cekilme_faktoru: Yeniden deneme arası geri çekilme çarpanı
        parcaboyutu: Dosya indirme parça boyutu (bayt)
        maks_dosya_boyutu: İndirilebilecek maksimum dosya boyutu (bayt)
        kullanici_araci: HTTP isteklerinde kullanılacak User-Agent string'i
    """
    
    maks_calisanlar: int = 5
    istekler_arasi_gecikme: float = 1.0
    zaman_asimi: int = 30
    maks_tekrar: int = 3
    geri_cekilme_faktoru: float = 2
    parcaboyutu: int = 8192
    maks_dosya_boyutu: int = 100 * 1024 * 1024  # 100MB
    kullanici_araci: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def __post_init__(self):
        """Yapılandırma doğrulaması"""
        if self.maks_calisanlar < 1:
            raise ValueError("maks_calisanlar en az 1 olmalıdır")
        if self.istekler_arasi_gecikme < 0:
            raise ValueError("istekler_arasi_gecikme negatif olamaz")
        if self.zaman_asimi < 1:
            raise ValueError("zaman_asimi en az 1 saniye olmalıdır")
        if self.maks_tekrar < 0:
            raise ValueError("maks_tekrar negatif olamaz")
        if self.parcaboyutu < 1024:
            raise ValueError("parcaboyutu en az 1024 bayt olmalıdır")