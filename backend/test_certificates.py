"""Teste do fluxo de CERTIFICADOS — gerar → upload/liberar → verificar → revogar.

Sobe o app com SQLite temporário, desliga o CSRF e exercita o caminho
inteiro (admin + delegado + rota publica + API), verificando:

  * geracao de codigos (unicidade, sem duplicar na 2a chamada)
  * validacao de upload (extensao, magic bytes, tamanho, campo ausente)
  * liberacao = upload do PDF para o BANCO + assinatura HMAC confere
  * rota publica /certificado/<code> (PDF do banco, fallback HTML, 404)
  * API /api/certificado/validar (400/404/signature_valid/has_pdf)
  * gate de assinatura quando a SECRET_KEY muda
  * revogacao (remover-pdf) e exclusao (linha inteira some)
  * premiacao (individual, delegacao, duplicado ignorado)
  * indice unico (student, edition, type)
  * cascade: excluir aluno apaga o certificado junto
  * serve_certificate: admin-only + codigo nao vira caminho de arquivo
  * SNAPSHOT: nome/pais/comitie copiados na emissao (gerar, premiar, upload)
  * assinatura sobrevive a renomear o aluno / trocar a delegacao
  * backfill do snapshot para linha antiga (idempotente)

O PDF mora em Certificate.pdf_data (bytea/BLOB) — nada de arquivo em disco,
porque o Render free nao tem disco persistente.

Uso:
    python test_certificates.py
"""
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

WORKDIR = os.path.join(tempfile.gettempdir(), 'swdl_cert_test')
shutil.rmtree(WORKDIR, ignore_errors=True)
os.makedirs(WORKDIR, exist_ok=True)
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(WORKDIR, 'certs.db').replace('\\', '/')

PDF_BYTES = b'%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n'

_failures = []
_checks = 0


def check(label, cond, extra=''):
    global _checks
    _checks += 1
    if cond:
        print(f'  ok   {label}')
    else:
        print(f'  FALHA {label} {extra}')
        _failures.append(label)


def section(title):
    print(f'\n== {title} ' + '=' * max(1, 60 - len(title)))


class FakeUpload:
    """FileStorage minimo para submeter PDF de teste."""
    def __init__(self, data, filename='cert.pdf'):
        self.data = data
        self.filename = filename
        self.stream = io.BytesIO(data)

    def save(self, dst):
        with open(dst, 'wb') as fh:
            fh.write(self.data)


