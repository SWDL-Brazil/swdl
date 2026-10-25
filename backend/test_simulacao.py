"""Teste das correções da fase "Durante a Simulação" (lotes 1-3).

Sobe o app com SQLite temporário (banco vazio + seed próprio), desliga o
CSRF e verifica:

  1. larguras de coluna committee == 300 (VARCHAR(30) quebrava o INSERT
     em Postgres com tema longo → "erro de servidor" ao criar votação)
  2. POST /admin/votacoes/nova com committee de 92 chars cria a sessão
  3. escopo de comitê: visible_to/is_visible_to + página do aluno + /api/votar
  4. filtros de presença aceitam presente/votante (moções e fila de oradores)
  5. WS: telão recebe speaker_queue_display; painel vote_list recebe
     vote_list_update (contrato emitido × escutado)
  6. contratos estáticos: CSRF no rowHtml, emenda 'success', IDs por
     sessão, rollback da chamada, stat-tiles reais, socket.io local,
     fallback de polling do telão, sem CDN

Uso:
    python test_simulacao.py
"""
import glob
import os
import sys
import tempfile

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LONG_THEME = ('A Proteção Internacional de Pessoas Deslocadas em '
              'Decorrencia de Eventos Climáticos Extremos')  # 92 chars

FAILURES = []


def check(name, cond, extra=''):
    status = 'OK ' if cond else 'FAIL'
    print(f'[{status}] {name}' + (f'  {extra}' if extra and not cond else ''))
    if not cond:
        FAILURES.append(name)


