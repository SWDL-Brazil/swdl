"""SWDL Admin — News Categories routes."""
import re
import unicodedata

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from routes.admin._helpers import admin_bp, admin_required
from models.category import Category
from models.news import News
from extensions import db


def _slugify(text):
    """'Educação Básica' -> 'educacao-basica' (sem acentos, só [a-z0-9-])."""
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return text or 'categoria'


def _validate(name, slug, icon, exclude_id=None):
    """Valida e normaliza. Retorna (slug, None) ou (None, mensagem de erro)."""
    name = name.strip()
    if not name:
        return None, 'O nome da categoria é obrigatório.'
    slug = (slug or '').strip() or _slugify(name)
    q = Category.query
    if exclude_id:
        q = q.filter(Category.id != exclude_id)
    if q.filter(db.func.lower(Category.name) == name.lower()).first():
        return None, f'Já existe uma categoria chamada "{name}".'
    if q.filter(Category.slug == slug).first():
        return None, f'Já existe uma categoria com o slug "{slug}".'
    return (slug, name, icon), None


@admin_bp.route('/categorias')
@login_required
@admin_required
def categories_list():
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    return render_template('admin/categories_list.html', categories=cats)


@admin_bp.route('/categorias/nova', methods=['POST'])
@login_required
@admin_required
def category_create():
    data, err = _validate(request.form.get('name', ''),
                          request.form.get('slug', ''),
                          request.form.get('icon', '').strip())
    if err:
        flash(err, 'error')
        return redirect(url_for('admin.categories_list'))
    slug, name, icon = data
    cat = Category(name=name, slug=slug, icon=icon)
    db.session.add(cat)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Não foi possível criar: já existe uma categoria com esse nome ou slug.', 'error')
        return redirect(url_for('admin.categories_list'))
    flash(f'Categoria "{name}" criada!', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/categorias/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def category_edit(id):
    cat = Category.query.get_or_404(id)
    data, err = _validate(request.form.get('name', ''),
                          request.form.get('slug', ''),
                          request.form.get('icon', '').strip(),
                          exclude_id=id)
    if err:
        flash(err, 'error')
        return redirect(url_for('admin.categories_list'))
    slug, name, icon = data
    cat.name = name
    cat.slug = slug
    cat.icon = icon
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Não foi possível salvar: já existe uma categoria com esse nome ou slug.', 'error')
        return redirect(url_for('admin.categories_list'))
    flash(f'Categoria "{name}" atualizada!', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/categorias/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def category_delete(id):
    cat = Category.query.get_or_404(id)
    News.query.filter_by(category_id=id).update({News.category_id: None})
    db.session.delete(cat)
    db.session.commit()
    flash(f'Categoria "{cat.name}" deletada.', 'info')
    return redirect(url_for('admin.categories_list'))
