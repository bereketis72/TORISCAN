import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# 1. Veri yollarını tanımlayalım
# Not: Veri klasörünüzün yolunu buraya yazın
base_path = os.getcwd()
train_path = os.path.join(base_path, 'archive', 'dataset')

print(f"Eğitim verisi aranan yol: {train_path}")

# 2. Resimleri yapay zekanın anlayacağı formata çeviren jeneratör
train_datagen = ImageDataGenerator(
    rescale=1./255,    # Renk değerlerini 0-255'ten 0-1 arasına çeker
    shear_range=0.2,   # Rastgele bükme (veri çeşitliliği için)
    zoom_range=0.2,    # Rastgele yakınlaştırma
    horizontal_flip=True, # Yatay çevirme
    validation_split=0.2  # %20'sini doğrulama için ayır
)

# 3. Klasörlerden verileri çekelim
try:
    train_set = train_datagen.flow_from_directory(
        train_path,
        target_size=(64, 64), # Resimleri 64x64 boyutuna küçültür (hız için)
        batch_size=32,
        class_mode='categorical',   # 4 sınıf: Normal, Diabetic Retinopathy, Cataract, Glaucoma
        subset='training'
    )
    
    validation_set = train_datagen.flow_from_directory(
        train_path,
        target_size=(64, 64),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )
    
    print("Veriler başarıyla yüklendi!")
    print(f"Sınıflar: {train_set.class_indices}")
    print(f"Eğitim seti: {train_set.samples} görüntü")
    print(f"Doğrulama seti: {validation_set.samples} görüntü")
except Exception as e:
    print(f"HATA: {e}")
    print("\nKlasör yapınız şöyle olmalı:")
    print("goz_data/")
    print("  └── archive/")
    print("      └── dataset/")
    print("          ├── normal/")
    print("          ├── diabetic_retinopathy/")
    print("          ├── cataract/")
    print("          └── glaucoma/")

# 4. Yapay Zeka Modelini Oluşturalım
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Flatten(),
    Dense(units=128, activation='relu'),
    Dense(units=4, activation='softmax') # 4 sınıf çıktısı
])

# 5. Modeli Derleyelim
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
print("Model mimarisi oluşturuldu.")

# 6. Modeli Eğitelim
if 'train_set' in locals():
    print("Eğitim başlıyor... Bu işlem birkaç dakika sürebilir.")
    history = model.fit(
        train_set, 
        validation_data=validation_set,
        epochs=10  # 10 tur (epoch) eğitim yapacak
    )

    # 7. Modeli Kaydedelim
    model.save('goz_modeli.h5')
    print("\n" + "="*60)
    print("Eğitim BİTTİ ve model 'goz_modeli.h5' olarak kaydedildi!")
    print("="*60)
    
    # Son doğruluk bilgisi
    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    print(f"\nSon Eğitim Doğruluğu: %{final_train_acc*100:.2f}")
    print(f"Son Doğrulama Doğruluğu: %{final_val_acc*100:.2f}")
    
    # Sınıf bilgilerini kaydet
    import json
    with open('sinif_bilgileri.json', 'w') as f:
        json.dump(train_set.class_indices, f)
    print("\nSınıf bilgileri 'sinif_bilgileri.json' dosyasına kaydedildi.")
else:
    print("Eğitim başlatılamadı. Lütfen veri klasörünü kontrol edin.")
