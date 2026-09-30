from flask import render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required, _log_audit
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
    students = Student.query.options(joinedload(Student.delegation)).order_by(Student.name).all()

    for s in students:
        deleg = s.delegation
        s._eligible = deleg and deleg.presence_status in ('presente', 'votante')

    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()

    return render_template('admin/certificates_list.html',
                           students=students,
                           total=len(students),
                           has_code=sum(1 for s in students if s.verification_code),
                           with_pdf=sum(1 for s in students if s.certificate_url),
                           eligible=sum(1 for s in students if s._eligible),
                           audit_logs=audit_logs)


@admin_bp.route('/certificados/gerar-codigos', methods=['POST'])
@login_required
@admin_required
def certificates_generate_codes():
    """Gera codigo de verificacao para elegiveis sem codigo.

    Com ``student_id`` no form, gera apenas para esse aluno.
    """
    student_id = request.form.get('student_id', type=int)
    query = Student.query.filter(Student.verification_code.is_(None))
    if student_id:
        query = query.filter(Student.id == student_id)
    students = query.all()
    count = 0
    for s in students:
        deleg = s.delegation
        if deleg and deleg.presence_status in ('presente', 'votante'):
            s.verification_code = generate_verification_code()
            count += 1
    db.session.commit()
    if student_id:
        _log_audit('generate_codes', 'student', student_id, details=f'{count} codigo gerado')
    else:
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
    student.certificate_released = True
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
    student.certificate_released = False
    db.session.commit()
    _log_audit('remove_certificate_pdf', 'student', student.id, student.name)
    flash(f'PDF de {student.name} removido.', 'info')
    return redirect(url_for('admin.certificates_list'))
