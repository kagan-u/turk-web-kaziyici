#!/usr/bin/env python3
"""
Komut satırı arayüzü için modül
"""

import argparse
import logging
import sys
from typing import List

from .config import WebKaziyiciYapilandirma
from .scraper import WebKaziyici


def setup_logging(verbose: bool = False):
    """Günlük kaydını yapılandır"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Komut satırı argümanlarını ayrıştır"""
    parser = argparse.ArgumentParser(
        description='Türk Web Kazıyıcı - Belirli dosya türlerini indirmek için web kazıyıcı',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek kullanım:
  %(prog)s --url-listesi https://example.com https://site.com --dosya-turleri .html .css
  %(prog)s --url-listesi https://site1.com --dosya-turleri .js --calisanlar 10 --gecikme 0.5
        """
    )
    
    parser.add_argument(
        '--url-listesi',
        nargs='+',
        required=True,
        help='Kazınacak URL listesi (birden fazla URL arasında boşluk bırakın)'
    )
    
    parser.add_argument(
        '--dosya-turleri',
        nargs='+',
        required=True,
        help='İndirilecek dosya türleri (örn: .html .css .js .png)'
    )
    
    parser.add_argument(
        '--cikis-klasoru',
        default='indirmeler',
        help='İndirilen dosyalar için çıkış klasörü (varsayılan: indirmeler)'
    )
    
    parser.add_argument(
        '--calisanlar',
        type=int,
        default=5,
        help='Maksimum iş parçacığı sayısı (varsayılan: 5)'
    )
    
    parser.add_argument(
        '--gecikme',
        type=float,
        default=1.0,
        help='İstekler arası gecikme süresi saniye cinsinden (varsayılan: 1.0)'
    )
    
    parser.add_argument(
        '--zaman-asimi',
        type=int,
        default=30,
        help='İstek zaman aşımı saniye cinsinden (varsayılan: 30)'
    )
    
    parser.add_argument(
        '--maks-dosya-boyutu',
        type=int,
        default=100,
        help='Maksimum dosya boyutu MB cinsinden (varsayılan: 100)'
    )
    
    parser.add_argument(
        '--ozet-dosyasi',
        default='kazima_ozeti.json',
        help='Özet rapor dosyası adı (varsayılan: kazima_ozeti.json)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Detaylı günlük kaydı'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> bool:
    """Argümanları doğrula"""
    if not args.url_listesi:
        print("Hata: En az bir URL belirtmelisiniz!", file=sys.stderr)
        return False
    
    if not args.dosya_turleri:
        print("Hata: En az bir dosya türü belirtmelisiniz!", file=sys.stderr)
        return False
    
    if args.calisanlar < 1 or args.calisanlar > 50:
        print("Hata: Çalışan sayısı 1-50 arasında olmalıdır!", file=sys.stderr)
        return False
    
    if args.gecikme < 0:
        print("Hata: Gecikme süresi negatif olamaz!", file=sys.stderr)
        return False
    
    return True


def main():
    """Ana fonksiyon"""
    args = parse_arguments()
    
    if not validate_arguments(args):
        sys.exit(1)
    
    setup_logging(args.verbose)
    
    try:
        # Yapılandırmayı oluştur
        yapilandirma = WebKaziyiciYapilandirma()
        yapilandirma.maks_calisanlar = args.calisanlar
        yapilandirma.istekler_arasi_gecikme = args.gecikme
        yapilandirma.zaman_asimi = args.zaman_asimi
        yapilandirma.maks_dosya_boyutu = args.maks_dosya_boyutu * 1024 * 1024
        
        # Kazıyıcıyı başlat
        kaziyici = WebKaziyici(yapilandirma)
        
        print(f"🚀 Web kazıma başlatılıyor...")
        print(f"📍 URL'ler: {len(args.url_listesi)} adet")
        print(f"📁 Dosya türleri: {', '.join(args.dosya_turleri)}")
        print(f"⚙️  Çalışanlar: {args.calisanlar}")
        print(f"⏱️  Gecikme: {args.gecikme} saniye")
        print("-" * 50)
        
        # Kazımayı başlat
        ozet = kaziyici.url_kaziyici(
            args.url_listesi,
            args.dosya_turleri,
            args.cikis_klasoru
        )
        
        # Özet raporu kaydet
        kaziyici.ozet_raporu_kaydet(ozet, args.ozet_dosyasi)
        
        # Sonuçları göster
        print("\n" + "="*60)
        print("✅ WEB KAZIMA TAMAMLANDI")
        print("="*60)
        print(f"📊 Toplam bulunan dosyalar: {ozet['kazima_ozeti']['toplam_bulunan_dosyalar']}")
        print(f"✅ Toplam indirilen dosyalar: {ozet['kazima_ozeti']['toplam_indirilen_dosyalar']}")
        print(f"💾 Toplam boyut: {ozet['kazima_ozeti']['toplam_boyut_mb']} MB")
        print(f"🎯 Başarı oranı: {ozet['kazima_ozeti']['basari_orani']}%")
        print(f"⏱️  Süre: {ozet['kazima_ozeti']['sure_saniye']:.2f} saniye")
        print(f"📈 Dosya/saniye: {ozet['performans_metrikleri']['saniye_basina_dosya']}")
        
        if ozet['dosya_turune_gore']:
            print("\n📁 Dosya türüne göre:")
            for dosya_turu, istatistik in ozet['dosya_turune_gore'].items():
                print(f"  {dosya_turu}: {istatistik['sayi']} dosya, {istatistik['toplam_boyut_mb']} MB")
        
        if ozet['basarisiz_indirmeler']:
            print(f"\n❌ Başarısız indirmeler: {len(ozet['basarisiz_indirmeler'])}")
            for basarisiz in ozet['basarisiz_indirmeler'][:5]:
                print(f"  - {basarisiz['url']}: {basarisiz['hata_mesaji']}")
        
        print(f"\n💾 Özet raporu kaydedildi: {args.ozet_dosyasi}")
        
        # Başarısızlık varsa uyarı ver
        if ozet['basarisiz_indirmeler']:
            print("\n⚠️  Bazı dosyalar indirilemedi. Detaylar için günlük dosyasını kontrol edin.")
            sys.exit(2)  # Kısmi başarı durumu
            
    except KeyboardInterrupt:
        print("\n❌ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()