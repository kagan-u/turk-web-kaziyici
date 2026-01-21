"""
Türk Web Kazıyici - Belirli dosya türleri için güçlü Python web kazıyıcı kütüphanesi

Bu kütüphane, web sitelerinden belirli dosya türlerini indirmek için gelişmiş
çoklu iş parçacıklı bir web kazıyıcı sağlar.
"""

__version__ = "1.0.0"
__author__ = "Kağan Ünal"
__email__ = "kaganunal.15@gmail.com"
__license__ = "MIT"

from .config import WebKaziyiciYapilandirma
from .models import IndirmeSonucu
from .scraper import WebKaziyici

__all__ = [
    "WebKaziyici",
    "WebKaziyiciYapilandirma", 
    "IndirmeSonucu",
    "__version__"
]