"""Teste funcional das correções da agenda admin.

Cobre: validação de data/hora, preservação de order/committee no edit,
reorder em 1 query, get_current_next() e override de fase nos dashboards.

Uso: python test_agenda.py
"""
import os
import sys
import tempfile
import shutil
from datetime import date

os.environ.setdefault('SECRET_KEY', 'test123')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAILURES = []


def check(name, cond, extra=''):
    status = 'OK ' if cond else 'FAIL'
    print(f'[{status}] {name}' + (f'  {extra}' if extra and not cond else ''))
    if not cond:
        FAILURES.append(name)


def main():
    db_path = os.path.join(tempfile.gettempdir(), 'swdl_agenda_test.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    real = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swdl.db')
    if os.path.exists(real):
        shutil.copyfile(real, db_path)
    os.environ['DATABASE_URL'] = 'sqlite:///' + db_path.replace('\\', '/')

    from app import create_app

    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        _run_checks(app, client)

    print()
    if FAILURES:
        print(f'FALHOU: {len(FAILURES)} checagem(s): {FAILURES}', file=sys.stderr)
        return 1
    print('OK: todas as checagens passaram.')
    return 0


def _run_checks(app, client):
    from extensions import db as _db
    from models.agenda import AgendaItem

    login = client.post('/admin/login', data={
        'email': 'admin@swdl.com',
        'password': os.environ['ADMIN_PASSWORD'],
    }, follow_redirects=False)
    check('login admin', login.status_code in (302, 200))

    # ── 1. validação: data inválida é rejeitada ─────────────────
    before = AgendaItem.query.count()
    r = client.post('/admin/agenda/novo', data={
        'title': 'Item inválido', 'day': '1', 'event_date': 'xx/xx/xxxx',
        'start_time': '08:00', 'status': 'auto',
    }, follow_redirects=False)
    check('rejeita data inválida', AgendaItem.query.count() == before,
          f'count {before} -> {AgendaItem.query.count()}')

    # ── 2. validação: término antes do início ───────────────────
    r = client.post('/admin/agenda/novo', data={
        'title': 'Item inválido', 'day': '1',
        'event_date': date.today().isoformat(),
        'start_time': '10:00', 'end_time': '09:00', 'status': 'auto',
    }, follow_redirects=False)
    check('rejeita fim antes do início', AgendaItem.query.count() == before)

    # ── 3. criação válida: order = fim do grupo ─────────────────
    r = client.post('/admin/agenda/novo', data={
        'title': 'Item criado pelo teste', 'day': '7',
        'event_date': date.today().isoformat(),
        'start_time': '08:00', 'end_time': '23:59',
        'status': 'auto', 'committee': 'CS', 'period_id': '',
    }, follow_redirects=False)
    check('cria item válido (302)', r.status_code == 302, f'status {r.status_code}')
    item = AgendaItem.query.filter_by(title='Item criado pelo teste').first()
    check('item criado', item is not None)
    check('order = 1 no grupo vazio', item and item.order == 1,
          f'order={item.order if item else None}')

    # ── 4. get_current_next(): item de hoje 00:00–23:59 = current
    with app.test_request_context():
        from routes.agenda_utils import get_current_next, get_resolved_phase
        current, nxt = get_current_next()
        check('current = item de hoje', current is not None and current.id == item.id,
              f'current={current.title if current else None}')
        check('next = None (sem item seguinte hoje)', nxt is None,
              f'next={nxt.title if nxt else None}')

        # fase resolvida nunca é None
        phase, _, _ = get_resolved_phase()
        check('resolved phase nunca None', phase in ('pre', 'during', 'post'), str(phase))

    # ── 5. edit preserva order e committee com sigla ────────────
    orig_order = item.order
    item.committee = 'DHR'
    _db.session.commit()
    r = client.post(f'/admin/agenda/{item.id}/editar', data={
        'title': 'Item criado pelo teste (editado)', 'day': '7',
        'event_date': date.today().isoformat(),
        'start_time': '08:00', 'end_time': '23:59',
        'status': 'auto', 'committee': 'DHR', 'period_id': '',
    }, follow_redirects=False)
    _db.session.refresh(item)
    check('edit preserva order', item.order == orig_order,
          f'{orig_order} -> {item.order}')
    check('edit preserva committee', item.committee == 'DHR', item.committee)

    # ── 6. form de edit mostra a sigla existente como selected ──
    html = client.get(f'/admin/agenda/{item.id}/editar').data.decode()
    check('form marca sigla atual', 'value="DHR" selected' in html)

    # ── 7. reorder em 1 chamada, preservando ids ────────────────
    r = client.post('/admin/agenda/reorder',
                    json={'items': [{'id': item.id, 'order': 0}]})
    check('reorder ok', r.status_code == 200 and r.get_json().get('ok') is True)
    _db.session.refresh(item)
    check('reorder grava order=0', item.order == 0, str(item.order))

    r = client.post('/admin/agenda/reorder', json={'items': 'nope'})
    check('reorder rejeita payload inválido', r.status_code == 400)

    # ── 8. override de fase vale no dashboard ───────────────────
    from models.event_config import EventConfig
    EventConfig.set_phase_override('during')
    html = client.get('/admin/').data.decode()
    check('dashboard aplica override during',
          'data-phase="during"' in html and 'AO VIVO' in html)
    EventConfig.set_phase_override(None)
    html = client.get('/admin/').data.decode()
    check('dashboard volta ao auto',
          'data-phase="post"' in html or 'data-phase="pre"' in html
          or 'data-phase="during"' in html)

    # ── 9. card "Agora" do aluno via API usa o helper ───────────
    r = client.get('/api/agenda/agora')
    check('api /agenda/agora 200', r.status_code == 200)
    payload = r.get_json()
    check('api current é o item de hoje',
          payload['current'] is not None
          and payload['current']['title'].startswith('Item criado'),
          str(payload['current']))

    # limpeza
    item = AgendaItem.query.filter_by(title='Item criado pelo teste (editado)').first()
    if item:
        _db.session.delete(item)
        _db.session.commit()


if __name__ == '__main__':
    sys.exit(main())
