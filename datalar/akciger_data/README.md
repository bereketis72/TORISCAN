# 🫁 Akciğer Zatürre Tespiti Veri Seti (Pneumonia Detection Dataset)

Bu klasör, **TORISCAN** projesi kapsamında akciğer X-ray görüntüleri kullanılarak zatürre (pneumonia) tespiti yapmak için hazırlanan veri setini ve ilgili betikleri içerir.

## Klasör Yapısı

Veri seti `raw/chest_xray` dizini altında organize edilmiştir ve aşağıdaki yapıya sahiptir:

```
akciger_data/
├── raw/
│   └── chest_xray/
│       ├── train/           # Model eğitimi için kullanılan görüntüler
│       │   ├── NORMAL/      # Sağlıklı akciğer görüntüleri
│       │   └── PNEUMONIA/   # Zatürreli akciğer görüntüleri
│       ├── test/            # Modelin nihai testi için ayrılmış görüntüler
│       └── val/             # Eğitim sırasında doğrulama (validation) için kullanılan görüntüler
├── zaturre_modeli.h5        # Eğitilmiş derin öğrenme modeli (Keras/TensorFlow)
├── egit.py                  # Modeli eğitmek için kullanılan Python betiği
├── tahmin_et.py             # Tekil görüntü üzerinde tahmin yapmak için betik
├── veri_kesfet.py           # Veri setini analiz etmek ve görselleştirmek için araçlar
└── ...
```

## Veri Seti Hakkında

- **Veri Kaynağı:** Chest X-Ray Images (Pneumonia)
- **Problem Türü:** İkili Sınıflandırma (Binary Classification)
- **Sınıflar:**
    1.  **NORMAL:** Herhangi bir enfeksiyon bulgusu olmayan sağlıklı akciğer filmleri.
    2.  **PNEUMONIA:** Bakteriyel veya viral zatürre enfeksiyonu içeren akciğer filmleri.

## Kurulum ve Kullanım

### Gereksinimler
Bu projeyi çalıştırmak için aşağıdaki Python kütüphanelerine ihtiyacınız vardır:
- `tensorflow`
- `numpy`
- `matplotlib`
- `opencv-python` (cv2)
- `scikit-learn`

### Modeli Eğitme
Modeli sıfırdan eğitmek için `egit.py` dosyasını çalıştırabilirsiniz:
```bash
python egit.py
```
Bu işlem, `raw/chest_xray/train` klasöründeki görüntüleri kullanarak bir CNN (Convolutional Neural Network) modeli eğitir ve `zaturre_modeli.h5` olarak kaydeder.

### Tahmin Yapma
Eğitilmiş modeli kullanarak bir görüntü üzerinde tahmin yapmak için:
```bash
python tahmin_et.py
```
*(Not: `tahmin_et.py` içerisinde test edilecek görüntü yolunu belirtmeniz gerekebilir.)*

## Model Bilgisi
- **Model Dosyası:** `zaturre_modeli.h5`
- **Mimari:** Konvolüsyonel Sinir Ağı (CNN) tabanlı mimari.
- **Girdi Boyutu:** Görüntüler model için optimize edilmiş boyuta (genellikle 224x224 veya 64x64) dönüştürülerek işlenir.

## Notlar
- Veri seti oldukça dengesiz olabilir (Pneumonia örnekleri Normal örneklerinden fazla olabilir), bu nedenle eğitim sırasında `class_weight` veya veri çoğaltma (augmentation) teknikleri kullanılmıştır.
- `raw` klasörü altındaki verilerin silinmemesi veya yerlerinin değiştirilmemesi önemlidir.
