import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="Zatürre Tespit Sistemi",
    layout="wide"
)

# Özel CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
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
    .pneumonia {
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
st.markdown('<div class="main-header"> Zatürre Tespit Sistemi</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Göğüs Röntgeni Analizi ile Yapay Zeka Destekli Tanı</div>', unsafe_allow_html=True)

# Model yükleme (cache ile sadece bir kez yükler)
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model('zaturre_modeli.h5')
        return model
    except Exception as e:
        st.error(f" Model yüklenemedi: {e}")
        return None

# Tahmin fonksiyonu
def make_prediction(img, model):
    # Resmi modelin beklediği boyuta getir
    img = img.resize((64, 64))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    # Tahmin yap
    prediction = model.predict(img_array, verbose=0)
    probability = prediction[0][0]
    
    return probability

# Ana uygulama
def main():
    model = load_model()
    
    if model is None:
        st.error("Model yüklenemedi. Lütfen 'zaturre_modeli.h5' dosyasının mevcut olduğundan emin olun.")
        return
    
    
    # Sidebar - Bilgi paneli
    with st.sidebar:
        st.header(" Model Bilgileri")
        st.info("""
        **Model Tipi:** CNN (Convolutional Neural Network)
        
        **Girdi Boyutu:** 64x64 piksel
        
        **Sınıflar:**
        - 🟢 Normal (Sağlıklı)
        - 🔴 Pneumonia (Zatürre)
        
       
        """)
        
        st.header(" Nasıl Kullanılır?")
        st.markdown("""
        1. Göğüs röntgeni görselini yükleyin
        2. Yapay zeka analiz edecek
        3. Sonuç ve güven skorunu görün
        """)
    
    # Ana içerik
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header(" Röntgen Görseli Yükleyin")
        uploaded_file = st.file_uploader(
            "Dosya seçin veya sürükleyip bırakın",
            type=['jpg', 'jpeg', 'png'],
            help="Göğüs röntgeni görselini yükleyin"
        )
        
        if uploaded_file is not None:
            # Görseli göster
            img = Image.open(uploaded_file)
            st.image(img, caption="Yüklenen Görsel", use_container_width=True)
            
            # RGB'ye çevir (model RGB bekliyor)
            if img.mode != 'RGB':
                img = img.convert('RGB')
    
    with col2:
        st.header("Analiz Sonucu")
        
        if uploaded_file is not None:
            with st.spinner('Analiz ediliyor...'):
                probability = make_prediction(img, model)
                
                # Sonucu belirle
                if probability > 0.5:
                    diagnosis = "ZATÜRRE (PNEUMONIA)"
                    confidence = probability * 100
                    color_class = "pneumonia"
                    emoji = "🔴"
                    advice = " Lütfen bir doktora danışın!"
                else:
                    diagnosis = "SAĞLIKLI (NORMAL)"
                    confidence = (1 - probability) * 100
                    color_class = "healthy"
                    emoji = "🟢"
                    advice = " Görsel normal görünüyor."
                
                # Sonucu göster
                st.markdown(f"""
                <div class="result-box {color_class}">
                    <h2>{emoji} {diagnosis}</h2>
                    <div class="confidence-score">%{confidence:.2f}</div>
                    <p style="font-size: 1.1rem; margin: 0;">Güven Skoru</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(advice)
                
                # Detaylı bilgi
                with st.expander(" Detaylı Analiz"):
                    st.write(f"**Ham Çıktı Değeri:** {probability:.4f}")
                    st.write(f"**Karar Eşiği:** 0.5")
                    
                    # İlerleme çubuğu
                    st.write("**Zatürre Olasılığı:**")
                    st.progress(float(probability))
                    
                    st.write("**Sağlıklı Olasılığı:**")
                    st.progress(float(1 - probability))
        else:
            st.info(" Lütfen sol taraftan bir röntgen görseli yükleyin")
    
    # Alt bilgi
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><strong>⚠️ DİKKAT:</strong> Bu sistem sadece eğitim amaçlıdır. 
        Kesin tanı için mutlaka bir sağlık uzmanına başvurun.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
