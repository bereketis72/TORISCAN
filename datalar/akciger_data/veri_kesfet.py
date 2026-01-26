import os
from PIL import Image
import numpy as np

# Veri seti yolu
base_path = 'raw/chest_xray'

# Her kategorideki görsel sayılarını say
def count_images(path):
    try:
        files = os.listdir(path)
        # Sadece görsel dosyalarını say
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        return len(image_files)
    except:
        return 0

# Train seti
train_normal = count_images(os.path.join(base_path, 'train', 'NORMAL'))
train_pneumonia = count_images(os.path.join(base_path, 'train', 'PNEUMONIA'))

# Test seti
test_normal = count_images(os.path.join(base_path, 'test', 'NORMAL'))
test_pneumonia = count_images(os.path.join(base_path, 'test', 'PNEUMONIA'))

# Validation seti
val_normal = count_images(os.path.join(base_path, 'val', 'NORMAL'))
val_pneumonia = count_images(os.path.join(base_path, 'val', 'PNEUMONIA'))

print("=" * 60)
print("VERİ SETİ ANALİZİ")
print("=" * 60)

print("\n📊 TRAIN SETİ:")
print(f"  ✓ Normal (Sağlıklı):  {train_normal:4d} görsel")
print(f"  ✗ Pneumonia (Hasta):  {train_pneumonia:4d} görsel")
print(f"  📁 Toplam:            {train_normal + train_pneumonia:4d} görsel")

print("\n📊 TEST SETİ:")
print(f"  ✓ Normal (Sağlıklı):  {test_normal:4d} görsel")
print(f"  ✗ Pneumonia (Hasta):  {test_pneumonia:4d} görsel")
print(f"  📁 Toplam:            {test_normal + test_pneumonia:4d} görsel")

print("\n📊 VALIDATION SETİ:")
print(f"  ✓ Normal (Sağlıklı):  {val_normal:4d} görsel")
print(f"  ✗ Pneumonia (Hasta):  {val_pneumonia:4d} görsel")
print(f"  📁 Toplam:            {val_normal + val_pneumonia:4d} görsel")

print("\n" + "=" * 60)
total = train_normal + train_pneumonia + test_normal + test_pneumonia + val_normal + val_pneumonia
print(f"🎯 GENEL TOPLAM: {total} görsel")
print("=" * 60)

# Örnek bir görselin boyutunu kontrol et
print("\n🔍 Örnek görsel boyutu kontrolü...")
try:
    sample_path = os.path.join(base_path, 'train', 'NORMAL')
    sample_files = os.listdir(sample_path)
    if sample_files:
        first_image_path = os.path.join(sample_path, sample_files[0])
        img = Image.open(first_image_path)
        print(f"  📐 Örnek görsel boyutu: {img.size} (Genişlik x Yükseklik)")
        print(f"  🎨 Renk modu: {img.mode}")
        
        # Birkaç örnek daha kontrol et
        sizes = []
        for i, filename in enumerate(sample_files[:10]):
            img = Image.open(os.path.join(sample_path, filename))
            sizes.append(img.size)
        
        sizes_array = np.array(sizes)
        print(f"  📊 İlk 10 görselden ortalama boyut: {sizes_array.mean(axis=0).astype(int)}")
        print(f"  📊 Min boyut: {sizes_array.min(axis=0)}")
        print(f"  📊 Max boyut: {sizes_array.max(axis=0)}")
except Exception as e:
    print(f"  ⚠️ Hata: {e}")

print("\n✅ Veri seti analizi tamamlandı!")
