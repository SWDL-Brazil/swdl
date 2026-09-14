"""SWDL Admin — News routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required
from models.news import News
from models.category import Category
from models.theme import Theme
from extensions import db
import os, uuid as _uuid


@admin_bp.route('/noticias')
@login_required
@admin_required
def news_list():
    news = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news_list.html', news=news)


@admin_bp.route('/noticias/nova', methods=['GET', 'POST'])
@login_required
@admin_required
def news_create():
    from config import Config
    if request.method == 'POST':
        cat_id = request.form.get('category_id', type=int)
        news = News(
            title      = request.form['title'],
            body       = request.form['body'],
            category_id = cat_id if cat_id else None,
            committee  = request.form.get('committee', 'geral'),
            tags       = request.form.get('tags', ''),
            is_crisis  = bool(request.form.get('is_crisis')),
            published  = request.form.get('action') == 'publish',
            author_id  = current_user.id,
        )
        file = request.files.get('cover_image')
        if file and file.filename:
            upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'news')
            os.makedirs(upload_dir, exist_ok=True)
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
            safe_name = f'news_{_uuid.uuid4().hex[:12]}.{ext}'
            filepath = os.path.join(upload_dir, safe_name)
            file.save(filepath)
            news.cover_image = url_for('admin.serve_upload', filename=f'news/{safe_name}', _external=False)
        news.save()
        flash('Notícia publicada com sucesso!', 'success')
        return redirect(url_for('admin.news_list'))
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    themes = Theme.query.order_by(Theme.name).all()
    return render_template('admin/news_form.html', news=None, categories=cats, available_themes=themes)


@admin_bp.route('/noticias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def news_edit(id):
    from config import Config
    news = News.query.get_or_404(id)
    if request.method == 'POST':
        cat_id = request.form.get('category_id', type=int)
        news.title      = request.form['title']
        news.body       = request.form['body']
        news.category_id = cat_id if cat_id else None
        news.committee  = request.form.get('committee', 'geral')
        news.tags       = request.form.get('tags', '')
        news.is_crisis  = bool(request.form.get('is_crisis'))
        news.published  = request.form.get('action') == 'publish'
        file = request.files.get('cover_image')
        if file and file.filename:
            upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'news')
            os.makedirs(upload_dir, exist_ok=True)
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
            safe_name = f'news_{_uuid.uuid4().hex[:12]}.{ext}'
            filepath = os.path.join(upload_dir, safe_name)
            file.save(filepath)
            news.cover_image = url_for('admin.serve_upload', filename=f'news/{safe_name}', _external=False)
        news.save()
        flash('Notícia atualizada.', 'success')
        return redirect(url_for('admin.news_list'))
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    themes = Theme.query.order_by(Theme.name).all()
    return render_template('admin/news_form.html', news=news, categories=cats, available_themes=themes)


@admin_bp.route('/noticias/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def news_delete(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    flash('Notícia removida.', 'info')
    return redirect(url_for('admin.news_list'))
