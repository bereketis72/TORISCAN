import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import os

# 1. Klasör yollarını tanımla
# os.getcwd() komutu kemik_data klasörünün tam yolunu otomatik alır.
base_path = os.getcwd() 

# Görüntülerdeki tam hiyerarşi: archive -> BoneFractureDataset -> training
train_path = os.path.join(base_path, 'archive', 'BoneFractureDataset', 'training')

print(f"Sistem şu adreste resim arıyor: {train_path}")

# 2. Resim Hazırlama (128x128 çözünürlük kemik detayları için idealdir)
train_datagen = ImageDataGenerator(rescale=1./255, horizontal_flip=True, zoom_range=0.2)

# Verileri klasörden çekiyoruz
try:
    train_set = train_datagen.flow_from_directory(
        train_path, 
        target_size=(128, 128), 
        batch_size=32,
        class_mode='binary'
    )
except Exception as e:
    print(f"Hata oluştu: {e}")
    print("İpucu: 'archive' veya 'BoneFractureDataset' klasör isimlerini kontrol edin.")

# 3. Kemik CNN Modeli Tasarımı
model = Sequential([
    tf.keras.layers.Input(shape=(128, 128, 3)),
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(1, activation='sigmoid') 
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 4. Eğitimi Başlat
if 'train_set' in locals():
    print("Kemik kırığı tespiti eğitimi başlıyor... Bu işlem verinin büyüklüğüne göre sürebilir.")
    model.fit(train_set, epochs=10)

    # 5. Modeli Kaydet
    model.save('kemik_modeli.h5')
    print("TEBRİKLER! Kemik modeli 'kemik_modeli.h5' adıyla kaydedildi.")
else:
    print("Eğitim başlatılamadı çünkü veri klasörü bulunamadı.")