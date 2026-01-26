import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import json

print("="*70)
print("GÖZ HASTALIĞI TESPİT SİSTEMİ - GELİŞMİŞ TEST ARACI (MULTI-CLASS)")
print("="*70)

# Model yükleme
print("\n[1/5] Model yükleniyor...")
try:
    model = tf.keras.models.load_model('goz_modeli.h5')
    print("✓ Model başarıyla yüklendi!")
    
    # Sınıf indekslerini yükle
    class_indices = {}
    if os.path.exists('sinif_bilgileri.json'):
        with open('sinif_bilgileri.json', 'r') as f:
            class_indices = json.load(f)
            print(f"✓ Sınıf bilgileri yüklendi: {class_indices}")
    else:
        print("⚠️ Uyarı: sinif_bilgileri.json bulunamadı")
except Exception as e:
    print(f"❌ HATA: Model yüklenemedi - {e}")
    print("Önce 'egit.py' çalıştırarak modeli eğitmelisiniz.")
    exit()

# Veri yolu
base_path = os.getcwd()
test_path = os.path.join(base_path, 'archive', 'dataset')

print(f"\n[2/5] Test verisi yolu: {test_path}")

# Test için kaç görsel kullanılsın?
print("\n" + "="*70)
print("TEST SEÇENEKLERİ")
print("="*70)
print("1. Hızlı Test (Her kategoriden 20 resim)")
print("2. Orta Test (Her kategoriden 100 resim)")
print("3. Tam Test (Tüm veri setini kullan - 4,217 görsel)")
print("4. Özel (Kendiniz belirleyin)")

choice = input("\nSeçiminiz (1-4): ").strip()

# Kaç resim test edilecek?
if choice == "1":
    max_images = 20
elif choice == "2":
    max_images = 100
elif choice == "3":
    max_images = None  # Hepsini kullan
elif choice == "4":
    max_images = int(input("Her kategoriden kaç resim? "))
else:
    print("Geçersiz seçim! Varsayılan olarak Hızlı Test yapılıyor.")
    max_images = 20

# Test veri jeneratörü (augmentation YOK!)
test_datagen = ImageDataGenerator(rescale=1./255)

print("\n[3/5] Test verisi yükleniyor...")
try:
    test_set = test_datagen.flow_from_directory(
        test_path,
        target_size=(64, 64),
        batch_size=1,
        class_mode='categorical',  # Multi-class için categorical
        shuffle=False  # Sıralı olsun ki karşılaştırma yapabilelim
    )
    print(f"✓ Toplam {test_set.samples} test görseli bulundu")
    print(f"  Sınıflar: {test_set.class_indices}")
    print(f"  Sınıf sayısı: {len(test_set.class_indices)}")
except Exception as e:
    print(f"❌ HATA: {e}")
    exit()

# Eğer özel sayı seçildiyse, sınırla
if max_images is not None:
    # Her sınıftan max_images kadar al
    num_classes = len(test_set.class_indices)
    total_to_test = max_images * num_classes
    test_samples = min(total_to_test, test_set.samples)
else:
    test_samples = test_set.samples

print(f"\n[4/5] {test_samples} görsel üzerinde tahmin yapılıyor...")
print("Bu işlem biraz zaman alabilir, lütfen bekleyin...\n")

# Tahminleri yap
predictions = []
true_labels = []
incorrect_files = []

for i in range(test_samples):
    # İlerleme göster (her 100 resimde)
    if (i + 1) % 100 == 0:
        print(f"  İşlendi: {i + 1}/{test_samples}")
    
    # Resmi al
    img, label = test_set.next()
    
    # Tahmin yap
    pred = model.predict(img, verbose=0)[0]
    pred_class = np.argmax(pred)
    true_class = np.argmax(label)
    
    predictions.append(pred_class)
    true_labels.append(true_class)
    
    # Yanlış tahminleri kaydet
    if pred_class != true_class:
        # Dosya adını bul
        file_index = test_set.batch_index - 1
        if file_index < len(test_set.filenames):
            filename = test_set.filenames[file_index]
            incorrect_files.append({
                'file': filename,
                'true': true_class,
                'predicted': pred_class,
                'confidence': pred[pred_class]
            })

