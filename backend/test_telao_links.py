"""Teste das conexões admin/student <-> telão.

Cobre os 6 gaps corrigidos:
 1. presença do aluno atualiza a chamada projetada
 2. alunos recebem vote_opened/vote_closed (room all_delegates)
 3. crise/urgent_alert chega ao telão
 4. painéis admin escutam a room 'admin'
 5. cronômetro de debate sobrevive a restart
 6. link /telao nos painéis admin e aluno

IMPORTANTE: as requests HTTP/SocketIO rodam FORA de um app context externo.
Com um `with app.app_context()` envolvendo tudo, o `g` vira compartilhado e o
flask_login deixa o `current_user` grudado no primeiro usuário logado.

Uso: python test_telao_links.py
"""
import os
import sys
import time
import importlib
import tempfile
import shutil

os.environ.setdefault('SECRET_KEY', 'test123')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FAILURES = []
STUDENT_EMAIL = 'telao_aluno@test.local'
STUDENT_PASS = 'senha123'


def check(name, cond, extra=''):
    status = 'OK ' if cond else 'FAIL'
    print(f'[{status}] {name}' + (f'  {extra}' if extra and not cond else ''))
    if not cond:
        FAILURES.append(name)


def _events(received, name):
    return [e for e in received if e.get('name') == name]


def _payload(events):
    ev = events[-1] if events else None
    return ev['args'][0] if ev and ev.get('args') else None


def main():
    db_path = os.path.join(tempfile.gettempdir(), 'swdl_telao_test.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    real = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swdl.db')
    if os.path.exists(real):
        shutil.copyfile(real, db_path)
    os.environ['DATABASE_URL'] = 'sqlite:///' + db_path.replace('\\', '/')

    from app import create_app
    from extensions import socketio

    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    with app.app_context():
        deleg_id = _seed_student()

    admin_client = app.test_client()
    student_client = app.test_client()

    telao = socketio.test_client(app, flask_test_client=app.test_client())
    telao.connect()
    telao.emit('join_telao', {})
    telao.get_received()   # descarta vote_opened/debate_timer_sync iniciais

    _check_gap1(app, student_client, telao, deleg_id)
    _check_gap2(app, student_client, socketio)
    _check_gap3(app, admin_client, telao)
    _check_gap4(admin_client)
    _check_gap5(app)
    _check_gap6(admin_client, student_client)

    telao.disconnect()

    print()
    if FAILURES:
        print(f'FALHOU: {len(FAILURES)} checagem(s): {FAILURES}', file=sys.stderr)
        return 1
    print('OK: todas as checagens passaram.')
    return 0


# ── setup ──────────────────────────────────────────────────────
def _seed_student():
    from extensions import db
    from models.user import User
    from models.student import Student
    from models.delegation import Delegation

    user = User.query.filter_by(email=STUDENT_EMAIL).first()
    if not user:
        user = User(name='Aluno Telao', email=STUDENT_EMAIL, role='student')
        user.set_password(STUDENT_PASS)
        db.session.add(user)
        db.session.flush()

    student = Student.query.filter_by(user_id=user.id).first()
    if not student:
        student = Student(name='Aluno Telao', email=STUDENT_EMAIL,
                          user_id=user.id)
        db.session.add(student)
        db.session.flush()
    if not student.delegation_id:
        deleg = Delegation(country='Teste Telao', country_flag='BR',
                           committee='TEST', presence_status='ausente')
        db.session.add(deleg)
        db.session.flush()
        student.delegation_id = deleg.id
    db.session.commit()
    return student.delegation_id


def _login_student(client):
    r = client.post('/student/login', data={
        'email': STUDENT_EMAIL, 'password': STUDENT_PASS,
    }, follow_redirects=False)
    return r.status_code in (200, 302)


def _login_admin(client):
    r = client.post('/admin/login', data={
        'email': 'admin@swdl.com', 'password': os.environ['ADMIN_PASSWORD'],
    }, follow_redirects=False)
    return r.status_code == 302


# ── 1. presença do aluno -> telão ──────────────────────────────
def _force_presence(app, deleg_id, status):
    from extensions import db
    from models.delegation import Delegation
    with app.app_context():
        db.session.get(Delegation, deleg_id).presence_status = status
        db.session.commit()


def _check_gap1(app, client, telao, deleg_id):
    check('login aluno', _login_student(client))

    _force_presence(app, deleg_id, 'ausente')
    telao.get_received()

    r = client.post('/api/student/presenca', json={'adapted': False})
    ok = r.status_code == 200 and (r.get_json() or {}).get('ok')
    check('aluno registra presença via API', bool(ok), str(r.status_code))

    got = _payload(_events(telao.get_received(), 'chamada_update'))
    check('presença do aluno chega ao telão',
          bool(got) and got.get('id') == deleg_id
          and got.get('status') == 'presente', str(got))

    _force_presence(app, deleg_id, 'ausente')
    telao.get_received()
    r = client.post('/student/presenca', data={'action': 'registrar'},
                    follow_redirects=False)
    got = _payload(_events(telao.get_received(), 'chamada_update'))
    check('formulário de presença também emite ao telão',
          r.status_code in (200, 302) and bool(got)
          and got.get('status') == 'presente', str(got))


