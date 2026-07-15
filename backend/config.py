# =============================================================
#  SWDL — config.py
# =============================================================
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY', 'swdl-secret-change-in-production')

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

    # Sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # WTForms CSRF
    WTF_CSRF_ENABLED = True

    # Ambiente
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'