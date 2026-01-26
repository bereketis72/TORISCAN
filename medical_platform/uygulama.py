from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import Babel, gettext as _
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
from ayarlar import Config
from veritabani_modelleri import db, User, Analysis, BatchAnalysis
from yapay_zeka_modelleri import AIModelManager

app = Flask(__name__)
app.config.from_object(Config)

# Veritabanini baslat
db.init_app(app)

# Babel for multi-language support
babel = Babel(app)

def get_locale():
    """Kullanıcının dil tercihini belirle"""
    return session.get('language', app.config['BABEL_DEFAULT_LOCALE'])

babel.init_app(app, locale_selector=get_locale)

# AI Model Manager'i baslat
ai_manager = None

def init_ai_models():
    """AI modellerini yükle"""
    global ai_manager
    if ai_manager is None:
        ai_manager = AIModelManager(app.config['MODELS_FOLDER'])

# Template filter - UTC'den Turkiye saatine cevir
@app.template_filter('datetime_tr')
def datetime_tr_filter(dt):
    """UTC datetime'i Turkiye saatine (UTC+3) cevirir"""
    if dt is None:
        return ''
    # UTC+3 ekle
    tr_time = dt + timedelta(hours=3)
    return tr_time.strftime('%d.%m.%Y %H:%M')

@app.before_request
def before_first_request():
    """İlk istek Öncesi çalışır"""
    init_ai_models()

def allowed_file(filename):
    """Dosya uzantısı kontrolü"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    """Login kontrolü için decorator"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('Lütfen giriş yapın'), 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Admin yetkisi kontrolü için decorator"""
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

# ================== ROUTES ==================

