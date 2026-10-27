from flask import render_template, redirect, url_for, flash, request, current_app, abort, make_response
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required, _log_audit
from models.student import Student
from models.delegation import Delegation
from models.theme import Theme
from models.user import User
from models.certificate import Certificate, CERT_TYPES, generate_verification_code
from models.certificate_person import CertificatePerson, PERSON_KINDS
from cert_storage import validate_pdf, pdf_response
from extensions import db
from sqlalchemy import select, func, case, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import io


def _current_year():
    return datetime.now(timezone.utc).year


def _used_codes(extra_check_student=False):
    """Todos os codigos em uso, em 2 queries (nao 2 por aluno)."""
    codes = {c for (c,) in db.session.query(Certificate.verification_code).all()}
    if extra_check_student:
        codes |= {c for (c,) in db.session.query(Student.verification_code)
                  .filter(Student.verification_code.isnot(None)).all()}
    return codes


def _pick_code(used):
    """Codigo SWDL-XXXXXX unico; registra em ``used`` para o lote corrente."""
    for _ in range(200):
        code = generate_verification_code()
        if code not in used:
            used.add(code)
            return code
    # Inalcancavel na pratica (36^6 espaco); melhor falhar alto do que
    # commitar uma linha com codigo duplicado (IntegrityError sem contexto).
    raise RuntimeError('nao foi possivel gerar codigo de verificacao unico')


def _themes_for_year(year):
    """Temas que possuem delegacoes nesta edicao (para o filtro de tema)."""
    rows = db.session.query(Theme.name).join(
        Delegation, Delegation.theme_id == Theme.id
    ).filter(
        Delegation.edition_year == year
    ).distinct().order_by(Theme.name).all()
    return [r[0] for r in rows if r[0]]


@admin_bp.route('/certificados/arquivo/<filename>')
@login_required
@admin_required
def serve_certificate(filename):
    """Serve o PDF do certificado a partir do banco (rota admin).

    ``filename`` e ``<CODE>.pdf`` — o codigo e a chave, nao um caminho.
    """
    code = filename[:-4] if filename.lower().endswith('.pdf') else filename
    cert = Certificate.query.filter_by(verification_code=code).first()
    if not cert or not cert.released or not cert.has_pdf:
        abort(404)
    return pdf_response(cert.pdf_data, cert.pdf_path or filename)


@admin_bp.route('/certificados')
@login_required
@admin_required
def certificates_list():
    """Gestao de certificados — filtravel por edicao e tipo."""
    from sqlalchemy.orm import joinedload
    from models.audit_log import AuditLog

    year = request.args.get('year', type=int)
    cert_type = request.args.get('type', '')
    committee_name = request.args.get('committee_name', '')

    years = [r[0] for r in db.session.query(Certificate.edition_year)
             .distinct().order_by(Certificate.edition_year.desc())]
    if not year:
        cy = _current_year()
        year = cy if cy in years else (years[0] if years else cy)

    # Ordena pelo SNAPSHOT (student_name): nenhuma juncao com students —
    # o nome exibido e o que foi emitido, nao o cadastro de hoje.
    query = Certificate.query
    if year:
        query = query.filter(Certificate.edition_year == year)
    if cert_type and cert_type in CERT_TYPES:
        query = query.filter(Certificate.type == cert_type)
    if committee_name:
        query = query.filter(Certificate.committee_name == committee_name)

    certs = query.order_by(Certificate.type,
                           func.coalesce(Certificate.student_name,
                                         Certificate.name, '').asc()).all()

    # Stats cobrem a edição inteira (ignoram o filtro de tipo da tabela)
    if cert_type and cert_type in CERT_TYPES:
        all_for_year = Certificate.query.filter_by(edition_year=year).all()
    else:
        all_for_year = certs

    # "Sem participacao" = alunos DA EDICAO (delegacao.edition_year == ano)
    # sem certificado de participacao naquele ano — 1 query, nao carrega
    # todos os alunos do banco (com varias edicoes o numero era mentira).
    part_ids = select(Certificate.student_id).where(
        Certificate.edition_year == year,
        Certificate.type == 'participation')
    edition_total, missing = db.session.execute(
        select(func.count(Student.id),
               func.coalesce(func.sum(case((Student.id.notin_(part_ids), 1),
                                           else_=0)), 0))
        .select_from(Student)
        .join(Delegation, Student.delegation_id == Delegation.id)
        .where(Delegation.edition_year == year)
    ).one()

    stats = {
        'total': len(all_for_year),
        'participation': sum(1 for c in all_for_year if c.type == 'participation'),
        'awards': sum(1 for c in all_for_year if c.type != 'participation'),
        'with_pdf': sum(1 for c in all_for_year if c.has_pdf),
        'released': sum(1 for c in all_for_year if c.released),
        'edition_students': edition_total,
        'missing_participation': missing,
    }

    students = Student.query.options(joinedload(Student.delegation))\
                            .order_by(Student.name).all()
    delegations = Delegation.query.options(joinedload(Delegation.students))\
                                   .order_by(Delegation.country).all()
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()
    themes = _themes_for_year(year)
    users = User.query.order_by(User.name).all()
    people = CertificatePerson.query.order_by(CertificatePerson.name).all()

    return render_template('admin/certificates_list.html',
                           certs=certs,
                           years=years,
                           current_year=year,
                           current_type=cert_type,
                           current_committee=committee_name,
                           cert_types=CERT_TYPES,
                           themes=themes,
                           people=people,
                           person_kinds=PERSON_KINDS,
                           stats=stats,
                           students=students,
                           delegations=delegations,
                           users=users,
                           audit_logs=audit_logs)