# ── 2. alunos na room all_delegates ────────────────────────────
def _check_gap2(app, client, socketio):
    sclient = socketio.test_client(app, flask_test_client=client)
    sclient.connect()
    sclient.get_received()
    sclient.emit('join_students', {})
    check('join_students responde open_sessions',
          bool(_events(sclient.get_received(), 'open_sessions')))

    socketio.emit('vote_opened', {'id': 999, 'title': 'Votação Teste'},
                  room='all_delegates')
    check('aluno recebe vote_opened',
          bool(_events(sclient.get_received(), 'vote_opened')), 'sem evento')

    socketio.emit('vote_closed', {'id': 999, 'title': 'Votação Teste'},
                  room='all_delegates')
    check('aluno recebe vote_closed',
          bool(_events(sclient.get_received(), 'vote_closed')), 'sem evento')
    sclient.disconnect()


# ── 3. crise chega ao telão ────────────────────────────────────
def _check_gap3(app, admin_client, telao):
    data = admin_client.get('/api/telao/estado').get_json() or {}
    check('estado do telão expõe crisis', 'crisis' in data, str(list(data)))

    check('login admin', _login_admin(admin_client))
    telao.get_received()

    r = admin_client.post('/admin/crise/ativar',
                          data={'message': 'Crise de teste no telão'},
                          follow_redirects=False)
    check('admin ativa crise', r.status_code == 302, str(r.status_code))

    got = _payload(_events(telao.get_received(), 'urgent_alert'))
    check('alerta urgente chega ao telão',
          bool(got) and got.get('message') == 'Crise de teste no telão', str(got))

    data = admin_client.get('/api/telao/estado').get_json() or {}
    check('poll do telão restaura a crise',
          data.get('crisis') == 'Crise de teste no telão',
          str(data.get('crisis')))

    telao.get_received()
    admin_client.post('/admin/crise/desativar', follow_redirects=False)
    check('ocultar crise chega ao telão',
          bool(_events(telao.get_received(), 'urgent_alert_hide')), 'sem evento')
    data = admin_client.get('/api/telao/estado').get_json() or {}
    # após desativar o alerta, sobra apenas o fallback (notícia de crise
    # publicada) — mesmo comportamento do banner do site público
    check('poll remove o alerta desativado',
          data.get('crisis') != 'Crise de teste no telão',
          str(data.get('crisis')))


# ── 4. painéis admin escutam a room 'admin' ────────────────────
def _check_gap4(admin_client):
    cases = [
        ('/admin/mocoes', 'motion_queue_updated'),
        ('/admin/resolucoes', 'resolution_list_updated'),
        ('/admin/speaker-queue', 'speaker_queue_updated'),
    ]
    for url, evt in cases:
        r = admin_client.get(url)
        html = r.get_data(as_text=True)
        check(f'{url} carrega socket.io',
              r.status_code == 200 and 'socket.io.min.js' in html,
              str(r.status_code))
        check(f'{url} escuta {evt}', evt in html, 'listener ausente')


# ── 5. cronômetro de debate persistido ─────────────────────────
def _check_gap5(app):
    with app.app_context():
        from models import debate_timer as dt
        from models.system_config import SystemConfig

        dt.reset()
        dt.start()
        st1 = dt.get_state()
        time.sleep(1.1)
        check('timer gravado no banco', bool(SystemConfig.get('debate_timer')))

        importlib.reload(dt)
        st2 = dt.get_state()
        check('timer sobrevive a restart',
              st2['running'] and st2['elapsed'] >= st1['elapsed'],
              f'{st1} -> {st2}')

        dt.pause()
        importlib.reload(dt)
        check('timer pausado persiste', dt.get_state()['running'] is False)
        dt.reset()


# ── 6. link /telao nos painéis ─────────────────────────────────
def _check_gap6(admin_client, student_client):
    r = admin_client.get('/admin/')
    html = r.get_data(as_text=True)
    check('sidebar admin tem link do Telão',
          r.status_code == 200 and '/telao' in html, str(r.status_code))

    check('login aluno (gap6)', _login_student(student_client))
    r = student_client.get('/student')
    html = r.get_data(as_text=True)
    check('sidebar do aluno tem link do Telão',
          r.status_code == 200 and '/telao' in html, str(r.status_code))


if __name__ == '__main__':
    sys.exit(main())
