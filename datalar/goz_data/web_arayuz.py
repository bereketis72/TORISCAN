import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os
import json

# Sayfa yapılandırması
st.set_page_config(
    page_title="Göz Hastalığı Tespit Sistemi",
    layout="wide",
    page_icon="👁️"
)

# Özel CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2e86de;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    .healthy {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .diseased {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .confidence-score {
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<div class="main-header">👁️ Göz Hastalığı Tespit Sistemi</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">4 Farklı Göz Hastalığı Tespiti (Multi-Class AI Model)</div>', unsafe_allow_html=True)

# Sınıf isimleri ve açıklamaları
DISEASE_INFO = {
    'Normal': {
        'emoji': '🟢',
        'description': 'Sağlıklı göz',
        'advice': 'Gözünüz sağlıklı görünüyor.',
        'color_class': 'healthy'
    },
    'diabetic_retinopathy': {
        'emoji': '🔴',
        'description': 'Diyabetik Retinopati',
        'advice': 'Diyabet hastalarında görülen retina hastalığı. Bir göz doktoruna danışın!',
        'color_class': 'diseased'
    },
    'cataract': {
        'emoji': '🟠',
        'description': 'Katarakt',
        'advice': 'Göz merceğinin bulanıklaşması. Tedavi için göz doktoruna başvurun!',
        'color_class': 'diseased'
    },
    'glaucoma': {
        'emoji': '🟡',
        'description': 'Glokom',
        'advice': 'Göz içi basıncının yükselmesi sonucu sinir hasarı. Acil göz muayenesi gerekir!',
        'color_class': 'diseased'
    }
}

# Model yükleme (cache ile sadece bir kez yükler)
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model('goz_modeli.h5')
        # Sınıf indekslerini yükle
        class_indices = {}
        if os.path.exists('sinif_bilgileri.json'):
            with open('sinif_bilgileri.json', 'r') as f:
                class_indices = json.load(f)
        return model, class_indices
    except Exception as e:
        st.error(f"Model yüklenemedi: {e}")
        return None, {}

# Tahmin fonksiyonu
def make_prediction(img, model, class_indices):
    # ÖNCE RGB'ye çevir (tutarlılık için)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resmi modelin beklediği boyuta getir
    img = img.resize((64, 64))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    # Tahmin yap
    prediction = model.predict(img_array, verbose=0)
    
    # En yüksek olasılıklı sınıfı bul
    predicted_class_idx = np.argmax(prediction[0])
    confidence = prediction[0][predicted_class_idx]
    
    # Sınıf ismini bul
    idx_to_class = {v: k for k, v in class_indices.items()} if class_indices else {}
    predicted_class = idx_to_class.get(predicted_class_idx, f"Sınıf {predicted_class_idx}")
    
    return predicted_class, confidence, prediction[0], class_indices

