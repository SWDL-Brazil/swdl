"""Smoke test das novas rotas de certificados: externo, organizador e PDF de codigos."""
import io
import os
import shutil
import sys
import tempfile

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('ADMIN_PASSWORD', 'swdl2025')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

WORKDIR = os.path.join(tempfile.gettempdir(), 'swdl_cert_new_test')
shutil.rmtree(WORKDIR, ignore_errors=True)
os.makedirs(WORKDIR, exist_ok=True)
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(WORKDIR, 'certs.db').replace('\\', '/')

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
from models.certificate import Certificate

client = app.test_client()
r = client.post('/admin/login', data={'email': 'admin@swdl.com', 'password': os.environ['ADMIN_PASSWORD']})
check('login admin', r.status_code in (200, 302), r.status_code)

# externo
r = client.post('/admin/certificados/gerar-externo', data={
    'year': 2026, 'name': 'Visitante Externo', 'type': 'external',
    'committee': 'CS', 'committee_name': 'Comite de Seguranca',
}, follow_redirects=False)
check('gerar-externo 302', r.status_code == 302, r.status_code)
with app.app_context():
    c = Certificate.query.filter_by(type='external').first()
    check('externo criado', c is not None)
    check('externo sem student', c.student_id is None)
    check('externo nome no snapshot', c.student_name == 'Visitante Externo', c.student_name)
    check('externo tema no snapshot', c.committee_name == 'Comite de Seguranca', c.committee_name)
    ext_id = c.id
    ext_code = c.verification_code

# sem nome -> erro (302)
r = client.post('/admin/certificados/gerar-externo', data={'year': 2026, 'name': '', 'type': 'external'}, follow_redirects=False)
check('externo sem nome rejeitado', r.status_code == 302)

# organizador
r = client.post('/admin/certificados/gerar-organizador', data={
    'year': 2026, 'name': 'Org Teste', 'committee': 'Geral',
}, follow_redirects=False)
check('gerar-organizador 302', r.status_code == 302, r.status_code)
with app.app_context():
    c = Certificate.query.filter_by(type='organizer').first()
    check('organizador criado', c is not None)
    check('organizador nome', c.student_name == 'Org Teste', c.student_name)
    org_id = c.id

# upload de PDF no externo
PDF = b'%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n'
r = client.post(f'/admin/certificados/{ext_id}/upload',
                data={'cert_file': (io.BytesIO(PDF), 'x.pdf')},
                content_type='multipart/form-data', follow_redirects=False)
check('upload externo 302', r.status_code == 302, r.status_code)
with app.app_context():
    c = db.session.get(Certificate, ext_id)
    check('externo liberado', c.released is True)
    check('externo assinado', bool(c.digital_signature))
    check('assinatura confere', c.verify_signature(app.config['SECRET_KEY']))

# API valida externo
r = client.get(f'/api/certificado/validar?code={ext_code}')
p = r.get_json()
check('API externo 200', r.status_code == 200, r.status_code)
check('API externo nome', p.get('name') == 'Visitante Externo', p.get('name'))
check('API externo signature_valid', p.get('signature_valid') is True, p.get('signature_valid'))

# PDF de codigos
r = client.get('/admin/certificados/codigos-pdf?year=2026')
check('codigos-pdf 200', r.status_code == 200, r.status_code)
check('codigos-pdf mimetype', r.mimetype == 'application/pdf', r.mimetype)
check('codigos-pdf header', r.data.startswith(b'%PDF-1.4'), r.data[:8])
check('codigos-pdf contem logo', b'SWDL' in r.data)
check('codigos-pdf logo embutida (JPEG)', b'/DCTDecode' in r.data)
check('codigos-pdf XObject /Logo', b'/Logo' in r.data)
check('codigos-pdf rodape', 'Página'.encode('latin-1') in r.data)

# listagem filtra por tema
r = client.get('/admin/certificados?year=2026&committee_name=Comite de Seguranca')
check('lista com filtro tema 200', r.status_code == 200, r.status_code)

# ── PDF: resumo, zebra, colunas e paginacao ──────────────────────
pdf_data = client.get('/admin/certificados/codigos-pdf?year=2026').data
check('pdf tem resumo por tipo', b'Resumo por tipo' in pdf_data)
check('pdf tem resumo por tema', b'Por tema' in pdf_data)
check('pdf tem cabecalho de tabela', b'(C\xf3digo) Tj' in pdf_data and b'(Nome) Tj' in pdf_data)
check('pdf tem status liberado/pendente', b'Liberado' in pdf_data or b'Pendente' in pdf_data)

from routes.admin import certificates as cert_routes

class _DummyCert:
    def __init__(self, i, long_name=False):
        self.verification_code = f'SWDL-{i:06d}'
        self.student_name = ('Nome Muito Longo Que Nao Cabe Na Coluna ' * 3) if long_name else f'Pessoa {i}'
        self.name = None
        self.type = 'participation'
        self.edition_year = 2026
        self.committee = 'CS'
        self.committee_name = 'Comite de Seguranca'
        self.released = False

    @property
    def display_name(self):
        return self.student_name

    @property
    def type_label(self):
        return 'Participacao'

