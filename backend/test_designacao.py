"""Testes do fluxo de designação de país (individual/dupla/trio).

Cobre as correções:
  1. get_current_delegation resolve via Student (membro 2+ de dupla/trio vota)
  2. student_assign cria Inscription se o aluno não tiver (membro secundário)
  3. Unicidade de país por tema/edição (mesmo tema bloqueia, tema diferente ok)
  4. Re-designação da própria delegação não é bloqueada (exclude_id)
  5. member_names() com dedup (formato não vira Dupla errada)
  6. committee customizado preservado ao re-designar com o mesmo tema
  7. POST /api/inscricao: individual+members e dupla com contagem errada -> 400

Uso:
    python test_designacao.py
"""
import os
import sys
import tempfile
import shutil
from datetime import datetime, timezone

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RESULTS = []


def check(name, cond, detail=''):
    RESULTS.append((name, bool(cond)))
    mark = 'PASS' if cond else 'FAIL'
    extra = f'  [{detail}]' if detail and not cond else ''
    print(f'{mark} - {name}{extra}')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    db_path = os.path.join(tempfile.gettempdir(), 'swdl_test_designacao.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    real = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swdl.db')
    if not os.path.exists(real):
        print(f'sem {real}', file=sys.stderr)
        return 1
    shutil.copyfile(real, db_path)
    os.environ['DATABASE_URL'] = 'sqlite:///' + db_path.replace('\\', '/')

    from app import create_app
    from extensions import db
    from models.student import Student
    from models.delegation import Delegation
    from models.theme import Theme
    from models.inscription import Inscription
    from models.user import User

    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    setup = {}

    with app.app_context():
        # ── cenário T1: delegação com 2º membro de login diferente ──
        deleg = None
        for d in Delegation.query.all():
            if len(list(d.students)) >= 2:
                deleg = d
                break
        if not deleg:
            d0 = Delegation.query.first()
            if d0:
                deleg = d0
                extra = Student(name='Membro Extra Teste', email='membro-extra-teste@t.com')
                db.session.add(extra)
                db.session.flush()
                extra.delegation_id = deleg.id
        member2 = None
        if deleg:
            members = list(deleg.students)
            member2 = members[1] if len(members) > 1 else (members[0] if members else None)
        if member2:
            if not member2.user_id:
                u = User(name=member2.name, email=member2.email, role='student')
                u.set_password('membro123')
                db.session.add(u)
                db.session.flush()
                member2.user_id = u.id
            else:
                u = User.query.get(member2.user_id)
                u.set_password('membro123')
            setup['member2_email'] = member2.email
            setup['deleg_country'] = deleg.country
            setup['deleg_id'] = deleg.id

        # cenário T2: aluno sem inscrição e sem delegação
        s_noin = Student(name='Aluno Sem Inscricao Teste',
                         email='aluno-sem-inscricao-teste@t.com')
        db.session.add(s_noin)
        db.session.flush()
        setup['s_noin_id'] = s_noin.id

        # cenário T3/T4: aluno livre + tema existente com país já designado
        used = None
        this_year = datetime.now(timezone.utc).year
        for d in Delegation.query.all():
            if d.country and d.theme_id and d.edition_year == this_year:
                used = d
                break
        s_free = Student(name='Aluno Livre Teste', email='aluno-livre-teste@t.com')
        db.session.add(s_free)
        db.session.flush()
        setup['s_free_id'] = s_free.id
        themes = Theme.query.all()
        setup['n_themes'] = len(themes)
        if used:
            setup['used_country'] = used.country
            setup['used_theme_id'] = used.theme_id
            other = next((t for t in themes if t.id != used.theme_id), None)
            setup['other_theme_id'] = other.id if other else None

        # cenário T5: dedup de member_names
        d5 = Delegation(country='Pais Dedup Teste', committee='Comite Dedup')
        ins5 = Inscription(name='Ana Dedup', email='ana-dedup-teste@t.com',
                           status='approved', type='delegate')
        db.session.add(d5)
        db.session.add(ins5)
        db.session.flush()
        d5.inscription_id = ins5.id
        s5 = Student(name='Ana Dedup', email='ana-dedup-2-teste@t.com')
        db.session.add(s5)
        db.session.flush()
        s5.delegation_id = d5.id
        d5.members = 'Ana Dedup, Bruno Dedup'
        setup['dedup_count'] = d5.member_count()
        setup['dedup_label'] = d5.group_label()

        # cenário T6: committee customizado
        d6 = next((d for d in Delegation.query.all()
                   if d.theme_id and d.country), None)
        if d6:
            d6.committee = 'Comite Custom Teste'
            setup['d6_id'] = d6.id
            setup['d6_country'] = d6.country
            setup['d6_theme_id'] = d6.theme_id
        db.session.commit()

    admin = app.test_client()
    aluno = app.test_client()

    r = admin.post('/admin/login', data={
        'email': 'admin@swdl.com', 'password': os.environ['ADMIN_PASSWORD'],
    }, follow_redirects=False)
    check('login admin', r.status_code in (200, 302), str(r.status_code))

    # ── T1: 2º membro de dupla/trio vota (get_current_delegation) ──
    if setup.get('member2_email'):
        r = aluno.post('/student/login', data={
            'email': setup['member2_email'], 'password': 'membro123',
        }, follow_redirects=False)
        check('login 2º membro', r.status_code in (200, 302), str(r.status_code))
        r = aluno.post('/api/votar', json={
            'session_id': 999999999, 'choice': 'favor',
        })
        body = r.get_data(as_text=True)
        check('2º membro resolve própria delegação (não 404)',
              r.status_code != 404 and 'Delegação não encontrada' not in body,
              f'{r.status_code} {body[:120]}')
        check('2º membro chega na checagem de sessão (400 esperado)',
              r.status_code == 400, f'{r.status_code} {body[:120]}')
    else:
        check('T1 cenário: delegação com 2º membro', False, 'sem delegacao')

    # ── T2: aluno sem inscrição consegue ser designado ──
    r = admin.post(f"/admin/alunos/{setup['s_noin_id']}/designar", data={
        'country': 'Pais Teste Sem Inscricao', 'theme_id': setup.get('other_theme_id') or '',
        'flag': '', 'flag_url': '', 'members': '',
    }, follow_redirects=False)
    check('designa aluno sem inscrição (não bloqueia mais)',
          r.status_code == 302 and (r.headers.get('Location') or '').rstrip('/').endswith('/admin/alunos'),
          f'{r.status_code} {r.headers.get("Location")}')
    with app.app_context():
        s = db.session.get(Student, setup['s_noin_id'])
        check('aluno sem inscrição ganhou delegação', s.delegation_id is not None)
        check('Inscription criada automaticamente',
              Inscription.query.filter_by(email=s.email, status='approved').count() == 1)

    # ── T3: país duplicado no MESMO tema é bloqueado ──
    if setup.get('used_country'):
        r = admin.post(f"/admin/alunos/{setup['s_free_id']}/designar", data={
            'country': setup['used_country'], 'theme_id': setup['used_theme_id'],
            'flag': '', 'flag_url': '', 'members': '',
        }, follow_redirects=False)
        with app.app_context():
            s = db.session.get(Student, setup['s_free_id'])
            blocked = s.delegation_id is None
        check('duplicado no mesmo tema BLOQUEADO', blocked,
              f'{r.status_code} {r.headers.get("Location")}')

        # ── T4: mesmo país em OUTRO tema é permitido ──
        if setup.get('other_theme_id'):
            r = admin.post(f"/admin/alunos/{setup['s_free_id']}/designar", data={
                'country': setup['used_country'], 'theme_id': setup['other_theme_id'],
                'flag': '', 'flag_url': '', 'members': '',
            }, follow_redirects=False)
            with app.app_context():
                s = db.session.get(Student, setup['s_free_id'])
                ok = s.delegation_id is not None
            check('mesmo país em tema diferente PERMITIDO', ok,
                  f'{r.status_code} {r.headers.get("Location")}')
        else:
            check('T4 (2º tema disponível)', False, 'so 1 tema no banco')

        # ── T4b: re-designar a própria delegação com o mesmo país passa ──
        s5id = setup['s_free_id']
        r = admin.post(f"/admin/alunos/{s5id}/designar", data={
            'country': setup['used_country'],
            'theme_id': setup.get('other_theme_id') or '',
            'flag': '', 'flag_url': '', 'members': '',
        }, follow_redirects=False)
        with app.app_context():
            s = db.session.get(Student, s5id)
            still = s.delegation_id is not None
        check('re-designação da própria delegação (mesmo país) OK', still,
              f'{r.status_code} {r.headers.get("Location")}')
    else:
        check('T3 cenário: delegação com país+tema+ano atual', False, 'nenhuma encontrada')

    # ── T5: dedup de member_names ──
    check('member_names dedup (Ana conta 1x -> 2 membros = Dupla)',
          setup.get('dedup_count') == 2 and setup.get('dedup_label') == 'Dupla',
          f"count={setup.get('dedup_count')} label={setup.get('dedup_label')}")

    # ── T6: committee customizado preservado ──
    if setup.get('d6_id'):
        r = admin.post(f"/admin/delegacoes/{setup['d6_id']}/designar", data={
            'country': setup['d6_country'], 'theme_id': setup['d6_theme_id'],
            'flag': '', 'flag_url': '', 'members': '',
        }, follow_redirects=False)
        with app.app_context():
            d = db.session.get(Delegation, setup['d6_id'])
            ok = d.committee == 'Comite Custom Teste'
        check('committee customizado preservado no re-design', ok,
              f'committee={d.committee!r}')

        # country vazio rejeitado em delegation_assign
        r = admin.post(f"/admin/delegacoes/{setup['d6_id']}/designar", data={
            'country': '', 'theme_id': setup['d6_theme_id'],
        }, follow_redirects=False)
        with app.app_context():
            d = db.session.get(Delegation, setup['d6_id'])
            ok = bool(d.country)
        check('country vazio rejeitado em delegation_assign', ok)

    # ── T7: validações de API de inscrição ──
    base = {
        'name': 'Teste Api Inscri', 'email': 'teste-api-inscri@t.com',
        'phone': '85999999999', 'instagram': '@testeapi',
        'accept_terms': True, 'motivation': 'teste',
    }
    r = app.test_client().post('/api/inscricao', json={
        **base, 'formato': 'individual',
        'members': [{'name': 'M', 'email': 'm@t.com', 'phone': '85999999998', 'instagram': '@m'}],
    })
    check('API: individual + members -> 400', r.status_code == 400,
          f'{r.status_code} {r.get_data(as_text=True)[:100]}')

    r = app.test_client().post('/api/inscricao', json={
        **base, 'formato': 'dupla', 'members': [],
    })
    check('API: dupla sem membro -> 400', r.status_code == 400,
          f'{r.status_code}')

    # ── resumo ──
    fails = [n for n, ok in RESULTS if not ok]
    print()
    if fails:
        print(f'FALHOU: {len(fails)}/{len(RESULTS)}')
        for n in fails:
            print('  -', n)
        return 1
    print(f'OK: {len(RESULTS)} verificações passaram.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
