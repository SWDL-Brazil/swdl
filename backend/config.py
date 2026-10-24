# =============================================================
#  SWDL — config.py
# =============================================================
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Segurança
    SECRET_KEY = os.environ['SECRET_KEY']

    # Banco de dados
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url or f'sqlite:///{os.path.join(BASE_DIR, "swdl.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload de arquivos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

    # Ambiente
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'

    # Sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = ENV == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # WTForms CSRF
    WTF_CSRF_ENABLED = True