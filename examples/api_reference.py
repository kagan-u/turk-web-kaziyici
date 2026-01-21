# Web Kazıma Yapılandırması
class WebKaziyiciYapilandirma:
    maks_calisanlar: int = 5                    # Maksimum iş parçacığı sayısı
    istekler_arasi_gecikme: float = 1.0         # İstekler arası gecikme (saniye)
    zaman_asimi: int = 30                       # Zaman aşımı süresi (saniye)
    maks_tekrar: int = 3                        # Maksimum yeniden deneme sayısı
    geri_cekilme_faktoru: float = 2             # Geri çekilme çarpanı
    parcaboyutu: int = 8192                     # İndirme parça boyutu (bayt)
    maks_dosya_boyutu: int = 100              # Maksimum dosya boyutu
    kullanici_araci: str = 'Mozilla/5.0...'     # User-Agent string     
#Web Kazıma Sınıfı
class WebKaziyici:
    def url_kaziyici(self, url_listesi: List[str], 
                    dosya_turleri: List[str], 
                    indirme_yolu: str = 'indirmeler') -> Dict:
        """URL'leri kazır ve belirtilen dosya türlerini indirir"""        
    def ozet_raporu_kaydet(self, ozet: Dict, dosya_adi: str = 'kazima_ozeti.json'):
        """Özet raporunu JSON dosyasına kaydeder"""