"""
Ana web kazıyıcı sınıfı ve iş mantığı
"""
#scraper.py
import os
from datetime import datetime
from urllib.parse import urljoin
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Set

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .config import WebKaziyiciYapilandirma
from .models import IndirmeSonucu
from .utils import (
    dosya_adi_temizle,
    dosya_uzantisi_al,
    klasor_yapisi_olustur,
    url_gecerli_mi
)

logger = logging.getLogger(__name__)


class WebKaziyici:
    """
    Belirli dosya türlerini indirmek için ana web kazıyıcı sınıfı
    
    Attributes:
        yapilandirma: WebKaziyiciYapilandirma nesnesi
        oturum: requests.Session nesnesi
        indirme_sonuclari: Başarılı ve başarısız tüm indirmelerin listesi
        basarisiz_indirmeler: Sadece başarısız indirmelerin listesi
        istatistikler: Kazıma istatistikleri
    """
    
    def __init__(self, yapilandirma: WebKaziyiciYapilandirma = None):
        self.yapilandirma = yapilandirma or WebKaziyiciYapilandirma()
        self.oturum = self._oturum_olustur()
        self.indirme_sonuclari: List[IndirmeSonucu] = []
        self.basarisiz_indirmeler: List[Dict] = []
        self.istatistikler = {
            'toplam_bulunan_dosyalar': 0,
            'toplam_indirilen_dosyalar': 0,
            'toplam_boyut': 0,
            'baslangic_zamani': None,
            'bitis_zamani': None
        }
    
    def _oturum_olustur(self) -> requests.Session:
        """
        Yeniden deneme mantığı ile requests oturumu oluştur
        
        Returns:
            Yapılandırılmış requests.Session nesnesi
        """
        oturum = requests.Session()
        
        # Tekrar stratejisini yapılandır
        tekrar_stratejisi = Retry(
            total=self.yapilandirma.maks_tekrar,
            backoff_factor=self.yapilandirma.geri_cekilme_faktoru,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adaptor = HTTPAdapter(
            max_retries=tekrar_stratejisi,
            pool_connections=10,
            pool_maxsize=10
        )
        oturum.mount("http://", adaptor)
        oturum.mount("https://", adaptor)
        
        # Başlıkları ayarla
        oturum.headers.update({
            'User-Agent': self.yapilandirma.kullanici_araci,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return oturum
    
    def _dosya_baglantilari_al(self, url: str, dosya_turleri: List[str]) -> List[Tuple[str, str]]:
        """
        Web sayfasından belirtilen türlerdeki dosya bağlantılarını çıkar
        
        Args:
            url: Kazınacak web sayfası URL'si
            dosya_turleri: Aranacak dosya uzantıları listesi
            
        Returns:
            (dosya_url, dosya_turu) tuple'larının listesi
        """
        dosya_baglantilari = []
        
        try:
            response = self.oturum.get(url, timeout=self.yapilandirma.zaman_asimi)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tüm bağlantıları ara
            for link in soup.find_all(['a', 'link', 'script', 'img']):
                href = link.get('href') or link.get('src') or link.get('data-src')
                if href:
                    absolute_url = urljoin(url, href)
                    
                    # URL geçerli mi kontrol et
                    if not url_gecerli_mi(absolute_url):
                        continue
                    
                    # Dosya türünü kontrol et
                    uzanti = dosya_uzantisi_al(absolute_url)
                    for dosya_turu in dosya_turleri:
                        if uzanti.lower() == dosya_turu.lower():
                            dosya_baglantilari.append((absolute_url, dosya_turu))
                            logger.debug(f"Bulundu: {absolute_url} ({dosya_turu})")
                            break
            
            logger.info(f"{url} adresinde {len(dosya_baglantilari)} dosya bulundu")
            return dosya_baglantilari
            
        except Exception as e:
            logger.error(f"{url} adresinden bağlantılar çıkarılırken hata: {str(e)}")
            return []
    
    def _dosya_indir(self, url: str, dosya_turu: str, temel_indirme_yolu: str) -> IndirmeSonucu:
        """
        Hata yönetimi ile tek dosyayı indir
        
        Args:
            url: İndirilecek dosyanın URL'si
            dosya_turu: Dosya uzantısı
            temel_indirme_yolu: Ana indirme klasörü
            
        Returns:
            IndirmeSonucu nesnesi
        """
        baslangic_zamani = time.time()
        
        try:
            # Önce HEAD isteği ile dosya bilgilerini al
            head_response = self.oturum.head(url, timeout=self.yapilandirma.zaman_asimi)
            head_response.raise_for_status()
            
            dosya_boyutu = int(head_response.headers.get('content-length', 0))
            
            if dosya_boyutu > self.yapilandirma.maks_dosya_boyutu:
                raise ValueError(f"Dosya çok büyük: {dosya_boyutu} bayt (max: {self.yapilandirma.maks_dosya_boyutu})")
            
            # Dosyayı indir
            response = self.oturum.get(url, timeout=self.yapilandirma.zaman_asimi, stream=True)
            response.raise_for_status()
            
            # Klasör yapısını oluştur
            indirme_klasoru = klasor_yapisi_olustur(temel_indirme_yolu, url)
            dosya_adi = dosya_adi_temizle(url)
            dosya_yolu = os.path.join(indirme_klasoru, dosya_adi)
            
            # Dosyayı kaydet
            indirilen_boyut = 0
            with open(dosya_yolu, 'wb') as dosya:
                for parca in response.iter_content(chunk_size=self.yapilandirma.parcaboyutu):
                    if parca:
                        dosya.write(parca)
                        indirilen_boyut += len(parca)
            
            indirme_suresi = time.time() - baslangic_zamani
            
            sonuc = IndirmeSonucu(
                url=url,
                dosya_yolu=dosya_yolu,
                dosya_turu=dosya_turu,
                durum='basarili',
                boyut=indirilen_boyut,
                indirme_suresi=indirme_suresi
            )
            
            logger.info(
                f"✅ {url} -> {dosya_yolu} "
                f"({indirilen_boyut} bayt, {indirme_suresi:.2f}s)"
            )
            return sonuc
            
        except Exception as e:
            indirme_suresi = time.time() - baslangic_zamani
            hata_mesaji = str(e)
            
            sonuc = IndirmeSonucu(
                url=url,
                dosya_yolu='',
                dosya_turu=dosya_turu,
                durum='basarisiz',
                boyut=0,
                indirme_suresi=indirme_suresi,
                hata_mesaji=hata_mesaji
            )
            
            logger.error(f"❌ {url} indirilemedi: {hata_mesaji}")
            return sonuc
    
    def url_kaziyici(self, url_listesi: List[str], dosya_turleri: List[str],
                     indirme_yolu: str = 'indirmeler') -> Dict:
        """
        URL'leri kazımak ve belirtilen dosya türlerini indirmek için ana yöntem
        
        Args:
            url_listesi: Kazınacak URL listesi
            dosya_turleri: İndirilecek dosya uzantıları listesi
            indirme_yolu: İndirilen dosyaların kaydedileceği ana klasör
            
        Returns:
            Kapsamlı kazıma özet raporu sözlüğü
        """
        self.istatistikler['baslangic_zamani'] = datetime.now()
        
        # İndirme klasörünü oluştur
        os.makedirs(indirme_yolu, exist_ok=True)
        
        logger.info(
            f"🚀 {len(url_listesi)} URL için kazıma başlatılıyor, "
            f"dosya türleri: {dosya_turleri}"
        )
        
        tum_dosya_baglantilari = []
        
        # Aşama 1: Tüm URL'lerden dosya bağlantılarını çıkar
        for url in url_listesi:
            if not url_gecerli_mi(url):
                logger.warning(f"⚠️ Geçersiz URL atlandı: {url}")
                continue
            
            logger.info(f"📍 İşleniyor: {url}")
            dosya_baglantilari = self._dosya_baglantilari_al(url, dosya_turleri)
            tum_dosya_baglantilari.extend(
                [(url, dosya_url, dosya_turu) 
                 for dosya_url, dosya_turu in dosya_baglantilari]
            )
            time.sleep(self.yapilandirma.istekler_arasi_gecikme)
        
        self.istatistikler['toplam_bulunan_dosyalar'] = len(tum_dosya_baglantilari)
        logger.info(f"📊 Toplam bulunan dosyalar: {len(tum_dosya_baglantilari)}")
        
        if not tum_dosya_baglantilari:
            logger.warning("❌ Hiçbir dosya bulunamadı!")
            return self._ozet_raporu_olustur()
        
        # Aşama 2: Çoklu iş parçacığı ile dosyaları indir
        with ThreadPoolExecutor(max_workers=self.yapilandirma.maks_calisanlar) as yurutucu:
            gelecek_baglantiya = {
                yurutucu.submit(
                    self._dosya_indir,
                    dosya_url,
                    dosya_turu,
                    indirme_yolu
                ): (kaynak_url, dosya_url, dosya_turu)
                for kaynak_url, dosya_url, dosya_turu in tum_dosya_baglantilari
            }
            
            for sayi, gelecek in enumerate(as_completed(gelecek_baglantiya), 1):
                kaynak_url, dosya_url, dosya_turu = gelecek_baglantiya[gelecek]
                try:
                    sonuc = gelecek.result()
                    self.indirme_sonuclari.append(sonuc)
                    
                    if sonuc.durum == 'basarili':
                        self.istatistikler['toplam_indirilen_dosyalar'] += 1
                        self.istatistikler['toplam_boyut'] += sonuc.boyut
                    else:
                        self.basarisiz_indirmeler.append(sonuc.to_dict())
                        
                    # İlerleme raporu
                    if sayi % 10 == 0:
                        logger.info(
                            f"📈 İlerleme: {sayi}/{len(tum_dosya_baglantilari)} dosya işlendi"
                        )
                        
                except Exception as e:
                    logger.error(f"💥 {dosya_url} kritik hata: {str(e)}")
                    self.basarisiz_indirmeler.append({
                        'url': dosya_url,
                        'dosya_turu': dosya_turu,
                        'hata_mesaji': f"Kritik hata: {str(e)}"
                    })
        
        self.istatistikler['bitis_zamani'] = datetime.now()
        
        # Özet raporu oluştur ve döndür
        return self._ozet_raporu_olustur()
    
    def ozet_raporu_kaydet(self, ozet: Dict, dosya_adi: str = 'kazima_ozeti.json'):
        """
        Özet raporunu JSON dosyasına kaydet
        
        Args:
            ozet: Özet raporu sözlüğü
            dosya_adi: Kaydedilecek dosya adı
        """
        import json
        
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            json.dump(ozet, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Özet raporu kaydedildi: {dosya_adi}")
    
    def _ozet_raporu_olustur(self) -> Dict:
        """
        Kapsamlı özet raporu oluştur
        
        Returns:
            Detaylı kazıma özet raporu sözlüğü
        """
        if not self.istatistikler['baslangic_zamani']:
            return {'hata': 'Kazıma başlatılmadı'}
        
        if not self.istatistikler['bitis_zamani']:
            self.istatistikler['bitis_zamani'] = datetime.now()
        
        sure = (self.istatistikler['bitis_zamani'] - 
                self.istatistikler['baslangic_zamani']).total_seconds()
        
        # Dosya türüne göre istatistikler
        dosya_turune_gore = {}
        for sonuc in self.indirme_sonuclari:
            if sonuc.durum == 'basarili':
                if sonuc.dosya_turu not in dosya_turune_gore:
                    dosya_turune_gore[sonuc.dosya_turu] = []
                dosya_turune_gore[sonuc.dosya_turu].append(sonuc)
        
        # Başarı oranı hesapla
        basari_orani = 0
        if self.istatistikler['toplam_bulunan_dosyalar'] > 0:
            basari_orani = (
                self.istatistikler['toplam_indirilen_dosyalar'] / 
                self.istatistikler['toplam_bulunan_dosyalar'] * 100
            )
        
        # Ortalama indirme süresi
        basarili_indirmeler = [r for r in self.indirme_sonuclari if r.durum == 'basarili']
        ortalama_indirme_suresi = 0
        if basarili_indirmeler:
            ortalama_indirme_suresi = sum(r.indirme_suresi for r in basarili_indirmeler) / len(basarili_indirmeler)
        
        ozet = {
            'kazima_ozeti': {
                'baslangic_zamani': self.istatistikler['baslangic_zamani'].isoformat(),
                'bitis_zamani': self.istatistikler['bitis_zamani'].isoformat(),
                'sure_saniye': round(sure, 2),
                'islenen_toplam_url': len(set(r.url for r in self.indirme_sonuclari)),
                'toplam_bulunan_dosyalar': self.istatistikler['toplam_bulunan_dosyalar'],
                'toplam_indirilen_dosyalar': self.istatistikler['toplam_indirilen_dosyalar'],
                'toplam_boyut_bayt': self.istatistikler['toplam_boyut'],
                'toplam_boyut_mb': round(self.istatistikler['toplam_boyut'] / (1024 * 1024), 2),
                'basari_orani': round(basari_orani, 2)
            },
            'dosya_turune_gore': {},
            'basarisiz_indirmeler': self.basarisiz_indirmeler,
            'performans_metrikleri': {
                'ortalama_indirme_suresi': round(ortalama_indirme_suresi, 2),
                'saniye_basina_dosya': round(
                    self.istatistikler['toplam_indirilen_dosyalar'] / max(sure, 0.01), 2
                )
            }
        }
        
        # Dosya türü istatistikleri
        for dosya_turu, dosyalar in dosya_turune_gore.items():
            toplam_boyut = sum(f.boyut for f in dosyalar)
            ozet['dosya_turune_gore'][dosya_turu] = {
                'sayi': len(dosyalar),
                'toplam_boyut_bayt': toplam_boyut,
                'toplam_boyut_mb': round(toplam_boyut / (1024 * 1024), 2),
                'ortalama_boyut_bayt': round(toplam_boyut / len(dosyalar), 0),
                'ortalama_indirme_suresi': round(
                    sum(f.indirme_suresi for f in dosyalar) / len(dosyalar), 2
                )
            }
        
        return ozet