# Ana uygulama
def main():
    model, class_indices = load_model()
    
    if model is None:
        st.error("Model yüklenemedi. Lütfen 'goz_modeli.h5' dosyasının mevcut olduğundan emin olun.")
        st.info("İpucu: Önce `python egit.py` komutunu çalıştırarak modeli eğitmelisiniz.")
        return
    
    # Sidebar - Bilgi paneli
    with st.sidebar:
        st.header("ℹ Model Bilgileri")
        st.info("""
        **Model Tipi:** CNN (Multi-Class)
        
        **Girdi Boyutu:** 64x64 piksel
        
        **Tespit Edilen Hastalıklar:**
        - 🟢 Normal (Sağlıklı)
        - 🔴 Diabetic Retinopathy
        - 🟠 Cataract (Katarakt)
        - 🟡 Glaucoma (Glokom)
        
        **Toplam Eğitim Verisi:** 4,217 retina görseli
        """)
        
        st.header(" Nasıl Kullanılır?")
        st.markdown("""
        1. Retina görselini yükleyin
        2. AI tüm hastalıkları analiz eder
        3. En olası tanıyı görün
        4. Tüm hastalık olasılıklarını inceleyin
        """)
        
        st.header("🏥 Hastalık Bilgileri")
        st.markdown("""
        **Diyabetik Retinopati:** Diyabet sonucu retina hasarı
        
        **Katarakt:** Göz merceği bulanıklaşması
        
        **Glokom:** Göz içi basıncı artışı, sinir hasarı
        """)
        
        st.header("⚠️ Önemli Uyarı")
        st.warning("""
        Bu sistem **sadece eğitim amaçlıdır**. 
        Kesin tanı için mutlaka bir **göz doktoruna** başvurun.
        """)
    
    # Ana içerik
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📸 Retina Görseli Yükleyin")
        uploaded_file = st.file_uploader(
            "Dosya seçin veya sürükleyip bırakın",
            type=['jpg', 'jpeg', 'png'],
            help="Retina görselini yükleyin"
        )
        
        if uploaded_file is not None:
            # Görseli göster
            img = Image.open(uploaded_file)
            st.image(img, caption="Yüklenen Görsel", use_container_width=True)
    
    with col2:
        st.header("🔬 Analiz Sonucu")
        
        if uploaded_file is not None:
            with st.spinner('4 farklı göz hastalığı analiz ediliyor...'):
                predicted_class, confidence, all_predictions, class_indices = make_prediction(img, model, class_indices)
                
                # Hastalık bilgisini al
                disease_key = predicted_class if predicted_class in DISEASE_INFO else 'diseased'
                
                # Normal mu hastalıklı mı kontrol et
                is_normal = 'normal' in predicted_class.lower()
                
                if is_normal:
                    info = DISEASE_INFO['Normal']
                    diagnosis = "SAĞLIKLI (NORMAL)"
                else:
                    info = DISEASE_INFO.get(predicted_class, {
                        'emoji': '🔴',
                        'description': predicted_class,
                        'advice': 'Lütfen bir göz doktoruna danışın!',
                        'color_class': 'diseased'
                    })
                    diagnosis = info['description'].upper()
                
                # Sonucu göster
                st.markdown(f"""
                <div class="result-box {info['color_class']}">
                    <h2>{info['emoji']} {diagnosis}</h2>
                    <div class="confidence-score">%{confidence*100:.2f}</div>
                    <p style="font-size: 1.1rem; margin: 0;">Güven Skoru</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"💡 {info['advice']}")
                
                # Tüm hastalık olasılıkları
                st.subheader("📊 Tüm Olasılıklar")
                
                # Sınıf indekslerini sırala
                idx_to_class = {v: k for k, v in class_indices.items()} if class_indices else {}
                
                for idx, prob in enumerate(all_predictions):
                    class_name = idx_to_class.get(idx, f"Sınıf {idx}")
                    
                    # Emoji al
                    if 'normal' in class_name.lower():
                        emoji = '🟢'
                    elif 'diabetic' in class_name.lower():
                        emoji = '🔴'
                    elif 'cataract' in class_name.lower():
                        emoji = '🟠'
                    elif 'glaucoma' in class_name.lower():
                        emoji = '🟡'
                    else:
                        emoji = '⚪'
                    
                    # Progress bar ile göster
                    st.write(f"{emoji} **{class_name}**")
                    st.progress(float(prob))
                    st.write(f"%{prob*100:.2f}")
                    st.write("")
                
                # Detaylı bilgi
                with st.expander("🔍 Detaylı Analiz"):
                    st.write(f"**Tahmin Edilen Sınıf:** {predicted_class}")
                    st.write(f"**Sınıf İndeksi:** {np.argmax(all_predictions)}")
                    st.write(f"**Ham Çıktı Değerleri:**")
                    for idx, prob in enumerate(all_predictions):
                        class_name = idx_to_class.get(idx, f"Sınıf {idx}")
                        st.write(f"  - {class_name}: {prob:.6f}")
        else:
            st.info("👈 Lütfen sol taraftan bir retina görseli yükleyin")
    
    # Alt bilgi
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><strong>⚠️ DİKKAT:</strong> Bu sistem sadece eğitim amaçlıdır. 
        Kesin tanı için mutlaka bir sağlık uzmanına başvurun.</p>
        <p>🤖 <strong>Multi-Class AI Model:</strong> 4,217 retina görüntüsü ile eğitilmiş CNN modeli</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
