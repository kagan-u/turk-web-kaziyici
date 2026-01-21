from turk_web_kaziyici import WebKaziyici, WebKaziyiciYapilandirma

# Kazıyıcıyı yapılandır
yapilandirma = WebKaziyiciYapilandirma()
yapilandirma.maks_calisanlar = 5
yapilandirma.istekler_arasi_gecikme = 1.0

# Kazıyıcıyı başlat
kaziyici = WebKaziyici(yapilandirma)

# URL'leri ve dosya türlerini belirle
url_listesi = ["https://example.com", "https://httpbin.org"]
dosya_turleri = [".html", ".css", ".js"]

# Kazımaya başla
ozet = kaziyici.url_kaziyici(url_listesi, dosya_turleri, "indirmeler")

# Sonuçları görüntüle
print(f"Toplam {ozet['kazima_ozeti']['toplam_indirilen_dosyalar']} dosya indirildi")
print(f"Başarı oranı: {ozet['kazima_ozeti']['basari_orani']}%")