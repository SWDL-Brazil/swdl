# =============================================================
#  SWDL — extensions.py
# =============================================================
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db            = SQLAlchemy()
login_manager = LoginManager()

# Detecta gevent automaticamente (Render não seta FLASK_ENV)
try:
    import gevent  # noqa
    async_mode = 'gevent'
except ImportError:
    async_mode = 'threading'

cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
socketio   = SocketIO(cors_allowed_origins=cors_origins, async_mode=async_mode,
                      manage_session=False, logger=False, engineio_logger=False,
                      ping_timeout=30, ping_interval=25)