print(f"✓ {test_samples} görsel analiz edildi!")

# Sınıf isimleri
idx_to_class = {v: k for k, v in test_set.class_indices.items()}
class_names = [idx_to_class[i] for i in range(len(idx_to_class))]

# Metrikleri hesapla
print("\n[5/5] Sonuçlar hesaplanıyor...\n")

# Confusion Matrix
cm = confusion_matrix(true_labels, predictions)

# Classification Report
report = classification_report(true_labels, predictions, 
                               target_names=class_names,
                               digits=4)

# Accuracy
accuracy = accuracy_score(true_labels, predictions)

# Sonuçları göster
print("="*70)
print("TEST SONUÇLARI - MULTI-CLASS CLASSIFICATION")
print("="*70)
print(f"\nToplam Test: {test_samples} görsel")
print(f"Sınıf Sayısı: {len(class_names)}")
print(f"Doğru Tahmin: {np.sum(np.array(predictions) == np.array(true_labels))}")
print(f"Yanlış Tahmin: {len(incorrect_files)}")
print(f"\n✓ Genel Doğruluk: %{accuracy*100:.2f}")

print("\n" + "="*70)
print("DETAYLI METRİKLER")
print("="*70)
print(report)

print("\n" + "="*70)
print("KARIŞIKLIK MATRİSİ (Confusion Matrix)")
print("="*70)

# Sınıf başına doğruluk
print("\nSınıf Bazında Performans:")
for i, class_name in enumerate(class_names):
    class_total = np.sum(cm[i])
    class_correct = cm[i][i]
    class_accuracy = (class_correct / class_total * 100) if class_total > 0 else 0
    print(f"  {class_name:<30} Doğruluk: %{class_accuracy:.2f} ({class_correct}/{class_total})")

# Confusion matrix grafiği
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names,
            yticklabels=class_names,
            cbar_kws={'label': 'Tahmin Sayısı'})
plt.title('Karışıklık Matrisi - Göz Hastalığı Tespiti (Multi-Class)', fontsize=16, pad=20)
plt.ylabel('Gerçek Sınıf', fontsize=12)
plt.xlabel('Tahmin Edilen Sınıf', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('karisiklik_matrisi.png', dpi=300, bbox_inches='tight')
print("\n✓ Grafik kaydedildi: 'karisiklik_matrisi.png'")

# Hatalı tahminler raporu
if incorrect_files:
    print(f"\n⚠️ {len(incorrect_files)} hatalı tahmin bulundu.")
    print("Detaylar 'hata_raporu.txt' dosyasına kaydediliyor...")
    
    with open('hata_raporu.txt', 'w', encoding='utf-8') as f:
        f.write("HATALI TAHMİNLER RAPORU - GÖZ HASTALIĞI TESPİTİ (MULTI-CLASS)\n")
        f.write("="*70 + "\n\n")
        
        for idx, item in enumerate(incorrect_files, 1):
            f.write(f"{idx}. Dosya: {item['file']}\n")
            f.write(f"   Gerçek: {class_names[item['true']]}\n")
            f.write(f"   Tahmin: {class_names[item['predicted']]}\n")
            f.write(f"   Güven: {item['confidence']:.4f}\n\n")
    
    print("✓ Hata raporu kaydedildi: 'hata_raporu.txt'")
    
    # En çok karıştırılan sınıfları bul
    print("\n" + "="*70)
    print("EN ÇOK KARIŞTIRILAN SINIFLAR")
    print("="*70)
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i != j and cm[i][j] > 0:
                print(f"{class_names[i]} → {class_names[j]}: {cm[i][j]} kez")
else:
    print("\n🎉 Mükemmel! Hiç hatalı tahmin yok!")

print("\n" + "="*70)
print("TEST TAMAMLANDI!")
print("="*70)
print(f"\nÇıktı Dosyaları:")
print(f"  - karisiklik_matrisi.png")
if incorrect_files:
    print(f"  - hata_raporu.txt")
