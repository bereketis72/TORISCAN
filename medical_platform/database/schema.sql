-- Medical Platform Veritabanı Şeması 

-- Veritabanı oluştur
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'MedicalPlatform')
BEGIN
    CREATE DATABASE MedicalPlatform;
END
GO

USE MedicalPlatform;
GO

-- Eski tabloları sil (eğer varsa)
-- Önce child tablolar silinmeli (Foreign Key kısıtlamaları yüzünden)
IF EXISTS (SELECT * FROM sysobjects WHERE name='analizler' AND xtype='U')
BEGIN
    DROP TABLE analizler;
    PRINT 'Eski analizler tablosu silindi';
END
GO

IF EXISTS (SELECT * FROM sysobjects WHERE name='toplu_analizler' AND xtype='U')
BEGIN
    DROP TABLE toplu_analizler;
    PRINT 'Eski toplu_analizler tablosu silindi';
END
GO

IF EXISTS (SELECT * FROM sysobjects WHERE name='kullanicilar' AND xtype='U')
BEGIN
    DROP TABLE kullanicilar;
    PRINT 'Eski kullanicilar tablosu silindi';
END
GO

-- Kullanıcılar Tablosu 
CREATE TABLE kullanicilar (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tc_kimlik NVARCHAR(11) NOT NULL UNIQUE,
    ad NVARCHAR(50) NOT NULL,
    soyad NVARCHAR(50) NOT NULL,
    telefon NVARCHAR(15) NOT NULL,
    sifre_hash NVARCHAR(255) NOT NULL,
    is_admin BIT NOT NULL DEFAULT 0,
    olusturma_tarihi DATETIME DEFAULT GETDATE()
);

-- Index oluştur
CREATE INDEX idx_kullanicilar_tc_kimlik ON kullanicilar(tc_kimlik);

PRINT 'Kullanicilar tablosu oluşturuldu';
GO

-- Toplu Analizler Tablosu
CREATE TABLE toplu_analizler (
    id INT IDENTITY(1,1) PRIMARY KEY,
    kullanici_id INT NOT NULL,
    model_tipi NVARCHAR(20) NOT NULL,
    durum NVARCHAR(20) NOT NULL DEFAULT 'processing',
    toplam_dosya INT DEFAULT 0,
    tamamlanan_dosya INT DEFAULT 0,
    olusturma_tarihi DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT FK_toplu_analizler_kullanicilar FOREIGN KEY (kullanici_id) 
        REFERENCES kullanicilar(id) ON DELETE CASCADE
);

CREATE INDEX idx_batch_user ON toplu_analizler(kullanici_id);
CREATE INDEX idx_batch_date ON toplu_analizler(olusturma_tarihi);

PRINT 'Toplu analizler tablosu oluşturuldu';
GO

-- Analizler Tablosu (Türkçe)
CREATE TABLE analizler (
    id INT IDENTITY(1,1) PRIMARY KEY,
    kullanici_id INT NOT NULL,
    batch_id INT NULL,
    model_tipi NVARCHAR(20) NOT NULL,
    gorsel_dosya_adi NVARCHAR(255) NOT NULL,
    tani_sonucu NVARCHAR(100) NOT NULL,
    guven_orani FLOAT NOT NULL,
    sonuc_json NVARCHAR(MAX),
    olusturma_tarihi DATETIME DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_analizler_kullanicilar FOREIGN KEY (kullanici_id) 
        REFERENCES kullanicilar(id) ON DELETE CASCADE,
        
    CONSTRAINT FK_analizler_batch FOREIGN KEY (batch_id) 
        REFERENCES toplu_analizler(id)
);

-- Index'ler oluştur
CREATE INDEX idx_analizler_kullanici_id ON analizler(kullanici_id);
CREATE INDEX idx_analizler_olusturma_tarihi ON analizler(olusturma_tarihi);
CREATE INDEX idx_analizler_batch_id ON analizler(batch_id);

PRINT 'Analizler tablosu oluşturuldu';
GO

-- Şifre Gizleme VIEW'ı Oluştur
IF NOT EXISTS (SELECT * FROM sys.views WHERE name='KullanicilarGizli')
BEGIN
    CREATE VIEW KullanicilarGizli AS
    SELECT 
        id,
        tc_kimlik,
        ad,
        soyad,
        telefon,
        REPLICATE('*', 10) AS sifre_hash,  -- Şifreyi otomatik maskele
        is_admin,
        olusturma_tarihi
    FROM kullanicilar;
    
    PRINT 'KullanicilarGizli VIEW oluşturuldu (şifreler otomatik gizlenir)';
END
GO

PRINT 'Veritabanı şeması başarıyla oluşturuldu!';
PRINT 'Tablolar: kullanicilar, toplu_analizler, analizler';
PRINT 'VIEW: KullanicilarGizli';