@app.route('/')
def index():
    """Ana sayfa"""
    # if 'user_id' in session:
    #     return redirect(url_for('dashboard'))
    return render_template('ana_sayfa.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kaydı"""
    if request.method == 'POST':
        tc_kimlik = request.form.get('tc_kimlik')
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        telefon = request.form.get('telefon')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validasyon
        if not all([tc_kimlik, ad, soyad, telefon, password, password_confirm]):
            flash('Tüm alanları doldurun', 'danger')
            return redirect(url_for('register'))
        
        if len(tc_kimlik) != 11 or not tc_kimlik.isdigit():
            flash('TC Kimlik numarası 11 haneli olmalıdır', 'danger')
            return redirect(url_for('register'))
        
        if password != password_confirm:
            flash('Şifreler eşleşmiyor', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır', 'danger')
            return redirect(url_for('register'))
        
        # TC Kimlik kontrolu
        existing_user = User.query.filter_by(tc_kimlik=tc_kimlik).first()
        if existing_user:
            flash('Bu TC Kimlik numarası zaten kayıtlı', 'danger')
            return redirect(url_for('register'))
        
        # Yeni kullanici olustur
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
    """Kullanıcı girişi"""
    if request.method == 'POST':
        tc_kimlik = request.form.get('tc_kimlik')
        password = request.form.get('password')
        
        if not tc_kimlik or not password:
            flash('TC Kimlik ve şifre gerekli', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(tc_kimlik=tc_kimlik).first()
        
        if user:
            if user.check_password(password):
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
    """Çıkış"""
    session.clear()
    flash('Çıkış yapıldı', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı paneli - Model seçimi"""
    user = User.query.get(session['user_id'])
    
    # Kullanicinin son analizleri
    recent_analyses = Analysis.query.filter_by(kullanici_id=user.id)\
                                   .order_by(Analysis.olusturma_tarihi.desc())\
                                   .limit(5)\
                                   .all()
    
    return render_template('panel.html', user=user, recent_analyses=recent_analyses)


@app.route('/analyze/<model_type>', methods=['GET', 'POST'])
@login_required
def analyze(model_type):
    """Görüntü yükleme ve analiz"""
    if model_type not in ['bone', 'eye', 'lung']:
        flash('Geçersiz model tipi', 'danger')
        return redirect(url_for('dashboard'))
    
    model_names = {
        'bone': 'Kemik Kırığı Analizi',
        'eye': 'Göz Hastalığı Analizi',
        'lung': 'Akciğer (Zaturre) Analizi'
    }
    
    if request.method == 'POST':
        # Dosya kontrolu
        if 'xray_image' not in request.files:
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)
        
        file = request.files['xray_image']
        
        if file.filename == '':
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Dosyayi kaydet
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{session['user_id']}_{model_type}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # AI tahmini yap
            result = ai_manager.predict(model_type, filepath)
            
            if 'error' in result:
                flash(f'Analiz hatası: {result["error"]}', 'danger')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
            
            # Sonucu veritabanina kaydet
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
    """Analiz sonucu göster"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Kullanicinin kendi analizi mi kontrol et
    if analysis.kullanici_id != session['user_id']:
        flash('Bu sonuca erişim yetkiniz yok', 'danger')
        return redirect(url_for('dashboard'))
    
    # JSON sonucu parse et
    result_data = json.loads(analysis.sonuc_json) if analysis.sonuc_json else {}
    
    return render_template('analiz_sonucu.html', analysis=analysis, result_data=result_data)


@app.route('/history')
@login_required
def history():
    """Geçmis analizler"""
    user = User.query.get(session['user_id'])
    analyses = Analysis.query.filter_by(kullanici_id=user.id)\
                             .order_by(Analysis.olusturma_tarihi.desc())\
                             .all()
    
    return render_template('gecmis_kayitlar.html', analyses=analyses)


@app.route('/profile')
@login_required
def profile():
    """Kullanıcı profili"""
    user = User.query.get(session['user_id'])
    return render_template('profilim.html', user=user)


@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    """Profil bilgilerini güncelle"""
    user = User.query.get(session['user_id'])
    
    ad = request.form.get('ad')
    soyad = request.form.get('soyad')
    telefon = request.form.get('telefon')
    
    if not all([ad, soyad, telefon]):
        flash('Tüm alanları doldurun', 'danger')
        return redirect(url_for('profile'))
    
    try:
        user.ad = ad
        user.soyad = soyad
        user.telefon = telefon
        
        db.session.commit()
        
        # Session'daki user_name'i guncelle
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
    """Şifre değiştirme"""
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password_confirm = request.form.get('new_password_confirm')
        
        if not all([old_password, new_password, new_password_confirm]):
            flash('Tüm alanları doldurun', 'danger')
            return redirect(url_for('change_password'))
        
        # Eski sifre kontrolu
        if not user.check_password(old_password):
            flash('Mevcut şifreniz yanlış', 'danger')
            return redirect(url_for('change_password'))
        
        # Yeni sifre uzunluk kontrolu
        if len(new_password) < 6:
            flash('Yeni şifre en az 6 karakter olmalıdır', 'danger')
            return redirect(url_for('change_password'))
        
        # Yeni sifre eslesme kontrolu
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
    """Hesabı sil"""
    user = User.query.get(session['user_id'])
    password = request.form.get('password')
    
    if not password:
        flash('Şifre gerekli', 'danger')
        return redirect(url_for('profile'))


# ================== LANGUAGE ROUTES ==================

@app.route('/set-language/<lang_code>')
def set_language(lang_code):
    """Dil değiştirme"""
    if lang_code in app.config['LANGUAGES']:
        session['language'] = lang_code
    return redirect(request.referrer or url_for('index'))


# ================== ADMIN ROUTES ==================

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin kontrol paneli"""
    # İstatistikler
    total_users = User.query.count()
    total_analyses = Analysis.query.count()
    total_batches = BatchAnalysis.query.count()
    
    # Model bazında istatistikler
    bone_count = Analysis.query.filter_by(model_tipi='bone').count()
    eye_count = Analysis.query.filter_by(model_tipi='eye').count()
    lung_count = Analysis.query.filter_by(model_tipi='lung').count()
    
    # Son kullanıcılar
    recent_users = User.query.order_by(User.olusturma_tarihi.desc()).limit(10).all()
    
    # Son analizler
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
    """Tüm kullanıcıları listele"""
    users = User.query.order_by(User.olusturma_tarihi.desc()).all()
    return render_template('admin_kullanicilar.html', users=users)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Kullanıcıyı sil"""
    user = User.query.get_or_404(user_id)
    
    # Kendi hesabını silemesin
    if user.id == session['user_id']:
        flash(_('Kendi hesabınızı silemezsiniz'), 'danger')
        return redirect(url_for('admin_users'))
    
    try:
        # Kullanıcının analizlerini sil
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
    """Tüm analizleri listele"""
    analyses = Analysis.query.order_by(Analysis.olusturma_tarihi.desc()).all()
    return render_template('admin_analizler.html', analyses=analyses)


# ================== BATCH ANALYSIS ROUTES ==================

@app.route('/analyze/batch/<model_type>')
@login_required
def batch_analyze(model_type):
    """Batch analiz sayfası"""
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
    """Batch analiz işleme"""
    if model_type not in ['bone', 'eye', 'lung']:
        return jsonify({'error': _('Geçersiz model tipi')}), 400
    
    # Dosyaları al
    files = request.files.getlist('batch_files')
    
    if not files or len(files) == 0:
        return jsonify({'error': _('Dosya seçilmedi')}), 400
    
    if len(files) > app.config['MAX_BATCH_SIZE']:
        return jsonify({'error': _('Maksimum {} dosya yükleyebilirsiniz').format(app.config['MAX_BATCH_SIZE'])}), 400
    
    # Batch kaydı oluştur
    try:
        batch = BatchAnalysis(
            kullanici_id=session['user_id'],
            model_tipi=model_type,
            toplam_dosya=len(files),
            durum='processing'
        )
        db.session.add(batch)
        db.session.commit()
        
        # Her dosyayı işle
        results = []
        for idx, file in enumerate(files):
            if file and allowed_file(file.filename):
                # Dosyayı kaydet
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{session['user_id']}_batch{batch.id}_{idx}_{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # AI tahmini yap
                result = ai_manager.predict(model_type, filepath)
                
                if 'error' not in result:
                    # Analiz kaydı oluştur
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
                
                # Progress güncelle
                batch.tamamlanan_dosya = idx + 1
                db.session.commit()
        
        # Batch durumunu güncelle
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
    """Batch sonuçları"""
    batch = BatchAnalysis.query.get_or_404(batch_id)
    
    # Kullanıcının kendi batch'i mi kontrol et
    if batch.kullanici_id != session['user_id']:
        flash(_('Bu sonuçlara erişim yetkiniz yok'), 'danger')
        return redirect(url_for('dashboard'))
    
    # Batch içindeki tüm analizleri al
    analyses = Analysis.query.filter_by(batch_id=batch_id).all()
    
    return render_template('toplu_sonuc.html', batch=batch, analyses=analyses)
    
    # Sifre kontrolu
    if not user.check_password(password):
        flash('Şifre yanlış. Hesap silinemedi.', 'danger')
        return redirect(url_for('profile'))
    
    try:
        # Kullanicinin tum analizlerini sil
        Analysis.query.filter_by(kullanici_id=user.id).delete()
        
        # Kullaniciyi sil
        db.session.delete(user)
        db.session.commit()
        
        # Session'i temizle
        session.clear()
        
        flash('Hesabınız başarıyla  silindi', 'info')
        return redirect(url_for('index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Hesap silme hatası: {str(e)}', 'danger')
        return redirect(url_for('profile'))




@app.cli.command()
def init_db():
    """Veritabanını oluştur"""
    db.create_all()
    print("Veritabanı tabloları oluşturuldu")


@app.cli.command()
def create_test_user():
    """Test kullanıcısını oluştur"""
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
    """Admin kullanıcısı oluştur"""
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
    print("Admin kullanıcısı oluşturuldu (TC: 99999999999, Şifre: admin123)")


if __name__ == '__main__':
    with app.app_context():
        # Veritabani tablolarini olustur
        db.create_all()
        print("Flask uygulaması başlatılıyor...")
        print("Lütfen bekleyin, tarayıcı otomatik açılacak...")
    
    # Tarayiciyi otomatik ac
    import webbrowser
    from threading import Timer
    
    # Tarayiciyi otomatik ac (Sadece ilk baslatmada, reloader restart ettiginde degil)
    import webbrowser
    from threading import Timer
    
    def open_browser():
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open_new("http://localhost:5000")
        
    Timer(1.5, open_browser).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
