from turk_web_kaziyici import WebKaziyici, WebKaziyiciYapilandirma
import logging

# Detaylı günlük kaydı için
logging.basicConfig(level=logging.INFO)

# Özel yapılandırma
yapilandirma = WebKaziyiciYapilandirma()
yapilandirma.maks_calisanlar = 10
yapilandirma.istekler_arasi_gecikme = 0.5
yapilandirma.maks_dosya_boyutu = 50 * 1024 * 1024  # 50MB sınır
yapilandirma.zaman_asimi = 60  # 60 saniye zaman aşımı

kaziyici = WebKaziyici(yapilandirma)

# Büyük ölçekli kazıma
url_listesi = [
    "https://site1.com",
    "https://site2.org", 
    "https://site3.net"
]
dosya_turleri = [".html", ".css", ".js", ".png", ".jpg", ".pdf"]

ozet = kaziyici.url_kaziyici(url_listesi, dosya_turleri, "buyuk_indirme")
kaziyici.ozet_raporu_kaydet(ozet, "detayli_rapor.json")