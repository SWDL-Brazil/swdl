"""SWDL Admin — News routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required
from models.news import News
from models.category import Category
from models.theme import Theme
from extensions import db
import os, uuid as _uuid


def _form_values(id=None, cover_image=None, slug=None):
    """Snapshot do que veio no POST — re-renderiza o form preservando o que o
    usuário digitou quando o save falha (em vez de estourar 500 e perder tudo)."""
    from types import SimpleNamespace
    f = request.form
    return SimpleNamespace(
        id=id,
        title=f.get('title', ''),
        excerpt=(f.get('excerpt') or '').strip(),
        body=f.get('body', ''),
        category_id=f.get('category_id', type=int),
        committee=f.get('committee') or 'geral',
        tags=f.get('tags', ''),
        is_crisis=bool(f.get('is_crisis')),
        published=f.get('action') == 'publish',
        cover_image=cover_image,
        slug=slug,
    )


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
            excerpt    = (request.form.get('excerpt') or '').strip() or None,
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
            news.cover_image = url_for('api.api_serve_news_upload', filename=safe_name, _external=False)
        cover_url = news.cover_image
        try:
            news.save()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar a notícia: {e}', 'error')
            cats = Category.query.order_by(Category.sort_order, Category.name).all()
            themes = Theme.query.order_by(Theme.name).all()
            return render_template('admin/news_form.html',
                                   news=_form_values(cover_image=cover_url),
                                   categories=cats, available_themes=themes)
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
        news.excerpt    = (request.form.get('excerpt') or '').strip() or None
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
            news.cover_image = url_for('api.api_serve_news_upload', filename=safe_name, _external=False)
        nid, old_slug, cover_url = news.id, news.slug, news.cover_image
        try:
            news.save()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar a notícia: {e}', 'error')
            cats = Category.query.order_by(Category.sort_order, Category.name).all()
            themes = Theme.query.order_by(Theme.name).all()
            return render_template('admin/news_form.html',
                                   news=_form_values(id=nid, cover_image=cover_url, slug=old_slug),
                                   categories=cats, available_themes=themes)
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