def _read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def main():
    db_path = os.path.join(tempfile.gettempdir(), 'swdl_simulacao_test.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ['DATABASE_URL'] = 'sqlite:///' + db_path.replace('\\', '/')

    from app import create_app
    from extensions import db, socketio

    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    check('tema longo tem 92 chars', len(LONG_THEME) == 92, str(len(LONG_THEME)))

    # ─────────────────────────── seed ───────────────────────────
    with app.app_context():
        from models.user import User
        from models.theme import Theme
        from models.delegation import Delegation
        from models.student import Student
        from models.vote import VoteSession

        theme_a = Theme(name=LONG_THEME)
        theme_b = Theme(name='Outro Comite')
        db.session.add_all([theme_a, theme_b])
        db.session.flush()

        deleg_a = Delegation(country='Brasil', country_flag='🇧🇷',
                             committee=theme_a.name, theme_id=theme_a.id,
                             presence_status='presente')
        deleg_b = Delegation(country='Argentina', country_flag='🇦🇷',
                             committee=theme_b.name, theme_id=theme_b.id,
                             presence_status='ausente')
        db.session.add_all([deleg_a, deleg_b])
        db.session.flush()

        user_s = User(name='Aluno Teste', email='aluno@test.local',
                      role='student')
        user_s.set_password('senha123')
        db.session.add(user_s)
        db.session.flush()

        student = Student(name='Aluno Teste', email='aluno@test.local',
                          user_id=user_s.id, delegation_id=deleg_a.id)
        db.session.add(student)

        s_geral = VoteSession(title='Votacao Geral', committee='geral',
                              status='open')
        s_a = VoteSession(title='Votacao Comite A', committee=theme_a.name,
                          status='open')
        s_b = VoteSession(title='Votacao Comite B', committee=theme_b.name,
                          status='open')
        db.session.add_all([s_geral, s_a, s_b])
        db.session.commit()

        admin = User.query.filter_by(email='admin@swdl.com').first()
        ids = dict(admin=admin.id, student=user_s.id,
                   deleg_a=deleg_a.id, deleg_b=deleg_b.id,
                   s_a=s_a.id, s_b=s_b.id, s_geral=s_geral.id)
        print(f"seed: admin={ids['admin']} student={ids['student']} "
              f"deleg_a={ids['deleg_a']} sessoes={ids['s_geral']}/{ids['s_a']}/{ids['s_b']}")

    # ─────────────────── 1. larguras de coluna (VARCHAR 300) ───────────────────
    from models.vote import VoteSession as _VS
    from models.delegation import Delegation as _Del
    from models.motion import Motion as _Mot
    from models.resolution import Resolution as _Res
    from models.speaker import SpeakerEntry as _Spk
    from models.speech_log import SpeechLog as _Log
    from models.participation import ParticipationHistory as _Part
    from models.certificate import Certificate as _Cert

    for model in (_VS, _Del, _Mot, _Res, _Spk, _Log, _Part, _Cert):
        length = model.__table__.columns['committee'].type.length
        check(f'{model.__tablename__}.committee == VARCHAR(300)', length == 300,
              f'length={length}')

    # ─────────────────── 2. criação de votação com tema longo ───────────────────
    admin_client = app.test_client()
    with admin_client.session_transaction() as sess:
        sess['_user_id'] = str(ids['admin'])
        sess['_fresh'] = True

    r = admin_client.post('/admin/votacoes/nova', data={
        'title': 'Resolução com tema longo',
        'description': 'regressão do 500',
        'committee': LONG_THEME,
        'duration_sec': '120',
    }, follow_redirects=False)
    check('POST /admin/votacoes/nova com committee de 92 chars → 302',
          r.status_code == 302, f'status={r.status_code}')

    with app.app_context():
        created = _VS.query.filter_by(title='Resolução com tema longo').first()
        check('sessão com committee longo persistida',
              created is not None and created.committee == LONG_THEME)

    # ─────────────────── 3. escopo de comitê ───────────────────
    with app.app_context():
        deleg_a = _Del.query.get(ids['deleg_a'])
        deleg_b = _Del.query.get(ids['deleg_b'])
        s_a = _VS.query.get(ids['s_a'])
        s_b = _VS.query.get(ids['s_b'])
        s_geral = _VS.query.get(ids['s_geral'])

        # a sessão criada acima é do mesmo comitê de deleg A → também visível
        expected = {ids['s_geral'], ids['s_a']}
        if created is not None:
            expected.add(created.id)
        visible = {s.id for s in _VS.visible_to(deleg_a).all()}
        check('visible_to(deleg A) = geral + comitê A', visible == expected,
              f'visible={sorted(visible)} esperado={sorted(expected)}')
        check('visible_to(deleg A) NÃO inclui comitê B', ids['s_b'] not in visible)
        check('is_visible_to: geral sempre True', s_geral.is_visible_to(deleg_a))
        check('is_visible_to: comitê A → True', s_a.is_visible_to(deleg_a))
        check('is_visible_to: comitê B → False', not s_b.is_visible_to(deleg_a))

    # página do aluno: só as sessões do próprio comitê + geral
    student_client = app.test_client()
    with student_client.session_transaction() as sess:
        sess['_user_id'] = str(ids['student'])
        sess['_fresh'] = True

    r = student_client.get('/student/votacao')
    body = r.get_data(as_text=True)
    check('GET /student/votacao → 200', r.status_code == 200, f'{r.status_code}')
    check('página mostra sessão geral', 'Votacao Geral' in body)
    check('página mostra sessão do próprio comitê', 'Votacao Comite A' in body)
    check('página NÃO mostra sessão de outro comitê', 'Votacao Comite B' not in body)

    # /api/votar: valida escopo (403) e depois permite voto no comitê certo
    r = student_client.post('/api/votar', json={'session_id': ids['s_b'],
                                                'choice': 'favor'})
    check('POST /api/votar em sessão de outro comitê → 403',
          r.status_code == 403, f'status={r.status_code} body={r.get_data(as_text=True)[:120]}')

    r = student_client.post('/api/votar', json={'session_id': ids['s_a'],
                                                'choice': 'favor'})
    data = r.get_json() or {}
    check('POST /api/votar no próprio comitê → ok', data.get('ok') is True,
          f'{r.status_code} {data}')

    # ─────────────────── 4. filtros de presença (presente + votante) ───────────────────
    r = admin_client.get('/admin/mocoes/nova')
    body = r.get_data(as_text=True)
    check('GET /admin/mocoes/nova → 200', r.status_code == 200, f'{r.status_code}')
    check('form de moção lista delegação presente (Brasil)', 'Brasil' in body)
    check('form de moção NÃO lista delegação ausente', 'Argentina' not in body)

    r = admin_client.get('/admin/speaker-queue')
    body = r.get_data(as_text=True)
    check('GET /admin/speaker-queue → 200', r.status_code == 200, f'{r.status_code}')
    check('fila de oradores lista delegação presente (Brasil)', 'Brasil' in body)

    # ─────────────────── 5. WS: telão e vote_list ───────────────────
    telao = socketio.test_client(app, flask_test_client=app.test_client())
    telao.connect()
    telao.emit('join_telao', {})
    telao.get_received()

    admin_ws = socketio.test_client(app, flask_test_client=admin_client)
    admin_ws.connect()
    admin_ws.emit('join_admin', {})   # entra em 'admin' + 'vote_list'
    admin_ws.get_received()

    r = admin_client.post('/admin/speaker-queue/add', json={
        'delegation_id': ids['deleg_a'], 'speaking_time': 60, 'topic': 'Tema X',
    })
    check('POST /admin/speaker-queue/add → success',
          (r.get_json() or {}).get('status') == 'success',
          f'{r.status_code} {r.get_data(as_text=True)[:120]}')

    events = [e['name'] for e in telao.get_received()]
    check('telão recebe speaker_queue_display', 'speaker_queue_display' in events,
          f'events={events}')

    r = student_client.post('/api/votar', json={'session_id': ids['s_geral'],
                                                'choice': 'contra'})
    check('voto na sessão geral → ok', (r.get_json() or {}).get('ok') is True)
    events = [e['name'] for e in admin_ws.get_received()]
    check('painel vote_list recebe vote_list_update', 'vote_list_update' in events,
          f'events={events}')

    telao.disconnect()
    admin_ws.disconnect()

    # ─────────────────── 6. contratos estáticos ───────────────────
    root = os.path.dirname(os.path.abspath(__file__))
    vote_list = _read(os.path.join(root, 'templates', 'admin', 'vote_list.html'))
    check('vote_list.html escuta vote_list_update', "socket.on('vote_list_update'" in vote_list)
    check('vote_list.html não escuta vote_update (contrato antigo)',
          "socket.on('vote_update'" not in vote_list)
    check('rowHtml injeta csrf_token', 'name="csrf_token"' in vote_list)

    vote_py = _read(os.path.join(root, 'routes', 'vote.py'))
    check('vote.py emite vote_list_update', "emit('vote_list_update'" in vote_py)
    check('rota morta /delegado/votar removida', 'delegate_vote_page' not in vote_py)

    student_py = _read(os.path.join(root, 'routes', 'student.py'))
    code_lines = [ln for ln in student_py.splitlines()
                  if not ln.lstrip().startswith('#')]
    check('student.py não chama get_agenda_status() bruto (só em comentário)',
          'get_agenda_status(' not in '\n'.join(code_lines))

    res_student = _read(os.path.join(root, 'templates', 'student', 'resolutions.html'))
    check("emenda: template checa status 'success'", "d.status === 'success'" in res_student)
    check("emenda: template não espera 'amendment'", "d.status === 'amendment'" not in res_student)

    voting_html = _read(os.path.join(root, 'templates', 'student', 'voting.html'))
    check('voting.html usa ids por sessão', 'voteOptions-{{ session.id }}' in voting_html)
    check('voting.html sem id global duplicado', 'id="voteOptions"' not in voting_html)
    voting_js = _read(os.path.join(root, 'static', 'js', 'student-voting.js'))
    check('student-voting.js resolve ids por sessão', "'voteOptions-' + sessionId" in voting_js)

    res_admin = _read(os.path.join(root, 'templates', 'admin', 'resolutions.html'))
    check('stat-tiles de resoluções renderizam stats reais', '{{ stats.draft }}' in res_admin)

    chamada = _read(os.path.join(root, 'templates', 'admin', 'chamada.html'))
    check('chamada.html tem rollback completo (rollbackPresence)', 'function rollbackPresence' in chamada)

    motion_py = _read(os.path.join(root, 'routes', 'motion.py'))
    sq_py = _read(os.path.join(root, 'routes', 'speaker_queue.py'))
    check('motion.py filtra presente+votante',
          "in_(['presente', 'votante'])" in motion_py)
    check('speaker_queue.py filtra presente+votante',
          "in_(['presente', 'votante'])" in sq_py)

    # socket.io servido localmente (sem cdnjs) em todos os templates
    cdn = [p for p in glob.glob(os.path.join(root, 'templates', '**', '*.html'),
                                recursive=True)
           if 'cdnjs.cloudflare.com/ajax/libs/socket.io' in _read(p)]
    check('nenhum template usa CDN do socket.io', not cdn, f'{cdn}')
    vendor = os.path.join(root, 'static', 'vendor', 'socket.io.min.js')
    check('socket.io.min.js versionado localmente', os.path.exists(vendor))
    telao_html = _read(os.path.join(root, 'templates', 'telao.html'))
    check('telao.html carrega o vendor local',
          'vendor/socket.io.min.js' in telao_html)

    telao_js = _read(os.path.join(root, 'static', 'js', 'telao.js'))
    check('telao.js tem fallback de polling da fila (LIST_SCREENS)', 'LIST_SCREENS' in telao_js)
    check('telao.js repinta só quando muda (lastListKey)', 'lastListKey' in telao_js)
    check('telao.js acende indicador de WS desconectado', 'updateConnectionDot(false);' in telao_js)

    seed = _read(os.path.join(root, 'register_students.py'))
    check('register_students.py não trunca committee em 30', '[:30]' not in seed)

    speaker_html = _read(os.path.join(root, 'templates', 'admin', 'speaker_queue.html'))
    check('speaker_queue.html usa postJson com erro visível', 'function postJson' in speaker_html)
    check('controlScreen reporta falha', 'Falha ao enviar ao Telão' in speaker_html)

    print()
    if FAILURES:
        print(f'FALHOU: {len(FAILURES)} checagem(ens): {FAILURES}', file=sys.stderr)
        return 1
    print('OK: todas as checagens passaram.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