@admin_bp.route('/certificados/gerar-codigos', methods=['POST'])
@login_required
@admin_required
def certificates_generate_codes():
    """Cria certificados de participacao (com codigo) sem gate de presenca.

    Com ``student_id`` no form, gera apenas para esse aluno.
    """
    year = request.form.get('year', type=int) or _current_year()
    student_id = request.form.get('student_id', type=int)

    # selectinload: delegacao + tema numa query extra (sem N+1 — no ReG
    # cada query custa ~180ms e uma edicao tem 100+ alunos).
    query = Student.query.options(
        selectinload(Student.delegation).selectinload(Delegation.theme))
    if student_id:
        query = query.filter(Student.id == student_id)
    students = query.all()

    existing = {c for (c,) in db.session.query(Certificate.student_id)
                .filter(Certificate.edition_year == year,
                        Certificate.type == 'participation').all()}
    used = _used_codes(extra_check_student=True)

    count = 0
    for s in students:
        if s.id in existing:
            continue
        cert = Certificate(student=s, edition_year=year,
                           type='participation',
                           verification_code=_pick_code(used))
        cert.fill_snapshot()
        db.session.add(cert)
        count += 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo ou certificado duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    if student_id:
        _log_audit('generate_codes', 'student', student_id, details=f'{count} codigo gerado ({year})')
    else:
        _log_audit('generate_codes', 'system', 0, details=f'{count} codigos gerados ({year})')
    flash(f'{count} certificados de participacao gerados para {year}!', 'success')
    return redirect(url_for('admin.certificates_list', year=year))


