"""Smoke test de performance do painel admin (Fase 1).

Sobe um app com SQLite temporário, desliga o CSRF, loga como admin e
requisita as telas principais, imprimindo status, X-Request-Time,
X-Query-Count e X-Query-Count por rota. Serve para:

  * garantir que nenhuma tela quebrou após as otimizações
  * comparar NÚMERO DE QUERIES antes/depois (a latência local é ~0,
    então só o count importa aqui)

Uso:
    python test_perf_pages.py
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
    ('dashboard',    '/admin/'),
    ('diretor',      '/admin/diretor'),
    ('alunos',       '/admin/alunos'),
    ('delegacoes',   '/admin/delegacoes'),
    ('inscricoes',   '/admin/inscricoes'),
    ('noticias',     '/admin/noticias'),
    ('agenda',       '/admin/agenda'),
    ('documentos',   '/admin/documentos'),
    ('dpos',         '/admin/dpos'),
    ('certificados', '/admin/certificados'),
    ('convocar',     '/admin/convocar'),
    ('chamada',      '/admin/chamada'),
    ('oradores',     '/admin/oradores'),
    ('temas',        '/admin/temas'),
    ('alertas',      '/admin/alertas'),
    ('notificacoes', '/admin/notificacoes'),
    ('categorias',   '/admin/categorias'),
    ('periods',      '/admin/periods'),
]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true',
                        help='usa uma CÓPIA de backend/swdl.db (dados reais)')
    args = parser.parse_args()

    db_path = os.path.join(tempfile.gettempdir(), 'swdl_perf_test.db')
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

    login = client.post('/admin/login', data={
        'email': 'admin@swdl.com',
        'password': os.environ['ADMIN_PASSWORD'],
    }, follow_redirects=False)
    print(f'login: {login.status_code} -> {login.headers.get("Location")}')
    if login.status_code not in (302, 200):
        print('FALHA no login', file=sys.stderr)
        return 1

    print(f"\n{'rota':<16} {'status':>6} {'ms':>7} {'queries':>8} {'db ms':>7} {'bytes':>7}")
    print('-' * 56)
    failures = []
    counts = {}
    for name, path in PAGES:
        t0 = time.perf_counter()
        resp = client.get(path)
        ms = (time.perf_counter() - t0) * 1000
        qs = resp.headers.get('X-Query-Count', '?')
        dbms = resp.headers.get('X-Query-Time', '?')
        counts[name] = qs
        flag = '' if resp.status_code == 200 else '  <-- FALHOU'
        print(f'{name:<16} {resp.status_code:>6} {ms:7.0f} {qs:>8} {dbms:>7} {len(resp.data):7d}{flag}')
        if resp.status_code != 200:
            failures.append((name, path, resp.status_code, resp.data[:400]))

    if failures:
        print('\nFALHAS:', file=sys.stderr)
        for name, path, code, body in failures:
            print(f'\n--- {name} ({path}) -> {code}\n{body!r}', file=sys.stderr)
        return 1

    print('\nOK: todas as telas retornaram 200.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
