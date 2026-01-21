from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class IndirmeSonucu:
    """
    Dosya indirme sonuçlarını saklayan veri sınıfı
    """
    
    url: str
    dosya_yolu: str
    dosya_turu: str
    durum: str
    boyut: int
    indirme_suresi: float
    hata_mesaji: Optional[str] = None

    def __post_init__(self):
        # Geçersiz değerleri kontrol et
        if not isinstance(boyut := self.boyut, int) or boyut < 0:
            raise ValueError(f"Boyut negatif veya geçersiz: {self.boyut}")
        if not isinstance(sure := self.indirme_suresi, (int, float)) or sure < 0:
            raise ValueError(f"İndirme süresi negatif veya geçersiz: {self.indirme_suresi}")
        if self.durum not in ("basarili", "basarisiz"):
            raise ValueError(f"Durum hatalı: {self.durum}")

    def to_dict(self) -> dict:
        """Nesneyi sözlük olarak döndür"""
        return asdict(self)
    
    def __str__(self) -> str:
        return f"IndirmeSonucu(url={self.url}, durum={self.durum}, boyut={self.boyut})"