# 🦴 Kemik Kırığı Tespiti Veri Seti (Bone Fracture Detection Dataset)

Bu klasör, **TORISCAN** projesi için X-ray görüntüleri üzerinden kemik kırıklarını tespit etmek amacıyla kullanılan veri setini ve ilgili model dosyalarını içerir.

## Klasör Yapısı

Veri seti `archive/BoneFractureDataset` altında eğitim ve test olmak üzere iki ana bölüme ayrılmıştır:

```
kemik_data/
├── archive/
│   └── BoneFractureDataset/
│       ├── training/        # Model eğitimi için ayrılmış veri
│       │   ├── fractured/       # Kırık kemik görüntüleri
│       │   └── not_fractured/   # Kırık olmayan (sağlam) kemik görüntüleri
│       └── testing/         # Model testi için ayrılmış veri
│           ├── fractured/
│           └── not_fractured/
├── kemik_modeli.h5          # Eğitilmiş ikili sınıflandırma modeli
├── kemik_egit.py            # Eğitim betiği
├── tahmin_kemik.py          # Tahminleme betiği
└── ...
```

## Veri Seti Hakkında

- **Veri Kaynağı:** Bone Fracture Detection Dataset
- **Problem Türü:** İkili Sınıflandırma (Binary Classification)
- **Sınıflar:**
    1.  **fractured:** Kemik bütünlüğünün bozulduğu, kırık veya çatlak içeren X-ray görüntüleri.
    2.  **not_fractured:** Herhangi bir kırık bulgusu olmayan normal kemik yapıları.

## Kurulum ve Kullanım

### Gereksinimler
- `tensorflow`
- `pandas`
- `numpy`
- `matplotlib`
- `scikit-learn`

### Modeli Eğitme
Modeli eğitmek için `kemik_egit.py` dosyasını çalıştırın:
```bash
python kemik_egit.py
```
Bu betik, veri setini yükler, gerekli ön işlemleri (resizing, normalization) yapar ve `kemik_modeli.h5` modelini oluşturur.

### Tahmin Yapma
Test verileri veya yeni bir görüntü üzerinde modelin başarısını görmek için:
```bash
python tahmin_kemik.py
```

## Model Bilgisi
- **Model Dosyası:** `kemik_modeli.h5`
- **Yaklaşım:** Görüntü sınıflandırma (Image Classification).
- **Eğitim Seti:** `archive/BoneFractureDataset/training`
- **Test Seti:** `archive/BoneFractureDataset/testing`

## Notlar
- Kemik görüntüleri kol, bacak, el gibi farklı vücut bölgelerini içerebilir.
- Model performansı görüntünün açısına ve kalitesine göre değişiklik gösterebilir.