def main():
    from app import create_app
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True

    from extensions import db
    from models.user import User
    from models.student import Student
    from models.delegation import Delegation
    from models.theme import Theme
    from models.certificate import Certificate, CERT_TYPES
    from cert_storage import validate_pdf, MAX_PDF_BYTES

    # ── seed: 1 delegacao (com tema), 2 alunos (um com User logavel) ────
    with app.app_context():
        theme = Theme(name='Estreito de Ormuz')
        db.session.add(theme)
        db.session.flush()
        deleg = Delegation(country='Brasil', country_flag='\U0001f1e7\U0001f1f7',
                           committee='CS', edition_year=2026, accepted=True,
                           theme_id=theme.id)
        db.session.add(deleg)
        db.session.flush()

        user = User(name='Ana Delegada', email='ana@teste.com', role='student')
        user.set_password('x')
        db.session.add(user)
        db.session.flush()

        ana = Student(name='Ana Delegada', email='ana@teste.com',
                      user_id=user.id, delegation_id=deleg.id)
        bia = Student(name='Bia Delegada', email='bia@teste.com',
                      delegation_id=deleg.id)
        db.session.add_all([ana, bia])
        db.session.commit()
        ANA_ID, BIA_ID, DELEG_ID, USER_ID = ana.id, bia.id, deleg.id, user.id
        ANA_GID = ana.global_id
        THEME_NAME = theme.name

    client = app.test_client()
    r = client.post('/admin/login', data={
        'email': 'admin@swdl.com',
        'password': os.environ['ADMIN_PASSWORD'],
    })
    check('login admin', r.status_code in (200, 302), r.status_code)

    # ── 1. geracao de codigos ───────────────────────────────────────────
    section('1. gerar codigos')
    r = client.post('/admin/certificados/gerar-codigos', data={'year': 2026},
                    follow_redirects=False)
    check('POST gerar-codigos 302', r.status_code == 302, r.status_code)

    with app.app_context():
        certs = Certificate.query.all()
        check('2 certificados criados (Ana + Bia)', len(certs) == 2, len(certs))
        check('codigos no formato SWDL-XXXXXX',
              all(c.verification_code.startswith('SWDL-') and
                  len(c.verification_code) == 11 for c in certs))
        check('codigos unicos', len({c.verification_code for c in certs}) == 2)
        check('nenhum liberado ainda', not any(c.released for c in certs))
        check('nenhum PDF ainda', not any(c.has_pdf for c in certs))
        ana_cert = next(c for c in certs if c.student_id == ANA_ID)
        check('snapshot preenchido na geracao (nome/pais/comitie/tema)',
              ana_cert.student_name == 'Ana Delegada'
              and ana_cert.global_id == ANA_GID
              and ana_cert.country == 'Brasil'
              and ana_cert.country_flag == '\U0001f1e7\U0001f1f7'
              and ana_cert.committee == 'CS'
              and ana_cert.committee_name == THEME_NAME,
              (ana_cert.student_name, ana_cert.country, ana_cert.committee,
               ana_cert.committee_name))
        check('display_name vem do snapshot',
              ana_cert.display_name == 'Ana Delegada', ana_cert.display_name)
        ANA_CODE = next(c.verification_code for c in certs if c.student_id == ANA_ID)

    r = client.post('/admin/certificados/gerar-codigos', data={'year': 2026},
                    follow_redirects=False)
    check('2a chamada nao duplica (302)', r.status_code == 302)
    with app.app_context():
        check('2a chamada criou 0', Certificate.query.count() == 2,
              Certificate.query.count())

    # ── 2. validacao de upload ──────────────────────────────────────────
    section('2. upload invalido')
    with app.app_context():
        cert_id = Certificate.query.filter_by(verification_code=ANA_CODE).first().id

    def upload(payload):
        data = {'cert_file': payload} if payload is not None else {}
        return client.post(f'/admin/certificados/{cert_id}/upload', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=False)

    r = upload((io.BytesIO(b'nao sou pdf'), 'x.pdf'))
    check('conteudo sem magic bytes rejeitado', r.status_code == 302)
    with app.app_context():
        c = db.session.get(Certificate, cert_id)
        check('continua nao liberado apos arquivo invalido', not c.released)
        check('nao gravou pdf_data', c.pdf_data is None)

    r = upload((io.BytesIO(b'oi'), 'x.txt'))
    check('extensao .txt rejeitada', r.status_code == 302)

    r = upload(None)
    check('sem campo cert_file rejeitado', r.status_code == 302)

    big = b'%PDF-1.4 ' + b'0' * (MAX_PDF_BYTES + 1024)
    r = upload((io.BytesIO(big), 'big.pdf'))
    check(f'PDF acima de {MAX_PDF_BYTES // (1024 * 1024)}MB rejeitado',
          r.status_code == 302)
    with app.app_context():
        c = db.session.get(Certificate, cert_id)
        check('nenhum lixo gravado', c.pdf_data is None and not c.released)

    check('validate_pdf devolve os bytes certos',
          validate_pdf(FakeUpload(PDF_BYTES)) == PDF_BYTES)
    try:
        validate_pdf(FakeUpload(b'xxx'))
        check('validate_pdf levanta ValueError', False)
    except ValueError:
        check('validate_pdf levanta ValueError', True)

    # ── 3. upload valido = liberacao + assinatura ───────────────────────
    section('3. upload = liberar + assinar')
    r = upload((io.BytesIO(PDF_BYTES), 'cert.pdf'))
    check('upload valido 302', r.status_code == 302, r.status_code)

    with app.app_context():
        c = db.session.get(Certificate, cert_id)
        check('released=True', c.released is True)
        check('pdf_data guarda os bytes', bytes(c.pdf_data) == PDF_BYTES)
        check('has_pdf=True', c.has_pdf is True)
        check('pdf_path = <CODE>.pdf', c.pdf_path == f'{ANA_CODE}.pdf', c.pdf_path)
        check('assinatura gravada', bool(c.digital_signature))
        check('signed_at preenchido', c.signed_at is not None)
        check('HMAC confere com a SECRET_KEY atual',
              c.verify_signature(app.config['SECRET_KEY']))
        check('nenhum arquivo criado no disco',
              not os.path.exists(os.path.join(WORKDIR, f'{ANA_CODE}.pdf')))

    # ── 4. rota publica ─────────────────────────────────────────────────
    section('4. rota publica /certificado/<code>')
    r = client.get(f'/certificado/{ANA_CODE}')
    check('PDF servido', r.status_code == 200 and r.mimetype == 'application/pdf',
          f'{r.status_code} {r.mimetype}')
    check('conteudo do PDF bate', r.data == PDF_BYTES)

    r = client.get('/certificado/SWDL-ZZZZZZ')
    check('codigo inexistente -> 404', r.status_code == 404, r.status_code)

    with app.app_context():
        bia_code = Certificate.query.filter_by(student_id=BIA_ID).first().verification_code
    r = client.get(f'/certificado/{bia_code}')
    check('certificado nao liberado -> 404', r.status_code == 404, r.status_code)

    # sem PDF (so a pagina HTML continua de pé)
    with app.app_context():
        c = db.session.get(Certificate, cert_id)
        c.pdf_data = None
        db.session.commit()
    r = client.get(f'/certificado/{ANA_CODE}')
    html = r.get_data(as_text=True)
    check('sem PDF -> pagina HTML 200', r.status_code == 200, r.status_code)
    check('HTML diz Validado (assinatura confere)',
          'V\xe1lido e Autenticado' in html)
    check('HTML mostra o codigo', ANA_CODE in html)

    # ── 5. gate de assinatura ──────────────────────────────────────────
    section('5. gate de assinatura (SECRET_KEY trocada)')
    original_key = app.config['SECRET_KEY']
    app.config['SECRET_KEY'] = 'chave-rotacionada'
    r = client.get(f'/certificado/{ANA_CODE}')
    html = r.get_data(as_text=True)
    check('HTML marca assinatura invalida',
          'Assinatura inv\xe1lida' in html and 'V\xe1lido e Autenticado' not in html)

    api = client.get(f'/api/certificado/validar?code={ANA_CODE}')
    payload = api.get_json()
    check('API 200 mesmo com assinatura invalida', api.status_code == 200)
    check('API signature_valid=False', payload.get('signature_valid') is False,
          payload.get('signature_valid'))
    app.config['SECRET_KEY'] = original_key

    # ── 6. API de validacao ────────────────────────────────────────────
    section('6. API /api/certificado/validar')
    r = client.get('/api/certificado/validar')
    check('sem code -> 400', r.status_code == 400, r.status_code)

    r = client.get('/api/certificado/validar?code=SWDL-ZZZZZZ')
    check('codigo desconhecido -> 404', r.status_code == 404, r.status_code)

    r = client.get(f'/api/certificado/validar?code={bia_code}')
    check('nao liberado -> 404', r.status_code == 404, r.status_code)

    r = client.get(f'/api/certificado/validar?code={ANA_CODE}')
    p = r.get_json()
    check('liberado -> 200/valid', r.status_code == 200 and p.get('valid') is True)
    check('signature_valid=True', p.get('signature_valid') is True)
    check('has_pdf=False (pdf_data vazio)', p.get('has_pdf') is False,
          p.get('has_pdf'))
    check('pdf_path aponta para a rota publica',
          p.get('pdf_path') == f'/certificado/{ANA_CODE}')
    check('type_label preenchido',
          p.get('type_label') == CERT_TYPES['participation'], p.get('type_label'))
    check('sem campo certificate_url mentiroso', 'certificate_url' not in p)
    check('dados da delegacao', p.get('country') == 'Brasil' and
          p.get('committee') == 'CS', p.get('country'))
    check('nome e id global vem do snapshot',
          p.get('name') == 'Ana Delegada' and p.get('global_id') == ANA_GID,
          (p.get('name'), p.get('global_id')))
    check('flag e tema no payload',
          p.get('country_flag') == '\U0001f1e7\U0001f1f7' and
          p.get('committee_name') == THEME_NAME,
          (p.get('country_flag'), p.get('committee_name')))

    # devolve o PDF ao banco
    with app.app_context():
        c = db.session.get(Certificate, cert_id)
        c.pdf_data = PDF_BYTES
        db.session.commit()

    r = client.get(f'/api/certificado/validar?code={ANA_CODE}')
    check('has_pdf=True com o PDF de volta', r.get_json().get('has_pdf') is True)
    r = client.get(f'/certificado/{ANA_CODE}')
    check('PDF servido de novo', r.status_code == 200 and r.data == PDF_BYTES)

    # ── 7. painel do delegado ──────────────────────────────────────────
    section('7. painel do delegado')
    student_client = app.test_client()
    with student_client.session_transaction() as sess:
        sess['_user_id'] = str(USER_ID)
        sess['_fresh'] = True
    r = student_client.get('/student/certificados')
    check('pagina 200', r.status_code == 200, r.status_code)
    body = r.get_data(as_text=True)
    check('lista o certificado liberado da Ana', ANA_CODE in body)
    check('nao lista o nao-liberado da Bia', bia_code not in body)

    r = student_client.get('/admin/certificados')
    check('delegado nao acessa admin (403)', r.status_code == 403, r.status_code)
    r = student_client.get(f'/admin/certificados/arquivo/{ANA_CODE}.pdf')
    check('delegado nao acessa arquivo admin (403)', r.status_code == 403,
          r.status_code)

    # ── 8. rota admin de arquivo ───────────────────────────────────────
    section('8. rota admin de arquivo / rota nao vira caminho')
    r = client.get(f'/admin/certificados/arquivo/{ANA_CODE}.pdf')
    check('admin baixa o PDF', r.status_code == 200 and r.data == PDF_BYTES,
          f'{r.status_code}')

    r = client.get('/admin/certificados/arquivo/..%2F..%2Fcerts.db')
    check('nome com traversal nao devolve 200', r.status_code != 200,
          r.status_code)
    r = client.get('/admin/certificados/arquivo/nao-existe.pdf')
    check('arquivo desconhecido -> 404', r.status_code == 404, r.status_code)

    # ── 9. premiacao ───────────────────────────────────────────────────
    section('9. premiacao')
    r = client.post('/admin/certificados/premiar', data={
        'student_id': ANA_ID, 'type': 'best_speaker', 'year': 2026,
    }, follow_redirects=False)
    check('premiar individual 302', r.status_code == 302, r.status_code)
    with app.app_context():
        n = Certificate.query.filter_by(student_id=ANA_ID, type='best_speaker').count()
        check('1 certificado de melhor orador', n == 1, n)

    r = client.post('/admin/certificados/premiar', data={
        'student_id': ANA_ID, 'type': 'best_speaker', 'year': 2026,
    }, follow_redirects=False)
    with app.app_context():
        n = Certificate.query.filter_by(student_id=ANA_ID, type='best_speaker').count()
        check('duplicado ignorado', n == 1, n)

    r = client.post('/admin/certificados/premiar', data={
        'delegation_id': DELEG_ID, 'type': 'best_delegation', 'year': 2026,
    }, follow_redirects=False)
    with app.app_context():
        n = Certificate.query.filter_by(type='best_delegation').count()
        check('melhor delegacao premia os 2 alunos', n == 2, n)

    r = client.post('/admin/certificados/premiar',
                    data={'student_id': ANA_ID, 'type': 'participation', 'year': 2026},
                    follow_redirects=False)
    check('participation nao aceita como premio', r.status_code == 302)

    # ── 10. indice unico ───────────────────────────────────────────────
    section('10. indice unico (student, edition, type)')
    with app.app_context():
        dup = Certificate(student_id=ANA_ID, edition_year=2026,
                          type='best_speaker', verification_code='SWDL-DUPDUP')
        db.session.add(dup)
        try:
            db.session.flush()
            check('indice unico bloqueia duplicata', False, 'flush passou')
        except Exception:
            db.session.rollback()
            check('indice unico bloqueia duplicata', True)

    # ── 11. revogacao e exclusao ───────────────────────────────────────
    section('11. revogacao (remover-pdf) e exclusao')
    with app.app_context():
        c = db.session.get(Certificate, cert_id)

    r = client.post(f'/admin/certificados/{cert_id}/remover-pdf',
                    follow_redirects=False)
    check('remover-pdf 302', r.status_code == 302, r.status_code)
    with app.app_context():
        c = db.session.get(Certificate, cert_id)
        check('released voltou a False', c.released is False)
        check('pdf_data limpo', c.pdf_data is None)
        check('assinatura limpa', c.digital_signature is None)
        check('codigo permanece', c.verification_code == ANA_CODE)

    r = client.get(f'/certificado/{ANA_CODE}')
    check('apos revogar -> 404', r.status_code == 404, r.status_code)
    r = client.get(f'/api/certificado/validar?code={ANA_CODE}')
    check('API apos revogar -> 404', r.status_code == 404, r.status_code)

    # exclusao total (a linha carrega o PDF, entao a linha some com ele)
    r = upload((io.BytesIO(PDF_BYTES), 'cert.pdf'))
    check('re-upload 302', r.status_code == 302)
    r = client.post(f'/admin/certificados/{cert_id}/excluir', follow_redirects=False)
    check('excluir 302', r.status_code == 302, r.status_code)
    with app.app_context():
        check('linha excluida (PDF junto)',
              db.session.get(Certificate, cert_id) is None)

    # ── 12. cascade: excluir aluno ─────────────────────────────────────
    section('12. cascade excluir aluno')
    with app.app_context():
        c = Certificate.query.filter_by(student_id=BIA_ID).first()
        bia_cert_id, bia_code = c.id, c.verification_code
        c.released = True
        c.pdf_data = PDF_BYTES
        c.pdf_path = f'{bia_code}.pdf'
        c.digital_signature = c.compute_signature(app.config['SECRET_KEY'])
        db.session.commit()
        c = db.session.get(Certificate, bia_cert_id)
        check('pdf_data da Bia gravado', c.has_pdf)

        student = db.session.get(Student, BIA_ID)
        db.session.delete(student)
        db.session.commit()
        check('linha do certificado apagada',
              db.session.get(Certificate, bia_cert_id) is None)

    # ── 13. snapshot: imutavel depois de assinado ──────────────────────
    section('13. snapshot: upload refresca / renomear nao quebra')
    with app.app_context():
        sp = Certificate.query.filter_by(student_id=ANA_ID,
                                         type='best_speaker').first()
        sp_id, sp_code = sp.id, sp.verification_code
        check('premio ja nasce com snapshot', sp.student_name == 'Ana Delegada',
              sp.student_name)

    # renomeia ANTES do upload: o snapshot e atualizado no ato da liberacao
    with app.app_context():
        ana = db.session.get(Student, ANA_ID)
        ana.name = 'Ana Nome Corrigido'
        db.session.commit()

    r = client.post(f'/admin/certificados/{sp_id}/upload',
                    data={'cert_file': (io.BytesIO(PDF_BYTES), 'sp.pdf')},
                    content_type='multipart/form-data', follow_redirects=False)
    check('upload do premio 302', r.status_code == 302, r.status_code)
    with app.app_context():
        sp = db.session.get(Certificate, sp_id)
        check('upload refresca o snapshot', sp.student_name == 'Ana Nome Corrigido',
              sp.student_name)
        check('assinatura vale com o snapshot do upload',
              sp.verify_signature(app.config['SECRET_KEY']))

    # renomeia DEPOIS de assinado: nem o que a pagina mostra nem o HMAC mudam
    with app.app_context():
        ana = db.session.get(Student, ANA_ID)
        ana.name = 'Ana Nome Final'
        deleg = db.session.get(Delegation, DELEG_ID)
        deleg.country = 'Argentina'
        deleg.country_flag = '\U0001f1f1\U0001f1f6'
        deleg.committee = 'DHR'
        db.session.commit()

    r = client.get(f'/api/certificado/validar?code={sp_code}')
    p = r.get_json()
    check('API mostra o nome de quando emitiu', p.get('name') == 'Ana Nome Corrigido',
          p.get('name'))
    check('API mostra o pais/comitie de quando emitiu',
          p.get('country') == 'Brasil' and p.get('committee') == 'CS',
          (p.get('country'), p.get('committee')))
    check('signature_valid continua True apos renomear',
          p.get('signature_valid') is True, p.get('signature_valid'))

    with app.app_context():
        sp = db.session.get(Certificate, sp_id)
        check('verify_signature no model continua True',
              sp.verify_signature(app.config['SECRET_KEY']))
        # pagina HTML (sem PDF) mostra o snapshot, nao o cadastro de hoje
        pdf_backup, sp.pdf_data = sp.pdf_data, None
        db.session.commit()

    r = client.get(f'/certificado/{sp_code}')
    html = r.get_data(as_text=True)
    check('pagina HTML 200 sem PDF', r.status_code == 200, r.status_code)
    check('HTML mostra o nome emitido',
          'Ana Nome Corrigido' in html, 'nome emitido ausente')
    check('HTML nao mostra o nome novo do cadastro',
          'Ana Nome Final' not in html, 'cadastro vazou')
    with app.app_context():
        sp = db.session.get(Certificate, sp_id)
        sp.pdf_data = pdf_backup
        db.session.commit()

    r = client.get('/admin/certificados')
    check('lista admin 200', r.status_code == 200, r.status_code)
    check('lista admin usa o snapshot',
          'Ana Nome Corrigido' in r.get_data(as_text=True))

    # ── 14. backfill do snapshot ───────────────────────────────────────
    section('14. backfill de snapshot (linha antiga)')
    with app.app_context():
        sp = db.session.get(Certificate, sp_id)
        sp.student_name = None
        sp.country = None
        sp.country_flag = None
        sp.committee = None
        sp.committee_name = None
        sp.global_id = None
        db.session.commit()

        from app import backfill_cert_snapshot
        n = backfill_cert_snapshot()
        check('backfill corrigiu a linha apagada', n == 1, n)
        sp = db.session.get(Certificate, sp_id)
        check('snapshot restaurado do cadastro atual',
              sp.student_name == 'Ana Nome Final'
              and sp.country == 'Argentina'
              and sp.committee == 'DHR'
              and sp.global_id == ANA_GID,
              (sp.student_name, sp.country, sp.committee, sp.global_id))

        n2 = backfill_cert_snapshot()
        check('backfill idempotente (0 na 2a vez)', n2 == 0, n2)

    # ── resumo ─────────────────────────────────────────────────────────
    print('\n' + '-' * 60)
    if _failures:
        print(f'FALHAS ({len(_failures)}/{_checks}):')
        for f in _failures:
            print(f'  - {f}')
        return 1
    print(f'OK: {_checks}/{_checks} checagens passaram.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
