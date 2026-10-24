from flask import render_template, redirect, url_for, flash, request, send_file, current_app, abort
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required, _log_audit
from models.student import Student
from models.delegation import Delegation
from models.certificate import Certificate, CERT_TYPES, generate_verification_code
from cert_storage import cert_path, is_pdf, save_cert_pdf, delete_cert_pdf
from extensions import db
from sqlalchemy import select, func, case
from sqlalchemy.exc import IntegrityError
import os
from datetime import datetime, timezone


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


@admin_bp.route('/certificados/arquivo/<filename>')
@login_required
@admin_required
def serve_certificate(filename):
    """Serve o arquivo PDF do certificado (rota admin)."""
    filepath = cert_path(filename)
    if not filepath:
        abort(403)
    if not os.path.isfile(filepath):
        abort(404)
    return send_file(filepath, mimetype='application/pdf')


@admin_bp.route('/certificados')
@login_required
@admin_required
def certificates_list():
    """Gestao de certificados — filtravel por edicao e tipo."""
    from sqlalchemy.orm import joinedload
    from models.audit_log import AuditLog

    year = request.args.get('year', type=int)
    cert_type = request.args.get('type', '')

    years = [r[0] for r in db.session.query(Certificate.edition_year)
             .distinct().order_by(Certificate.edition_year.desc())]
    if not year:
        cy = _current_year()
        year = cy if cy in years else (years[0] if years else cy)

    query = Certificate.query.options(
        joinedload(Certificate.student).joinedload(Student.delegation))
    if year:
        query = query.filter(Certificate.edition_year == year)
    if cert_type and cert_type in CERT_TYPES:
        query = query.filter(Certificate.type == cert_type)

    certs = query.join(Student, Certificate.student_id == Student.id)\
                 .order_by(Certificate.type, Student.name).all()

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
        'with_pdf': sum(1 for c in all_for_year if c.pdf_path),
        'released': sum(1 for c in all_for_year if c.released),
        'edition_students': edition_total,
        'missing_participation': missing,
    }

    students = Student.query.options(joinedload(Student.delegation))\
                            .order_by(Student.name).all()
    delegations = Delegation.query.options(joinedload(Delegation.students))\
                                   .order_by(Delegation.country).all()
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()

    return render_template('admin/certificates_list.html',
                           certs=certs,
                           years=years,
                           current_year=year,
                           current_type=cert_type,
                           cert_types=CERT_TYPES,
                           stats=stats,
                           students=students,
                           delegations=delegations,
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

    query = Student.query
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
        cert = Certificate(student_id=s.id, edition_year=year,
                           type='participation',
                           verification_code=_pick_code(used))
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
        deleg = Delegation.query.get_or_404(delegation_id)
        targets = list(deleg.students)
        if not targets:
            flash('Delegacao sem alunos vinculados.', 'error')
            return redirect(url_for('admin.certificates_list', year=year))
    elif student_id:
        targets = [Student.query.get_or_404(student_id)]
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
        db.session.add(Certificate(
            student_id=s.id, edition_year=year, type=cert_type,
            verification_code=_pick_code(used), notes=notes))
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

    if 'cert_file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.certificates_list', year=cert.edition_year))
    file = request.files['cert_file']
    if not file or not file.filename:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.certificates_list', year=cert.edition_year))
    if not is_pdf(file):
        flash('Apenas arquivos PDF sao permitidos.', 'error')
        return redirect(url_for('admin.certificates_list', year=cert.edition_year))

    safe_name = save_cert_pdf(cert.verification_code, file)

    cert.pdf_path = safe_name
    cert.released = True
    secret = current_app.config.get('SECRET_KEY', 'swdl-secret')
    cert.digital_signature = cert.compute_signature(secret)
    cert.signed_at = datetime.now(timezone.utc)
    db.session.commit()

    student_name = cert.student.name if cert.student else '?'
    _log_audit('upload_certificate', 'certificate', cert.id, student_name,
               details=f'PDF enviado: {safe_name} ({cert.type_label} {cert.edition_year})')
    flash(f'PDF de {student_name} ({cert.type_label}) enviado e liberado!', 'success')
    return redirect(url_for('admin.certificates_list', year=cert.edition_year))


@admin_bp.route('/certificados/<int:id>/remover-pdf', methods=['POST'])
@login_required
@admin_required
def certificate_remove_pdf(id):
    """Remove o PDF e revoga a liberacao (o codigo permanece)."""
    cert = Certificate.query.get_or_404(id)

    if cert.pdf_path:
        delete_cert_pdf(cert.pdf_path)

    cert.pdf_path = None
    cert.released = False
    cert.digital_signature = None
    cert.signed_at = None
    db.session.commit()

    student_name = cert.student.name if cert.student else '?'
    _log_audit('remove_certificate_pdf', 'certificate', cert.id, student_name,
               details=f'{cert.type_label} {cert.edition_year}')
    flash(f'PDF de {student_name} ({cert.type_label}) removido.', 'info')
    return redirect(url_for('admin.certificates_list', year=cert.edition_year))


@admin_bp.route('/certificados/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def certificate_delete(id):
    """Exclui um certificado (linha + PDF — o arquivo sai via evento after_delete)."""
    cert = Certificate.query.get_or_404(id)

    student_name = cert.student.name if cert.student else '?'
    details = f'{cert.type_label} {cert.edition_year} [{cert.verification_code}]'
    db.session.delete(cert)
    db.session.commit()

    _log_audit('delete_certificate', 'certificate', id, student_name, details=details)
    flash(f'Certificado de {student_name} ({details}) excluido.', 'info')
    return redirect(url_for('admin.certificates_list'))
