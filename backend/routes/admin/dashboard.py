"""SWDL Admin — Dashboard routes."""
from flask import render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required, moderator_required
from models.agenda import AgendaItem
from models.inscription import Inscription
from models.delegation import Delegation
from models.user import User
from models.student import Student
from models.document import Document
from models.event_config import EventConfig
from models.urgent_alert import UrgentAlert
from models.news import News
from routes.agenda_utils import get_agenda_status
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from extensions import db


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
    }

    rel_stats = db.session.query(
        func.count().filter(Delegation.presence_status.in_(['presente', 'votante'])).label('presentes'),
        func.count().filter(Delegation.presence_status == 'ausente').label('ausentes'),
        func.count().filter(Delegation.orador == True).label('oradores'),
        func.count().filter(Delegation.dpo_uploaded == True).label('dpos'),
    ).select_from(Delegation).first()
    stats['presentes'] = rel_stats.presentes
    stats['ausentes']  = rel_stats.ausentes
    stats['oradores']  = rel_stats.oradores
    stats['dpos']      = rel_stats.dpos

    stu_stats = db.session.query(
        func.count().filter(Student.delegation_id.is_(None)).label('no_deleg'),
        func.count().filter(Student.convened == True).label('convened'),
        func.count().filter(Student.read_only == True).label('read_only'),
    ).select_from(Student).first()
    stats['students_no_deleg'] = stu_stats.no_deleg
    stats['convened']          = stu_stats.convened
    stats['read_only']         = stu_stats.read_only
    recent_students      = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    recent_news          = News.query.order_by(News.created_at.desc()).limit(5).all()
    pending_inscriptions = Inscription.query.filter_by(status='pending').order_by(
                           Inscription.submitted_at.desc()).limit(5).all()
    current_agenda       = AgendaItem.query.filter_by(status='now').first()
    event_phase, _, _     = get_agenda_status()
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


@admin_bp.route('/diretor')
@login_required
@moderator_required
def director_dashboard():
    """Dashboard focado em moderação para a Mesa Diretora."""
    from models.theme import Theme
    from models.vote import VoteSession
    from models.student import Student
    themes = Theme.query.order_by(Theme.name).all()
    phase  = get_agenda_status()[0] or 'pre'
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

    # Itens da agenda por dia (para timeline) — batch query
    days_raw = AgendaItem.query.with_entities(AgendaItem.day).distinct().order_by(AgendaItem.day).all()
    days_agenda = [d[0] for d in days_raw]
    agenda_items_by_day = {}
    if days_agenda:
        day_counts = db.session.query(
            AgendaItem.day, db.func.count()
        ).filter(AgendaItem.day.in_(days_agenda)).group_by(AgendaItem.day).all()
        agenda_items_by_day = dict(day_counts)

    # Stats por tema — batch GROUP BY (1 query em vez de 6*N)
    from sqlalchemy import func
    theme_rows = db.session.query(
        Delegation.theme_id,
        func.count().label('total'),
        func.count().filter(Delegation.presence_status == 'presente').label('presentes'),
        func.count().filter(Delegation.presence_status == 'votante').label('votantes'),
        func.count().filter(Delegation.presence_status == 'ausente').label('ausentes'),
        func.count().filter(Delegation.orador == True).label('oradores'),
        func.count().filter(Delegation.dpo_uploaded == True).label('dpos'),
    ).group_by(Delegation.theme_id).all()
    theme_stats = {}
    for row in theme_rows:
        theme_stats[row.theme_id] = {
            'total': row.total, 'presentes': row.presentes,
            'votantes': row.votantes, 'ausentes': row.ausentes,
            'oradores': row.oradores, 'dpos': row.dpos,
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