dummies = [_DummyCert(i, long_name=(i == 0)) for i in range(60)]
big_pdf = cert_routes._build_codes_pdf(dummies, 2026, 'todos')
check('pdf paginado gera 2 paginas', b'/Count 2' in big_pdf, big_pdf[:200])
check('pdf pagina 1 de 2', '(Página 1 de 2)'.encode('latin-1') in big_pdf)
check('pdf repete cabecalho na pagina 2', big_pdf.count(b'(C\xf3digo) Tj') == 2,
      big_pdf.count(b'(C\xf3digo) Tj'))
check('pdf zebra presente', b'0.955 0.955 0.955 rg' in big_pdf)
check('pdf nome longo truncado com ...', b'...' in big_pdf)
check('pdf nao estoura margem direita', b'(Comite de Seguranca (CS))' not in big_pdf)

empty_pdf = cert_routes._build_codes_pdf([], 2026, 'todos')
check('pdf vazio e valido', empty_pdf.startswith(b'%PDF-1.4') and b'Nenhum certificado' in empty_pdf)

# ── Pessoas: CRUD + gerar a partir do cadastro ──────────────────
r = client.get('/admin/certificados/pessoas')
check('pessoas pagina 200', r.status_code == 200, r.status_code)

r = client.post('/admin/certificados/pessoas/nova', data={
    'kind': 'external', 'name': 'Pessoa Cadastrada', 'email': 'pessoa@exemplo.com',
    'committee': 'DHR', 'committee_name': 'Direitos Humanos', 'country': 'Brasil',
}, follow_redirects=False)
check('criar pessoa 302', r.status_code == 302, r.status_code)

from models.certificate_person import CertificatePerson
with app.app_context():
    person = CertificatePerson.query.filter_by(name='Pessoa Cadastrada').first()
    check('pessoa criada', person is not None)
    check('pessoa tipo', person.kind == 'external', person.kind if person else None)
    person_id = person.id

r = client.post(f'/admin/certificados/pessoas/{person_id}/gerar',
                data={'year': 2026, 'type': 'external'}, follow_redirects=False)
check('gerar a partir da pessoa 302', r.status_code == 302, r.status_code)
with app.app_context():
    c = Certificate.query.filter_by(person_id=person_id).first()
    check('certificado da pessoa criado', c is not None)
    check('certificado herdou nome', c.student_name == 'Pessoa Cadastrada',
          c.student_name if c else None)
    check('certificado herdou tema', c.committee_name == 'Direitos Humanos',
          c.committee_name if c else None)

# dedupe: mesmo tipo/edicao nao duplica
r = client.post(f'/admin/certificados/pessoas/{person_id}/gerar',
                data={'year': 2026, 'type': 'external'}, follow_redirects=False)
with app.app_context():
    n = Certificate.query.filter_by(person_id=person_id, type='external').count()
    check('nao duplica certificado da pessoa', n == 1, n)

# externo com "salvar em pessoas" cria ficha e vincula
r = client.post('/admin/certificados/gerar-externo', data={
    'year': 2026, 'type': 'external', 'name': 'Auto Salvar',
    'email': 'auto@exemplo.com', 'committee': 'CS',
    'committee_name': 'Comite de Seguranca', 'save_person': '1',
}, follow_redirects=False)
check('externo com save_person 302', r.status_code == 302, r.status_code)
with app.app_context():
    p = CertificatePerson.query.filter_by(name='Auto Salvar').first()
    check('save_person criou pessoa', p is not None)
    c = Certificate.query.filter_by(name='Auto Salvar').first()
    check('certificado vinculado a pessoa', bool(c and c.person_id == (p.id if p else None)),
          (c.person_id if c else None, p.id if p else None))

# editar e excluir pessoa
r = client.post(f'/admin/certificados/pessoas/{person_id}/editar', data={
    'kind': 'organizer', 'name': 'Pessoa Cadastrada Editada', 'email': 'editada@exemplo.com',
}, follow_redirects=False)
check('editar pessoa 302', r.status_code == 302, r.status_code)
with app.app_context():
    p = db.session.get(CertificatePerson, person_id)
    check('pessoa editada', p.name == 'Pessoa Cadastrada Editada', p.name)

r = client.post(f'/admin/certificados/pessoas/{person_id}/excluir', follow_redirects=False)
check('excluir pessoa 302', r.status_code == 302, r.status_code)
with app.app_context():
    check('pessoa removida', db.session.get(CertificatePerson, person_id) is None)
    c = Certificate.query.filter_by(student_name='Pessoa Cadastrada').first()
    check('certificado mantido sem vinculo', bool(c) and c.person_id is None,
          (bool(c), c.person_id if c else None))

# lista de certificados nao quebra com pessoas cadastradas
r = client.get('/admin/certificados?year=2026&type=external')
check('lista externos 200', r.status_code == 200, r.status_code)

print('\n' + '-' * 50)
if fails:
    print(f'FALHAS ({len(fails)}): {fails}')
    sys.exit(1)
print('OK: todos os testes novos passaram.')
