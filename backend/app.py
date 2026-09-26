# =============================================================
#  SWDL — app.py
# =============================================================

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
from flask import Flask
from flask_cors import CORS
from extensions import db, login_manager, socketio, csrf
from config import Config


# ── Instrumentação de performance (Fase 0) ───────────────────────
_perf_queries_registered = False


def _count_query(conn, cursor, statement, parameters, context, executemany):
    """Conta queries SQL executadas dentro da request atual."""
    try:
        from flask import g, has_request_context
        if has_request_context():
            g._perf_queries = getattr(g, '_perf_queries', 0) + 1
    except Exception:
        pass


def _setup_perf(app):
    """Headers X-Request-Time / X-Query-Count + log de requests lentas.

    - Todo request expõe o custo no header (visível no DevTools → Network).
    - Requests com tempo >= PERF_SLOW_MS (default 300) viram warning no
      stdout, aparecendo no Render → Logs como "SLOW ...".
    """
    global _perf_queries_registered
    if not _perf_queries_registered:
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        event.listen(Engine, 'before_cursor_execute', _count_query)
        _perf_queries_registered = True

    slow_ms = float(os.environ.get('PERF_SLOW_MS', '300'))

    @app.before_request
    def _perf_start():
        import time
        from flask import g
        g._perf_t0 = time.perf_counter()
        g._perf_queries = 0

    @app.after_request
    def _perf_end(response):
        import time
        from flask import g, request
        t0 = getattr(g, '_perf_t0', None)
        if t0 is None:
            return response
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        queries = getattr(g, '_perf_queries', 0)
        response.headers['X-Request-Time'] = f'{elapsed_ms:.0f}ms'
        response.headers['X-Query-Count'] = str(queries)
        if elapsed_ms >= slow_ms:
            logger.warning('SLOW %.0fms queries=%d %s %s status=%s',
                           elapsed_ms, queries, request.method,
                           request.path, response.status_code)
        return response


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta área.'
    socketio.init_app(app)
    csrf.init_app(app)
    CORS(app, origins=[
        'https://swdl-5a3fa.web.app',
        'https://swdl-5a3fa.firebaseapp.com',
        'https://swdl.vercel.app',
        'https://swdl-git-*.vercel.app',
        'http://localhost:3000',
        'http://localhost:3001',
    ])

    # Instrumentação de performance (headers + log de SLOW)
    _setup_perf(app)

    @app.route('/favicon.ico')
    def favicon():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'favicon.svg', mimetype='image/svg+xml')

    # Handler global para capturar erros 500
    import traceback, sys
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f'500 error: {e}')
        tb = traceback.format_exc()
        logger.error(tb)
        db.session.rollback()
        if app.config.get('DEBUG'):
            return f'500 Error<br><pre>{tb}</pre>', 500
        return 'Erro interno do servidor.', 500

    # Registra blueprints
    from routes.auth     import auth_bp
    from routes.admin    import admin_bp
    from routes.api      import api_bp
    from routes.vote     import vote_bp
    from routes.student  import student_bp
    from routes.speaker_queue import speaker_bp
    from routes.motion   import motion_bp
    from routes.resolution import resolution_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,   url_prefix='/admin')
    app.register_blueprint(api_bp,     url_prefix='/api')
    app.register_blueprint(vote_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(speaker_bp)
    app.register_blueprint(motion_bp)
    app.register_blueprint(resolution_bp)
    app.register_blueprint(analytics_bp)

    # Cria as tabelas se não existirem
    with app.app_context():
        # Importar models para garantir que o SQLAlchemy os conheça
        from models.user import User
        from models.inscription import Inscription
        from models.inscription_member import InscriptionMember
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
        from models.speaker import SpeakerEntry
        from models.motion import Motion
        from models.resolution import Resolution, Amendment
        from models.speech_log import SpeechLog
        from models.event_period import EventPeriod
        from models.urgent_alert import UrgentAlert

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
        from models.inscription_member import InscriptionMember
        from models.news import News, slugify
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
        from models.speaker import SpeakerEntry
        from models.motion import Motion
        from models.resolution import Resolution, Amendment
        from models.speech_log import SpeechLog

        tables = {
            User.__tablename__: User,
            Delegation.__tablename__: Delegation,
            Inscription.__tablename__: Inscription,
            InscriptionMember.__tablename__: InscriptionMember,
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
            SpeakerEntry.__tablename__: SpeakerEntry,
            Motion.__tablename__: Motion,
            Resolution.__tablename__: Resolution,
            Amendment.__tablename__: Amendment,
            SpeechLog.__tablename__: SpeechLog,
        }

        for table_name, model in tables.items():
            try:
                existing_cols = {c['name']: c for c in inspector.get_columns(table_name)}
            except Exception:
                continue  # tabela não existe
            for col_name, col in model.__table__.columns.items():
                if col_name in ('id',):
                    continue
                if col_name not in existing_cols:
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
                    continue
                # Redimensiona VARCHARs existentes quando o modelo pede mais espaço
                col_type_info = existing_cols[col_name].get('type')
                col_type_name = getattr(col_type_info, '__class__', type(col_type_info)).__name__
                if col_type_name in ('VARCHAR', 'NVARCHAR', 'String'):
                    existing_len = getattr(col_type_info, 'length', None)
                    new_len = getattr(col.type, 'length', None)
                    target = None
                    if new_len is None:
                        target = 'TEXT'  # modelo virou Text -> remove limite
                    elif existing_len and new_len and new_len > existing_len:
                        target = f'VARCHAR({new_len})'
                    if target:
                        try:
                            if is_pg:
                                stmt = f'ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE {target}'
                                with db.engine.connect() as conn:
                                    conn.execute(sa.text(stmt))
                                    conn.commit()
                            print(f'[MIGRATION] {table_name}.{col_name} redimensionada para {target}.')
                        except Exception as e:
                            print(f'[MIGRATION] Erro ao redimensionar {table_name}.{col_name}: {e}')

        # Backfill: gera slugs únicos para notícias antigas que ficaram sem slug
        from models.news import News
        try:
            from sqlalchemy import func
            missing = News.query.filter(
                (News.slug.is_(None)) | (News.slug == '')
            ).all()
            for n in missing:
                base = slugify(n.title) or 'noticia'
                slug = base
                i = 1
                while News.query.filter(News.slug == slug).filter(News.id != n.id).first():
                    slug = f'{base}-{i}'; i += 1
                n.slug = slug
            if missing:
                db.session.commit()
                print(f'[MIGRATION] Slugs gerados para {len(missing)} notícia(s).')
        except Exception as e:
            print(f'[MIGRATION] Erro ao gerar slugs: {e}')

        # ── ÍNDICES DE PERFORMANCE ────────────────────────────
        indexes_to_create = [
            ('ix_votesession_status',      'vote_sessions',    'status'),
            ('ix_news_created_at',         'news',             'created_at'),
            ('ix_student_created_at',      'students',         'created_at'),
            ('ix_urgent_alert_active_ts',  'urgent_alerts',    'active, created_at'),
        ]
        existing_indexes = set()
        for tbl in inspector.get_table_names():
            for idx in inspector.get_indexes(tbl):
                existing_indexes.add(idx['name'])
        for idx_name, table, cols in indexes_to_create:
            if idx_name not in existing_indexes:
                try:
                    col_list = ', '.join(cols.split(', '))
                    stmt = f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({col_list})'
                    with db.engine.connect() as conn:
                        conn.execute(sa.text(stmt))
                        conn.commit()
                    print(f'[MIGRATION] Índice {idx_name} criado.')
                except Exception as e:
                    print(f'[MIGRATION] Erro ao criar índice {idx_name}: {e}')


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
            admin_password = os.environ.get('ADMIN_PASSWORD', 'swdl2025')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print('[SWDL] Admin padrão criado → admin@swdl.com / swdl2025')

        # Garante que o EventConfig existe
        EventConfig._ensure()
        print('[SWDL] EventConfig verificado.')


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)