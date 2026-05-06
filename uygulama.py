# KÜTÜPHANE İÇE AKTARMALARI 
from veritabani_modelleri import User, Analysis, BatchAnalysis
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import Babel, gettext as _
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
from ayarlar import Config
from veritabani_modelleri import db, User, Analysis, BatchAnalysis
from yapay_zeka_modelleri import AIModelManager

# FLASK UYGULAMASI KURULUMU 
app = Flask(__name__)
app.config.from_object(Config)

# Veritabanını başlat
db.init_app(app)

# ÇOK DİLLİ DESTEK BABEL 
babel = Babel(app)

def get_locale():
    """Kullanıcının seçtiği dili session'dan alır"""
    return session.get('language', app.config['BABEL_DEFAULT_LOCALE'])

babel.init_app(app, locale_selector=get_locale)

# YAPAY ZEKA MODELLERİ 
ai_manager = None

def init_ai_models():
    """AI modellerini ilk kez yükler (singleton pattern)"""
    global ai_manager
    if ai_manager is None:
        ai_manager = AIModelManager(app.config['MODELS_FOLDER'])

# TEMPLATE FİLTRELERİ 
@app.template_filter('datetime_tr')
def datetime_tr_filter(dt):
    """UTC datetime'ı Türkiye saatine (UTC+3) çevirir ve formatlar"""
    if dt is None:
        return ''
    tr_time = dt + timedelta(hours=3)
    return tr_time.strftime('%d.%m.%Y %H:%M')

# UYGULAMA BAŞLATMA 
@app.before_request
def before_first_request():
    """Her istekten önce AI modellerinin yüklü olduğundan emin olur"""
    init_ai_models()

