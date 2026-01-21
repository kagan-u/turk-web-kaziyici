#!/usr/bin/env python3
"""
Türk Web Kazıyıcı - Komut Satırı Arayüzü

Kullanım:
    python -m turk_web_kaziyici --url-listesi URL1 URL2 --dosya-turleri .html .css
"""

import sys
from .cli import main


if __name__ == "__main__":
    sys.exit(main())