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
print(" " * 15 + "GELISMIS TEST SISTEMI")
print("=" * 70)

# Model yukle
print("\n[1/5] Model yukleniyor...")
model = tf.keras.models.load_model('zaturre_modeli.h5')
print("      Model basariyla yuklendi!")

# Test klasoru yollari
test_normal_path = r'raw\chest_xray\chest_xray\test\NORMAL'
test_pneumonia_path = r'raw\chest_xray\chest_xray\test\PNEUMONIA'

# Kullanici girdisi
print("\n[2/5] Test yapisi belirleniyor...")
print("\nNasil test yapmak istersiniz?")
print("  1) Hizli Test (Her kategoriden 10 resim)")
print("  2) Orta Test (Her kategoriden 50 resim)")
print("  3) Tam Test (Tum test setini kullan)")
print("  4) Ozel (Kendi sayinizi belirleyin)")

choice = input("\nSeciminiz (1-4): ")

if choice == '1':
    num_samples = 10
elif choice == '2':
    num_samples = 50
elif choice == '3':
    num_samples = 999999  # Tum resimleri al
elif choice == '4':
    num_samples = int(input("Her kategoriden kac resim test edilsin? "))
else:
    print("Gecersiz secim! Varsayilan olarak 10 resim kullanilacak.")
    num_samples = 10

# Resimleri yukle
def load_random_images(folder_path, num_samples, true_label):
    """Klasorden rastgele resimler yukle"""
    all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Rastgele secim
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
            # Resmi yukle ve isle
            img = image.load_img(img_path, target_size=(64, 64))
            img_array = image.img_to_array(img)
            img_array = img_array / 255.0
            
            images.append(img_array)
            labels.append(true_label)
            filenames.append(filename)
        except:
            continue
    
    return np.array(images), np.array(labels), filenames

print(f"\n[3/5] Resimler yukleniyor (Her kategoriden {num_samples} resim)...")

# Normal resimleri yukle (label: 0)
normal_images, normal_labels, normal_files = load_random_images(test_normal_path, num_samples, 0)
print(f"      Saglikli resimler: {len(normal_images)} adet")

# Pneumonia resimleri yukle (label: 1)
pneumonia_images, pneumonia_labels, pneumonia_files = load_random_images(test_pneumonia_path, num_samples, 1)
print(f"      Zaturre resimleri: {len(pneumonia_images)} adet")

# Birlestir
all_images = np.concatenate([normal_images, pneumonia_images])
all_labels = np.concatenate([normal_labels, pneumonia_labels])
all_files = normal_files + pneumonia_files

print(f"      TOPLAM: {len(all_images)} resim yuklendi")

# Tahminleri yap
print("\n[4/5] Tahminler yapiliyor...")
predictions = model.predict(all_images, verbose=0)
predicted_labels = (predictions > 0.5).astype(int).flatten()

# Performans metrikleri
print("\n[5/5] Sonuclar hesaplaniyor...\n")
print("=" * 70)
print(" " * 25 + "SONUCLAR")
print("=" * 70)

accuracy = accuracy_score(all_labels, predicted_labels)
print(f"\n DOGRULUK ORANI: %{accuracy * 100:.2f}")

# Detayli rapor
print("\n DETAYLI RAPOR:")
print("-" * 70)
report = classification_report(all_labels, predicted_labels, 
                               target_names=['Normal', 'Pneumonia'],
                               digits=3)
print(report)

# Karisiklik matrisi
cm = confusion_matrix(all_labels, predicted_labels)
print("\n KARISIKLIK MATRISI:")
print("-" * 70)
print(f"                    Tahmin: Normal    Tahmin: Pneumonia")
print(f"Gercek: Normal          {cm[0][0]:3d}              {cm[0][1]:3d}")
print(f"Gercek: Pneumonia       {cm[1][0]:3d}              {cm[1][1]:3d}")

# Hatalari kaydet
print("\n\n HATALI TAHMINLER:")
print("-" * 70)
errors = []
for i, (true_label, pred_label, filename) in enumerate(zip(all_labels, predicted_labels, all_files)):
    if true_label != pred_label:
        if true_label == 0:
            error_type = "YALANCI POZITIF (Saglikli'yi Zaturre dedi)"
        else:
            error_type = "YALANCI NEGATIF (Zaturre'yi Saglikli dedi)"
        
        errors.append({
            'filename': filename,
            'true': 'Normal' if true_label == 0 else 'Pneumonia',
            'predicted': 'Normal' if pred_label == 0 else 'Pneumonia',
            'type': error_type,
            'confidence': predictions[i][0]
        })

if errors:
    print(f"\nToplam {len(errors)} hatali tahmin bulundu:\n")
    for i, error in enumerate(errors[:10], 1):  # Ilk 10 hatayi goster
        print(f"{i}. {error['filename']}")
        print(f"   Gercek: {error['true']} | Tahmin: {error['predicted']}")
        print(f"   Tip: {error['type']}")
        print(f"   Guven: %{error['confidence'] * 100:.2f}\n")
    
    if len(errors) > 10:
        print(f"... ve {len(errors) - 10} hata daha")
    
    # Hatalari dosyaya kaydet
    with open('hata_raporu.txt', 'w', encoding='utf-8') as f:
        f.write("HATALI TAHMINLER RAPORU\n")
        f.write("=" * 70 + "\n\n")
        for error in errors:
            f.write(f"Dosya: {error['filename']}\n")
            f.write(f"Gercek: {error['true']} | Tahmin: {error['predicted']}\n")
            f.write(f"Tip: {error['type']}\n")
            f.write(f"Guven: %{error['confidence'] * 100:.2f}\n\n")
    
    print(f"\n Tum hatalar 'hata_raporu.txt' dosyasina kaydedildi.")
else:
    print("\n Hic hatali tahmin yok! Model mukemmel!")

# Gorsellestime
print("\n\n KARISIKLIK MATRISI GRAFIGI olusturuluyor...")
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal', 'Pneumonia'],
            yticklabels=['Normal', 'Pneumonia'])
plt.ylabel('Gercek Deger')
plt.xlabel('Tahmin')
plt.title('Karisiklik Matrisi')
plt.savefig('karisiklik_matrisi.png', dpi=150, bbox_inches='tight')
print("      Grafik 'karisiklik_matrisi.png' olarak kaydedildi!")

print("\n" + "=" * 70)
print(" " * 20 + "TEST TAMAMLANDI!")
print("=" * 70)
