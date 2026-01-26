import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

print("=" * 50)
print("🦴 KEMİK KIRIĞI TAHMİN SİSTEMİ")
print("=" * 50)

# Modeli yükle
model = load_model('kemik_kirigi_modeli.h5')
print("✅ Model yüklendi!")

# Kullanıcıdan resim yolu al
resim_yolu = input("\n📸 Kemik röntgeni yolunu girin: ")

try:
    # Resmi yükle ve hazırla
    img = image.load_img(resim_yolu, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalizasyon
    
    # Tahmin yap
    tahmin = model.predict(img_array)[0][0]
    
    print("\n" + "=" * 50)
    print("📊 TAHMİN SONUCU")
    print("=" * 50)
    
    if tahmin > 0.5:
        print(f"🔴 KIRIK TESPİT EDİLDİ!")
        print(f"🎯 Güven Skoru: %{tahmin*100:.2f}")
        print("\n⚠️ Lütfen bir doktora danışın!")
    else:
        print(f"🟢 NORMAL (Kırık tespit edilmedi)")
        print(f"🎯 Güven Skoru: %{(1-tahmin)*100:.2f}")
        print("\n✅ Kemik yapısı normal görünüyor.")
    
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    print("💡 Lütfen geçerli bir röntgen görüntüsü yolu girin.")
