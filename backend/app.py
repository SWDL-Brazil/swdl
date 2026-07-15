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


def _to_pg_type(col):
    """Converte tipo SQLAlchemy para string DDL PostgreSQL."""
    t = type(col.type)
    if t.__name__ == 'Boolean':
        return 'BOOLEAN DEFAULT FALSE'
    if t.__name__ == 'DateTime':
        return 'TIMESTAMP'
    if t.__name__ == 'Text':
        return 'TEXT'
    if t.__name__ == 'Integer':
        fk = list(col.foreign_keys)
        ref = ', '.join(f'{fk.column.table.name}({fk.column.name})' for fk in fk) if fk else ''
        return f'INTEGER REFERENCES {ref}' if ref else 'INTEGER'
    if t.__name__ == 'String':
        length = getattr(col.type, 'length', 255)
        return f'VARCHAR({length})'
    return 'TEXT'


def _run_migrations(app):
    """Adiciona colunas novas em todas as tabelas existentes."""
    with app.app_context():
        import sqlalchemy as sa
        is_pg = db.engine.dialect.name == 'postgresql'
        inspector = sa.inspect(db.engine)

        from models.user import User
        from models.delegation import Delegation
        from models.inscription import Inscription
        from models.news import News
        from models.student import Student
        from models.document import Document
        from models.event_config import EventConfig
        from models.theme import Theme
        from models.category import Category
        from models.agenda import AgendaItem
        from models.audit_log import AuditLog
        from models.participation import ParticipationHistory
        from models.urgent_alert import UrgentAlert
        from models.vote import VoteSession, Vote
        from models.system_config import SystemConfig

        tables = {
            User.__tablename__: User,
            Delegation.__tablename__: Delegation,
            Inscription.__tablename__: Inscription,
            News.__tablename__: News,
            Student.__tablename__: Student,
            Document.__tablename__: Document,
            EventConfig.__tablename__: EventConfig,
            Theme.__tablename__: Theme,
            Category.__tablename__: Category,
            AgendaItem.__tablename__: AgendaItem,
            AuditLog.__tablename__: AuditLog,
            ParticipationHistory.__tablename__: ParticipationHistory,
            UrgentAlert.__tablename__: UrgentAlert,
            VoteSession.__tablename__: VoteSession,
            Vote.__tablename__: Vote,
            SystemConfig.__tablename__: SystemConfig,
        }

        for table_name, model in tables.items():
            try:
                existing = {c['name'] for c in inspector.get_columns(table_name)}
            except Exception:
                continue  # tabela não existe
            for col_name, col in model.__table__.columns.items():
                if col_name in existing or col_name == 'id':
                    continue
                col_type = _to_pg_type(col)
                try:
                    if is_pg:
                        stmt = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type}'
                        with db.engine.connect() as conn:
                            conn.execute(sa.text(stmt))
                            conn.commit()
                    else:
                        with db.engine.connect() as conn:
                            conn.execute(sa.text(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}'))
                            conn.commit()
                    print(f'[MIGRATION] Coluna {table_name}.{col_name} criada.')
                except Exception as e:
                    print(f'[MIGRATION] Erro ao adicionar {table_name}.{col_name}: {e}')


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