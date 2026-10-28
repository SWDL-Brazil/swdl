"""Testes da tela Alunos > Recuperar alunos (recriar Student a partir de
inscricao/login/delegacao). Roda contra um banco temporario.
"""
import os
import shutil
import sys
import tempfile

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

WORKDIR = os.path.join(tempfile.gettempdir(), 'swdl_restore_test')
shutil.rmtree(WORKDIR, ignore_errors=True)
os.makedirs(WORKDIR, exist_ok=True)
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(WORKDIR, 'restore.db').replace('\\', '/')

fails = []


def check(label, cond, extra=''):
    print(('  ok   ' if cond else '  FALHA ') + label + ('' if cond else f' {extra}'))
    if not cond:
        fails.append(label)


from app import create_app
app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

from extensions import db
from models.theme import Theme
from models.delegation import Delegation
from models.student import Student
from models.user import User
from models.inscription import Inscription
from models.participation import ParticipationHistory
from models.certificate import Certificate

with app.app_context():
    theme = Theme(name='Comite de Seguranca')
    db.session.add(theme)
    db.session.flush()

    # A: inscricao aprovada + delegacao China (auto-detectavel)
    ins_a = Inscription(name='Guilherme Santiago Pereira',
                        email='guilherme@exemplo.com', status='approved',
                        type='delegate')
    db.session.add(ins_a)
    db.session.flush()
    deleg_a = Delegation(country='China', country_flag='CN', theme_id=theme.id,
                         edition_year=2026, committee='CS', inscription_id=ins_a.id)
    db.session.add(deleg_a)
    db.session.flush()

    # B: inscricao aprovada sem delegacao (admin escolhe uma)
    ins_b = Inscription(name='Sem Delegacao', email='semdeleg@exemplo.com',
                        status='approved', type='delegate')
    db.session.add(ins_b)
    db.session.flush()
    deleg_b = Delegation(country='Canada', country_flag='CA', theme_id=theme.id,
                         edition_year=2027, committee='CS')
    db.session.add(deleg_b)
    db.session.flush()

    # C: so login (inscricao apagada), delegacao por user_id
    user_c = User(name='Isaac Lauro de Moura', email='isaac@exemplo.com',
                  role='student')
    user_c.set_password('teste123')
    db.session.add(user_c)
    db.session.flush()
    deleg_c = Delegation(country='Eua', country_flag='US', theme_id=theme.id,
                         edition_year=2026, committee='CS', user_id=user_c.id)
    db.session.add(deleg_c)
    db.session.flush()

    # D: aluno completo (nao deve aparecer na tela)
    ins_d = Inscription(name='Aluno Certo', email='certo@exemplo.com',
                        status='approved', type='delegate')
    db.session.add(ins_d)
    user_d = User(name='Aluno Certo', email='certo@exemplo.com', role='student')
    user_d.set_password('teste123')
    db.session.add(user_d)
    db.session.flush()
    db.session.add(Student(name='Aluno Certo', email='certo@exemplo.com',
                           user_id=user_d.id))

    # E: inscricao aprovada + delegacao (admin vai deixar pendente de proposito)
    ins_e = Inscription(name='Forcar Pendente', email='pendente-forcado@exemplo.com',
                        status='approved', type='delegate')
    db.session.add(ins_e)
    db.session.flush()
    deleg_e = Delegation(country='Japao', country_flag='JP', theme_id=theme.id,
                         edition_year=2026, committee='CS', inscription_id=ins_e.id)
    db.session.add(deleg_e)
    db.session.flush()

    # F: inscricao pendente (nao deve aparecer)
    db.session.add(Inscription(name='Inscricao Pendente', email='pendente@exemplo.com',
                               status='pending', type='delegate'))

    # G: membro de trio sem vinculo — pista é o texto `members` da delegacao
    deleg_g = Delegation(country='Argentina', country_flag='AR', theme_id=theme.id,
                         edition_year=2026, committee='CS',
                         members='Gabrielly Viana Munhoz, Outra Pessoa')
    db.session.add(deleg_g)
    db.session.add(Inscription(name='Gabrielly Viana Munhoz',
                               email='gabrielly@exemplo.com', status='approved',
                               type='delegate'))
    db.session.commit()

    deleg_a_id, deleg_b_id, deleg_c_id, deleg_g_id = (
        deleg_a.id, deleg_b.id, deleg_c.id, deleg_g.id)

