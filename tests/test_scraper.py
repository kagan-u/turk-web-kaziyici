"""
test_scraper.py - Web Kazıyıcı testleri
"""

from datetime import datetime
import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import time

from turk_web_kaziyici.config import WebKaziyiciYapilandirma
from turk_web_kaziyici.models import IndirmeSonucu
from turk_web_kaziyici.scraper import WebKaziyici


class TestWebKaziyiciYapilandirma:
    """WebKaziyiciYapilandirma testleri"""
    
    def test_varsayilan_yapilandirma(self):
        """Varsayılan yapılandırma testi"""
        config = WebKaziyiciYapilandirma()
        
        assert config.maks_calisanlar == 5
        assert config.istekler_arasi_gecikme == 1.0
        assert config.maks_dosya_boyutu == 100 * 1024 * 1024
    
    def test_gecersiz_maks_calisanlar(self):
        """Geçersiz iş parçacığı sayısı testi"""
        with pytest.raises(ValueError):
            WebKaziyiciYapilandirma(maks_calisanlar=0)
    
    def test_gecersiz_gecikme(self):
        """Geçersiz gecikme süresi testi"""
        with pytest.raises(ValueError):
            WebKaziyiciYapilandirma(istekler_arasi_gecikme=-1.0)


class TestWebKaziyici:
    """WebKaziyici sınıfı testleri"""
    
    @pytest.fixture
    def temp_dizin(self):
        """Geçici indirme dizini"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def basit_kaziyici(self):
        """Basit yapılandırılmış kazıyıcı"""
        config = WebKaziyiciYapilandirma()
        config.maks_calisanlar = 2
        config.istekler_arasi_gecikme = 0.1
        config.zaman_asimi = 5
        return WebKaziyici(config)
    
    def test_kaziyici_olusturma(self, basit_kaziyici):
        """Kazıyıcı oluşturma testi"""
        assert basit_kaziyici is not None
        assert basit_kaziyici.oturum is not None
        assert isinstance(basit_kaziyici.yapilandirma, WebKaziyiciYapilandirma)
    
    def test_oturum_olusturma(self, basit_kaziyici):
        """Oturum oluşturma testi"""
        oturum = basit_kaziyici._oturum_olustur()
        assert oturum is not None
        assert 'User-Agent' in oturum.headers
    
    @patch('requests.Session.get')
    def test_dosya_baglantilari_al(self, mock_get, basit_kaziyici):
        """Dosya bağlantıları çıkarma testi"""
        # Mock HTML içeriği
        mock_html = '''
        <html>
            <a href="/style.css">CSS</a>
            <a href="/script.js">JS</a>
            <link href="/theme.css" rel="stylesheet">
            <a href="/page.html">HTML</a>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        baglantilar = basit_kaziyici._dosya_baglantilari_al(
            "https://example.com",
            [".css", ".js"]
        )
        
        assert len(baglantilar) == 3  # 2 CSS + 1 JS
        assert all(isinstance(b, tuple) for b in baglantilar)
        assert all(len(b) == 2 for b in baglantilar)
    
    @patch('requests.Session.head')
    @patch('requests.Session.get')
    def test_dosya_indir_basarili(self, mock_get, mock_head, basit_kaziyici, temp_dizin):
        """Başarılı dosya indirme testi"""
        # Mock HEAD yanıtı
        mock_head_response = Mock()
        mock_head_response.headers = {'content-length': '1024'}
        mock_head_response.raise_for_status = Mock()
        mock_head.return_value = mock_head_response
        
        # Mock GET yanıtı
        mock_get_response = Mock()
        mock_get_response.iter_content = Mock(return_value=[b'test', b'data'])
        mock_get_response.raise_for_status = Mock()
        mock_get.return_value = mock_get_response
        
        sonuc = basit_kaziyici._dosya_indir(
            "https://example.com/test.css",
            ".css",
            temp_dizin
        )
        
        assert isinstance(sonuc, IndirmeSonucu)
        assert sonuc.durum == 'basarili'
        assert sonuc.boyut == 8  # "testdata" uzunluğu
        assert sonuc.dosya_turu == '.css'
        assert os.path.exists(sonuc.dosya_yolu)
        
        # Temizlik
        if os.path.exists(sonuc.dosya_yolu):
            os.remove(sonuc.dosya_yolu)
    
    @patch('requests.Session.head')
    def test_dosya_indir_buyuk_dosya(self, mock_head, basit_kaziyici, temp_dizin):
        """Büyük dosya indirme testi (hata)"""
        # Mock HEAD yanıtı - çok büyük dosya
        mock_head_response = Mock()
        mock_head_response.headers = {'content-length': '200000000'}  # 200MB
        mock_head_response.raise_for_status = Mock()
        mock_head.return_value = mock_head_response
        
        sonuc = basit_kaziyici._dosya_indir(
            "https://example.com/big.file",
            ".file",
            temp_dizin
        )
        
        assert isinstance(sonuc, IndirmeSonucu)
        assert sonuc.durum == 'basarisiz'
        assert sonuc.boyut == 0
        assert 'çok büyük' in sonuc.hata_mesaji.lower()
    
    def test_ozet_raporu_olustur(self, basit_kaziyici):
        """Özet raporu oluşturma testi"""
        # Test verileri ekle
        basit_kaziyici.istatistikler['baslangic_zamani'] = datetime.now()
        time.sleep(0.1)  # Küçük gecikme
        basit_kaziyici.istatistikler['bitis_zamani'] = datetime.now()
        
        # Başarılı indirme ekle
        basit_kaziyici.indirme_sonuclari.append(
            IndirmeSonucu(
                url="https://example.com/test.html",
                dosya_yolu="test.html",
                dosya_turu=".html",
                durum="basarili",
                boyut=1024,
                indirme_suresi=1.0
            )
        )
        
        basit_kaziyici.istatistikler['toplam_bulunan_dosyalar'] = 1
        basit_kaziyici.istatistikler['toplam_indirilen_dosyalar'] = 1
        basit_kaziyici.istatistikler['toplam_boyut'] = 1024
        
        ozet = basit_kaziyici._ozet_raporu_olustur()
        
        assert 'kazima_ozeti' in ozet
        assert 'dosya_turune_gore' in ozet
        assert 'performans_metrikleri' in ozet
        assert ozet['kazima_ozeti']['toplam_indirilen_dosyalar'] == 1
        assert ozet['kazima_ozeti']['basari_orani'] == 100.0
    
    @patch('turk_web_kaziyici.scraper.WebKaziyici._dosya_baglantilari_al')
    @patch('turk_web_kaziyici.scraper.WebKaziyici._dosya_indir')
    def test_url_kaziyici_tam_ucakus(self, mock_indir, mock_baglantilar, basit_kaziyici, temp_dizin):
        """Tam uçuş test - tüm kazıma süreci"""
        # Mock bağlantı verileri
        mock_baglantilar.return_value = [
            ("https://example.com/style.css", ".css"),
            ("https://example.com/script.js", ".js")
        ]
        
        # Mock indirme sonuçları
        mock_indir.side_effect = [
            IndirmeSonucu(
                url="https://example.com/style.css",
                dosya_yolu=os.path.join(temp_dizin, "example.com", "style.css"),
                dosya_turu=".css",
                durum="basarili",
                boyut=2048,
                indirme_suresi=1.0
            ),
            IndirmeSonucu(
                url="https://example.com/script.js",
                dosya_yolu=os.path.join(temp_dizin, "example.com", "script.js"),
                dosya_turu=".js",
                durum="basarili",
                boyut=1024,
                indirme_suresi=0.5
            )
        ]
        
        ozet = basit_kaziyici.url_kaziyici(
            ["https://example.com"],
            [".css", ".js"],
            temp_dizin
        )
        
        assert ozet['kazima_ozeti']['toplam_bulunan_dosyalar'] == 2
        assert ozet['kazima_ozeti']['toplam_indirilen_dosyalar'] == 2
        assert ozet['kazima_ozeti']['basari_orani'] == 100.0
        assert '.css' in ozet['dosya_turune_gore']
        assert '.js' in ozet['dosya_turune_gore']
    
    def test_bos_url_listesi(self, basit_kaziyici, temp_dizin):
        """Boş URL listesi testi"""
        ozet = basit_kaziyici.url_kaziyici([], [".html"], temp_dizin)
        
        assert ozet['kazima_ozeti']['toplam_bulunan_dosyalar'] == 0
        assert ozet['kazima_ozeti']['toplam_indirilen_dosyalar'] == 0
    
    @patch('turk_web_kaziyici.scraper.WebKaziyici._dosya_baglantilari_al')
    def test_hic_dosya_bulunamadi(self, mock_baglantilar, basit_kaziyici, temp_dizin):
        """Hiç dosya bulunamayan durum testi"""
        mock_baglantilar.return_value = []
        
        ozet = basit_kaziyici.url_kaziyici(
            ["https://example.com"],
            [".html"],
            temp_dizin
        )
        
        assert ozet['kazima_ozeti']['toplam_bulunan_dosyalar'] == 0
        assert len(basit_kaziyici.indirme_sonuclari) == 0


class TestHataDurumlari:
    """Hata durumu testleri"""
    
    def test_gecersiz_url(self):
        """Geçersiz URL testi"""
        config = WebKaziyiciYapilandirma()
        kaziyici = WebKaziyici(config)
        
        ozet = kaziyici.url_kaziyici(
            ["gecersiz-url"],
            [".html"],
            "test_indirmeler"
        )
        
        assert ozet['kazima_ozeti']['toplam_bulunan_dosyalar'] == 0
        assert len(kaziyici.indirme_sonuclari) == 0