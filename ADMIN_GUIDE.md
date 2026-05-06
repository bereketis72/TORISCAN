# Admin Girişi Nasıl Yapılır?

## 1. Admin Kullanıcısı Oluşturma

Terminal'de şu komutu çalıştırın:
```powershell
cd C:\Users\berek\Desktop\medical\medical_platform
flask create-admin
```

Bu komut otomatik olarak admin kullanıcısı oluşturur:
- **TC Kimlik:** 99999999999
- **Şifre:** admin123

## 2. Admin Olarak Giriş Yapma

1. Uygulamayı başlatın: `python uygulama.py`
2. Tarayıcıda `http://localhost:5000` adresine gidin
3. **"Giriş Yap"** butonuna tıklayın
4. Giriş bilgilerini girin:
   - TC Kimlik: **99999999999**
   - Şifre: **admin123**
5. Giriş yaptıktan sonra navbar'da **kırmızı "Admin Panel"** butonu görünecek

## 3. Admin Paneline Erişim

Admin olarak giriş yaptıktan sonra:
- Navbar'da (sağ üstte) **kırmızı "Admin Panel"** butonunu göreceksiniz
- Bu butona tıklayarak admin paneline erişebilirsiniz
- Admin panel URL'i: `http://localhost:5000/admin`

## Admin Panel Özellikleri

✅ **İstatistikler:**
- Toplam kullanıcı sayısı
- Toplam analiz sayısı
- Model bazında kullanım istatistikleri

✅ **Kullanıcı Yönetimi:**
- Tüm kullanıcıları listeleme
- Kullanıcı silme (kendi hesabınız hariç)

✅ **Analiz Yönetimi:**
- Tüm analizleri görüntüleme
- Batch analizleri takip etme

## Önemli Notlar

⚠️ Normal kullanıcılar admin paneline **erişemez**
⚠️ Admin butonunu sadece **admin kullanıcılar** görebilir
⚠️ Admin, kendi hesabını **silemez**