client = app.test_client()
r = client.post('/admin/login', data={'email': 'admin@swdl.com',
                                      'password': os.environ['ADMIN_PASSWORD']})
check('login admin', r.status_code in (200, 302), r.status_code)

# ── Listagem ────────────────────────────────────────────────────────────────
r = client.get('/admin/alunos/recuperar')
html = r.get_data(as_text=True)
check('pagina 200', r.status_code == 200, r.status_code)
check('lista Guilherme', 'Guilherme Santiago Pereira' in html)
check('lista sem delegacao', 'Sem Delegacao' in html)
check('lista login orfao (Isaac)', 'Isaac Lauro de Moura' in html)
check('lista Gabrielly (pista por membros)', 'Gabrielly Viana Munhoz' in html)
check('nao lista aluno completo', 'Aluno Certo' not in html)
check('nao lista inscricao pendente', 'Inscricao Pendente' not in html)
check('tem seletor de delegacao', 'name="deleg_0"' in html)
check('seletor traz China', 'China' in html)
check('seletor traz contagem de alunos', 'aluno' in html)
check('mostra tag de login', 'src-login' in html)
check('mostra tag de inscricao', 'src-inscricao' in html)

# ── A: restaurar com deteccao automatica (inscricao -> delegacao) ───────────
r = client.post('/admin/alunos/recuperar',
                data={'rows': '0', 'email_0': 'guilherme@exemplo.com',
                      'emit_code': '1'},
                follow_redirects=False)
check('restaurar 302', r.status_code == 302, r.status_code)
with app.app_context():
    st = Student.query.filter_by(email='guilherme@exemplo.com').first()
    check('aluno criado', st is not None)
    check('nome preservado', st and st.name == 'Guilherme Santiago Pereira',
          st.name if st else None)
    check('delegacao detectada (China)', st and st.delegation_id == deleg_a_id,
          st.delegation_id if st else None)
    check('login criado', st and st.user_id is not None)
    check('historico criado', st and ParticipationHistory.query.filter_by(
        student_id=st.id).count() == 1)
    cert = Certificate.query.filter_by(student_id=st.id).first() if st else None
    check('certificado gerado', cert is not None)
    check('certificado no ano da delegacao', cert and cert.edition_year == 2026,
          cert.edition_year if cert else None)
    check('snapshot com nome', cert and cert.student_name == 'Guilherme Santiago Pereira',
          cert.student_name if cert else None)
    check('snapshot com tema', cert and cert.committee_name == 'Comite de Seguranca',
          cert.committee_name if cert else None)
    check('codigo gerado', cert and cert.verification_code,
          cert.verification_code if cert else None)

r = client.get('/admin/alunos/recuperar')
check('Guilherme saiu da lista', 'guilherme@exemplo.com' not in r.get_data(as_text=True))

# ── B: delegacao escolhida na mao (Canada/2027) ────────────────────────────
r = client.post('/admin/alunos/recuperar',
                data={'rows': '0', 'email_0': 'semdeleg@exemplo.com',
                      'deleg_0': str(deleg_b_id), 'emit_code': '1'},
                follow_redirects=False)
check('restaurar com escolha 302', r.status_code == 302, r.status_code)
with app.app_context():
    st = Student.query.filter_by(email='semdeleg@exemplo.com').first()
    check('aluno na delegacao escolhida', st and st.delegation_id == deleg_b_id,
          st.delegation_id if st else None)
    cert = Certificate.query.filter_by(student_id=st.id).first() if st else None
    check('certificado usa o ano da delegacao', cert and cert.edition_year == 2027,
          cert.edition_year if cert else None)

