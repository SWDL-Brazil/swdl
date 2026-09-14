"""SWDL Admin — News Categories routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required
from models.category import Category
from models.news import News
from extensions import db


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
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    icon = request.form.get('icon', '').strip()
    if not name:
        flash('O nome da categoria é obrigatório.', 'error')
        return redirect(url_for('admin.categories_list'))
    if not slug:
        slug = name.lower().replace(' ', '-')
    if Category.query.filter_by(slug=slug).first():
        flash('Já existe uma categoria com este slug.', 'error')
        return redirect(url_for('admin.categories_list'))
    cat = Category(name=name, slug=slug, icon=icon)
    db.session.add(cat)
    db.session.commit()
    flash(f'Categoria "{name}" criada!', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/categorias/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def category_edit(id):
    cat = Category.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    icon = request.form.get('icon', '').strip()
    if not name:
        flash('O nome é obrigatório.', 'error')
        return redirect(url_for('admin.categories_list'))
    if not slug:
        slug = name.lower().replace(' ', '-')
    existing = Category.query.filter(Category.slug == slug, Category.id != id).first()
    if existing:
        flash('Outra categoria já usa este slug.', 'error')
        return redirect(url_for('admin.categories_list'))
    cat.name = name
    cat.slug = slug
    cat.icon = icon
    db.session.commit()
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
