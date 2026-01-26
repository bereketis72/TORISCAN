import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

print("=" * 70)
print(" " * 20 + "HATA ANALIZI ARACI")
print("=" * 70)

# Model yukle
print("\n[1/4] Model yukleniyor...")
model = tf.keras.models.load_model('zaturre_modeli.h5')
print("      Model basariyla yuklendi!")

# Analiz fonksiyonlari
def analyze_image_properties(img_path):
    """Gorselin ozelliklerini analiz et"""
    img = Image.open(img_path)
    img_array = np.array(img)
    
    # Griye cevir
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array
    
    properties = {
        'boyut': img.size,
        'mod': img.mode,
        'ortalama_parlaklik': np.mean(gray),
        'parlaklik_std': np.std(gray),
        'min_parlaklik': np.min(gray),
        'max_parlaklik': np.max(gray),
        'kontrast': np.max(gray) - np.min(gray)
    }
    
    return properties

def make_prediction_with_confidence(img_path):
    """Tahmin yap ve guven skorunu don"""
    img = image.load_img(img_path, target_size=(64, 64))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    prediction = model.predict(img_array, verbose=0)
    return prediction[0][0]

def find_errors():
    """Test setinde hatalari bul"""
    test_normal_path = r'raw\chest_xray\chest_xray\test\NORMAL'
    test_pneumonia_path = r'raw\chest_xray\chest_xray\test\PNEUMONIA'
    
    errors = []
    
    print("\n[2/4] Normal (Saglikli) resimler kontrol ediliyor...")
    normal_files = [f for f in os.listdir(test_normal_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    for i, filename in enumerate(normal_files):
        img_path = os.path.join(test_normal_path, filename)
        try:
            prob = make_prediction_with_confidence(img_path)
            if prob > 0.5:  # Yalanci pozitif (Saglikliyi Zaturre dedi)
                errors.append({
                    'path': img_path,
                    'filename': filename,
                    'true_label': 'Normal',
                    'predicted_label': 'Pneumonia',
                    'type': 'YALANCI POZITIF',
                    'confidence': prob,
                    'properties': analyze_image_properties(img_path)
                })
        except:
            continue
        
        if (i + 1) % 50 == 0:
            print(f"      {i + 1}/{len(normal_files)} resim kontrol edildi...")
    
    print(f"\n[3/4] Pneumonia (Zaturre) resimler kontrol ediliyor...")
    pneumonia_files = [f for f in os.listdir(test_pneumonia_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    for i, filename in enumerate(pneumonia_files):
        img_path = os.path.join(test_pneumonia_path, filename)
        try:
            prob = make_prediction_with_confidence(img_path)
            if prob <= 0.5:  # Yalanci negatif (Zaturreyi Saglikli dedi)
                errors.append({
                    'path': img_path,
                    'filename': filename,
                    'true_label': 'Pneumonia',
                    'predicted_label': 'Normal',
                    'type': 'YALANCI NEGATIF',
                    'confidence': prob,
                    'properties': analyze_image_properties(img_path)
                })
        except:
            continue
        
        if (i + 1) % 50 == 0:
            print(f"      {i + 1}/{len(pneumonia_files)} resim kontrol edildi...")
    
    return errors

# Hatalari bul
errors = find_errors()

print(f"\n[4/4] Analiz tamamlandi!\n")
print("=" * 70)
print(" " * 25 + "SONUCLAR")
print("=" * 70)

if not errors:
    print("\n Hic hatali tahmin bulunamadi! Model mukemmel caliisiyor!")
else:
    print(f"\n Toplam {len(errors)} hatali tahmin bulundu.")
    
    # Hata tiplerini say
    yalanci_pozitif = sum(1 for e in errors if e['type'] == 'YALANCI POZITIF')
    yalanci_negatif = sum(1 for e in errors if e['type'] == 'YALANCI NEGATIF')
    
    print(f"\n HATA DAGILIMI:")
    print(f"   Yalanci Pozitif (Saglikli -> Zaturre): {yalanci_pozitif}")
    print(f"   Yalanci Negatif (Zaturre -> Saglikli): {yalanci_negatif}")
    
    # Ortalama ozellikleri hesapla
    yp_brightness = [e['properties']['ortalama_parlaklik'] for e in errors if e['type'] == 'YALANCI POZITIF']
    yn_brightness = [e['properties']['ortalama_parlaklik'] for e in errors if e['type'] == 'YALANCI NEGATIF']
    
    print(f"\n ORTALAMA PARLAKLIK ANALIZI:")
    if yp_brightness:
        print(f"   Yalanci Pozitifler: {np.mean(yp_brightness):.2f}")
    if yn_brightness:
        print(f"   Yalanci Negatifler: {np.mean(yn_brightness):.2f}")
    
    # Gorsellestime - En kotu 6 hatayi goster
    print(f"\n EN KOTU 6 HATALI TAHMIN GOSTERILIYOR...\n")
    
    # Guven skoruna gore sirala (en eminken yanildiklarini bul)
    errors_sorted = sorted(errors, key=lambda x: abs(x['confidence'] - 0.5), reverse=True)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, error in enumerate(errors_sorted[:6]):
        if i >= 6:
            break
        
        img = mpimg.imread(error['path'])
        axes[i].imshow(img, cmap='gray')
        
        title = f"{error['type']}\n"
        title += f"Gercek: {error['true_label']}\n"
        title += f"Tahmin: {error['predicted_label']}\n"
        title += f"Guven: %{error['confidence'] * 100:.1f}"
        
        # Renk secimi
        if error['type'] == 'YALANCI POZITIF':
            color = 'red'
        else:
            color = 'orange'
        
        axes[i].set_title(title, fontsize=10, color=color, weight='bold')
        axes[i].axis('off')
    
    # Bos grafikleri kapat
    for i in range(len(errors_sorted[:6]), 6):
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.savefig('hata_analizi.png', dpi=150, bbox_inches='tight')
    print("      Gorsel 'hata_analizi.png' olarak kaydedildi!")
    
    # Detayli rapor olustur
    print("\n DETAYLI RAPOR OLUSTURULUYOR...")
    with open('detayli_hata_raporu.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(" " * 20 + "DETAYLI HATA RAPORU\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Toplam Hata Sayisi: {len(errors)}\n")
        f.write(f"Yalanci Pozitif: {yalanci_pozitif}\n")
        f.write(f"Yalanci Negatif: {yalanci_negatif}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("TUM HATALI TAHMINLER:\n")
        f.write("=" * 70 + "\n\n")
        
        for i, error in enumerate(errors, 1):
            f.write(f"{i}. {error['filename']}\n")
            f.write(f"   Tip: {error['type']}\n")
            f.write(f"   Gercek: {error['true_label']} | Tahmin: {error['predicted_label']}\n")
            f.write(f"   Guven Skoru: %{error['confidence'] * 100:.2f}\n")
            f.write(f"   Boyut: {error['properties']['boyut']}\n")
            f.write(f"   Ortalama Parlaklik: {error['properties']['ortalama_parlaklik']:.2f}\n")
            f.write(f"   Kontrast: {error['properties']['kontrast']:.2f}\n")
            f.write(f"   Parlaklik Std: {error['properties']['parlaklik_std']:.2f}\n")
            f.write("\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("IYILESTIRME ONERILERI:\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("1. VERİ ARTIRMA: Daha fazla cesitli veri ile egitim yapin\n")
        f.write("2. EPOCH SAYISI: Epoch sayisini artirin (ornegin 10 veya 20)\n")
        f.write("3. MODEL MIMARISI: Daha derin bir CNN mimarisi deneyin\n")
        f.write("4. GORUNTU ONISLEME: Parlaklik normalizasyonu ekleyin\n")
        f.write("5. ESIK DEGERI: 0.5 yerine optimize edilmis bir esik kullanin\n")
    
    print("      'detayli_hata_raporu.txt' dosyasi olusturuldu!")
    
    # Ozet istatistikler
    print(f"\n\n GORSEL OZELLIKLERI ANALIZI:")
    print("-" * 70)
    
    for error_type in ['YALANCI POZITIF', 'YALANCI NEGATIF']:
        filtered = [e for e in errors if e['type'] == error_type]
        if filtered:
            avg_brightness = np.mean([e['properties']['ortalama_parlaklik'] for e in filtered])
            avg_contrast = np.mean([e['properties']['kontrast'] for e in filtered])
            
            print(f"\n {error_type}:")
            print(f"   Ortalama Parlaklik: {avg_brightness:.2f}")
            print(f"   Ortalama Kontrast: {avg_contrast:.2f}")

print("\n" + "=" * 70)
print(" " * 20 + "ANALIZ TAMAMLANDI!")
print("=" * 70)
print("\n OLUSTURULAN DOSYALAR:")
print("   - hata_analizi.png (En kotu 6 hata)")
print("   - detayli_hata_raporu.txt (Tam rapor)")
print("\n")
