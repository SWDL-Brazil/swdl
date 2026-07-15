# =============================================================
#  SWDL — routes/admin.py
# =============================================================
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, jsonify, send_file, current_app)
from flask_login import login_required, current_user
from extensions import db, socketio
from models.news         import News
from models.agenda       import AgendaItem
from models.inscription  import Inscription
from models.delegation   import Delegation
from models.user         import User
from models.student      import Student
from models.document     import Document
from models.event_config import EventConfig
from models.audit_log   import AuditLog
from models.category    import Category
from models.theme      import Theme
from models.urgent_alert import UrgentAlert
from datetime import datetime
import os, uuid as _uuid, hmac, hashlib

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator: só admin (não diretores)."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def moderator_required(f):
    """Decorator: admin ou diretor (mesa)."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.context_processor
def inject_globals():
    from models.theme import Theme
    try:
        themes = Theme.query.order_by(Theme.name).all()
        phase  = EventConfig.get_phase()
        active_invoke = EventConfig.get_invoke()
        return dict(available_themes=themes, event_phase=phase, active_invoke=active_invoke,
                    is_admin=current_user.is_admin() if current_user.is_authenticated else False)
    except Exception:
        db.session.rollback()
        return dict(available_themes=[], event_phase='pre', active_invoke=None)


# ── DASHBOARD HOME ─────────────────────────────────────────────
@admin_bp.route('/')
@login_required
def dashboard():
    # Redireciona diretores para o dashboard deles
    if current_user.is_director():
        return redirect(url_for('admin.director_dashboard'))
    if not current_user.is_admin():
        abort(403)

    from models.vote import VoteSession
    from models.theme import Theme

    stats = {
        'news':           News.query.count(),
        'inscriptions':   Inscription.query.filter_by(status='pending').count(),
        'students':       Student.query.count(),
        'delegations':    Delegation.query.count(),
        'agenda':         AgendaItem.query.count(),
        'participations': 0,
        'certificates':   Student.query.filter(Student.certificate_released == True).count(),
        'themes':         Theme.query.count(),
        'open_votes':     VoteSession.query.filter_by(status='open').count(),
        'presentes':      Delegation.query.filter(Delegation.presence_status.in_(['presente', 'votante'])).count(),
        'ausentes':       Delegation.query.filter_by(presence_status='ausente').count(),
        'oradores':       Delegation.query.filter(Delegation.orador == True).count(),
        'dpos':           Delegation.query.filter(Delegation.dpo_uploaded == True).count(),
        'students_no_deleg': Student.query.filter(Student.delegation_id.is_(None)).count(),
        'convened':       Student.query.filter(Student.convened == True).count(),
        'read_only':      Student.query.filter(Student.read_only == True).count(),
    }
    recent_students      = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_news          = News.query.order_by(News.created_at.desc()).limit(5).all()
    pending_inscriptions = Inscription.query.filter_by(status='pending').order_by(
                           Inscription.submitted_at.desc()).limit(5).all()
    current_agenda       = AgendaItem.query.filter_by(status='now').first()
    event_phase          = EventConfig.get_phase()
    days_agenda          = AgendaItem.query.with_entities(AgendaItem.day).distinct().order_by(AgendaItem.day).all()

    inscricoes_abertas = EventConfig.get_inscricoes_abertas()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_news=recent_news,
                           recent_students=recent_students,
                           pending_inscriptions=pending_inscriptions,
                           current_agenda=current_agenda,
                           event_phase=event_phase,
                           days_agenda=[d[0] for d in days_agenda],
                           inscricoes_abertas=inscricoes_abertas)

# ══════════════════════════════════════════════════════════════
#  TEMAS / DEBATES (Substitui os antigos Comitês)
# ══════════════════════════════════════════════════════════════

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
    name = request.form.get('name', '').strip()
    image = request.form.get('image', '').strip()
    if not name:
        flash('O nome do tema não pode estar vazio.', 'error')
        return redirect(url_for('admin.themes_list'))
    if Theme.query.filter_by(name=name).first():
        flash('Já existe um tema com este nome.', 'error')
        return redirect(url_for('admin.themes_list'))
    theme = Theme(name=name, image=image)
    db.session.add(theme)
    db.session.commit()
    flash(f'Tema "{name}" criado com sucesso!', 'success')
    return redirect(url_for('admin.themes_list'))


@admin_bp.route('/temas/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def theme_edit(id):
    theme = Theme.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    image = request.form.get('image', '').strip()
    if not name:
        flash('O nome é obrigatório.', 'error')
        return redirect(url_for('admin.themes_list'))
    existing = Theme.query.filter(Theme.name == name, Theme.id != id).first()
    if existing:
        flash('Já existe outro tema com este nome.', 'error')
        return redirect(url_for('admin.themes_list'))
    theme.name = name
    theme.image = image
    db.session.commit()
    flash(f'Tema "{name}" atualizado!', 'success')
    return redirect(url_for('admin.themes_list'))


@admin_bp.route('/temas/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def theme_delete(id):
    theme = Theme.query.get_or_404(id)
    db.session.delete(theme)
    db.session.commit()
    flash('Tema deletado.', 'info')
    return redirect(url_for('admin.themes_list'))


# ══════════════════════════════════════════════════════════════
#  CATEGORIAS DE NOTÍCIAS
# ══════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════
#  ALERTAS URGENTES (TICKER)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/alertas')
@login_required
@admin_required
def alerts_list():
    alerts = UrgentAlert.query.order_by(UrgentAlert.created_at.desc()).all()
    return render_template('admin/alerts_list.html', alerts=alerts)


@admin_bp.route('/alertas/criar', methods=['POST'])
@login_required
@admin_required
def alert_create():
    message = request.form.get('message', '').strip()
    if not message:
        flash('A mensagem é obrigatória.', 'error')
        return redirect(url_for('admin.alerts_list'))
    alert = UrgentAlert(message=message, active=True, created_by=current_user.id)
    db.session.add(alert)
    db.session.commit()
    flash('🚨 Alerta urgente ativado!', 'success')
    return redirect(url_for('admin.alerts_list'))


@admin_bp.route('/alertas/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def alert_toggle(id):
    alert = UrgentAlert.query.get_or_404(id)
    alert.active = not alert.active
    db.session.commit()
    flash(f'Alerta {"ativado" if alert.active else "desativado"}.', 'info')
    return redirect(url_for('admin.alerts_list'))


@admin_bp.route('/alertas/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def alert_delete(id):
    alert = UrgentAlert.query.get_or_404(id)
    db.session.delete(alert)
    db.session.commit()
    flash('Alerta removido.', 'info')
    return redirect(url_for('admin.alerts_list'))


# ══════════════════════════════════════════════════════════════
#  NOTÍCIAS
# ══════════════════════════════════════════════════════════════

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
    if request.method == 'POST':
        cat_id = request.form.get('category_id', type=int)
        news = News(
            title      = request.form['title'],
            body       = request.form['body'],
            category_id = cat_id if cat_id else None,
            committee  = request.form.get('committee', 'geral'),
            tags       = request.form.get('tags', ''),
            is_crisis  = bool(request.form.get('is_crisis')),
            published  = bool(request.form.get('published')),
            author_id  = current_user.id,
        )
        db.session.add(news)
        db.session.commit()
        flash('Notícia publicada com sucesso!', 'success')
        return redirect(url_for('admin.news_list'))
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    return render_template('admin/news_form.html', news=None, categories=cats)


@admin_bp.route('/noticias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def news_edit(id):
    news = News.query.get_or_404(id)
    if request.method == 'POST':
        cat_id = request.form.get('category_id', type=int)
        news.title      = request.form['title']
        news.body       = request.form['body']
        news.category_id = cat_id if cat_id else None
        news.committee  = request.form.get('committee', 'geral')
        news.tags       = request.form.get('tags', '')
        news.is_crisis  = bool(request.form.get('is_crisis'))
        news.published  = bool(request.form.get('published'))
        db.session.commit()
        flash('Notícia atualizada.', 'success')
        return redirect(url_for('admin.news_list'))
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    return render_template('admin/news_form.html', news=news, categories=cats)


@admin_bp.route('/noticias/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def news_delete(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    flash('Notícia removida.', 'info')
    return redirect(url_for('admin.news_list'))


# ══════════════════════════════════════════════════════════════
#  AGENDA
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/agenda')
@login_required
@admin_required
def agenda_list():
    days = {}
    for day in [1, 2, 3]:
        days[day] = AgendaItem.query.filter_by(day=day).order_by(
                    AgendaItem.order, AgendaItem.start_time).all()
    return render_template('admin/agenda_list.html', days=days)


@admin_bp.route('/agenda/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def agenda_create():
    if request.method == 'POST':
        item = AgendaItem(
            day         = int(request.form['day']),
            start_time  = request.form['start_time'],
            end_time    = request.form.get('end_time', ''),
            title       = request.form['title'],
            description = request.form.get('description', ''),
            location    = request.form.get('location', ''),
            status      = request.form.get('status', 'next'),
            committee   = request.form.get('committee', ''),
            order       = int(request.form.get('order', 0)),
        )
        db.session.add(item)
        db.session.commit()
        flash('Item de agenda adicionado!', 'success')
        return redirect(url_for('admin.agenda_list'))
    return render_template('admin/agenda_form.html', item=None)


@admin_bp.route('/agenda/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def agenda_edit(id):
    item = AgendaItem.query.get_or_404(id)
    if request.method == 'POST':
        item.day         = int(request.form['day'])
        item.start_time  = request.form['start_time']
        item.end_time    = request.form.get('end_time', '')
        item.title       = request.form['title']
        item.description = request.form.get('description', '')
        item.location    = request.form.get('location', '')
        item.status      = request.form.get('status', 'next')
        item.committee   = request.form.get('committee', '')
        item.order       = int(request.form.get('order', 0))
        db.session.commit()
        flash('Agenda atualizada.', 'success')
        return redirect(url_for('admin.agenda_list'))
    return render_template('admin/agenda_form.html', item=item)


@admin_bp.route('/agenda/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def agenda_delete(id):
    item = AgendaItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item removido.', 'info')
    return redirect(url_for('admin.agenda_list'))


@admin_bp.route('/agenda/<int:id>/status/<string:status>', methods=['POST'])
@login_required
@admin_required
def agenda_set_status(id, status):
    """Muda status de um item rapidamente (ex: marcar como 'now')."""
    allowed = ('now', 'next', 'done', 'break', 'vote', 'crisis', 'open')
    if status not in allowed:
        abort(400)
    # Se marcando como 'now', remove 'now' dos outros
    if status == 'now':
        AgendaItem.query.filter_by(status='now').update({'status': 'done'})
    item = AgendaItem.query.get_or_404(id)
    item.status = status
    db.session.commit()
    flash(f'Status atualizado para "{status}".', 'success')
    return redirect(url_for('admin.agenda_list'))


# ══════════════════════════════════════════════════════════════
#  INSCRIÇÕES
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/inscricoes')
@login_required
@admin_required
def inscriptions_list():
    status_filter = request.args.get('status', 'all')
    q = Inscription.query
    if status_filter != 'all':
        q = q.filter_by(status=status_filter)
    inscriptions = q.order_by(Inscription.submitted_at.desc()).all()
    return render_template('admin/inscriptions_list.html',
                           inscriptions=inscriptions,
                           status_filter=status_filter)


@admin_bp.route('/inscricoes/<int:id>')
@login_required
@admin_required
def inscription_detail(id):
    ins = Inscription.query.get_or_404(id)
    return render_template('admin/inscription_detail.html', ins=ins)


@admin_bp.route('/inscricoes/<int:id>/aprovar', methods=['POST'])
@login_required
@admin_required
def inscription_approve(id):
    ins = Inscription.query.get_or_404(id)
    ins.status      = 'approved'
    ins.reviewed_at = datetime.utcnow()
    ins.reviewed_by = current_user.id

    # Cria conta de usuário + perfil de aluno automaticamente
    from models.user import User
    from models.student import Student
    from models.system_config import SystemConfig
    from services.email_service import send_approval_email
    from services.whatsapp_service import send_approval_whatsapp
    import re

    existing_user = User.query.filter_by(email=ins.email).first()
    if not existing_user:
        first    = re.sub(r'[^a-zA-Z]', '', ins.name.split()[0]).lower()[:4]
        password = f'{first}2025'

        user = User(name=ins.name, email=ins.email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id = user.id,
            name    = ins.name,
            email   = ins.email,
        )
        db.session.add(student)
        db.session.flush()

        # Cria delegação vazia vinculada ao aluno
        if not ins.delegation:
            deleg = Delegation(
                inscription_id=ins.id,
                user_id=user.id,
            )
            db.session.add(deleg)
        else:
            ins.delegation.user_id = user.id

        db.session.commit()

        # ── Envio automático de notificações ─────────────────
        notificacoes = []
        auto_email    = SystemConfig.get('auto_email', '1') == '1'
        auto_whatsapp = SystemConfig.get('auto_whatsapp', '0') == '1'

        if auto_email:
            ok, msg = send_approval_email(
                SystemConfig.get,
                to_email=ins.email,
                student_name=ins.name,
                login_email=ins.email,
                password=password,
            )
            notificacoes.append(f'E-mail: {"✅" if ok else "❌"} {msg}')

        if auto_whatsapp and ins.phone:
            ok, msg = send_approval_whatsapp(
                SystemConfig.get,
                to_phone=ins.phone,
                student_name=ins.name,
                login_email=ins.email,
                password=password,
            )
            notificacoes.append(f'WhatsApp: {"✅" if ok else "❌"} {msg}')

        msg_notificacoes = ' | '.join(notificacoes) if notificacoes else 'Notificações desabilitadas'

        flash(
            f'✅ Inscrição de {ins.name} aprovada! '
            f'Conta criada — Login: {ins.email} | Senha: {password}'
            f'<br><small style="color:var(--muted)">{msg_notificacoes}</small>',
            'success'
        )
    else:
        flash(f'✅ Inscrição de {ins.name} aprovada! (Usuário já existia)', 'success')
        db.session.commit()

    return redirect(url_for('admin.inscriptions_list'))


@admin_bp.route('/inscricoes/<int:id>/rejeitar', methods=['POST'])
@login_required
@admin_required
def inscription_reject(id):
    ins = Inscription.query.get_or_404(id)
    ins.status      = 'rejected'
    ins.reviewed_at = datetime.utcnow()
    ins.reviewed_by = current_user.id
    db.session.commit()
    flash(f'Inscrição de {ins.name} rejeitada.', 'info')
    return redirect(url_for('admin.inscriptions_list'))


# ══════════════════════════════════════════════════════════════
#  DELEGAÇÕES (designar países)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/delegacoes')
@login_required
@admin_required
def delegations_list():
    delegations = Delegation.query.all()
    return render_template('admin/delegations_list.html',
                           delegations=delegations)


@admin_bp.route('/delegacoes/<int:id>/designar', methods=['GET', 'POST'])
@login_required
@admin_required
def delegation_assign(id):
    from models.theme import Theme
    from models.student import Student
    deleg = Delegation.query.get_or_404(id)
    if request.method == 'POST':
        theme_name = request.form['committee']
        theme = Theme.query.filter_by(name=theme_name).first()
        deleg.theme_id    = theme.id if theme else None
        deleg.country      = request.form['country']
        deleg.country_flag = request.form.get('flag', '')
        deleg.committee    = theme_name
        deleg.pair_name    = request.form.get('pair_name', '')
        deleg.flag_animation = bool(request.form.get('flag_animation'))
        student = Student.query.filter_by(delegation_id=deleg.id).first()
        if student and not student.convened:
            student.convened = True
        db.session.commit()
        flash(f'País {deleg.country} designado com sucesso!', 'success')
        return redirect(url_for('admin.delegations_list'))
    available_themes = Theme.query.all()
    return render_template('admin/delegation_assign.html', deleg=deleg, available_themes=available_themes)


@admin_bp.route('/delegacoes/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def delegation_delete(id):
    from models.vote import Vote
    deleg = Delegation.query.get_or_404(id)

    # Deleta os votos da delegação primeiro para evitar erros de Foreign Key
    Vote.query.filter_by(delegation_id=deleg.id).delete()

    user_to_delete = None
    if deleg.user_id:
        user_to_delete = User.query.get(deleg.user_id)

    ins_to_delete = None
    if deleg.inscription_id:
        ins_to_delete = Inscription.query.get(deleg.inscription_id)

    db.session.delete(deleg)

    if user_to_delete:
        db.session.delete(user_to_delete)

    if ins_to_delete:
        db.session.delete(ins_to_delete)

    db.session.commit()
    flash('Delegação e login deletados com sucesso.', 'success')
    return redirect(url_for('admin.delegations_list'))


# ══════════════════════════════════════════════════════════════
#  CRISE BANNER
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/crise/ativar', methods=['POST'])
@login_required
@admin_required
def crisis_activate():
    # Em produção: salvar mensagem no DB ou cache e fazer push via WebSocket
    message = request.form.get('message', 'Crise diplomática ativada.')
    flash(f'Banner de crise ativado: "{message}"', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/crise/desativar', methods=['POST'])
@login_required
@admin_required
def crisis_deactivate():
    flash('Banner de crise desativado.', 'info')
    return redirect(url_for('admin.dashboard'))


# ══════════════════════════════════════════════════════════════
#  CRONÔMETRO DE ORATÓRIA
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/cronometro')
@login_required
@moderator_required
def cronometro_panel():
    """Painel de controle do cronômetro de oratória."""
    return render_template('admin/cronometro.html')


# ── WebSocket direto: admin → telão ────────────────────────
@socketio.on('admin_timer_start')
def on_admin_timer_start(data):
    duration = int((data or {}).get('duration', 90))
    print(f'[CRONOMETRO WS] start duration={duration}')
    socketio.emit('speech_timer_start', {'duration': duration}, room='telao')


@socketio.on('admin_timer_stop')
def on_admin_timer_stop(data):
    print('[CRONOMETRO WS] stop')
    socketio.emit('speech_timer_stop', {}, room='telao')


@socketio.on('admin_timer_reset')
def on_admin_timer_reset(data):
    print('[CRONOMETRO WS] reset')
    socketio.emit('speech_timer_reset', {}, room='telao')


# ══════════════════════════════════════════════════════════════
#  LISTA DE ORADORES
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/oradores')
@login_required
@moderator_required
def oradores_panel():
    """Painel para admin selecionar oradores."""
    committee_filter = request.args.get('committee', 'all')

    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None),
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    q = Delegation.query
    if committee_filter != 'all':
        q = q.filter_by(committee=committee_filter)
    delegations = q.order_by(Delegation.country).all()

    return render_template('admin/oradores.html',
                           delegations=delegations,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@admin_bp.route('/oradores/toggle', methods=['POST'])
@login_required
@moderator_required
def oradores_toggle():
    """AJAX — adiciona/remove delegacao da lista de oradores."""
    data = request.get_json(silent=True) or {}
    deleg_id = data.get('id')
    if not deleg_id:
        return jsonify({'status': 'error', 'message': 'ID obrigatório'}), 400

    deleg = Delegation.query.get(deleg_id)
    if not deleg:
        return jsonify({'status': 'error', 'message': 'Delegação não encontrada'}), 404

    deleg.orador = not deleg.orador
    db.session.commit()

    # Se o telao estiver exibindo a lista, atualiza em tempo real
    orador_payload = {
        'id':        deleg.id,
        'country':   deleg.country or '?',
        'flag':      deleg.country_flag or '',
        'flag_url':  deleg.flag_url or '',
        'committee': deleg.committee or '',
    }
    socketio.emit('oradores_toggle', {
        'orador': deleg.orador,
        'delegacao': orador_payload,
    }, room='telao')

    return jsonify({
        'status': 'success',
        'orador': deleg.orador,
        'id': deleg.id,
        'country': deleg.country,
        'flag': deleg.country_flag or '',
        'flag_url': deleg.flag_url or '',
        'committee': deleg.committee or '',
    })


@admin_bp.route('/oradores/telao', methods=['POST'])
@login_required
@moderator_required
def oradores_control_screen():
    """Controla exibição da lista de oradores no telão."""
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'show')
    print(f'[ORADORES] Controle telao: action={action} (por {current_user.email})')

    if action == 'show':
        committee_filter = data.get('committee', 'all')
        q = Delegation.query.filter(Delegation.orador == True)
        if committee_filter != 'all':
            q = q.filter_by(committee=committee_filter)
        oradores = q.order_by(Delegation.country).all()

        payload = {
            'committee': committee_filter,
            'oradores': [{
                'id':        d.id,
                'country':   d.country or '?',
                'flag':      d.country_flag or '',
                'flag_url':  d.flag_url or '',
                'committee': d.committee or '',
            } for d in oradores],
        }
        socketio.emit('oradores_show', payload, room='telao')
    else:
        socketio.emit('oradores_hide', {}, room='telao')

    return jsonify({'status': 'success', 'action': action})


# ══════════════════════════════════════════════════════════════
#  DPOs (Documento de Posição Oficial)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/dpos')
@login_required
@moderator_required
def dpos_list():
    """Lista todos os DPOs enviados pelos delegados."""
    from models.delegation import Delegation
    dpos = Delegation.query.filter(Delegation.dpo_uploaded == True)\
        .order_by(Delegation.id.desc()).all()
    return render_template('admin/dpos_list.html', dpos=dpos)


@admin_bp.route('/dpos/<int:id>/download')
@login_required
@moderator_required
def dpo_download(id):
    """Faz o download do arquivo DPO."""
    from flask import send_file
    from models.delegation import Delegation
    import os

    deleg = Delegation.query.get_or_404(id)
    if not deleg.dpo_path or not os.path.isfile(deleg.dpo_path):
        flash('Arquivo DPO não encontrado no servidor.', 'error')
        return redirect(url_for('admin.dpos_list'))

    return send_file(
        deleg.dpo_path,
        as_attachment=True,
        download_name=os.path.basename(deleg.dpo_path)
    )


# ══════════════════════════════════════════════════════════════
#  CRIAR CREDENCIAIS DO DELEGADO
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/delegacoes/<int:id>/credenciais', methods=['POST'])
@login_required
@admin_required
def delegation_create_credentials(id):
    """Cria login para o delegado acessar o portal."""
    from models.user import User
    deleg = Delegation.query.get_or_404(id)

    if not deleg.inscription:
        flash('Delegação sem inscrição vinculada.', 'error')
        return redirect(url_for('admin.delegations_list'))

    ins = deleg.inscription

    # Verifica se já tem conta
    existing = User.query.filter_by(email=ins.email, role='delegate').first()
    if existing:
        flash(f'Delegado {ins.name} já possui credenciais.', 'info')
        return redirect(url_for('admin.delegations_list'))

    # Gera senha padrão: primeiros 4 chars do nome + ano
    import re
    first_name = re.sub(r'[^a-zA-Z]', '', ins.name.split()[0]).lower()[:4]
    password   = f'{first_name}2025'

    user = User(name=ins.name, email=ins.email, role='delegate')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # garante o user.id

    deleg.user_id = user.id
    db.session.commit()

    flash(
        f'Credenciais criadas para {ins.name} → '
        f'Login: {ins.email} | Senha: {password}',
        'success'
    )
    return redirect(url_for('admin.delegations_list'))


# ══════════════════════════════════════════════════════════════
#  SEED DE TESTE (remover em produção)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/seed-teste')
@login_required
@admin_required
def seed_test_delegate():
    """Cria um delegado de teste completo. Remover antes do evento."""
    from models.user        import User
    from models.inscription import Inscription
    from models.delegation  import Delegation
    from datetime import datetime

    # Evita duplicata
    if User.query.filter_by(email='delegado@teste.com').first():
        flash('Delegado de teste já existe! Login: delegado@teste.com / teste2025', 'info')
        return redirect(url_for('admin.delegations_list'))

    # 1. Inscrição
    ins = Inscription(
        name         = 'Ana Silva (Teste)',
        email        = 'delegado@teste.com',
        phone        = '(19) 99999-0000',
        grade        = '2º Ano EM',
        partner_name = 'Bruno Costa (Teste)',
        motivation   = 'Quero representar o Brasil no CS!',
        interests    = 'Paz e Segurança, Direitos Humanos',
        type         = 'delegate',
        status       = 'approved',
        reviewed_at  = datetime.utcnow(),
    )
    db.session.add(ins)
    db.session.flush()

    # 2. Usuário
    user = User(name='Ana Silva (Teste)', email='delegado@teste.com', role='delegate')
    user.set_password('teste2025')
    db.session.add(user)
    db.session.flush()

    # 3. Delegação com país designado
    deleg = Delegation(
        inscription_id = ins.id,
        user_id        = user.id,
        country        = 'Brasil',
        country_flag   = '🇧🇷',
        committee      = 'cs',
        pair_name      = 'Bruno Costa (Teste)',
        accepted       = False,
        dpo_uploaded   = False,
    )
    db.session.add(deleg)
    db.session.commit()

    flash('✅ Delegado de teste criado! Login: delegado@teste.com / teste2025', 'success')
    return redirect(url_for('admin.delegations_list'))


# ══════════════════════════════════════════════════════════════
#  CRIAR ALUNO (Step 1: apenas conta)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def delegate_create():
    """Step 1: cria apenas a conta do aluno (name + email).
    A designação de país/tema/dupla é feita depois em /alunos."""
    from models.user        import User
    from models.inscription import Inscription
    from models.student     import Student
    from datetime import datetime
    import re

    error = None

    if request.method == 'POST':
        name  = request.form['name'].strip()
        email = request.form['email'].strip()

        if User.query.filter_by(email=email).first():
            error = f'Já existe um usuário com o e-mail {email}.'
        else:
            first    = re.sub(r'[^a-zA-Z]', '', name.split()[0]).lower()[:4]
            password = f'{first}2025'

            ins = Inscription(
                name        = name,
                email       = email,
                phone       = request.form.get('phone', ''),
                type        = 'delegate',
                status      = 'approved',
                reviewed_at = datetime.utcnow(),
                reviewed_by = current_user.id,
            )
            db.session.add(ins)

            user = User(name=name, email=email, role='student')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id = user.id,
                name    = name,
                email   = email,
            )
            db.session.add(student)
            db.session.commit()

            # ── Notificações automáticas ─────────────────
            from models.system_config import SystemConfig
            from services.email_service import send_approval_email
            from services.whatsapp_service import send_approval_whatsapp

            notificacoes = []
            if SystemConfig.get('auto_email', '1') == '1':
                ok, msg = send_approval_email(SystemConfig.get, email, name, email, password)
                notificacoes.append(f'E-mail: {"✅" if ok else "❌"} {msg}')

            if SystemConfig.get('auto_whatsapp', '0') == '1' and ins.phone:
                ok, msg = send_approval_whatsapp(SystemConfig.get, ins.phone, name, email, password)
                notificacoes.append(f'WhatsApp: {"✅" if ok else "❌"} {msg}')

            msg_notif = ' | '.join(notificacoes) if notificacoes else ''
            flash(
                f'✅ Conta de aluno criada! '
                f'Login: {email} | Senha: {password} | '
                f'ID Global: {student.global_id[:12]}...'
                + (f'<br><small style="color:var(--muted)">{msg_notif}</small>' if msg_notif else ''),
                'success'
            )
            return redirect(url_for('admin.students_list'))

    return render_template('admin/delegate_create.html', error=error)


# ══════════════════════════════════════════════════════════════
#  LISTAR ALUNOS
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/alunos')
@login_required
@admin_required
def students_list():
    """Lista todos os alunos cadastrados com status da designação."""
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students_list.html', students=students)


# ══════════════════════════════════════════════════════════════
#  CONVOCAR ALUNOS PARA SIMULAÇÃO
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/convocar')
@login_required
@admin_required
def convocar_page():
    """Lista alunos prontos para serem convocados à simulação."""
    from models.theme import Theme
    students = Student.query.order_by(Student.created_at.desc()).all()
    themes = Theme.query.all()
    return render_template('admin/convocar.html', students=students, themes=themes)


@admin_bp.route('/convocar/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def convocar_toggle(id):
    """Alterna o status de convocação de um aluno."""
    student = Student.query.get_or_404(id)
    student.convened = not student.convened
    db.session.commit()
    status = 'convocado' if student.convened else 'desconvocado'
    flash(f'{student.name} {status} com sucesso!', 'success')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/<int:id>/tema', methods=['POST'])
@login_required
@admin_required
def convocar_set_theme(id):
    """Define o tema/debate ao qual o aluno será convocado."""
    from models.delegation import Delegation
    from models.theme import Theme
    from models.participation import ParticipationHistory
    student = Student.query.get_or_404(id)
    theme_id = request.form.get('theme_id', type=int)
    theme = Theme.query.get(theme_id) if theme_id else None

    if student.delegation:
        student.delegation.theme_id = theme.id if theme else None
        student.delegation.edition_year = datetime.utcnow().year
    else:
        delegation = Delegation(
            committee=theme.name if theme else None,
            theme_id=theme.id if theme else None,
            edition_year=datetime.utcnow().year
        )
        db.session.add(delegation)
        db.session.flush()
        student.delegation_id = delegation.id

    student.convened = True

    # Cria registro de participação para este ano
    _ensure_participation_history(student)

    db.session.commit()
    flash(f'{student.name} convocado para {theme.name if theme else "nenhum tema"}!', 'success')
    return redirect(url_for('admin.convocar_page'))


def _ensure_participation_history(student):
    """Cria ParticipationHistory para o ano atual se ainda não existir."""
    from models.participation import ParticipationHistory
    year = datetime.utcnow().year
    existing = ParticipationHistory.query.filter_by(
        student_id=student.id, year=year
    ).first()
    if not existing and student.delegation:
        deleg = student.delegation
        entry = ParticipationHistory(
            student_id=student.id,
            year=year,
            committee=deleg.committee,
            committee_name=deleg.theme.name if deleg.theme else (deleg.committee or ''),
            country=deleg.country or '',
            country_flag=deleg.country_flag or '',
            role='delegate',
            delegation_name=f"{deleg.country or ''} @ {deleg.committee or ''}",
        )
        db.session.add(entry)


# ── Convocar em lote ──────────────────────────────────────────

@admin_bp.route('/convocar/todos', methods=['POST'])
@login_required
@admin_required
def convocar_all():
    """Convoca todos os alunos pendentes."""
    students = Student.query.filter_by(convened=False).all()
    for s in students:
        s.convened = True
        _ensure_participation_history(s)
    db.session.commit()
    flash(f'📢 {len(students)} alunos convocados!', 'success')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/desconvocar-todos', methods=['POST'])
@login_required
@admin_required
def convocar_uncall_all():
    """Remove convocação de todos os alunos."""
    Student.query.update({Student.convened: False})
    db.session.commit()
    flash('🔕 Todos os alunos foram desconvocados.', 'info')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/por-tema/<int:theme_id>', methods=['POST'])
@login_required
@admin_required
def convocar_by_theme(theme_id):
    """Convoca todos os alunos de um tema específico que ainda não foram convocados."""
    from models.theme import Theme
    from models.delegation import Delegation
    theme = Theme.query.get_or_404(theme_id)
    delegation_ids = db.session.query(Delegation.id).filter(Delegation.theme_id == theme_id)
    students = Student.query.filter(
        Student.convened == False,
        Student.delegation_id.in_(delegation_ids)
    ).all()
    for s in students:
        s.convened = True
        _ensure_participation_history(s)
    db.session.commit()
    flash(f'📢 {len(students)} alunos de "{theme.name}" convocados!', 'success')
    return redirect(url_for('admin.convocar_page'))


# ══════════════════════════════════════════════════════════════
#  DESIGNAR PAÍS/TEMA/DUPLA (Step 2)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/alunos/<int:id>/designar', methods=['GET', 'POST'])
@login_required
@admin_required
def student_assign(id):
    """Step 2: atribui país, tema e dupla a um aluno existente."""
    from models.delegation import Delegation
    from models.theme import Theme

    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        country  = request.form.get('country', '').strip()
        flag     = request.form.get('flag', '').strip()
        flag_url = request.form.get('flag_url', '').strip()
        committee = request.form.get('committee', '').strip()
        pair_name = request.form.get('pair_name', '').strip()

        if not country:
            flash('O país é obrigatório.', 'error')
            return render_template('admin/student_assign.html', student=student)

        # Reuse or create delegation
        deleg = Delegation.query.filter_by(user_id=student.user_id).first()
        if not deleg:
            ins = Inscription.query.filter_by(email=student.email, status='approved').first()
            if not ins:
                flash('Inscrição não encontrada para este aluno.', 'error')
                return redirect(url_for('admin.students_list'))

            deleg = Delegation(
                inscription_id=ins.id,
                user_id=student.user_id,
                edition_year=datetime.utcnow().year,
            )
            db.session.add(deleg)
            db.session.flush()
        else:
            deleg.edition_year = datetime.utcnow().year

        theme = Theme.query.filter_by(name=committee).first()
        deleg.theme_id    = theme.id if theme else None
        deleg.country      = country
        deleg.country_flag = flag
        deleg.flag_url     = flag_url
        deleg.committee    = committee
        deleg.pair_name    = pair_name
        deleg.flag_animation = bool(request.form.get('flag_animation'))
        db.session.flush()

        student.delegation_id = deleg.id
        student.convened = True
        db.session.commit()

        flash(f'🌍 {country} designado para {student.name}!', 'success')
        return redirect(url_for('admin.students_list'))

    return render_template('admin/student_assign.html', student=student)


# ── Travamento manual ─────────────────────────────────────────

@admin_bp.route('/alunos/travar', methods=['POST'])
@login_required
@admin_required
def students_lock_all():
    """Trava todos os alunos (read_only = True)."""
    count = Student.query.update({Student.read_only: True})
    db.session.commit()
    flash(f'🔒 {count} alunos travados. Eles não poderão mais registrar presença ou votar.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/alunos/destravar', methods=['POST'])
@login_required
@admin_required
def students_unlock_all():
    """Destrava todos os alunos (read_only = False)."""
    count = Student.query.update({Student.read_only: False})
    db.session.commit()
    flash(f'🔓 {count} alunos destravados.', 'success')
    return redirect(url_for('admin.dashboard'))


# ── Controle de Inscrições ─────────────────────────────────────

@admin_bp.route('/config/inscricoes/toggle', methods=['POST'])
@login_required
@admin_required
def inscricoes_toggle():
    """Abre/fecha inscrições de delegados."""
    current = EventConfig.get_inscricoes_abertas()
    EventConfig.set_inscricoes_abertas(not current)
    status = 'abertas' if not current else 'fechadas'
    flash(f'📋 Inscrições de delegados {status}!', 'success')
    return redirect(url_for('admin.dashboard'))


# ══════════════════════════════════════════════════════════════
#  CONTROLE DE FASE DO EVENTO
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/fase/<string:phase>', methods=['POST'])
@login_required
@admin_required
def set_phase(phase):
    """Altera a fase global do evento (pre / during / post).
    Gatilhos:
      - ao mudar para 'post': compila certificados + trava alunos (read_only)
      - ao mudar para 'pre' ou 'during': destrava alunos"""
    allowed = ('pre', 'during', 'post')
    if phase not in allowed:
        flash('Fase inválida.', 'error')
    else:
        EventConfig.set_phase(phase)
        if phase == 'post':
            locked = Student.query.update({Student.read_only: True})
            _compile_certificates()
            flash(f'🏁 Evento encerrado. {locked} alunos travados. Certificados compilados.', 'success')
        else:
            unlocked = Student.query.update({Student.read_only: False})
            db.session.commit()
            flash(f'Fase alterada para {phase}. {unlocked} alunos destravados.', 'success')
    return redirect(url_for('admin.dashboard'))


# ══════════════════════════════════════════════════════════════
#  CHAMADA / LISTA DE PRESENÇA
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/chamada')
@login_required
@moderator_required
def chamada_panel():
    """Painel de chamada — admin marca presença de cada delegação."""
    committee_filter = request.args.get('committee', 'all')
    
    # Busca comitês distintos direto do banco
    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None), 
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    q = Delegation.query
    if committee_filter != 'all':
        q = q.filter_by(committee=committee_filter)
    delegations = q.order_by(Delegation.country).all()
    
    return render_template('admin/chamada.html',
                           delegations=delegations,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@admin_bp.route('/delegacoes/<int:id>/presenca/<string:status>', methods=['POST'])
@login_required
@moderator_required
def set_presence(id, status):
    """AJAX — atualiza presença e emite via WebSocket para o telão."""
    allowed = ('ausente', 'presente', 'votante')
    if status not in allowed:
        return jsonify({'status': 'error', 'message': 'Status inválido'}), 400

    deleg = Delegation.query.get_or_404(id)
    deleg.presence_status = status
    db.session.commit()

    # Emite atualização individual para o telão
    socketio.emit('chamada_update', {
        'id':         deleg.id,
        'country':    deleg.country or '?',
        'flag':       deleg.country_flag or '',
        'flag_url':   deleg.flag_url or '',
        'committee':  deleg.committee or '',
        'status':     status,
    }, room='telao')

    return jsonify({'status': 'success', 'presence': status})


@admin_bp.route('/chamada/telao', methods=['POST'])
@login_required
@moderator_required
def chamada_control_screen():
    """Controla exibição da chamada no telão público."""
    data   = request.get_json(silent=True) or {}
    action = data.get('action', 'show')

    if action == 'show':
        committee_filter = data.get('committee', 'all')
        q = Delegation.query
        if committee_filter != 'all':
            q = q.filter_by(committee=committee_filter)
        delegations = q.order_by(Delegation.country).all()

        payload = {
            'committee': committee_filter,
            'delegations': [{
                'id':         d.id,
                'country':    d.country or '?',
                'flag':       d.country_flag or '',
                'flag_url':   d.flag_url or '',
                'committee':  d.committee or '',
                'status':     d.presence_status or 'ausente',
            } for d in delegations],
        }
        socketio.emit('chamada_show', payload, room='telao')
    else:
        socketio.emit('chamada_hide', {}, room='telao')

    return jsonify({'status': 'success', 'action': action})


# ══════════════════════════════════════════════════════════════
#  DOCUMENTOS (enviados pelo admin para os delegados)
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/documentos')
@login_required
@admin_required
def documentos_list():
    """Lista todos os documentos enviados."""
    from models.theme import Theme
    documentos = Document.query.order_by(Document.created_at.desc()).all()
    return render_template('admin/documentos_list.html', documentos=documentos)


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

    safe_name = f'doc_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}_{file.filename}'
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


# ══════════════════════════════════════════════════════════════
#  INVOCAÇÃO ATIVA DE SESSÕES
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/invocar', methods=['POST'])
@login_required
@moderator_required
def invocar_sessao():
    """Redireciona os alunos ativos para a URL fornecida."""
    target_url = request.form.get('target_url', '').strip()
    if not target_url:
        flash('A URL de destino é obrigatória para invocar a sessão.', 'error')
        return redirect(url_for('admin.invocar_page'))

    label = request.form.get('label', target_url).strip()
    EventConfig.set_invoke(target_url, label)

    # Emite para todos os alunos na sala 'all_students'
    socketio.emit('invoke_session', {'url': target_url, 'label': label}, room='all_students')

    flash(f'🔔 Alunos invocados para: {label}', 'success')
    return redirect(url_for('admin.invocar_page'))


@admin_bp.route('/invocar/parar', methods=['POST'])
@login_required
@moderator_required
def invocar_parar():
    """Para a invocação ativa."""
    EventConfig.clear_invoke()
    socketio.emit('invoke_clear', {}, room='all_students')
    flash('🔕 Invocação encerrada.', 'info')
    return redirect(url_for('admin.invocar_page'))


@admin_bp.route('/invocar')
@login_required
@moderator_required
def invocar_page():
    """Página dedicada para invocar alunos."""
    active_invoke = EventConfig.get_invoke()
    return render_template('admin/invocar.html', active_invoke=active_invoke)


# ══════════════════════════════════════════════════════════════
#  CERTIFICADOS — Gestão e Compilação Automática
# ══════════════════════════════════════════════════════════════

def _compile_certificates():
    """Algoritmo de Compilação por Assiduidade.
    Gera certificate_hash e certificate_url para alunos elegíveis
    (que registraram presença como 'presente' ou 'votante')."""
    from models.student import Student
    from models.delegation import Delegation
    students = Student.query.all()
    generated = 0
    for student in students:
        deleg = Delegation.query.get(student.delegation_id) if student.delegation_id else None
        if deleg and deleg.presence_status in ('presente', 'votante'):
            if not student.certificate_hash:
                student.certificate_hash = str(_uuid.uuid4())
            if not student.certificate_url:
                student.certificate_url = url_for('certificate_view', hash=student.certificate_hash, _external=True) if student.certificate_hash else ''
            generated += 1
    db.session.commit()
    return generated


def _sign_certificate(student):
    """Gera uma assinatura HMAC-SHA256 para o certificado."""
    if not student.certificate_hash:
        return None
    secret = current_app.config.get('SECRET_KEY', 'swdl-secret')
    student.digital_signature = student.compute_signature(secret)
    student.signed_at = datetime.utcnow()
    db.session.commit()
    return student.digital_signature


def _log_audit(action, target_type, target_id, target_name='', details=''):
    log = AuditLog(
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        user_id=current_user.id,
        user_name=current_user.name or current_user.email,
        details=details,
    )
    db.session.add(log)
    db.session.commit()


@admin_bp.route('/certificados')
@login_required
@admin_required
def certificates_list():
    """Página de gestão de certificados."""
    from models.student import Student
    from models.delegation import Delegation
    students = Student.query.order_by(Student.name).all()

    eligible = 0
    for s in students:
        deleg = Delegation.query.get(s.delegation_id) if s.delegation_id else None
        s._eligible = deleg and deleg.presence_status in ('presente', 'votante')

    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()

    return render_template('admin/certificates_list.html',
                           students=students,
                           total=len(students),
                           released=sum(1 for s in students if s.certificate_released),
                           has_hash=sum(1 for s in students if s.certificate_hash),
                           eligible=sum(1 for s in students if s._eligible),
                           event_phase=EventConfig.get_phase(),
                           audit_logs=audit_logs)


@admin_bp.route('/certificados/compilar', methods=['POST'])
@login_required
@admin_required
def certificates_compile():
    """Executa o algoritmo de compilação por assiduidade."""
    count = _compile_certificates()
    _log_audit('compile_certificates', 'system', 0, details=f'Compilados {count} certificados')
    flash(f'✅ Certificados compilados para {count} alunos com presença registrada!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/<int:id>/liberar', methods=['POST'])
@login_required
@admin_required
def certificate_release(id):
    """Libera o certificado de um aluno específico."""
    from models.student import Student
    student = Student.query.get_or_404(id)
    if not student.certificate_hash:
        student.certificate_hash = str(_uuid.uuid4())
        student.certificate_url = url_for('certificate_view', hash=student.certificate_hash, _external=True)
    student.certificate_released = True
    db.session.commit()
    _log_audit('release_certificate', 'student', student.id, student.name)
    flash(f'✅ Certificado liberado para {student.name}!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/liberar-todos', methods=['POST'])
@login_required
@admin_required
def certificates_release_all():
    """Libera certificados de todos os alunos com hash gerado."""
    from models.student import Student
    students = Student.query.filter(
        Student.certificate_hash.isnot(None),
        Student.certificate_hash != '',
        Student.certificate_released == False
    ).all()
    for s in students:
        s.certificate_released = True
    db.session.commit()
    _log_audit('release_all_certificates', 'system', 0, details=f'{len(students)} certificados liberados em lote')
    flash(f'✅ {len(students)} certificados liberados em lote!', 'success')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/reverter/<int:id>', methods=['POST'])
@login_required
@admin_required
def certificate_revoke(id):
    """Reverte a liberação de um certificado."""
    from models.student import Student
    student = Student.query.get_or_404(id)
    student.certificate_released = False
    db.session.commit()
    _log_audit('revoke_certificate', 'student', student.id, student.name)
    flash(f'🔒 Certificado de {student.name} revertido.', 'info')
    return redirect(url_for('admin.certificates_list'))


# ── Assinatura Digital ────────────────────────────────────────

@admin_bp.route('/certificados/<int:id>/assinar', methods=['POST'])
@login_required
@admin_required
def certificate_sign(id):
    """Assina digitalmente (HMAC) o certificado de um aluno."""
    student = Student.query.get_or_404(id)
    if not student.certificate_hash:
        student.certificate_hash = str(_uuid.uuid4())
        student.certificate_url = url_for('vote.certificate_view', hash=student.certificate_hash, _external=True)
        db.session.commit()
    sig = _sign_certificate(student)
    if sig:
        _log_audit('sign_certificate', 'student', student.id, student.name)
        flash(f'✅ Certificado de {student.name} assinado digitalmente!', 'success')
    else:
        flash('⚠️ Não foi possível assinar.', 'error')
    return redirect(url_for('admin.certificates_list'))


@admin_bp.route('/certificados/assinar-todos', methods=['POST'])
@login_required
@admin_required
def certificates_sign_all():
    """Assina digitalmente todos os certificados compilados."""
    students = Student.query.filter(
        Student.certificate_hash.isnot(None),
        Student.certificate_hash != '',
    ).all()
    count = 0
    for s in students:
        sig = _sign_certificate(s)
        if sig:
            count += 1
    _log_audit('sign_all_certificates', 'system', 0, details=f'{count} certificados assinados')
    flash(f'✅ {count} certificados assinados digitalmente!', 'success')
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
    flash(f'🔓 Assinatura removida de {student.name}.', 'info')
    return redirect(url_for('admin.certificates_list'))


# ══════════════════════════════════════════════════════════════
#  DASHBOARD DO DIRETOR (Mesa / Chair)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO DE NOTIFICAÇÕES
# ══════════════════════════════════════════════════════════════

@admin_bp.route('/notificacoes', methods=['GET', 'POST'])
@login_required
@admin_required
def notifications_config():
    from models.system_config import SystemConfig

    if request.method == 'POST':
        section = request.form.get('section', '')

        if section == 'email':
            SystemConfig.set('smtp_server', request.form.get('smtp_server', ''))
            SystemConfig.set('smtp_port',   request.form.get('smtp_port', '587'))
            SystemConfig.set('smtp_user',   request.form.get('smtp_user', ''))
            SystemConfig.set('smtp_pass',   request.form.get('smtp_pass', ''))
            SystemConfig.set('from_email',  request.form.get('from_email', ''))
            flash('Configurações de e-mail salvas!', 'success')

        elif section == 'whatsapp':
            SystemConfig.set('whatsapp_api_url', request.form.get('whatsapp_api_url', ''))
            SystemConfig.set('whatsapp_api_key', request.form.get('whatsapp_api_key', ''))
            flash('Configurações de WhatsApp salvas!', 'success')

        elif section == 'general':
            SystemConfig.set('auto_email',    '1' if request.form.get('auto_email') else '0')
            SystemConfig.set('auto_whatsapp', '1' if request.form.get('auto_whatsapp') else '0')
            flash('Preferências de disparo salvas!', 'success')

        return redirect(url_for('admin.notifications_config'))

    configs = {
        'smtp_server': SystemConfig.get('smtp_server', ''),
        'smtp_port':   SystemConfig.get('smtp_port', '587'),
        'smtp_user':   SystemConfig.get('smtp_user', ''),
        'smtp_pass':   SystemConfig.get('smtp_pass', ''),
        'from_email':  SystemConfig.get('from_email', ''),
        'whatsapp_api_url': SystemConfig.get('whatsapp_api_url', ''),
        'whatsapp_api_key': SystemConfig.get('whatsapp_api_key', ''),
        'auto_email':    SystemConfig.get('auto_email', '1'),
        'auto_whatsapp': SystemConfig.get('auto_whatsapp', '0'),
    }
    return render_template('admin/notifications_config.html', configs=configs)


@admin_bp.route('/notificacoes/testar-email', methods=['POST'])
@login_required
@admin_required
def test_email_config():
    from models.system_config import SystemConfig
    from services.email_service import send_approval_email

    success, msg = send_approval_email(
        SystemConfig.get,
        to_email=current_user.email,
        student_name=current_user.name,
        login_email='teste@exemplo.com',
        password='teste2025',
    )
    if success:
        flash(f'E-mail de teste enviado para {current_user.email}! Verifique sua caixa de entrada.', 'success')
    else:
        flash(f'Falha ao enviar e-mail de teste: {msg}', 'error')
    return redirect(url_for('admin.notifications_config'))


@admin_bp.route('/diretor')
@login_required
@moderator_required
def director_dashboard():
    """Dashboard focado em moderação para a Mesa Diretora."""
    from models.theme import Theme
    from models.vote import VoteSession
    from models.student import Student
    themes = Theme.query.order_by(Theme.name).all()
    phase  = EventConfig.get_phase()
    theme_id = request.args.get('theme_id', None)
    if theme_id and theme_id != 'all':
        try:
            theme_id = int(theme_id)
        except ValueError:
            theme_id = None
    else:
        theme_id = None

    def _base_q():
        q = Delegation.query
        if theme_id:
            q = q.filter_by(theme_id=theme_id)
        return q

    total_deleg = _base_q().count()

    # Oradores ativos
    oradores_count = _base_q().filter(Delegation.orador == True).count()

    # Chamada stats
    presentes = _base_q().filter_by(presence_status='presente').count()
    votantes  = _base_q().filter_by(presence_status='votante').count()
    ausentes  = _base_q().filter_by(presence_status='ausente').count()

    # Votações
    open_votes = VoteSession.query.filter_by(status='open').count()
    total_votes = VoteSession.query.count()

    # DPOs
    dpos = _base_q().filter(Delegation.dpo_uploaded == True).count()

    # Alunos / delegações
    convened = Student.query.filter(Student.convened == True).count()
    no_deleg = Student.query.filter(Student.delegation_id.is_(None)).count()
    total_students = Student.query.count()

    # Agenda
    agenda_count = AgendaItem.query.count()
    current_agenda = AgendaItem.query.filter_by(status='now').first()

    # Certificados
    certificates = Student.query.filter(Student.certificate_released == True).count()

    # Itens da agenda por dia (para timeline)
    days_raw = AgendaItem.query.with_entities(AgendaItem.day).distinct().order_by(AgendaItem.day).all()
    days_agenda = [d[0] for d in days_raw]
    agenda_items_by_day = {}
    for day in days_agenda:
        agenda_items_by_day[day] = AgendaItem.query.filter_by(day=day).count()

    # Stats por tema (para o contexto)
    theme_stats = {}
    for t in themes:
        tq = Delegation.query.filter_by(theme_id=t.id)
        theme_stats[t.id] = {
            'total': tq.count(),
            'presentes': tq.filter_by(presence_status='presente').count(),
            'votantes': tq.filter_by(presence_status='votante').count(),
            'ausentes': tq.filter_by(presence_status='ausente').count(),
            'oradores': tq.filter(Delegation.orador == True).count(),
            'dpos': tq.filter(Delegation.dpo_uploaded == True).count(),
        }

    selected_theme = Theme.query.get(theme_id) if theme_id else None

    return render_template('admin/dashboard_director.html',
                           themes=themes,
                           event_phase=phase,
                           theme_id=theme_id or 'all',
                           selected_theme=selected_theme,
                           total_deleg=total_deleg,
                           oradores_count=oradores_count,
                           presentes=presentes,
                           votantes=votantes,
                           ausentes=ausentes,
                           open_votes=open_votes,
                           total_votes=total_votes,
                           dpos=dpos,
                           convened=convened,
                           no_deleg=no_deleg,
                           total_students=total_students,
                           agenda_count=agenda_count,
                           current_agenda=current_agenda,
                           certificates=certificates,
                           days_agenda=days_agenda,
                           agenda_items_by_day=agenda_items_by_day,
                           theme_stats=theme_stats)
