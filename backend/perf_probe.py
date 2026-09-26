#!/usr/bin/env python3
"""SWDL — sonda de performance do painel admin (Fase 0 de otimização).

Mede, para cada rota admin: TTFB (até o primeiro byte), tempo total de
download e os headers X-Request-Time / X-Query-Count expostos pela
instrumentação do backend (app.py::_setup_perf).

Só faz GETs (mais 1 POST de login) — não altera nada no servidor.

Uso:
    set ADMIN_PASSWORD=senha          (default de dev: swdl2025)
    python perf_probe.py                                  # produção
    python perf_probe.py --base http://127.0.0.1:5000      # local

Interpretação rápida:
    - TTFB alto + X-Request-Time alto + queries altas  -> N+1 / queries pesadas
    - TTFB alto + queries baixas                       -> rede/instância/bloqueio
    - 1ª passagem lenta, demais rápidas                -> cold start da instância
    - X-Request-Time baixo mas total alto              -> entrega de assets
"""
import argparse
import http.cookiejar
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROUTES = [
    ('dashboard',      '/admin/'),
    ('alunos',         '/admin/alunos'),
    ('delegacoes',     '/admin/delegacoes'),
    ('inscricoes',     '/admin/inscricoes'),
    ('noticias',       '/admin/noticias'),
    ('agenda',         '/admin/agenda'),
    ('documentos',     '/admin/documentos'),
    ('dpos',           '/admin/dpos'),
    ('certificados',   '/admin/certificados'),
    ('convocar',       '/admin/convocar'),
    ('chamada',        '/admin/chamada'),
    ('oradores',       '/admin/oradores'),
    ('temas',          '/admin/temas'),
    ('notificacoes',   '/admin/notificacoes'),
    ('diretor',        '/admin/diretor'),
    ('static admin.css', '/static/css/admin.css'),
    ('api status',     '/api/status'),
]

CSRF_RE = re.compile(r'<meta\s+name="csrf-token"\s+content="([^"]+)"')


def build_opener():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def login(base, email, password, timeout):
    opener, _ = build_opener()
    login_url = base.rstrip('/') + '/admin/login'

    try:
        resp = opener.open(login_url, timeout=timeout)
        html = resp.read().decode('utf-8', 'replace')
    except urllib.error.URLError as exc:
        print(f'ERRO: nao consegui abrir {login_url} -> {exc}', file=sys.stderr)
        sys.exit(2)

    m = CSRF_RE.search(html)
    csrf = m.group(1) if m else ''
    data = urllib.parse.urlencode({
        'email': email,
        'password': password,
        'csrf_token': csrf,
        'remember': 'y',
    }).encode()
    req = urllib.request.Request(login_url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    t0 = time.perf_counter()
    try:
        resp = opener.open(req, timeout=timeout)
        body = resp.read().decode('utf-8', 'replace')
        final_url = resp.geturl()
    except urllib.error.URLError as exc:
        print(f'ERRO no login: {exc}', file=sys.stderr)
        sys.exit(2)
    login_ms = (time.perf_counter() - t0) * 1000

    if 'E-mail ou senha incorretos' in body:
        print('ERRO: credenciais invalidas (ADMIN_EMAIL/ADMIN_PASSWORD).',
              file=sys.stderr)
        sys.exit(2)
    if '/admin/login' in final_url:
        print(f'ERRO: login nao concluido (ficou em {final_url}).', file=sys.stderr)
        sys.exit(2)

    print(f'login OK ({login_ms:.0f}ms) -> {final_url}\n')
    return opener


def measure(opener, url, timeout):
    req = urllib.request.Request(url, method='GET')
    t0 = time.perf_counter()
    try:
        resp = opener.open(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        return dict(status=exc.code, ttfb=elapsed, total=elapsed,
                    srv='-', nq='-', size=0)
    except urllib.error.URLError as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        return dict(status='ERR', ttfb=elapsed, total=elapsed,
                    srv='-', nq='-', size=0, err=str(exc.reason))

    ttfb = (time.perf_counter() - t0) * 1000
    body = resp.read()
    total = (time.perf_counter() - t0) * 1000
    return dict(
        status=resp.status,
        ttfb=ttfb,
        total=total,
        srv=resp.headers.get('X-Request-Time') or '-',
        nq=resp.headers.get('X-Query-Count') or '-',
        size=len(body),
    )


def fmt(result):
    if result.get('err'):
        return f"{result['status']:<6} {result['ttfb']:7.0f} {result['total']:7.0f}  erro: {result['err']}"
    return (f"{str(result['status']):<6} {result['ttfb']:7.0f} {result['total']:7.0f} "
            f"{result['srv']:>10} {result['nq']:>6} {result['size']:8d}")


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    parser = argparse.ArgumentParser(description='Sonda de performance do admin SWDL')
    parser.add_argument('--base', default=os.environ.get('BASE_URL', 'https://swdl.onrender.com'))
    parser.add_argument('--email', default=os.environ.get('ADMIN_EMAIL', 'admin@swdl.com'))
    parser.add_argument('--password', default=os.environ.get('ADMIN_PASSWORD', 'swdl2025'))
    parser.add_argument('--runs', type=int, default=2, help='passes por rota (default 2)')
    parser.add_argument('--only', default='', help='rota unica (substring do nome, ex: dashboard)')
    parser.add_argument('--timeout', type=float, default=90.0)
    args = parser.parse_args()

    routes = ROUTES
    if args.only:
        routes = [r for r in ROUTES if args.only in r[0]]
        if not routes:
            print(f"rota '{args.only}' nao encontrada. opcoes: "
                  + ', '.join(r[0] for r in ROUTES), file=sys.stderr)
            sys.exit(2)

    base = args.base.rstrip('/')
    print(f'base: {base}  |  email: {args.email}  |  passes: {args.runs}\n')

    opener = login(base, args.email, args.password, args.timeout)

    header = (f"{'rota':<18} {'pass':>4} {'status':>6} {'TTFB':>7} {'total':>7} "
              f"{'srv':>10} {'queries':>6} {'bytes':>8}")
    print(header)
    print('-' * len(header))

    all_srv = []
    summary = {}
    for name, path in routes:
        for run in range(1, args.runs + 1):
            res = measure(opener, base + path, args.timeout)
            print(f'{name:<18} {run:>4} {fmt(res)}')
            if run == args.runs:
                summary[name] = res
                if res['srv'] != '-':
                    try:
                        all_srv.append(float(res['srv'].replace('ms', '')))
                    except ValueError:
                        pass

    print('\n── resumo (ultimo pass) ──────────────────────────────')
    print(header)
    print('-' * len(header))
    for name, res in summary.items():
        print(f'{name:<18} {"":>4} {fmt(res)}')

    if all_srv:
        print(f"\ntempo medio do servidor (header X-Request-Time): "
              f"{statistics.mean(all_srv):.0f}ms | mediana "
              f"{statistics.median(all_srv):.0f}ms | max {max(all_srv):.0f}ms")
    else:
        print('\nheaders X-Request-Time/X-Query-Count ausentes -> '
              'deploy ainda sem a instrumentacao da Fase 0.')

    print('''
interpretacao:
  * TTFB ~ total ~ X-Request-Time  -> tempo quase todo no servidor (queries/logica)
  * TTFB baixo + total alto        -> download de assets (css/js/png)
  * pass 1 muito mais lento        -> cold start da instancia Render
  * queries altas (X-Query-Count)  -> N+1; mirar em eager loading + paginação''')


if __name__ == '__main__':
    main()
