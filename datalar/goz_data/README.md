# 👁️ Göz Hastalıkları Tespiti Veri Seti (Eye Disease Detection Dataset)

Bu klasör, **TORISCAN** projesi kapsamında retinal göz taraması (fundus) görüntüleri kullanılarak çeşitli göz hastalıklarının sınıflandırılması için hazırlanan veri setini içerir.

## Klasör Yapısı

Veri seti `archive/dataset` dizini altında sınıf isimlerine göre klasörlenmiş şekilde bulunmaktadır:

```
goz_data/
├── archive/
│   └── dataset/
│       ├── cataract/              # Katarakt hastası göz görüntüleri
│       ├── diabetic_retinopathy/  # Diyabetik retinopati hastası görüntüleri
│       ├── glaucoma/              # Glokom (Göz tansiyonu) hastası görüntüleri
│       └── normal/                # Sağlıklı göz görüntüleri
├── goz_modeli.h5                  # Eğitilmiş çok sınıflı sınıflandırma modeli
├── egit.py                        # Modeli eğitmek için kullanılan betik
├── tahmin_et.py                   # Görüntü tahmini yapmak için betik
├── sinif_bilgileri.json           # Sınıf indekslerini ve isimlerini içeren metadata
└── ...
```

## Veri Seti Hakkında

- **Problem Türü:** Çok Sınıflı Sınıflandırma (Multi-class Classification)
- **Sınıflar ve Açıklamaları:**
    1.  **cataract (Katarakt):** Göz merceğinin saydamlığını kaybederek matlaşması durumu.
    2.  **diabetic_retinopathy (Diyabetik Retinopati):** Şeker hastalığına bağlı olarak retinadaki kan damarlarının hasar görmesi.
    3.  **glaucoma (Glokom):** Göz içi basıncının artması sonucu görme sinirinin zarar görmesi.
    4.  **normal (Normal):** Herhangi bir hastalık belirtisi göstermeyen sağlıklı retina görüntüleri.

## Kurulum ve Kullanım

### Gereksinimler
- `tensorflow`
- `pillow` (PIL)
- `numpy`
- `matplotlib`

### Modeli Eğitme
Model eğitimi için aşağıdaki komutu kullanabilirsiniz. Bu işlem görüntüleri ilgili klasörlerden okur, ön işleme tabi tutar ve modeli eğitir.
```bash
python egit.py
```
Eğitim sonucunda `goz_modeli.h5` dosyası oluşturulur veya güncellenir.

### Tahmin Yapma
Kullanıcıdan alınan bir göz görüntüsünün hangi hastalığa ait olduğunu tahmin etmek için:
```bash
python tahmin_et.py
```

## Model Bilgisi
- **Model Dosyası:** `goz_modeli.h5`
- **Çıktı Katmanı:** 4 nöronlu Softmax katmanı (Her bir sınıfın olasılığını döndürür).
- **Veri Meta:** Sınıf isimleri ve etiket eşleşmeleri `sinif_bilgileri.json` dosyasında tutulabilir.

## Önemli Notlar
- Görüntülerin kalitesi ve aydınlatma koşulları model başarımını etkileyebilir.
- `archive` klasörü içindeki veri yapısı (sınıf klasörleri) `ImageDataGenerator` veya `image_dataset_from_directory` gibi fonksiyonlarla uyumlu olacak şekilde düzenlenmiştir.