# ── C + G: lote (login orfao + pista por membros) ──────────────────────────
r = client.post('/admin/alunos/recuperar',
                data={'rows': ['0', '1'],
                      'email_0': 'isaac@exemplo.com',
                      'email_1': 'gabrielly@exemplo.com',
                      'emit_code': '1'}, follow_redirects=False)
check('lote 302', r.status_code == 302, r.status_code)
with app.app_context():
    isaac = Student.query.filter_by(email='isaac@exemplo.com').first()
    gab = Student.query.filter_by(email='gabrielly@exemplo.com').first()
    check('login orfao recriado', isaac is not None)
    check('login orfao na delegacao Eua', isaac and isaac.delegation_id == deleg_c_id,
          isaac.delegation_id if isaac else None)
    check('login orfao com certificado', isaac and Certificate.query.filter_by(
        student_id=isaac.id).count() == 1)
    check('pista por membros funcionou', gab and gab.delegation_id == deleg_g_id,
          gab.delegation_id if gab else None)

# ── E: escolher "deixar pendente" de proposito ─────────────────────────────
r = client.post('/admin/alunos/recuperar',
                data={'rows': '0', 'email_0': 'pendente-forcado@exemplo.com',
                      'deleg_0': '', 'emit_code': '1'}, follow_redirects=False)
check('pendente 302', r.status_code == 302, r.status_code)
with app.app_context():
    st = Student.query.filter_by(email='pendente-forcado@exemplo.com').first()
    check('ficou pendente (sem delegacao)', st and st.delegation_id is None,
          st.delegation_id if st else None)
    check('pendente sem certificado', st and Certificate.query.filter_by(
        student_id=st.id).count() == 0)

# ── Duplicado nao recria ───────────────────────────────────────────────────
r = client.post('/admin/alunos/recuperar',
                data={'rows': '0', 'email_0': 'guilherme@exemplo.com'},
                follow_redirects=True)
check('duplicado 200', r.status_code == 200, r.status_code)
check('avisa que nao recriou', 'já tinham aluno' in r.get_data(as_text=True))
with app.app_context():
    check('nao duplicou aluno', Student.query.filter_by(
        email='guilherme@exemplo.com').count() == 1)
    check('nao duplicou certificado', Certificate.query.filter_by(
        type='participation').count() == 4, Certificate.query.filter_by(
        type='participation').count())

# ── Pagina final + aba Alunos + Certificados ───────────────────────────────
r = client.get('/admin/alunos/recuperar')
html = r.get_data(as_text=True)
check('pagina final 200', r.status_code == 200, r.status_code)
check('mensagem nenhum orfao', 'Nenhum aluno órfão' in html)

r = client.get('/admin/alunos')
html = r.get_data(as_text=True)
check('Alunos lista Guilherme', 'Guilherme Santiago Pereira' in html)
check('Alunos lista Isaac', 'Isaac Lauro de Moura' in html)
check('Alunos lista o pendente', 'Forcar Pendente' in html)

r = client.get('/admin/certificados?year=2026')
html = r.get_data(as_text=True)
check('Certificados lista Guilherme', 'Guilherme Santiago Pereira' in html)
with app.app_context():
    check('pendente sem certificado emitido', Certificate.query.filter_by(
        student_name='Forcar Pendente').count() == 0)

r = client.get('/admin/certificados?year=2027')
check('Certificados 2027 lista escolhido', 'Sem Delegacao' in r.get_data(as_text=True))

# ── POST sem selecao ────────────────────────────────────────────────────────
r = client.post('/admin/alunos/recuperar', data={}, follow_redirects=True)
check('sem selecao 200', r.status_code == 200, r.status_code)
check('sem selecao avisa', 'Marque pelo menos um aluno' in r.get_data(as_text=True))

print('-' * 50)
if fails:
    print(f'FALHAS: {len(fails)}')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('OK: recuperar alunos passou.')
