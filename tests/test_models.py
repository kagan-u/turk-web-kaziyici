"""
test_models.py - Veri modeli testleri
"""

import pytest
from turk_web_kaziyici.models import IndirmeSonucu


class TestIndirmeSonucu:
    """IndirmeSonucu sınıfı testleri"""
    
    def test_indirme_sonucu_olusturma(self):
        """Temel IndirmeSonucu oluşturma testi"""
        sonuc = IndirmeSonucu(
            url="https://example.com/test.html",
            dosya_yolu="indirmeler/example.com/test.html",
            dosya_turu=".html",
            durum="basarili",
            boyut=1024,
            indirme_suresi=1.5,
            hata_mesaji=None
        )
        
        assert sonuc.url == "https://example.com/test.html"
        assert sonuc.dosya_yolu == "indirmeler/example.com/test.html"
        assert sonuc.dosya_turu == ".html"
        assert sonuc.durum == "basarili"
        assert sonuc.boyut == 1024
        assert sonuc.indirme_suresi == 1.5
        assert sonuc.hata_mesaji is None
    
    def test_indirme_sonucu_basarili(self):
        """Başarılı indirme sonucu testi"""
        sonuc = IndirmeSonucu(
            url="https://example.com/style.css",
            dosya_yolu="indirmeler/example.com/style.css",
            dosya_turu=".css",
            durum="basarili",
            boyut=2048,
            indirme_suresi=0.8
        )
        
        assert sonuc.durum == "basarili"
        assert sonuc.hata_mesaji is None
        assert sonuc.boyut > 0
    
    def test_indirme_sonucu_basarisiz(self):
        """Başarısız indirme sonucu testi"""
        sonuc = IndirmeSonucu(
            url="https://example.com/broken.js",
            dosya_yolu="",
            dosya_turu=".js",
            durum="basarisiz",
            boyut=0,
            indirme_suresi=2.0,
            hata_mesaji="404: Dosya bulunamadı"
        )
        
        assert sonuc.durum == "basarisiz"
        assert sonuc.boyut == 0
        assert sonuc.hata_mesaji == "404: Dosya bulunamadı"
        assert sonuc.dosya_yolu == ""
    
    def test_to_dict(self):
        """to_dict metodu testi"""
        sonuc = IndirmeSonucu(
            url="https://example.com/test.html",
            dosya_yolu="indirmeler/example.com/test.html",
            dosya_turu=".html",
            durum="basarili",
            boyut=1024,
            indirme_suresi=1.5,
            hata_mesaji=None
        )
        
        sonuc_dict = sonuc.to_dict()
        
        assert isinstance(sonuc_dict, dict)
        assert sonuc_dict['url'] == "https://example.com/test.html"
        assert sonuc_dict['durum'] == "basarili"
        assert sonuc_dict['boyut'] == 1024
    
    def test_str_repr(self):
        """__str__ metodu testi"""
        sonuc = IndirmeSonucu(
            url="https://example.com/test.html",
            dosya_yolu="indirmeler/example.com/test.html",
            dosya_turu=".html",
            durum="basarili",
            boyut=1024,
            indirme_suresi=1.5
        )
        
        str_repr = str(sonuc)
        assert "IndirmeSonucu" in str_repr
        assert "basarili" in str_repr
        assert "1024" in str_repr
    
    def test_gecersiz_degerler(self):
        """Geçersiz değerlerle oluşturma testi"""
        # Negatif boyut
        with pytest.raises((ValueError, TypeError)):
            IndirmeSonucu(
                url="https://example.com/test.html",
                dosya_yolu="test.html",
                dosya_turu=".html",
                durum="basarili",
                boyut=-100,  # Geçersiz
                indirme_suresi=1.5
            )