"""Smoke test do painel do DELEGADO (student).

Sobe o app com SQLite temporário (cópia de swdl.db com --real), injeta a
sessão de um usuário student e requisita as 11 telas do painel, garantindo
que o redesign/renomeações de classes não quebraram nenhuma rota.

Uso:
    python test_student_pages.py --real
"""
import os
import sys
import tempfile
import time

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    ('login',        '/student/login'),
    ('dashboard',    '/student'),
    ('presenca',     '/student/presenca'),
    ('votacao',      '/student/votacao'),
    ('documentos',   '/student/documentos'),
    ('comunicados',  '/student/comunicados'),
    ('certificados', '/student/certificados'),
    ('perfil',       '/student/perfil'),
    ('historico',    '/student/historico'),
    ('mocoes',       '/delegado/mocoes'),
    ('resolucoes',   '/delegado/resolucoes'),
]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true',
                        help='usa uma CÓPIA de backend/swdl.db (dados reais)')
    args = parser.parse_args()

    db_path = os.path.join(tempfile.gettempdir(), 'swdl_student_test.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    if args.real:
        import shutil
        real = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swdl.db')
        if not os.path.exists(real):
            print(f'sem {real}', file=sys.stderr)
            return 1
        shutil.copyfile(real, db_path)
        print(f'usando cópia de {real}')
    os.environ['DATABASE_URL'] = 'sqlite:///' + db_path.replace('\\', '/')

    from app import create_app
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    client = app.test_client()

    # login anônimo da tela de login
    r = client.get('/student/login')
    print(f'login page: {r.status_code}')
    if r.status_code != 200:
        print(r.data[:400], file=sys.stderr)
        return 1

    # injeta sessão de um student existente
    from models.user import User
    with app.app_context():
        student = User.query.filter_by(role='student').first()
        if not student:
            print('sem usuário student no banco', file=sys.stderr)
            return 1
        sid = student.id
        print(f'logando como student id={sid} ({student.email})')

    with client.session_transaction() as sess:
        sess['_user_id'] = str(sid)
        sess['_fresh'] = True

    print(f"\n{'rota':<16} {'status':>6} {'ms':>7} {'queries':>8} {'db ms':>7} {'bytes':>7}")
    print('-' * 56)
    failures = []
    for name, path in PAGES:
        t0 = time.perf_counter()
        resp = client.get(path)
        ms = (time.perf_counter() - t0) * 1000
        qs = resp.headers.get('X-Query-Count', '?')
        dbms = resp.headers.get('X-Query-Time', '?')
        # /student/login devolve 302 quando a sessão já está logada (esperado)
        ok = resp.status_code == 200 or (name == 'login' and resp.status_code == 302)
        flag = '' if ok else '  <-- FALHOU'
        print(f'{name:<16} {resp.status_code:>6} {ms:7.0f} {qs:>8} {dbms:>7} {len(resp.data):7d}{flag}')
        if not ok:
            failures.append((name, path, resp.status_code, resp.data[:400]))

    if failures:
        print('\nFALHAS:', file=sys.stderr)
        for name, path, code, body in failures:
            print(f'\n--- {name} ({path}) -> {code}\n{body!r}', file=sys.stderr)
        return 1

    print('\nOK: todas as telas do delegado retornaram 200.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
