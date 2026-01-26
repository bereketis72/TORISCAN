import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import random
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import seaborn as sns

print("=" * 70)
print(" " * 15 + "GELİŞMİŞ TEST SİSTEMİ - KEMİK KIRIĞI")
print("=" * 70)

# Model yukle
print("\n[1/5] Model yükleniyor...")
model = tf.keras.models.load_model('kemik_modeli.h5')
print("      ✅ Model başarıyla yüklendi!")

# Test klasoru yollari
test_normal_path = os.path.join('archive', 'BoneFractureDataset', 'test', 'not fractured')
test_fractured_path = os.path.join('archive', 'BoneFractureDataset', 'test', 'fractured')

# Klasör kontrolü
if not os.path.exists(test_normal_path):
    print(f"\n❌ HATA: '{test_normal_path}' bulunamadı!")
    print("Lütfen veri klasörü yapınızı kontrol edin.")
    exit()

# Kullanici girdisi
print("\n[2/5] Test yapısı belirleniyor...")
print("\nNasıl test yapmak istersiniz?")
print("  1) Hızlı Test (Her kategoriden 10 resim)")
print("  2) Orta Test (Her kategoriden 50 resim)")
print("  3) Tam Test (Tüm test setini kullan)")
print("  4) Özel (Kendi sayınızı belirleyin)")

choice = input("\nSeçiminiz (1-4): ")

if choice == '1':
    num_samples = 10
elif choice == '2':
    num_samples = 50
elif choice == '3':
    num_samples = 999999  # Tüm resimleri al
elif choice == '4':
    num_samples = int(input("Her kategoriden kaç resim test edilsin? "))
else:
    print("Geçersiz seçim! Varsayılan olarak 10 resim kullanılacak.")
    num_samples = 10

# Resimleri yukle
def load_random_images(folder_path, num_samples, true_label):
    """Klasörden rastgele resimler yükle"""
    all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Rastgele seçim
    if len(all_files) > num_samples:
        selected_files = random.sample(all_files, num_samples)
    else:
        selected_files = all_files
    
    images = []
    labels = []
    filenames = []
    
    for filename in selected_files:
        img_path = os.path.join(folder_path, filename)
        try:
            # Resmi yükle ve işle
            img = image.load_img(img_path, target_size=(64, 64))
            img_array = image.img_to_array(img)
            img_array = img_array / 255.0
            
            images.append(img_array)
            labels.append(true_label)
            filenames.append(filename)
        except:
            continue
    
    return np.array(images), np.array(labels), filenames

print(f"\n[3/5] Resimler yükleniyor (Her kategoriden {num_samples} resim)...")

# Normal resimleri yukle (label: 0)
normal_images, normal_labels, normal_files = load_random_images(test_normal_path, num_samples, 0)
print(f"      Sağlıklı resimler: {len(normal_images)} adet")

# Fractured resimleri yukle (label: 1)
fractured_images, fractured_labels, fractured_files = load_random_images(test_fractured_path, num_samples, 1)
print(f"      Kırık resimler: {len(fractured_images)} adet")

# Birleştir
all_images = np.concatenate([normal_images, fractured_images])
all_labels = np.concatenate([normal_labels, fractured_labels])
all_files = normal_files + fractured_files

print(f"      TOPLAM: {len(all_images)} resim yüklendi")

# Tahminleri yap
print("\n[4/5] Tahminler yapılıyor...")
predictions = model.predict(all_images, verbose=0)
predicted_labels = (predictions > 0.5).astype(int).flatten()

# Performans metrikleri
print("\n[5/5] Sonuçlar hesaplanıyor...\n")
print("=" * 70)
print(" " * 25 + "SONUÇLAR")
print("=" * 70)

accuracy = accuracy_score(all_labels, predicted_labels)
print(f"\n✅ DOĞRULUK ORANI: %{accuracy * 100:.2f}")

# Detaylı rapor
print("\n📊 DETAYLI RAPOR:")
print("-" * 70)
report = classification_report(all_labels, predicted_labels, 
                               target_names=['Normal', 'Fractured'],
                               digits=3)
print(report)

# Karışıklık matrisi
cm = confusion_matrix(all_labels, predicted_labels)
print("\n📈 KARIŞIKLIK MATRİSİ:")
print("-" * 70)
print(f"                    Tahmin: Normal    Tahmin: Fractured")
print(f"Gerçek: Normal          {cm[0][0]:3d}              {cm[0][1]:3d}")
print(f"Gerçek: Fractured       {cm[1][0]:3d}              {cm[1][1]:3d}")

# Hataları kaydet
print("\n\n❌ HATALI TAHMİNLER:")
print("-" * 70)
errors = []
for i, (true_label, pred_label, filename) in enumerate(zip(all_labels, predicted_labels, all_files)):
    if true_label != pred_label:
        if true_label == 0:
            error_type = "YALANCI POZİTİF (Sağlıklı'yı Kırık dedi)"
        else:
            error_type = "YALANCI NEGATİF (Kırık'ı Sağlıklı dedi)"
        
        errors.append({
            'filename': filename,
            'true': 'Normal' if true_label == 0 else 'Fractured',
            'predicted': 'Normal' if pred_label == 0 else 'Fractured',
            'type': error_type,
            'confidence': predictions[i][0]
        })

if errors:
    print(f"\nToplam {len(errors)} hatalı tahmin bulundu:\n")
    for i, error in enumerate(errors[:10], 1):  # İlk 10 hatayı göster
        print(f"{i}. {error['filename']}")
        print(f"   Gerçek: {error['true']} | Tahmin: {error['predicted']}")
        print(f"   Tip: {error['type']}")
        print(f"   Güven: %{error['confidence'] * 100:.2f}\n")
    
    if len(errors) > 10:
        print(f"... ve {len(errors) - 10} hata daha")
    
    # Hataları dosyaya kaydet
    with open('hata_raporu.txt', 'w', encoding='utf-8') as f:
        f.write("HATALI TAHMİNLER RAPORU - KEMİK KIRIĞI\n")
        f.write("=" * 70 + "\n\n")
        for error in errors:
            f.write(f"Dosya: {error['filename']}\n")
            f.write(f"Gerçek: {error['true']} | Tahmin: {error['predicted']}\n")
            f.write(f"Tip: {error['type']}\n")
            f.write(f"Güven: %{error['confidence'] * 100:.2f}\n\n")
    
    print(f"\n💾 Tüm hatalar 'hata_raporu.txt' dosyasına kaydedildi.")
else:
    print("\n✅ Hiç hatalı tahmin yok! Model mükemmel!")

# Görselleştirme
print("\n\n📊 KARIŞIKLIK MATRİSİ GRAFİĞİ oluşturuluyor...")
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal', 'Fractured'],
            yticklabels=['Normal', 'Fractured'])
plt.ylabel('Gerçek Değer')
plt.xlabel('Tahmin')
plt.title('Karışıklık Matrisi - Kemik Kırığı Tespiti')
plt.savefig('karisiklik_matrisi.png', dpi=150, bbox_inches='tight')
print("      ✅ Grafik 'karisiklik_matrisi.png' olarak kaydedildi!")

print("\n" + "=" * 70)
print(" " * 20 + "TEST TAMAMLANDI!")
print("=" * 70)
