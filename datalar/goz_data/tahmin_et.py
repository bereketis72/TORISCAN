import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import json
import os

# Sınıf isimleri
CLASS_NAMES = {
    0: 'Cataract (Katarakt)',
    1: 'Diabetic Retinopathy (Diyabetik Retinopati)',
    2: 'Glaucoma (Glokom)',
    3: 'Normal (Sağlıklı)'
}

# Model yükleme
print("Model yükleniyor...")
try:
    model = tf.keras.models.load_model('goz_modeli.h5')
    print("✓ Model başarıyla yüklendi!")
    
    # Sınıf indekslerini yükle (varsa)
    if os.path.exists('sinif_bilgileri.json'):
        with open('sinif_bilgileri.json', 'r') as f:
            class_indices = json.load(f)
            # Sınıf isimlerini güncelle
            CLASS_NAMES = {v: k for k, v in class_indices.items()}
            print(f"Sınıflar: {class_indices}")
except:
    print("❌ HATA: 'goz_modeli.h5' bulunamadı!")
    print("Önce 'egit.py' çalıştırarak modeli eğitmelisiniz.")
    exit()

# Kullanıcıdan görsel yolu al
resim_yolu = input("\nRetina görselinin yolunu girin: ")

try:
    # Görseli yükle ve işle
    img = Image.open(resim_yolu)
    
    # RGB'ye çevir
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Boyutlandır
    img = img.resize((64, 64))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    # Tahmin yap
    print("\nAnaliz ediliyor...")
    prediction = model.predict(img_array, verbose=0)
    predicted_class = np.argmax(prediction[0])
    confidence = prediction[0][predicted_class] * 100
    
    # Sonucu göster
    print("\n" + "="*60)
    
    class_name = CLASS_NAMES.get(predicted_class, f"Sınıf {predicted_class}")
    
    if predicted_class == 3 or 'Normal' in class_name:
        print("🟢 SONUÇ: NORMAL (SAĞLIKLI)")
        print(f"Güven Skoru: %{confidence:.2f}")
        print("\nGöz sağlıklı görünüyor.")
    else:
        print(f"🔴 SONUÇ: {class_name.upper()}")
        print(f"Güven Skoru: %{confidence:.2f}")
        print("\n⚠️ Lütfen bir göz doktoruna danışın!")
    
    print("="*60)
    
    # Tüm olasılıkları göster
    print("\nDetaylı Analiz:")
    print("-" * 60)
    for idx, prob in enumerate(prediction[0]):
        class_label = CLASS_NAMES.get(idx, f"Sınıf {idx}")
        print(f"{class_label:<40} %{prob*100:>6.2f}")
    
except FileNotFoundError:
    print(f"❌ HATA: '{resim_yolu}' bulunamadı!")
except Exception as e:
    print(f"❌ HATA: {e}")
