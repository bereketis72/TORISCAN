import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os
import json

class AIModelManager:
    """AI model yöneticisi"""
    
    def __init__(self, models_folder):
        self.models_folder = models_folder
        self.models = {}
        self.class_info = {}
        self._load_all_models()
    
    def _load_all_models(self):
        """Tüm AI modellerini yükle"""
        try:
            # Kemik kırığı modeli
            kemik_path = os.path.join(self.models_folder, 'kemik_modeli.h5')
            if os.path.exists(kemik_path):
                self.models['bone'] = tf.keras.models.load_model(kemik_path)
                print("✓ Kemik modeli yüklendi")
            
            # Göz hastalığı modeli
            goz_path = os.path.join(self.models_folder, 'goz_modeli.h5')
            if os.path.exists(goz_path):
                self.models['eye'] = tf.keras.models.load_model(goz_path)
                print("✓ Göz modeli yüklendi")
                
                # Sınıf bilgilerini yükle
                class_info_path = os.path.join(self.models_folder, 'sinif_bilgileri.json')
                if os.path.exists(class_info_path):
                    with open(class_info_path, 'r', encoding='utf-8') as f:
                        self.class_info['eye'] = json.load(f)
            
            # Zatürre modeli
            zaturre_path = os.path.join(self.models_folder, 'zaturre_modeli.h5')
            if os.path.exists(zaturre_path):
                self.models['lung'] = tf.keras.models.load_model(zaturre_path)
                print("✓ Zatürre modeli yüklendi")
        
        except Exception as e:
            print(f"✗ Model yükleme hatası: {e}")
    
    def preprocess_image(self, img_path, target_size=(64, 64)):
        """Resmi model için hazırla"""
        img = Image.open(img_path)
        
        # RGB'ye çevir
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Yeniden boyutlandır
        img = img.resize(target_size)
        
        # Array'e çevir ve normalize et
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        
        return img_array
    
    def predict_bone(self, img_path):
        """Kemik kırığı tahmini"""
        if 'bone' not in self.models:
            return {"error": "Kemik modeli yüklenmedi"}
        
        try:
            # Resmi hazırla
            img_array = self.preprocess_image(img_path)
            
            # Tahmin yap
            prediction = self.models['bone'].predict(img_array, verbose=0)
            probability = prediction[0][0]
            
            # Sonucu yorumla
            if probability > 0.5:
                diagnosis = "Kırık Tespit Edildi"
                confidence = float(probability * 100)
                is_healthy = False
            else:
                diagnosis = "Normal (Kırık Yok)"
                confidence = float((1 - probability) * 100)
                is_healthy = True
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "is_healthy": is_healthy,
                "raw_prediction": float(probability),
                "model_type": "bone"
            }
        
        except Exception as e:
            return {"error": f"Tahmin hatası: {str(e)}"}
    
    def predict_eye(self, img_path):
        """Göz hastalığı tahmini (4 sınıf)"""
        if 'eye' not in self.models:
            return {"error": "Göz modeli yüklenmedi"}
        
        try:
            # Resmi hazırla
            img_array = self.preprocess_image(img_path)
            
            # Tahmin yap
            prediction = self.models['eye'].predict(img_array, verbose=0)
            
            # En yüksek olasılıklı sınıfı bul
            predicted_class_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][predicted_class_idx] * 100)
            
            # Sınıf ismini bul
            class_indices = self.class_info.get('eye', {})
            idx_to_class = {v: k for k, v in class_indices.items()} if class_indices else {}
            predicted_class = idx_to_class.get(predicted_class_idx, f"Sınıf {predicted_class_idx}")
            
            # Türkçe tanı isimleri
            disease_names = {
                'Normal': 'Normal (Sağlıklı)',
                'diabetic_retinopathy': 'Diyabetik Retinopati',
                'cataract': 'Katarakt',
                'glaucoma': 'Glokom'
            }
            
            diagnosis = disease_names.get(predicted_class, predicted_class)
            is_healthy = 'normal' in predicted_class.lower()
            
            # Tüm sınıf olasılıkları
            all_probabilities = {}
            for idx, prob in enumerate(prediction[0]):
                class_name = idx_to_class.get(idx, f"Sınıf {idx}")
                all_probabilities[class_name] = float(prob * 100)
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "is_healthy": is_healthy,
                "raw_prediction": str(predicted_class),
                "all_probabilities": all_probabilities,
                "model_type": "eye"
            }
        
        except Exception as e:
            return {"error": f"Tahmin hatası: {str(e)}"}
    
    def predict_lung(self, img_path):
        """Zatürre tahmini"""
        if 'lung' not in self.models:
            return {"error": "Zatürre modeli yüklenmedi"}
        
        try:
            # Resmi hazırla
            img_array = self.preprocess_image(img_path)
            
            # Tahmin yap
            prediction = self.models['lung'].predict(img_array, verbose=0)
            probability = prediction[0][0]
            
            # Sonucu yorumla
            if probability > 0.5:
                diagnosis = "Zatürre (Pneumonia)"
                confidence = float(probability * 100)
                is_healthy = False
            else:
                diagnosis = "Normal (Sağlıklı)"
                confidence = float((1 - probability) * 100)
                is_healthy = True
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "is_healthy": is_healthy,
                "raw_prediction": float(probability),
                "model_type": "lung"
            }
        
        except Exception as e:
            return {"error": f"Tahmin hatası: {str(e)}"}
    
    def predict(self, model_type, img_path):
        """Genel tahmin fonksiyonu"""
        if model_type == 'bone':
            return self.predict_bone(img_path)
        elif model_type == 'eye':
            return self.predict_eye(img_path)
        elif model_type == 'lung':
            return self.predict_lung(img_path)
        else:
            return {"error": "Geçersiz model tipi"}
