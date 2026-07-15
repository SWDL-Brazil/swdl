# =============================================================
#  SWDL — extensions.py
# =============================================================
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db            = SQLAlchemy()
login_manager = LoginManager()

# Usa gevent em produção, threading em desenvolvimento
async_mode = 'gevent' if os.environ.get('FLASK_ENV') == 'production' else 'threading'
socketio   = SocketIO(cors_allowed_origins="*", async_mode=async_mode)