# YARDIMCI FONKSİYONLAR 
def allowed_file(filename):
    """Yüklenen dosyanın uzantısının JPG, JPEG veya PNG olup olmadığını kontrol eder"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#  DECORATOR FONKSİYONLAR 
def login_required(f):
    """Kullanıcının giriş yapmış olması gereken sayfalar için decorator"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('Lütfen giriş yapın'), 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Admin yetkisi gereken sayfalar için decorator"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('Lütfen giriş yapın'), 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash(_('Bu sayfaya erişim yetkiniz yok'), 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# GENEL SAYFA ROUTE'LARI
@app.route('/')
def index():
    """Ana karşılama sayfası"""
    return render_template('ana_sayfa.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Yeni kullanıcı kaydı oluşturma sayfası"""
    if request.method == 'POST':
        # Form verilerini al
        tc_kimlik = request.form.get('tc_kimlik')
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        telefon = request.form.get('telefon')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Tüm alanların dolu olup olmadığını kontrol et
        if not all([tc_kimlik, ad, soyad, telefon, password, password_confirm]):
            flash('Tüm alanları doldurun', 'danger')
            return redirect(url_for('register'))
        
        # TC Kimlik formatı kontrolü (11 haneli sayı)
        if len(tc_kimlik) != 11 or not tc_kimlik.isdigit():
            flash('TC Kimlik numarası 11 haneli olmalıdır', 'danger')
            return redirect(url_for('register'))
        
        # Şifrelerin eşleşip eşleşmediğini kontrol et
        if password != password_confirm:
            flash('Şifreler eşleşmiyor', 'danger')
            return redirect(url_for('register'))
        
        # Şifre minimum uzunluk kontrolü
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır', 'danger')
            return redirect(url_for('register'))
        
        # TC Kimlik numarasının daha önce kayıtlı olup olmadığını kontrol et
        existing_user = User.query.filter_by(tc_kimlik=tc_kimlik).first()
        if existing_user:
            flash('Bu TC Kimlik numarası zaten kayıtlı', 'danger')
            return redirect(url_for('register'))
        
        # Yeni kullanıcı kaydı oluştur
        try:
            new_user = User(
                tc_kimlik=tc_kimlik,
                ad=ad,
                soyad=soyad,
                telefon=telefon
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Kayıt sırasında hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('kayit_ol.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfası"""
    if request.method == 'POST':
        tc_kimlik = request.form.get('tc_kimlik')
        password = request.form.get('password')
        
        # Boş alan kontrolü
        if not tc_kimlik or not password:
            flash('TC Kimlik ve şifre gerekli', 'danger')
            return redirect(url_for('login'))
        
        # Kullanıcıyı veritabanında ara
        user = User.query.filter_by(tc_kimlik=tc_kimlik).first()
        
        if user:
            # Şifreyi kontrol et
            if user.check_password(password):
                # Session bilgilerini kaydet
                session['user_id'] = user.id
                session['user_name'] = f"{user.ad} {user.soyad}"
                session['is_admin'] = user.is_admin
                flash(f'Hoş geldiniz, {user.ad} {user.soyad}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Girdiğiniz şifre hatalı.', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Bu TC Kimlik numarası ile kayıtlı kullanıcı bulunamadı.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('oturum_ac.html')


@app.route('/logout')
def logout():
    """Kullanıcı çıkış işlemi - session'ı temizler"""
    session.clear()
    flash('Çıkış yapıldı', 'info')
    return redirect(url_for('index'))


# KULLANICI PANELİ ROUTE'LARI 

@app.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı ana paneli - Model seçimi ve son analizler"""
    user = User.query.get(session['user_id'])
    
    # Kullanıcının son 5 analizini getir
    recent_analyses = Analysis.query.filter_by(kullanici_id=user.id)\
                                   .order_by(Analysis.olusturma_tarihi.desc())\
                                   .limit(5)\
                                   .all()
    
    return render_template('panel.html', user=user, recent_analyses=recent_analyses)


#  ANALİZ ROUTE'LARI 

@app.route('/analyze/<model_type>', methods=['GET', 'POST'])
@login_required
def analyze(model_type):
    """Tekli görüntü yükleme ve AI analizi yapma"""
    # Model tipinin geçerli olup olmadığını kontrol et
    if model_type not in ['bone', 'eye', 'lung']:
        flash('Geçersiz model tipi', 'danger')
        return redirect(url_for('dashboard'))
    
    # Model isimleri
    model_names = {
        'bone': 'Kemik Kırığı Analizi',
        'eye': 'Göz Hastalığı Analizi',
        'lung': 'Akciğer (Zaturre) Analizi'
    }
    
    if request.method == 'POST':
        # Dosya yüklenip yüklenmediğini kontrol et
        if 'xray_image' not in request.files:
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)
        
        file = request.files['xray_image']
        
        if file.filename == '':
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Güvenli dosya adı oluştur ve kaydet
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{session['user_id']}_{model_type}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # AI ile tahmin yap
            result = ai_manager.predict(model_type, filepath)
            
            # Hata kontrolü
            if 'error' in result:
                flash(f'Analiz hatası: {result["error"]}', 'danger')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
            
            # Analiz sonucunu veritabanına kaydet
            try:
                analysis = Analysis(
                    kullanici_id=session['user_id'],
                    model_tipi=model_type,
                    gorsel_dosya_adi=unique_filename,
                    tani_sonucu=result['diagnosis'],
                    guven_orani=result['confidence'],
                    sonuc_json=json.dumps(result, ensure_ascii=False)
                )
                db.session.add(analysis)
                db.session.commit()
                
                return redirect(url_for('result', analysis_id=analysis.id))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Kayıt hatası: {str(e)}', 'danger')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
        
        else:
            flash('Geçersiz dosya formatı. Sadece JPG, JPEG ve PNG kabul edilir.', 'danger')
            return redirect(request.url)
    
    return render_template('analiz_yap.html', model_type=model_type, model_name=model_names[model_type])


@app.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    """Tekli analiz sonucu gösterme sayfası"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Kullanıcının kendi analizine erişip erişmediğini kontrol et
    if analysis.kullanici_id != session['user_id']:
        flash('Bu sonuca erişim yetkiniz yok', 'danger')
        return redirect(url_for('dashboard'))
    
    # JSON sonucunu Python sözlüğüne çevir
    result_data = json.loads(analysis.sonuc_json) if analysis.sonuc_json else {}
    
    return render_template('analiz_sonucu.html', analysis=analysis, result_data=result_data)


@app.route('/history')
@login_required
def history():
    """Kullanıcının geçmiş tüm analizlerini listeler"""
    user = User.query.get(session['user_id'])
    analyses = Analysis.query.filter_by(kullanici_id=user.id)\
                             .order_by(Analysis.olusturma_tarihi.desc())\
                             .all()
    
    return render_template('gecmis_kayitlar.html', analyses=analyses)


# PROFİL YÖNETİMİ ROUTE'LARI 
@app.route('/profile')
@login_required
def profile():
    """Kullanıcı profil bilgileri sayfası"""
    user = User.query.get(session['user_id'])
    return render_template('profilim.html', user=user)


@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    """Profil bilgilerini güncelleme (ad, soyad, telefon)"""
    user = User.query.get(session['user_id'])
    
    ad = request.form.get('ad')
    soyad = request.form.get('soyad')
    telefon = request.form.get('telefon')
    
    # Boş alan kontrolü
    if not all([ad, soyad, telefon]):
        flash('Tüm alanları doldurun', 'danger')
        return redirect(url_for('profile'))
    
    try:
        user.ad = ad
        user.soyad = soyad
        user.telefon = telefon
        
        db.session.commit()
        
        # Session'daki ismi güncelle
        session['user_name'] = f"{ad} {soyad}"
        
        flash('Profil bilgileriniz güncellendi', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Güncelleme hatasi: {str(e)}', 'danger')
        return redirect(url_for('profile'))


@app.route('/profile/password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Şifre değiştirme sayfası"""
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password_confirm = request.form.get('new_password_confirm')
        
        # Boş alan kontrolü
        if not all([old_password, new_password, new_password_confirm]):
            flash('Tüm alanları doldurun', 'danger')
            return redirect(url_for('change_password'))
        
        # Eski şifre doğrulama
        if not user.check_password(old_password):
            flash('Mevcut şifreniz yanlış', 'danger')
            return redirect(url_for('change_password'))
        
        # Yeni şifre uzunluk kontrolü
        if len(new_password) < 6:
            flash('Yeni şifre en az 6 karakter olmalıdır', 'danger')
            return redirect(url_for('change_password'))
        
        # Yeni şifrelerin eşleşme kontrolü
        if new_password != new_password_confirm:
            flash('Yeni şifreler eşleşmiyor', 'danger')
            return redirect(url_for('change_password'))
        
        try:
            user.set_password(new_password)
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Şifre değiştirme hatası: {str(e)}', 'danger')
            return redirect(url_for('change_password'))
    
    return render_template('sifre_degistir.html')


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    """Kullanıcı hesabını tamamen silme"""
    user = User.query.get(session['user_id'])
    password = request.form.get('password')
    
    # Şifre girilmiş mi kontrol et
    if not password:
        flash('Şifre gerekli', 'danger')
        return redirect(url_for('profile'))
    
    # Şifre doğrulama
    if not user.check_password(password):
        flash('Yanlış şifre', 'danger')
        return redirect(url_for('profile'))
    
    try:
        # 1. Batch'lere ait analizleri sil
        batch_ids = [b.id for b in BatchAnalysis.query.filter_by(kullanici_id=user.id).all()]
        if batch_ids:
            Analysis.query.filter(Analysis.batch_id.in_(batch_ids)).delete(synchronize_session=False)
            db.session.flush()
        
        # 2. Kullanıcının diğer analizlerini sil
        Analysis.query.filter_by(kullanici_id=user.id).delete()
        db.session.flush()
        
        # 3. Batch kayıtlarını sil
        BatchAnalysis.query.filter_by(kullanici_id=user.id).delete()
        db.session.flush()
        
        # 4. Kullanıcıyı sil
        db.session.delete(user)
        db.session.commit()
        
        # Session'ı temizle
        session.clear()
        
        flash('Hesabınız ve tüm verileriniz başarıyla silindi', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Hesap silme hatası: {str(e)}', 'danger')
        return redirect(url_for('profile'))


# DİL DEĞİŞTİRME 

@app.route('/set-language/<lang_code>')
def set_language(lang_code):
    """Uygulama dilini değiştirme (TR/EN)"""
    if lang_code in app.config['LANGUAGES']:
        session['language'] = lang_code
    return redirect(request.referrer or url_for('index'))


#ADMİN PANELİ ROUTE'LARI 

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin kontrol paneli - İstatistikler ve özet bilgiler"""
    # Genel istatistikler
    total_users = User.query.count()
    total_analyses = Analysis.query.count()
    total_batches = BatchAnalysis.query.count()
    
    # Model bazında istatistikler
    bone_count = Analysis.query.filter_by(model_tipi='bone').count()
    eye_count = Analysis.query.filter_by(model_tipi='eye').count()
    lung_count = Analysis.query.filter_by(model_tipi='lung').count()
    
    # Son kayıtlı kullanıcılar
    recent_users = User.query.order_by(User.olusturma_tarihi.desc()).limit(10).all()
    
    # Son yapılan analizler
    recent_analyses = Analysis.query.order_by(Analysis.olusturma_tarihi.desc()).limit(10).all()
    
    return render_template('admin_panel.html',
                         total_users=total_users,
                         total_analyses=total_analyses,
                         total_batches=total_batches,
                         bone_count=bone_count,
                         eye_count=eye_count,
                         lung_count=lung_count,
                         recent_users=recent_users,
                         recent_analyses=recent_analyses)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Tüm kullanıcıları listeleme sayfası (Admin)"""
    users = User.query.order_by(User.olusturma_tarihi.desc()).all()
    return render_template('admin_kullanicilar.html', users=users)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Admin tarafından kullanıcı silme"""
    user = User.query.get_or_404(user_id)
    
    # Admin kendi hesabını silemesin
    if user.id == session['user_id']:
        flash(_('Kendi hesabınızı silemezsiniz'), 'danger')
        return redirect(url_for('admin_users'))
    
    try:
        # Kullanıcının tüm verilerini sil
        Analysis.query.filter_by(kullanici_id=user.id).delete()
        BatchAnalysis.query.filter_by(kullanici_id=user.id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        flash(_('Kullanıcı başarıyla silindi'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Kullanıcı silinirken hata oluştu: {}').format(str(e)), 'danger')
    
    return redirect(url_for('admin_users'))


@app.route('/admin/analyses')
@admin_required
def admin_analyses():
    """Tüm analizleri listeleme sayfası (Admin)"""
    analyses = Analysis.query.order_by(Analysis.olusturma_tarihi.desc()).all()
    return render_template('admin_analizler.html', analyses=analyses)


#  TOPLU ANALİZ ROUTE'LARI 

@app.route('/analyze/batch/<model_type>')
@login_required
def batch_analyze(model_type):
    """Toplu (batch) analiz sayfası - Birden fazla görüntü yükleme"""
    # Model tipi kontrolü
    if model_type not in ['bone', 'eye', 'lung']:
        flash(_('Geçersiz model tipi'), 'danger')
        return redirect(url_for('dashboard'))
    
    model_names = {
        'bone': _('Kemik Kırığı Analizi'),
        'eye': _('Göz Hastalığı Analizi'),
        'lung': _('Akciğer (Zatürre) Analizi')
    }
    
    return render_template('toplu_analiz.html', 
                         model_type=model_type, 
                         model_name=model_names[model_type],
                         max_batch_size=app.config['MAX_BATCH_SIZE'])


@app.route('/analyze/batch/<model_type>/process', methods=['POST'])
@login_required
def batch_analyze_process(model_type):
    """Toplu analiz işleme - Birden fazla görüntüyü AI ile analiz et"""
    # Model tipi kontrolü
    if model_type not in ['bone', 'eye', 'lung']:
        return jsonify({'error': _('Geçersiz model tipi')}), 400
    
    # Yüklenen dosyaları al
    files = request.files.getlist('batch_files')
    
    # Dosya var mı kontrolü
    if not files or len(files) == 0:
        return jsonify({'error': _('Dosya seçilmedi')}), 400
    
    # Maksimum dosya sayısı kontrolü
    if len(files) > app.config['MAX_BATCH_SIZE']:
        return jsonify({'error': _('Maksimum {} dosya yükleyebilirsiniz').format(app.config['MAX_BATCH_SIZE'])}), 400
    
    try:
        # Batch kaydı oluştur
        batch = BatchAnalysis(
            kullanici_id=session['user_id'],
            model_tipi=model_type,
            toplam_dosya=len(files),
            durum='processing'
        )
        db.session.add(batch)
        db.session.commit()
        
        # Her dosyayı sırayla işle
        results = []
        for idx, file in enumerate(files):
            if file and allowed_file(file.filename):
                # Güvenli dosya adı oluştur
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{session['user_id']}_batch{batch.id}_{idx}_{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # AI tahmini yap
                result = ai_manager.predict(model_type, filepath)
                
                # Hata yoksa analiz kaydı oluştur
                if 'error' not in result:
                    analysis = Analysis(
                        kullanici_id=session['user_id'],
                        batch_id=batch.id,
                        model_tipi=model_type,
                        gorsel_dosya_adi=unique_filename,
                        tani_sonucu=result['diagnosis'],
                        guven_orani=result['confidence'],
                        sonuc_json=json.dumps(result, ensure_ascii=False)
                    )
                    db.session.add(analysis)
                    
                    results.append({
                        'filename': file.filename,
                        'diagnosis': result['diagnosis'],
                        'confidence': result['confidence'],
                        'image': unique_filename
                    })
                
                # İlerleme durumunu güncelle
                batch.tamamlanan_dosya = idx + 1
                db.session.commit()
        
        # Batch durumunu tamamlandı olarak işaretle
        batch.durum = 'completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'batch_id': batch.id,
            'results': results
        })
    
    except Exception as e:
        if batch:
            batch.durum = 'failed'
            db.session.commit()
        return jsonify({'error': str(e)}), 500


@app.route('/batch/result/<int:batch_id>')
@login_required
def batch_result(batch_id):
    """Toplu analiz sonuçlarını gösterme sayfası"""
    batch = BatchAnalysis.query.get_or_404(batch_id)
    
    # Kullanıcının kendi batch'ine erişip erişmediğini kontrol et
    if batch.kullanici_id != session['user_id']:
        flash(_('Bu sonuçlara erişim yetkiniz yok'), 'danger')
        return redirect(url_for('dashboard'))
    
    # Bu batch'e ait tüm analizleri getir
    analyses = Analysis.query.filter_by(batch_id=batch_id).all()
    
    return render_template('toplu_sonuc.html', batch=batch, analyses=analyses)

@app.cli.command()
def init_db():
    """Veritabanı tablolarını oluşturur"""
    db.create_all()
    print("Veritabanı tabloları oluşturuldu")


@app.cli.command()
def create_test_user():
    """Test amaçlı kullanıcı oluşturur"""
    test_user = User(
        tc_kimlik='12345678901',
        ad='Test',
        soyad='Kullanıcı',
        telefon='05551234567'
    )
    test_user.set_password('123456')
    
    db.session.add(test_user)
    db.session.commit()
    print("Test kullanicisi olusturuldu (TC: 12345678901, Sifre: 123456)")


@app.cli.command()
def create_admin():
    """Admin kullanıcısı oluşturur"""
    admin_user = User(
        tc_kimlik='99999999999',
        ad='Admin',
        soyad='User',
        telefon='05559999999',
        is_admin=True
    )
    admin_user.set_password('admin123')
    
    db.session.add(admin_user)
    db.session.commit()
    print("Admin kullanıcısı oluşturuldu (TC: 99999999999, Şifre: 727272)")


if __name__ == '__main__':
    with app.app_context():
        # Veritabanı tablolarını oluştur
        db.create_all()
        print("Flask uygulaması başlatılıyor...")
        print("Lütfen bekleyin, tarayıcı otomatik açılacak...")
    
    # Tarayıcıyı otomatik aç (sadece ilk başlatmada)
    import webbrowser
    from threading import Timer
    
    def open_browser():
        """Tarayıcıyı otomatik açar (Flask reloader çalışırken tekrar açmaz)"""
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open_new("http://localhost:5000")
    
    Timer(1.5, open_browser).start()
    
    # Flask uygulamasını başlat (debug modu açık)
    app.run(debug=True, host='0.0.0.0', port=5000)