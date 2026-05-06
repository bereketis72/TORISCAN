"""
Veritabanı şemasını güncellemek için migration script
Bu dosyayı çalıştırarak yeni kolonları ekleyebilirsiniz.
"""
import sys
import os
# Parent klasörü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyodbc
from ayarlar import Config

def update_database():
    """Veritabanı şemasını güncelle"""
    
    # Bağlantı oluştur
    if Config.USE_WINDOWS_AUTH:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={Config.DB_SERVER};DATABASE={Config.DB_NAME};Trusted_Connection=yes'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={Config.DB_SERVER};DATABASE={Config.DB_NAME};UID={Config.DB_USERNAME};PWD={Config.DB_PASSWORD}'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Veritabanına bağlandı...")
        
        # 1. is_admin kolonu ekle
        print("\n1. User tablosunu güncelleniyor...")
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.columns 
                               WHERE object_id = OBJECT_ID(N'kullanicilar') 
                               AND name = 'is_admin')
                BEGIN
                    ALTER TABLE kullanicilar
                    ADD is_admin BIT NOT NULL DEFAULT 0;
                END
            """)
            conn.commit()
            print("   ✓ is_admin kolonu eklendi")
        except Exception as e:
            print(f"   ! is_admin kolonu zaten mevcut veya hata: {e}")
        
        # 2. BatchAnalysis tablosu oluştur
        print("\n2. BatchAnalysis tablosu oluşturuluyor...")
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects 
                               WHERE object_id = OBJECT_ID(N'toplu_analizler') 
                               AND type in (N'U'))
                BEGIN
                    CREATE TABLE toplu_analizler (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        kullanici_id INT NOT NULL,
                        model_tipi VARCHAR(20) NOT NULL,
                        durum VARCHAR(20) NOT NULL DEFAULT 'processing',
                        toplam_dosya INT DEFAULT 0,
                        tamamlanan_dosya INT DEFAULT 0,
                        olusturma_tarihi DATETIME DEFAULT GETUTCDATE(),
                        FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id)
                    );
                    
                    CREATE INDEX idx_batch_user ON toplu_analizler(kullanici_id);
                    CREATE INDEX idx_batch_date ON toplu_analizler(olusturma_tarihi);
                END
            """)
            conn.commit()
            print("   ✓ toplu_analizler tablosu oluşturuldu")
        except Exception as e:
            print(f"   ! toplu_analizler tablosu zaten mevcut veya hata: {e}")
        
        # 3. batch_id kolonu ekle
        print("\n3. Analysis tablosu güncelleniyor...")
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.columns 
                               WHERE object_id = OBJECT_ID(N'analizler') 
                               AND name = 'batch_id')
                BEGIN
                    ALTER TABLE analizler
                    ADD batch_id INT NULL;
                    
                    ALTER TABLE analizler
                    ADD CONSTRAINT FK_analizler_batch
                    FOREIGN KEY (batch_id) REFERENCES toplu_analizler(id);
                    
                    CREATE INDEX idx_analysis_batch ON analizler(batch_id);
                END
            """)
            conn.commit()
            print("   ✓ batch_id kolonu eklendi")
        except Exception as e:
            print(f"   ! batch_id kolonu zaten mevcut veya hata: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Veritabanı güncellemeleri tamamlandı!")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return False

if __name__ == '__main__':
    update_database()
