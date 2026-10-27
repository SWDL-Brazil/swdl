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
check('codigos-pdf contem rodape', b'Pagina' in r.data)

# listagem filtra por tema
r = client.get('/admin/certificados?year=2026&committee_name=Comite de Seguranca')
check('lista com filtro tema 200', r.status_code == 200, r.status_code)

print('\n' + '-' * 50)
if fails:
    print(f'FALHAS ({len(fails)}): {fails}')
    sys.exit(1)
print('OK: todos os testes novos passaram.')
