import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# 1. Modeli Yükle
model = tf.keras.models.load_model('zaturre_modeli.h5')

# 2. Test edilecek resmin yolunu belirle (Test klasöründen bir tane seçelim)
# Not: Kendi klasör yapına göre yolu kontrol et
# NORMAL klasöründen bir resim seçiyoruz
resim_yolu = r'raw\chest_xray\chest_xray\test\NORMAL\IM-0001-0001.jpeg'
# 3. Resmi yapay zekanın anlayacağı boyuta getir
test_image = image.load_img(resim_yolu, target_size=(64, 64))
test_image = image.img_to_array(test_image)
test_image = np.expand_dims(test_image, axis=0)
test_image = test_image / 255.0

# 4. Tahmin Yap
sonuc = model.predict(test_image)

if sonuc[0][0] > 0.5:
    tahmin = "ZATÜRRE (PNEUMONIA)"
    olasılık = sonuc[0][0] * 100
else:
    tahmin = "SAĞLIKLI (NORMAL)"
    olasılık = (1 - sonuc[0][0]) * 100

print(f"\nYapay Zeka Tahmini: {tahmin}")
print(f"Doğruluk Olasılığı: %{olasılık:.2f}")