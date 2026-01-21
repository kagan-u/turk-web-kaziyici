# Katkıda Bulunma Rehberi / Contributing Guide

## Türkçe

### Katkıda Bulunmak İçin:

1. **Fork Yapın**: Projeyi fork edin
2. **Branch Oluşturun**: `git checkout -b ozellik-adi`
3. **Değişikliklerinizi Yapın**: Kodu geliştirin
4. **Test Edin**: `pytest` ile testleri çalıştırın
5. **Commit Yapın**: `git commit -m 'Yeni özellik eklendi'`
6. **Push Yapın**: `git push origin ozellik-adi`
7. **Pull Request Oluşturun**: Değişikliklerinizi gönderin

### Kod Stili:

- **Black** kullanın: `black src/`
- **Type hints** ekleyin
- **Docstring** yazın
- **PEP 8** standartlarına uygun olun

### Test Yazma:

```python
def test_fonksiyon_adi():
    # Given: Başlangıç durumu
    # When: İşlem yapılır
    # Then: Beklenen sonuç
    assert True
```
### English
## How to Contribute: ##
- **Fork it**: Fork the repository
- **Create Branch**: git checkout -b feature-name
- **Make Changes**: Develop your code
- **Test**: Run tests with pytest
- **Commit**: git commit -m 'Add new feature'
- **Push**: git push origin feature-name
- **Create Pull Request**: Submit your changes 
## Code Style: ##
- **Use Black**: black src/
- **Add type hints**
- **Write docstrings**
- **Follow PEP 8 standards**
## Writing Tests:
```python
def test_function_name():
    # Given: Initial state
    # When: Action performed
    # Then: Expected result
    assert True
    ```

    