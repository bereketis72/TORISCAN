from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Kullanıcı tablosu"""
    __tablename__ = 'kullanicilar'
    
    # Temel bilgiler
    id = db.Column(db.Integer, primary_key=True)
    tc_kimlik = db.Column(db.String(11), unique=True, nullable=False, index=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    telefon = db.Column(db.String(15), nullable=False)
    sifre_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Kullanıcının analizleri ile ilişki
    analizler = db.relationship('Analysis', backref='kullanici', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Şifreyi hashle"""
        self.sifre_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.sifre_hash, password)
    
    def __repr__(self):
        # Şifreyi gizle
        gizli_sifre = '*' * 7
        return f'<User {self.ad} {self.soyad} (Şifre: {gizli_sifre})>'


class Analysis(db.Model):
    """Analiz kayıtları tablosu"""
    __tablename__ = 'analizler'
    
    # Temel bilgiler
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False, index=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('toplu_analizler.id'), nullable=True, index=True)
    model_tipi = db.Column(db.String(20), nullable=False)  # bone, eye, lung
    gorsel_dosya_adi = db.Column(db.String(255), nullable=False)
    
    # Sonuçlar
    tani_sonucu = db.Column(db.String(100), nullable=False)
    guven_orani = db.Column(db.Float, nullable=False)
    sonuc_json = db.Column(db.Text, nullable=True)
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Analysis {self.model_tipi} - {self.tani_sonucu}>'
    
    def get_model_name_tr(self):
        """Model adını Türkçe olarak döndür"""
        model_names = {
            'bone': 'Kemik Kırığı',
            'eye': 'Göz Hastalığı',
            'lung': 'Akciğer (Zatürre)'
        }
        return model_names.get(self.model_tipi, self.model_tipi)


class BatchAnalysis(db.Model):
    """Batch analiz kayıtları tablosu"""
    __tablename__ = 'toplu_analizler'
    
    # Temel bilgiler
    id = db.Column(db.Integer, primary_key=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False, index=True)
    model_tipi = db.Column(db.String(20), nullable=False)  # bone, eye, lung
    
    # Batch durumu
    durum = db.Column(db.String(20), default='processing', nullable=False)  # processing, completed, failed
    toplam_dosya = db.Column(db.Integer, default=0)
    tamamlanan_dosya = db.Column(db.Integer, default=0)
    
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # İlişkiler
    analizler = db.relationship('Analysis', backref='batch', lazy=True)
    
    def __repr__(self):
        return f'<BatchAnalysis {self.model_tipi} - {self.durum}>'
