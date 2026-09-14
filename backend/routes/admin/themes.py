"""SWDL Admin — Themes (Temas/Debates) routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required
from models.theme import Theme
from extensions import db
import os, uuid as _uuid


@admin_bp.route('/temas')
@login_required
@admin_required
def themes_list():
    themes = Theme.query.order_by(Theme.name).all()
    return render_template('admin/themes_list.html', themes=themes)


@admin_bp.route('/temas/novo', methods=['POST'])
@login_required
@admin_required
def theme_create():
    from config import Config
    name = request.form.get('name', '').strip()
    if not name:
        flash('O nome do tema não pode estar vazio.', 'error')
        return redirect(url_for('admin.themes_list'))
    if Theme.query.filter_by(name=name).first():
        flash('Já existe um tema com este nome.', 'error')
        return redirect(url_for('admin.themes_list'))
    image = ''
    file = request.files.get('image')
    if file and file.filename:
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'themes')
        os.makedirs(upload_dir, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'png'
        safe_name = f'theme_{_uuid.uuid4().hex[:12]}.{ext}'
        filepath = os.path.join(upload_dir, safe_name)
        file.save(filepath)
        image = url_for('admin.serve_upload', filename=f'themes/{safe_name}', _external=False)
    theme = Theme(name=name, image=image)
    db.session.add(theme)
    db.session.commit()
    flash(f'Tema "{name}" criado com sucesso!', 'success')
    return redirect(url_for('admin.themes_list'))


@admin_bp.route('/temas/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def theme_edit(id):
    from config import Config
    theme = Theme.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    if not name:
        flash('O nome é obrigatório.', 'error')
        return redirect(url_for('admin.themes_list'))
    existing = Theme.query.filter(Theme.name == name, Theme.id != id).first()
    if existing:
        flash('Já existe outro tema com este nome.', 'error')
        return redirect(url_for('admin.themes_list'))
    theme.name = name
    file = request.files.get('image')
    if file and file.filename:
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'themes')
        os.makedirs(upload_dir, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'png'
        safe_name = f'theme_{_uuid.uuid4().hex[:12]}.{ext}'
        filepath = os.path.join(upload_dir, safe_name)
        file.save(filepath)
        theme.image = url_for('admin.serve_upload', filename=f'themes/{safe_name}', _external=False)
    db.session.commit()
    flash(f'Tema "{name}" atualizado!', 'success')
    return redirect(url_for('admin.themes_list'))


@admin_bp.route('/temas/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def theme_delete(id):
    theme = Theme.query.get_or_404(id)
    if theme.delegations:
        flash(f'Não é possível deletar: {len(theme.delegations)} delegação(ões) usa(m) este tema.', 'error')
        return redirect(url_for('admin.themes_list'))
    db.session.delete(theme)
    db.session.commit()
    flash('Tema deletado.', 'info')
    return redirect(url_for('admin.themes_list'))
