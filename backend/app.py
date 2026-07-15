# =============================================================
#  SWDL — app.py
# =============================================================

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask
from extensions import db, login_manager, socketio
from config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta área.'
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app)

    # Handler global para capturar erros 500
    import traceback, sys
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f'500 error: {e}')
        tb = traceback.format_exc()
        logger.error(tb)
        db.session.rollback()
        return f'500 Error<br><pre>{tb}</pre>', 500

    # Registra blueprints
    from routes.auth     import auth_bp
    from routes.admin    import admin_bp
    from routes.api      import api_bp
    from routes.vote     import vote_bp
    from routes.student  import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,   url_prefix='/admin')
    app.register_blueprint(api_bp,     url_prefix='/api')
    app.register_blueprint(vote_bp)
    app.register_blueprint(student_bp)

    # Cria as tabelas se não existirem
    with app.app_context():
        # Importar models para garantir que o SQLAlchemy os conheça
        from models.user import User
        from models.inscription import Inscription
        from models.delegation import Delegation
        from models.news import News
        from models.agenda import AgendaItem
        from models.vote import VoteSession, Vote
        from models.theme import Theme
        from models.document import Document
        from models.student import Student
        from models.participation import ParticipationHistory
        from models.event_config import EventConfig
        from models.system_config import SystemConfig

        db.create_all()
        _run_migrations(app)
        _seed_admin(app)

    return app


def _run_migrations(app):
    """Migration: adiciona colunas novas em tabelas existentes."""
    with app.app_context():
        import sqlalchemy as sa
        is_pg = db.engine.dialect.name == 'postgresql'

        _bool = 'BOOLEAN DEFAULT FALSE' if is_pg else 'BOOLEAN DEFAULT 0'
        _bool_true = 'BOOLEAN DEFAULT TRUE' if is_pg else 'BOOLEAN DEFAULT 1'
        migs = [
            ('delegations', 'theme_id', 'INTEGER REFERENCES themes(id)'),
            ('news', 'slug', 'VARCHAR(100)'),
            ('news', 'excerpt', 'VARCHAR(300)'),
            ('news', 'cover_image', 'VARCHAR(300)'),
            ('news', 'updated_at', 'TIMESTAMP' if is_pg else 'DATETIME'),
            ('news', 'is_crisis', 'BOOLEAN'),
            ('news', 'committee', 'VARCHAR(30)'),
            ('students', 'read_only', _bool),
            ('students', 'adapted_device', _bool),
            ('students', 'certificate_hash', 'VARCHAR(128)'),
            ('students', 'certificate_url', 'VARCHAR(500)'),
            ('students', 'certificate_released', _bool),
            ('students', 'convened', _bool),
            ('documents', 'category', "VARCHAR(50) DEFAULT 'guias'"),
            ('delegations', 'flag_url', 'VARCHAR(300)'),
            ('delegations', 'presence_status', "VARCHAR(20) DEFAULT 'ausente'"),
            ('delegations', 'flag_animation', _bool_true),
            ('delegations', 'orador', _bool),
            ('event_config', 'inscricoes_abertas', _bool),
            ('event_config', 'invoke_url', "VARCHAR(500) DEFAULT ''"),
            ('event_config', 'invoke_label', "VARCHAR(100) DEFAULT ''"),
            ('event_config', 'invoke_active', _bool),
            ('event_config', 'invoke_at', 'TIMESTAMP' if is_pg else 'DATETIME'),
            ('news', 'category_id', 'INTEGER REFERENCES categories(id)'),
            ('students', 'digital_signature', 'TEXT'),
        ]

        for table, col, col_type in migs:
            try:
                if is_pg:
                    stmt = f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}'
                else:
                    # SQLite: check if column exists first
                    with db.engine.connect() as conn:
                        import sqlite3
                        cols = [c['name'] for c in sa.inspect(db.engine).get_columns(table)]
                        if col not in cols:
                            conn.execute(sa.text(f'ALTER TABLE {table} ADD COLUMN {col} {col_type}'))
                            conn.commit()
                            print(f'[MIGRATION] Coluna {table}.{col} criada.')
                if is_pg:
                    with db.engine.connect() as conn:
                        conn.execute(sa.text(stmt))
                        conn.commit()
                        print(f'[MIGRATION] Coluna {table}.{col} criada.')
            except Exception as e:
                print(f'[MIGRATION] Erro ao adicionar {table}.{col}: {e}')


def _seed_admin(app):
    from models.user import User
    from models.event_config import EventConfig
    with app.app_context():
        if not User.query.filter_by(email='admin@swdl.com').first():
            admin = User(
                name='Administrador SWDL',
                email='admin@swdl.com',
                role='admin'
            )
            admin.set_password('swdl2025')
            db.session.add(admin)
            db.session.commit()
            print('[SWDL] Admin padrão criado → admin@swdl.com / swdl2025')

        # Garante que o EventConfig existe (via raw SQL para evitar erro de schema)
        import sqlalchemy as sa
        try:
            cfg = db.session.execute(sa.text('SELECT id, phase FROM event_config LIMIT 1')).fetchone()
        except Exception:
            cfg = None
        if not cfg:
            db.session.execute(sa.text("INSERT INTO event_config (phase) VALUES ('pre')"))
            db.session.commit()
            print('[SWDL] EventConfig criado (fase: pre).')


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)