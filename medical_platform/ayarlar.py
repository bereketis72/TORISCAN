import os
from urllib.parse import quote_plus

class Config:
    # Flask güvenlik anahtarı
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    
    # MSSQL Veritabanı bağlantı bilgileri
    DB_SERVER = os.environ.get('DB_SERVER') or 'Bereket\\SQLEXPRESS02'
    DB_NAME = os.environ.get('DB_NAME') or 'MedicalPlatform'
    DB_USERNAME = os.environ.get('DB_USERNAME') or 'sa'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '727272'
    
    # Windows Authentication kullan (True/False)
    USE_WINDOWS_AUTH = os.environ.get('USE_WINDOWS_AUTH', 'False').lower() == 'true'
    
    # Veritabanı bağlantı string'i oluştur
    if USE_WINDOWS_AUTH:
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes'
    else:
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
    
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Dosya yükleme ayarları
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # AI modelleri klasörü
    MODELS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models_ai')
    
    # Session ayarları
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 saat
    
    # Babel - Multi-language desteği
    BABEL_DEFAULT_LOCALE = 'tr'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    LANGUAGES = {
        'tr': 'Türkçe',
        'en': 'English'
    }
    
    # Batch analiz ayarları
    MAX_BATCH_SIZE = 10  # Tek seferde maximum 10 dosya
