import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

# Resimlerin olduğu klasör yolu
# Doğru yol: chest_xray klasörünün içinde bir tane daha chest_xray var
klasor_yolu = r'data\raw\chest_xray\chest_xray\train\PNEUMONIA'

# Klasördeki resimleri listele ve ilkini seç
resimler = os.listdir(klasor_yolu)
ilk_resim_yolu = os.path.join(klasor_yolu, resimler[0])

print(f"Açılan Resim: {resimler[0]}")

# Resmi oku ve göster
img = mpimg.imread(ilk_resim_yolu)
plt.figure(figsize=(10, 7))
plt.imshow(img, cmap='gray')
plt.title(f"Zatürre Örneği: {resimler[0]}")
plt.axis('off') # Kenardaki sayıları kapatır
plt.show()