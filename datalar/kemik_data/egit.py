import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# 1. Veri yollarını tanımlayalım
# Not: Veri klasörünüzün yolunu buraya yazın
base_path = os.getcwd()
train_path = os.path.join(base_path, 'archive', 'BoneFractureDataset', 'training')
test_path = os.path.join(base_path, 'archive', 'BoneFractureDataset', 'test')

print(f"Eğitim verisi aranan yol: {train_path}")

# 2. Resimleri yapay zekanın anlayacağı formata çeviren jeneratör
train_datagen = ImageDataGenerator(
    rescale=1./255,    # Renk değerlerini 0-255'ten 0-1 arasına çeker
    shear_range=0.2,   # Rastgele bükme (veri çeşitliliği için)
    zoom_range=0.2,    # Rastgele yakınlaştırma
    horizontal_flip=True # Yatay çevirme
)

test_datagen = ImageDataGenerator(rescale=1./255)

# 3. Klasörlerden verileri çekelim
try:
    train_set = train_datagen.flow_from_directory(
        train_path,
        target_size=(64, 64), # Resimleri 64x64 boyutuna küçültür (hız için)
        batch_size=32,
        class_mode='binary'   # Sadece iki sınıf var: Normal veya Kırık
    )
    print("Veriler başarıyla yüklendi!")
except Exception as e:
    print(f"HATA: {e}")
    print("\nKlasör yapınız şöyle olmalı:")
    print("kemik_data/")
    print("  └── archive/")
    print("      └── BoneFractureDataset/")
    print("          └── training/")
    print("              ├── fractured/")
    print("              └── not fractured/")

# 4. Yapay Zeka Modelini Oluşturalım
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    MaxPooling2D(pool_size=(2, 2)),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),

    Flatten(),
    Dense(units=128, activation='relu'),
    Dense(units=1, activation='sigmoid') # 0: Normal, 1: Kırık
])

# 5. Modeli Derleyelim
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
print("Model mimarisi oluşturuldu.")

# 6. Modeli Eğitelim
if 'train_set' in locals():
    print("Eğitim başlıyor... Bu işlem birkaç dakika sürebilir.")
    model.fit(train_set, epochs=5) # 5 tur (epoch) eğitim yapacak

    # 7. Modeli Kaydedelim
    model.save('kemik_modeli.h5')
    print("\n" + "="*60)
    print("Eğitim BİTTİ ve model 'kemik_modeli.h5' olarak kaydedildi!")
    print("="*60)
else:
    print("Eğitim başlatılamadı. Lütfen veri klasörünü kontrol edin.")