@admin_bp.route('/certificados/premiar', methods=['POST'])
@login_required
@admin_required
def certificate_award():
    """Cria certificado(s) de premiacao (melhor delegacao/orador/vestimenta)."""
    student_id = request.form.get('student_id', type=int)
    delegation_id = request.form.get('delegation_id', type=int)
    cert_type = request.form.get('type', '')
    year = request.form.get('year', type=int) or _current_year()
    notes = request.form.get('notes', '').strip() or None

    if cert_type not in CERT_TYPES or cert_type == 'participation':
        flash('Tipo de premiacao invalido.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    targets = []
    if cert_type == 'best_delegation' and delegation_id:
        # traz alunos + delegacao + tema de uma vez (evita N+1 no lote)
        deleg = Delegation.query.options(
            selectinload(Delegation.students)
            .selectinload(Student.delegation)
            .selectinload(Delegation.theme)
        ).get_or_404(delegation_id)
        targets = list(deleg.students)
        if not targets:
            flash('Delegacao sem alunos vinculados.', 'error')
            return redirect(url_for('admin.certificates_list', year=year))
    elif student_id:
        targets = [Student.query.options(
            selectinload(Student.delegation).selectinload(Delegation.theme)
        ).get_or_404(student_id)]
    else:
        flash('Selecione um aluno (ou uma delegacao para "Melhor Delegacao").', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    existing = {sid for (sid,) in db.session.query(Certificate.student_id)
                .filter(Certificate.edition_year == year,
                        Certificate.type == cert_type).all()}
    used = _used_codes()

    count = 0
    skipped = 0
    for s in targets:
        if s.id in existing:
            skipped += 1
            continue
        cert = Certificate(student=s, edition_year=year, type=cert_type,
                           verification_code=_pick_code(used), notes=notes)
        cert.fill_snapshot()
        db.session.add(cert)
        existing.add(s.id)
        count += 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo ou certificado duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    _log_audit('award_certificate', 'system', 0,
               details=f'{count}x {CERT_TYPES[cert_type]} ({year})')
    msg = f'{count} certificado(s) de "{CERT_TYPES[cert_type]}" criado(s)!'
    if skipped:
        msg += f' {skipped} ja existiam e foram ignorados.'
    flash(msg + ' Faca o upload do PDF para liberar.', 'success')
    return redirect(url_for('admin.certificates_list', year=year, type=cert_type))


@admin_bp.route('/certificados/<int:id>/upload', methods=['POST'])
@login_required
@admin_required
def certificate_upload(id):
    """Upload do PDF de um certificado — libera e assina (HMAC)."""
    cert = Certificate.query.get_or_404(id)

    file = request.files.get('cert_file')
    try:
        data = validate_pdf(file)
    except ValueError as exc:
        flash(str(exc), 'error')
        return redirect(url_for('admin.certificates_list', year=cert.edition_year))

    cert.pdf_data = data
    cert.pdf_path = f'{cert.verification_code}.pdf'
    cert.released = True
    # Snapshot de novo no momento da liberacao: e o nome/pais/comitie que
    # entram na assinatura, e tem que casar com o PDF que o admin acabou de
    # subir (pode ter havido correcao de cadastro desde a geracao do codigo).
    cert.fill_snapshot()
    secret = current_app.config.get('SECRET_KEY', 'swdl-secret')
    cert.digital_signature = cert.compute_signature(secret)
    cert.signed_at = datetime.now(timezone.utc)
    db.session.commit()

    student_name = cert.display_name
    _log_audit('upload_certificate', 'certificate', cert.id, student_name,
               details=f'PDF salvo: {cert.pdf_path} ({cert.type_label} {cert.edition_year})')
    flash(f'PDF de {student_name} ({cert.type_label}) enviado e liberado!', 'success')
    return redirect(url_for('admin.certificates_list', year=cert.edition_year))


@admin_bp.route('/certificados/<int:id>/remover-pdf', methods=['POST'])
@login_required
@admin_required
def certificate_remove_pdf(id):
    """Apaga o PDF e revoga a liberacao (o codigo permanece)."""
    cert = Certificate.query.get_or_404(id)

    cert.pdf_data = None
    cert.pdf_path = None
    cert.released = False
    cert.digital_signature = None
    cert.signed_at = None
    db.session.commit()

    student_name = cert.display_name
    _log_audit('remove_certificate_pdf', 'certificate', cert.id, student_name,
               details=f'{cert.type_label} {cert.edition_year}')
    flash(f'PDF de {student_name} ({cert.type_label}) removido.', 'info')
    return redirect(url_for('admin.certificates_list', year=cert.edition_year))


@admin_bp.route('/certificados/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def certificate_delete(id):
    """Exclui um certificado (linha — o PDF mora na mesma linha)."""
    cert = Certificate.query.get_or_404(id)

    student_name = cert.display_name
    details = f'{cert.type_label} {cert.edition_year} [{cert.verification_code}]'
    db.session.delete(cert)
    db.session.commit()

    _log_audit('delete_certificate', 'certificate', id, student_name, details=details)
    flash(f'Certificado de {student_name} ({details}) excluido.', 'info')
    return redirect(url_for('admin.certificates_list'))


# ════════════════════════════════════════════════════════════════════
#  CERTIFICADOS — pessoas externas / organizadores (sem aluno vinculado)
# ════════════════════════════════════════════════════════════════════

def _form_person_data():
    """Le os campos de pessoa do form e devolve um dict normalizado."""
    return {
        'name': (request.form.get('name') or '').strip(),
        'email': (request.form.get('email') or '').strip() or None,
        'committee': (request.form.get('committee') or '').strip() or None,
        'committee_name': (request.form.get('committee_name') or '').strip() or None,
        'country': (request.form.get('country') or '').strip() or None,
        'country_flag': (request.form.get('country_flag') or '').strip() or None,
        'notes': (request.form.get('notes') or '').strip() or None,
    }


def _apply_person_to_form_data(data, person):
    """Se uma pessoa cadastrada foi escolhida, os dados dela vencem."""
    if not person:
        return data
    data['name'] = person.name
    data['email'] = person.email
    data['committee'] = person.committee
    data['committee_name'] = person.committee_name
    data['country'] = person.country
    data['country_flag'] = person.country_flag
    if person.notes and not data.get('notes'):
        data['notes'] = person.notes
    return data


def _save_person_from_form(data, kind, person_id=None):
    """Cria/atualiza uma CertificatePerson. Devolve a pessoa ou None."""
    person = db.session.get(CertificatePerson, person_id) if person_id else None
    if person is None and not data.get('name'):
        return None
    if person is None:
        person = CertificatePerson(kind=kind)
        db.session.add(person)
    person.kind = kind if kind in PERSON_KINDS else 'external'
    person.name = data['name']
    person.email = data['email']
    person.committee = data['committee']
    person.committee_name = data['committee_name']
    person.country = data['country']
    person.country_flag = data['country_flag']
    person.notes = data['notes']
    # Garante o id antes do certificado referenciar a pessoa (person_id).
    db.session.flush()
    return person


def _create_external_certificate(data, cert_type, year, person=None, notes=None):
    """Cria o Certificate (ainda NAO liberado) para externo/organizador."""
    used = _used_codes()
    cert = Certificate(
        student_id=None,
        person_id=person.id if person else None,
        edition_year=year,
        type=cert_type,
        name=data['name'],
        email=data['email'],
        awarded_by=current_user.id if current_user.is_authenticated else None,
        verification_code=_pick_code(used),
        notes=notes or data.get('notes'),
    )
    cert.fill_snapshot(
        name=data['name'], country=data['country'],
        country_flag=data['country_flag'], committee=data['committee'],
        committee_name=data['committee_name'],
    )
    db.session.add(cert)
    return cert


@admin_bp.route('/certificados/gerar-externo', methods=['POST'])
@login_required
@admin_required
def certificate_generate_external():
    """Gera certificado para pessoa externa (sem cadastro de aluno)."""
    year = request.form.get('year', type=int) or _current_year()
    cert_type = request.form.get('type', 'external')
    person_id = request.form.get('person_id', type=int)

    if cert_type not in CERT_TYPES or cert_type == 'participation':
        flash('Tipo de certificado invalido para emissao externa.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    person = db.session.get(CertificatePerson, person_id) if person_id else None
    data = _apply_person_to_form_data(_form_person_data(), person)
    if not data['name']:
        flash('Informe o nome da pessoa (ou cadastre em Pessoas).', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    # "Salvar em Pessoas": reaproveita a ficha no proximo certificado.
    if request.form.get('save_person') and not person:
        person = _save_person_from_form(data, cert_type)

    cert = _create_external_certificate(data, cert_type, year, person=person)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    _log_audit('generate_external_certificate', 'certificate', cert.id, data['name'],
               details=f'{cert_type} ({year})')
    flash(f'Certificado de "{CERT_TYPES[cert_type]}" criado para {data["name"]}! '
          f'Faca o upload do PDF para liberar.', 'success')
    return redirect(url_for('admin.certificates_list', year=year, type=cert_type))


@admin_bp.route('/certificados/gerar-organizador', methods=['POST'])
@login_required
@admin_required
def certificate_generate_organizer():
    """Gera certificado de Organizador (usuario do sistema ou nome livre)."""
    year = request.form.get('year', type=int) or _current_year()
    person_id = request.form.get('person_id', type=int)
    user_id = request.form.get('user_id', type=int)

    person = db.session.get(CertificatePerson, person_id) if person_id else None
    data = _apply_person_to_form_data(_form_person_data(), person)

    # Usuario do sistema: usa nome/email quando os campos estao vazios.
    if not person and user_id:
        user = db.session.get(User, user_id)
        if not user:
            flash('Usuario selecionado nao encontrado.', 'error')
            return redirect(url_for('admin.certificates_list', year=year))
        data['name'] = data['name'] or user.name
        data['email'] = data['email'] or user.email

    if not data['name']:
        flash('Informe o nome do organizador (ou cadastre em Pessoas).', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    if request.form.get('save_person') and not person:
        person = _save_person_from_form(data, 'organizer')

    cert = _create_external_certificate(data, 'organizer', year, person=person)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    _log_audit('generate_organizer_certificate', 'certificate', cert.id, data['name'],
               details=f'organizador ({year})')
    flash(f'Certificado de Organizador criado para {data["name"]}! '
          f'Faca o upload do PDF para liberar.', 'success')
    return redirect(url_for('admin.certificates_list', year=year, type='organizer'))


# ════════════════════════════════════════════════════════════════════
#  PESSOAS — cadastro de externos (Portas Abertas) e organizadores
# ════════════════════════════════════════════════════════════════════

@admin_bp.route('/certificados/pessoas')
@login_required
@admin_required
def certificate_people_list():
    """Lista/gerencia as pessoas sem cadastro de aluno."""
    kind = request.args.get('kind', '')
    query = CertificatePerson.query
    if kind in PERSON_KINDS:
        query = query.filter_by(kind=kind)
    people = query.order_by(CertificatePerson.name).all()

    counts = dict(
        db.session.query(Certificate.person_id, func.count(Certificate.id))
        .filter(Certificate.person_id.isnot(None))
        .group_by(Certificate.person_id).all()
    )

    return render_template('admin/certificate_people.html',
                           people=people,
                           current_kind=kind,
                           person_kinds=PERSON_KINDS,
                           cert_types=CERT_TYPES,
                           counts=counts,
                           current_year=_current_year())


@admin_bp.route('/certificados/pessoas/nova', methods=['POST'])
@login_required
@admin_required
def certificate_person_create():
    data = _form_person_data()
    kind = request.form.get('kind', 'external')
    if kind not in PERSON_KINDS:
        flash('Tipo de pessoa invalido.', 'error')
        return redirect(url_for('admin.certificate_people_list'))
    if not data['name']:
        flash('Informe o nome da pessoa.', 'error')
        return redirect(url_for('admin.certificate_people_list'))
    person = _save_person_from_form(data, kind)
    db.session.commit()
    _log_audit('create_certificate_person', 'certificate_person', person.id,
               person.name, details=kind)
    flash(f'Pessoa "{person.name}" cadastrada.', 'success')
    return redirect(url_for('admin.certificate_people_list'))


@admin_bp.route('/certificados/pessoas/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def certificate_person_edit(id):
    person = CertificatePerson.query.get_or_404(id)
    data = _form_person_data()
    kind = request.form.get('kind', person.kind)
    if kind not in PERSON_KINDS:
        kind = person.kind
    if not data['name']:
        flash('Informe o nome da pessoa.', 'error')
        return redirect(url_for('admin.certificate_people_list'))
    _save_person_from_form(data, kind, person_id=person.id)
    db.session.commit()
    _log_audit('edit_certificate_person', 'certificate_person', person.id,
               person.name, details=kind)
    flash(f'Pessoa "{person.name}" atualizada.', 'success')
    return redirect(url_for('admin.certificate_people_list'))


@admin_bp.route('/certificados/pessoas/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def certificate_person_delete(id):
    person = CertificatePerson.query.get_or_404(id)
    name = person.name
    # Desvincula certificados existentes (mantem o historico/PDF).
    Certificate.query.filter_by(person_id=person.id).update({'person_id': None})
    db.session.delete(person)
    db.session.commit()
    _log_audit('delete_certificate_person', 'certificate_person', id, name)
    flash(f'Pessoa "{name}" removida (certificados mantidos).', 'info')
    return redirect(url_for('admin.certificate_people_list'))


@admin_bp.route('/certificados/pessoas/<int:id>/gerar', methods=['POST'])
@login_required
@admin_required
def certificate_person_generate(id):
    """Gera certificado a partir de uma pessoa cadastrada."""
    person = CertificatePerson.query.get_or_404(id)
    year = request.form.get('year', type=int) or _current_year()
    cert_type = request.form.get('type') or (
        'organizer' if person.kind == 'organizer' else 'external')
    if cert_type not in CERT_TYPES or cert_type == 'participation':
        flash('Tipo invalido.', 'error')
        return redirect(url_for('admin.certificate_people_list'))

    existing = Certificate.query.filter_by(
        person_id=person.id, edition_year=year, type=cert_type).first()
    if existing:
        flash(f'{person.name} ja tem "{CERT_TYPES[cert_type]}" em {year} '
              f'({existing.verification_code}).', 'error')
        return redirect(url_for('admin.certificate_people_list'))

    data = {
        'name': person.name, 'email': person.email,
        'committee': person.committee, 'committee_name': person.committee_name,
        'country': person.country, 'country_flag': person.country_flag,
        'notes': person.notes,
    }
    cert = _create_external_certificate(data, cert_type, year, person=person)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificate_people_list'))

    _log_audit('generate_person_certificate', 'certificate', cert.id, person.name,
               details=f'{cert_type} ({year})')
    flash(f'Certificado de "{CERT_TYPES[cert_type]}" criado para {person.name}! '
          f'Faca o upload do PDF.', 'success')
    return redirect(url_for('admin.certificates_list', year=year, type=cert_type))


# ════════════════════════════════════════════════════════════════════
#  CERTIFICADOS — PDF personalizado com os codigos de verificacao
# ════════════════════════════════════════════════════════════════════

def _pdf_escape(text):
    """Escapa texto para insercao em string de conteudo PDF."""
    if text is None:
        return ''
    return str(text).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


# Paleta do portal
NAVY = '0.051 0.106 0.165'    # #0D1B2A
GOLD = '0.788 0.659 0.298'    # #C9A84C
INK = '0.10 0.10 0.10'
MUTED = '0.42 0.42 0.42'
WHITE = '0.97 0.97 0.97'
ZEBRA = '0.955 0.955 0.955'

# x, largura de cada coluna da tabela (pagina A4 612pt, margens 40)
COLS = [
    ('Código', 40, 64),
    ('Nome', 106, 158),
    ('Tipo', 266, 78),
    ('Edição', 346, 34),
    ('Tema / Comitê', 382, 140),
    ('Status', 524, 48),
]

# Rotulos curtos para caber na coluna Tipo (o rotulo oficial e longo demais)
PDF_TYPE_LABELS = {
    'participation':   'Participação',
    'best_delegation': 'Melhor Delegação',
    'best_speaker':    'Melhor Orador(a)',
    'best_dress':      'Melhor Vestimenta',
    'organizer':       'Organizador',
    'external':        'Portas Abertas',
}


def _pdf_fit(text, width, font_size=8.0):
    """Trunca o texto para caber na largura (aprox. Helvetica) com '...'."""
    text = '' if text is None else str(text)
    if not text:
        return ''
    max_chars = max(1, int(width / (font_size * 0.52)))
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[:max_chars - 3] + '...'


def _pdf_fit_size(text, width, preferred=8.0, minimum=6.6):
    """Cabe o texto reduzindo a fonte antes de cortar. Devolve (texto, tamanho)."""
    text = '' if text is None else str(text)
    if not text:
        return '', preferred
    size = preferred
    while size > minimum and len(text) * size * 0.52 > width:
        size = round(size - 0.2, 1)
    if len(text) * size * 0.52 > width:
        text = _pdf_fit(text, width, size)
    return text, size


def _op_text(ops, text, x, y, size=8.0, color=INK, font='F1'):
    ops.append('BT')
    ops.append(f'/{font} {size} Tf')
    ops.append(f'{color} rg')
    ops.append(f'{x} {y} Td')
    ops.append(f'({_pdf_escape(text)}) Tj')
    ops.append('ET')


def _op_rect(ops, x, y, w, h, color):
    ops.append(f'{color} rg')
    ops.append(f'{x} {y} {w} {h} re f')


def _op_line(ops, x1, y1, x2, y2, color=GOLD, width=0.6):
    ops.append(f'{color} RG')
    ops.append(f'{width} w')
    ops.append(f'{x1} {y1} m')
    ops.append(f'{x2} {y2} l')
    ops.append('S')


def _summary_lines(certs):
    """Linhas de resumo por tipo e por tema para o topo da primeira pagina."""
    from collections import Counter
    by_type = Counter(c.type for c in certs)
    by_theme = Counter((c.committee_name or c.committee or 'Sem tema') for c in certs)

    parts = [f'{CERT_TYPES.get(k, k)}: {v}' for k, v in sorted(by_type.items())]
    line1 = 'Resumo por tipo: ' + ('  |  '.join(parts) if parts else 'nenhum certificado')

    themes = sorted(by_theme.items(), key=lambda kv: (-kv[1], kv[0]))
    theme_txt = ', '.join(f'{t} ({n})' for t, n in themes)
    line2 = 'Por tema: ' + (theme_txt if theme_txt else 'sem tema')
    return [line1, line2]


def _draw_page_header(ops, year, filters_desc, summary, first_page):
    """Logo SWDL + titulo + filtros/resumo (so na 1a pagina)."""
    _op_rect(ops, 40, 744, 150, 32, NAVY)
    _op_text(ops, 'SWDL', 52, 756, 17, GOLD, 'F2')
    _op_text(ops, 'SESI WORLD DIPLOMACY LEAGUE', 52, 746, 6.5, GOLD, 'F1')
    _op_line(ops, 40, 736, 572, 736, GOLD, 1.5)
    _op_text(ops, f'Códigos de Verificação de Certificados · Edição {year}',
             40, 721, 12, NAVY, 'F2')

    y = 708
    if first_page and filters_desc:
        _op_text(ops, f'Filtros: {filters_desc}', 40, y, 7.5, MUTED)
        y -= 12
    if first_page and summary:
        for line in summary:
            _op_text(ops, _pdf_fit(line, 532, 7.5), 40, y, 7.5, '0.25 0.25 0.25')
            y -= 11
    return y - 6


def _draw_table_header(ops, y):
    _op_rect(ops, 40, y - 4, 532, 15, NAVY)
    for label, x, w in COLS:
        _op_text(ops, _pdf_fit(label, w - 6, 7.5), x + 3, y, 7.5, WHITE, 'F2')
    return y - 19


def _draw_row(ops, cert, y, zebra):
    if zebra:
        _op_rect(ops, 40, y - 4, 532, 13, ZEBRA)
    theme = cert.committee_name or cert.committee or ''
    if cert.committee_name and cert.committee:
        theme = f'{cert.committee_name} ({cert.committee})'
    values = [
        cert.verification_code,
        cert.display_name or '',
        PDF_TYPE_LABELS.get(cert.type, cert.type_label),
        str(cert.edition_year),
        theme,
        'Liberado' if cert.released else 'Pendente',
    ]
    for i, ((label, x, w), val) in enumerate(zip(COLS, values)):
        if i in (1, 4):
            # Nome e tema: reduz a fonte antes de cortar (nome completo importa)
            txt, size = _pdf_fit_size(val, w - 6, 8.0, 6.6)
            _op_text(ops, txt, x + 3, y, size, INK)
        else:
            _op_text(ops, _pdf_fit(val, w - 6, 8.0), x + 3, y, 8.0, INK)
    return y - 13


def _draw_footer(ops, page_num, total_pages, now_str):
    _op_line(ops, 40, 46, 572, 46, GOLD, 0.6)
    _op_text(ops, f'Página {page_num} de {total_pages}', 40, 34, 7, MUTED)
    _op_text(ops, now_str, 430, 34, 7, MUTED)
    _op_text(ops,
             'Validação pública: /certificado/<codigo>  |  '
             '/api/certificado/validar?code=<codigo>',
             40, 24, 6.8, MUTED)


def _build_codes_pdf(certs, year, filters_desc):
    """Gera um PDF valido (apenas stdlib) com cabecalho, rodape, logo e tabela.

    Colunas em posicao fixa (nome nunca estoura a margem), linhas zebradas,
    cabecalho de tabela repetido em cada pagina e resumo por tipo/tema.
    """
    from datetime import datetime as _dt

    PAGE_W, PAGE_H = 612, 792
    now_str = _dt.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')
    summary = _summary_lines(certs)

    # ── Paginacao dinamica ──────────────────────────────────────────
    pages_ops = []
    if not certs:
        ops = []
        y = _draw_page_header(ops, year, filters_desc, summary, True)
        y = _draw_table_header(ops, y)
        _op_text(ops, 'Nenhum certificado encontrado para este filtro.',
                 40, y - 6, 9, MUTED)
        pages_ops.append(ops)
    else:
        idx = 0
        page_num = 1
        while idx < len(certs):
            ops = []
            y = _draw_page_header(ops, year, filters_desc, summary, page_num == 1)
            y = _draw_table_header(ops, y)
            row_i = 0
            while idx < len(certs) and y >= 64:
                y = _draw_row(ops, certs[idx], y, row_i % 2 == 1)
                idx += 1
                row_i += 1
            if row_i == 0:  # seguranca contra loop infinito
                idx += 1
            pages_ops.append(ops)
            page_num += 1

    total_pages = len(pages_ops)
    for i, ops in enumerate(pages_ops, start=1):
        _draw_footer(ops, i, total_pages, now_str)

    streams = ['\n'.join(ops).encode('latin-1', 'replace') for ops in pages_ops]

    # ── Objetos PDF ─────────────────────────────────────────────────
    objs = []

    def obj(content):
        objs.append(content)
        return len(objs)

    contents = [
        obj(f'<< /Length {len(s)} >>\nstream\n{s.decode("latin-1", "replace")}\nendstream\nendobj')
        for s in streams
    ]
    font1 = obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica '
                '/Encoding /WinAnsiEncoding >>')
    font2 = obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold '
                '/Encoding /WinAnsiEncoding >>')

    page_objs = []
    for c in contents:
        page_objs.append(obj(
            f'<< /Type /Page /Parent 0 0 R /Resources << /Font << /F1 {font1} 0 R '
            f'/F2 {font2} 0 R >> >> /MediaBox [0 0 {PAGE_W} {PAGE_H}] '
            f'/Contents {c} 0 R >>'
        ))

    pages_obj = obj(
        f'<< /Type /Pages /Kids [{" ".join(str(n) + " 0 R" for n in page_objs)}] '
        f'/Count {len(page_objs)} >>'
    )
    for p in page_objs:
        for j, content in enumerate(objs):
            if j + 1 == p:
                objs[j] = content.replace('/Parent 0 0 R', f'/Parent {pages_obj} 0 R')
                break

    catalog = obj(f'<< /Type /Catalog /Pages {pages_obj} 0 R >>')

    # ── Serializa ───────────────────────────────────────────────────
    buf = io.BytesIO()
    buf.write(b'%PDF-1.4\n')
    xref = []
    for i, content in enumerate(objs, start=1):
        xref.append(buf.tell())
        buf.write(f'{i} 0 obj\n{content}\nendobj\n'.encode('latin-1'))
    xref_start = buf.tell()
    count = len(objs) + 1
    buf.write(b'xref\n')
    buf.write(f'0 {count}\n'.encode('ascii'))
    buf.write(b'0000000000 65535 f \n')
    for pos in xref:
        buf.write(f'{pos:010d} 00000 n \n'.encode('ascii'))
    buf.write(b'trailer\n')
    buf.write(f'<< /Size {count} /Root {catalog} 0 R >>\n'.encode('ascii'))
    buf.write(b'startxref\n')
    buf.write(f'{xref_start}\n'.encode('ascii'))
    buf.write(b'%%EOF\n')
    return buf.getvalue()


@admin_bp.route('/certificados/codigos-pdf')
@login_required
@admin_required
def certificates_codes_pdf():
    """Gera um PDF personalizado com a lista de codigos de verificacao.

    Query params: year, type, committee_name (mesmos da listagem).
    """
    year = request.args.get('year', type=int) or _current_year()
    cert_type = request.args.get('type', '')
    committee_name = request.args.get('committee_name', '')

    query = Certificate.query.filter(Certificate.edition_year == year)
    if cert_type and cert_type in CERT_TYPES:
        query = query.filter(Certificate.type == cert_type)
    if committee_name:
        query = query.filter(Certificate.committee_name == committee_name)

    certs = query.order_by(
        Certificate.type,
        func.coalesce(Certificate.student_name, Certificate.name, '').asc()
    ).all()

    filters_parts = []
    if cert_type:
        filters_parts.append(f'tipo={CERT_TYPES[cert_type]}')
    if committee_name:
        filters_parts.append(f'tema={committee_name}')
    filters_desc = ' | '.join(filters_parts) if filters_parts else 'todos'

    pdf_bytes = _build_codes_pdf(certs, year, filters_desc)

    _log_audit('download_codes_pdf', 'system', 0,
               details=f'{len(certs)} codigos — edicao {year} {filters_desc}')

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="codigos_certificados_swdl_{year}.pdf"'
    return response
