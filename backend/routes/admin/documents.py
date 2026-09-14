from flask import render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required
from models.document import Document
from models.theme import Theme
from extensions import db
import os
from datetime import datetime, timezone


@admin_bp.route('/documentos')
@login_required
@admin_required
def documentos_list():
    """Lista todos os documentos enviados."""
    documentos = Document.query.order_by(Document.created_at.desc()).all()
    themes = Theme.query.order_by(Theme.name).all()
    return render_template('admin/documentos_list.html', documentos=documentos, available_themes=themes)


@admin_bp.route('/documentos/enviar', methods=['POST'])
@login_required
@admin_required
def documento_enviar():
    """Faz upload de um novo documento."""
    title = request.form.get('title', '').strip()
    if not title:
        flash('O título é obrigatório.', 'error')
        return redirect(url_for('admin.documentos_list'))

    description = request.form.get('description', '').strip()
    theme_id = request.form.get('theme_id', '').strip()
    theme_id = int(theme_id) if theme_id else None
    category = request.form.get('category', 'guias').strip()

    file = request.files.get('file')
    if not file or not file.filename:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('admin.documentos_list'))

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ('pdf', 'doc', 'docx'):
        flash('Formato permitido: PDF, DOC, DOCX.', 'error')
        return redirect(url_for('admin.documentos_list'))

    from config import Config
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'documentos')
    os.makedirs(upload_dir, exist_ok=True)

    safe_name = f'doc_{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}_{file.filename}'
    filepath = os.path.join(upload_dir, safe_name)
    file.save(filepath)

    doc = Document(
        title=title,
        description=description,
        file_path=filepath,
        category=category,
        theme_id=theme_id,
    )
    db.session.add(doc)
    db.session.commit()
    flash(f'Documento "{title}" enviado com sucesso!', 'success')
    return redirect(url_for('admin.documentos_list'))


@admin_bp.route('/documentos/<int:id>/download')
@login_required
@admin_required
def documento_download(id):
    """Download de um documento."""
    doc = Document.query.get_or_404(id)
    if not os.path.isfile(doc.file_path):
        flash('Arquivo não encontrado no servidor.', 'error')
        return redirect(url_for('admin.documentos_list'))
    return send_file(
        doc.file_path,
        as_attachment=True,
        download_name=doc.filename(),
    )


@admin_bp.route('/documentos/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def documento_deletar(id):
    """Deleta um documento."""
    doc = Document.query.get_or_404(id)
    if os.path.isfile(doc.file_path):
        os.remove(doc.file_path)
    db.session.delete(doc)
    db.session.commit()
    flash('Documento deletado.', 'info')
    return redirect(url_for('admin.documentos_list'))
