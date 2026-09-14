from flask import render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required, _sign_certificate, _log_audit
from models.student import Student, generate_verification_code
from models.delegation import Delegation
from extensions import db
from config import Config
import os
from datetime import datetime, timezone


@admin_bp.route('/certificados/arquivo/<filename>')
@login_required
def serve_certificate(filename):
    """Serve o arquivo PDF do certificado."""
    cert_dir = os.path.join(Config.UPLOAD_FOLDER, 'certificates')
    filepath = os.path.realpath(os.path.join(cert_dir, filename))
    if not filepath.startswith(os.path.realpath(cert_dir)):
        from flask import abort
        abort(403)
    if not os.path.isfile(filepath):
        from flask import abort
        abort(404)
    return send_file(filepath, mimetype='application/pdf')


@admin_bp.route('/certificados')
@login_required
@admin_required
def certificates_list():
    """Pagina de gestao de certificados."""
    from sqlalchemy.orm import joinedload
    from models.audit_log import AuditLog
    from routes.agenda_utils import get_agenda_status
    students = Student.query.options(joinedload(Student.delegation)).order_by(Student.name).all()

    for s in students:
        deleg = s.delegation
        s._eligible = deleg and deleg.presence_status in ('presente', 'votante')

    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()

    return render_template('admin/certificates_list.html',
                           students=students,
                           total=len(students),
                           released=sum(1 for s in students if s.certificate_released),
                           has_code=sum(1 for s in students if s.verification_code),
                           eligible=sum(1 for s in students if s._eligible),
                           event_phase=get_agenda_status()[0] or 'pre',
                           audit_logs=audit_logs)


@admin_bp.route('/certificados/gerar-codigos', methods=['POST'])
@login_required
@admin_required
def certificates_generate_codes():
    """Gera codigo de verificacao para todos os elegiveis sem codigo."""
    students = Student.query.filter(Student.verification_code.is_(None)).all()
    count = 0
    for s in students:
        deleg = s.delegation
        if deleg and deleg.presence_status in ('presente', 'votante'):
            s.verification_code = generate_verification_code()
            count += 1
    db.session.commit()
    _log_audit('generate_codes', 'system', 0, details=f'{count} codigos gerados')
    flash(f'{count} codigos de verificacao gerados!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/<int:id>/upload', methods=['POST'])
@login_required
@admin_required
def certificate_upload(id):
    """Upload do PDF personalizado de um aluno."""
    student = Student.query.get_or_404(id)

    if not student.verification_code:
        student.verification_code = generate_verification_code()
        db.session.flush()

    if 'cert_file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.certificates_list'))

    file = request.files['cert_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.certificates_list'))

    if not file.filename.lower().endswith('.pdf'):
        flash('Apenas arquivos PDF sao permitidos.', 'error')
        return redirect(url_for('admin.certificates_list'))

    cert_dir = os.path.join(Config.UPLOAD_FOLDER, 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    safe_name = f'{student.verification_code}.pdf'
    filepath = os.path.join(cert_dir, safe_name)
    file.save(filepath)

    student.certificate_url = url_for('admin.serve_certificate', filename=safe_name, _external=True)
    db.session.commit()
    _log_audit('upload_certificate', 'student', student.id, student.name,
               details=f'PDF enviado: {safe_name}')
    flash(f'PDF de {student.name} enviado com sucesso!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/<int:id>/remover-pdf', methods=['POST'])
@login_required
@admin_required
def certificate_remove_pdf(id):
    """Remove o PDF uploadado de um aluno."""
    student = Student.query.get_or_404(id)

    if student.verification_code:
        cert_dir = os.path.join(Config.UPLOAD_FOLDER, 'certificates')
        filepath = os.path.join(cert_dir, f'{student.verification_code}.pdf')
        if os.path.isfile(filepath):
            try: os.remove(filepath)
            except OSError: pass

    student.certificate_url = None
    db.session.commit()
    _log_audit('remove_certificate_pdf', 'student', student.id, student.name)
    flash(f'PDF de {student.name} removido.', 'info')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/<int:id>/liberar', methods=['POST'])
@login_required
@admin_required
def certificate_release(id):
    """Libera o certificado de um aluno especifico."""
    student = Student.query.get_or_404(id)
    if not student.verification_code:
        student.verification_code = generate_verification_code()
    student.certificate_released = True
    db.session.commit()
    _log_audit('release_certificate', 'student', student.id, student.name)
    flash(f'Certificado liberado para {student.name}!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/liberar-todos', methods=['POST'])
@login_required
@admin_required
def certificates_release_all():
    """Libera certificados de todos os alunos com codigo gerado."""
    students = Student.query.filter(
        Student.verification_code.isnot(None),
        Student.verification_code != '',
        Student.certificate_released == False
    ).all()
    for s in students:
        s.certificate_released = True
    db.session.commit()
    _log_audit('release_all_certificates', 'system', 0, details=f'{len(students)} certificados liberados em lote')
    flash(f'{len(students)} certificados liberados em lote!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/reverter/<int:id>', methods=['POST'])
@login_required
@admin_required
def certificate_revoke(id):
    """Reverte a liberacao de um certificado."""
    student = Student.query.get_or_404(id)
    student.certificate_released = False
    db.session.commit()
    _log_audit('revoke_certificate', 'student', student.id, student.name)
    flash(f'Certificado de {student.name} revertido.', 'info')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/<int:id>/assinar', methods=['POST'])
@login_required
@admin_required
def certificate_sign(id):
    """Assina digitalmente (HMAC) o certificado de um aluno."""
    student = Student.query.get_or_404(id)
    if not student.verification_code:
        student.verification_code = generate_verification_code()
        db.session.commit()
    sig = _sign_certificate(student)
    if sig:
        _log_audit('sign_certificate', 'student', student.id, student.name)
        flash(f'Certificado de {student.name} assinado digitalmente!', 'success')
    else:
        flash('Nao foi possivel assinar.', 'error')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/assinar-todos', methods=['POST'])
@login_required
@admin_required
def certificates_sign_all():
    """Assina digitalmente todos os certificados com codigo."""
    students = Student.query.filter(
        Student.verification_code.isnot(None),
        Student.verification_code != '',
    ).all()
    count = 0
    for s in students:
        sig = _sign_certificate(s)
        if sig:
            count += 1
    _log_audit('sign_all_certificates', 'system', 0, details=f'{count} certificados assinados')
    flash(f'{count} certificados assinados digitalmente!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/<int:id>/remover-assinatura', methods=['POST'])
@login_required
@admin_required
def certificate_unsign(id):
    """Remove a assinatura digital de um certificado."""
    student = Student.query.get_or_404(id)
    student.digital_signature = None
    student.signed_at = None
    db.session.commit()
    _log_audit('unsign_certificate', 'student', student.id, student.name)
    flash(f'Assinatura removida de {student.name}.', 'info')
    return redirect(url_for('admin.certificates_list'))
