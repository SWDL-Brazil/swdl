# =============================================================
#  SWDL — routes/vote.py
#  Sistema de votação em tempo real via WebSocket
# =============================================================
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify)
from flask_login import login_required, current_user
from flask_socketio import emit, join_room
from extensions import db, socketio
from models.vote       import VoteSession, Vote
from models.delegation import Delegation
from datetime import datetime

vote_bp = Blueprint('vote', __name__)


def moderator_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator():
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def _broadcast_results(session_id):
    """Emite os resultados atualizados para todos os clientes."""
    session = VoteSession.query.get(session_id)
    if session:
        data = session.to_dict()
        socketio.emit('vote_update', data, room=f'session_{session_id}')
        socketio.emit('vote_update', data, room='admin')
        socketio.emit('vote_update', data, room='telao')


# ══════════════════════════════════════════════════════════════
#  ADMIN — gerenciar sessões de votação
# ══════════════════════════════════════════════════════════════

@vote_bp.route('/admin/votacoes')
@login_required
@moderator_required
def vote_list():
    sessions = VoteSession.query.order_by(VoteSession.created_at.desc()).all()
    return render_template('admin/vote_list.html', sessions=sessions)


@vote_bp.route('/admin/votacoes/nova', methods=['GET', 'POST'])
@login_required
@moderator_required
def vote_create():

    if request.method == 'POST':
        session = VoteSession(
            title        = request.form['title'],
            description  = request.form.get('description', ''),
            committee    = request.form.get('committee', 'geral'),
            duration_sec = int(request.form.get('duration_sec', 120)),
            status       = 'open',
            created_by   = current_user.id,
        )
        db.session.add(session)
        db.session.commit()

        # Notifica todos que uma nova votação abriu
        data = session.to_dict()
        socketio.emit('vote_opened', data, room='all_delegates')
        socketio.emit('vote_opened', data, room='telao')
        flash(f'Votação "{session.title}" aberta!', 'success')
        return redirect(url_for('vote.vote_list'))

    return render_template('admin/vote_form.html', session=None)


@vote_bp.route('/admin/votacoes/<int:id>/fechar', methods=['POST'])
@login_required
@moderator_required
def vote_close(id):

    session = VoteSession.query.get_or_404(id)
    session.status    = 'closed'
    session.closed_at = datetime.utcnow()
    db.session.commit()

    # Notifica fechamento
    data = session.to_dict()
    socketio.emit('vote_closed', data, room='all_delegates')
    socketio.emit('vote_closed', data, room='admin')
    socketio.emit('vote_closed', data, room='telao')
    flash(f'Votação "{session.title}" encerrada.', 'info')
    return redirect(url_for('vote.vote_list'))


@vote_bp.route('/admin/votacoes/<int:id>/deletar', methods=['POST'])
@login_required
@moderator_required
def vote_delete(id):
    session = VoteSession.query.get_or_404(id)
    db.session.delete(session)
    db.session.commit()
    flash('Votação removida.', 'info')
    return redirect(url_for('vote.vote_list'))


@vote_bp.route('/admin/votacoes/<int:id>/resultados')
@login_required
@moderator_required
def vote_results(id):
    session = VoteSession.query.get_or_404(id)
    votes   = Vote.query.filter_by(session_id=id).all()

    # Enriquece com dados da delegação
    vote_details = []
    for v in votes:
        deleg = Delegation.query.get(v.delegation_id)
        vote_details.append({
            'country':  deleg.country if deleg else '?',
            'flag':     deleg.country_flag if deleg else '',
            'flag_url': deleg.flag_url if deleg else '',
            'choice':   v.choice,
            'voted_at': v.voted_at,
        })

    return render_template('admin/vote_results.html',
                           session=session,
                           vote_details=vote_details)


# ══════════════════════════════════════════════════════════════
#  DELEGADO — página dedicada de votação
# ══════════════════════════════════════════════════════════════

@vote_bp.route('/delegado/votar')
@login_required
def delegate_vote_page():
    if current_user.role not in ('student', 'delegate'):
        return redirect(url_for('auth.student_login'))

    delegation    = Delegation.query.filter_by(user_id=current_user.id).first()
    open_sessions = VoteSession.query.filter_by(status='open').all()

    # Marca quais a delegação já votou (inclui parceiro)
    voted_ids = set()
    if delegation:
        voted_ids = {
            v.session_id for v in
            Vote.query.filter_by(delegation_id=delegation.id).all()
        }

    return render_template('delegate/vote_page.html',
                           delegation=delegation,
                           open_sessions=open_sessions,
                           voted_ids=voted_ids)


# ══════════════════════════════════════════════════════════════
#  API — submeter voto
# ══════════════════════════════════════════════════════════════

@vote_bp.route('/api/votar', methods=['POST'])
@login_required
def api_submit_vote():
    if current_user.role != 'delegate':
        return jsonify({'ok': False, 'error': 'Acesso negado'}), 403

    data       = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    choice     = data.get('choice')

    if choice not in ('favor', 'contra', 'abstencao'):
        return jsonify({'ok': False, 'error': 'Voto inválido'}), 400

    delegation = Delegation.query.filter_by(user_id=current_user.id).first()
    if not delegation:
        return jsonify({'ok': False, 'error': 'Delegação não encontrada'}), 404

    vote_session = VoteSession.query.get(session_id)
    if not vote_session or vote_session.status != 'open':
        return jsonify({'ok': False, 'error': 'Votação encerrada ou não encontrada'}), 400

    # Verifica se a delegação está presente (regra de integridade)
    if delegation.presence_status == 'ausente':
        return jsonify({'ok': False, 'error': 'Presença obrigatória para votar. Registre sua presença primeiro.'}), 403

    # Verifica voto duplicado
    existing = Vote.query.filter_by(
        session_id=session_id, delegation_id=delegation.id
    ).first()
    if existing:
        return jsonify({'ok': False, 'error': 'Você já votou nesta sessão'}), 409

    # Registra voto
    vote = Vote(
        session_id    = session_id,
        delegation_id = delegation.id,
        choice        = choice,
    )
    db.session.add(vote)
    db.session.commit()

    # Broadcast em tempo real
    _broadcast_results(session_id)

    # Atualiza vote list
    all_sessions = VoteSession.query.order_by(VoteSession.created_at.desc()).all()
    socketio.emit('sessions_sync', [s.to_dict() for s in all_sessions], room='vote_list')

    return jsonify({'ok': True, 'choice': choice})


# ══════════════════════════════════════════════════════════════
#  WEBSOCKET — eventos
# ══════════════════════════════════════════════════════════════

@socketio.on('join_session')
def on_join_session(data):
    session_id = data.get('session_id')
    join_room(f'session_{session_id}')
    # Envia estado atual imediatamente
    session = VoteSession.query.get(session_id)
    if session:
        emit('vote_update', session.to_dict())


@socketio.on('join_admin')
def on_join_admin(data):
    join_room('admin')
    join_room('vote_list')


@socketio.on('join_vote_list')
def on_join_vote_list(data):
    join_room('vote_list')
    # Envia todas as sessões para sincronizar a tabela
    sessions = VoteSession.query.order_by(VoteSession.created_at.desc()).all()
    emit('sessions_sync', [s.to_dict() for s in sessions])


@socketio.on('join_delegates')
def on_join_delegates(data):
    join_room('all_delegates')
    open_sessions = VoteSession.query.filter_by(status='open').all()
    emit('open_sessions', [s.to_dict() for s in open_sessions])


@socketio.on('join_telao')
def on_join_telao(data):
    join_room('telao')
    # Envia sessão aberta imediatamente ao telão conectar
    session = VoteSession.query.filter_by(status='open')                               .order_by(VoteSession.created_at.desc()).first()
    if session:
        emit('vote_opened', session.to_dict())


# ══════════════════════════════════════════════════════════════
#  CERTIFICADOS — visualização pública
# ══════════════════════════════════════════════════════════════

@vote_bp.route('/certificado/<hash>')
def certificate_view(hash):
    """Página pública de visualização de certificado."""
    from models.student import Student
    student = Student.query.filter_by(certificate_hash=hash).first()
    if not student or not student.certificate_released:
        return render_template('public/certificate_invalid.html'), 404
    return render_template('public/certificate_view.html',
                           student=student)


# ── API: checar votações abertas e status de voto ─────────────
@vote_bp.route('/api/votacoes/abertas')
@login_required
def api_open_sessions():
    delegation    = Delegation.query.filter_by(user_id=current_user.id).first()
    open_sessions = VoteSession.query.filter_by(status='open').all()

    voted_ids = set()
    if delegation:
        voted_ids = {
            v.session_id for v in
            Vote.query.filter_by(delegation_id=delegation.id).all()
        }

    result = []
    for s in open_sessions:
        d = s.to_dict()
        d['already_voted'] = s.id in voted_ids
        result.append(d)

    return jsonify(result)


# ══════════════════════════════════════════════════════════════
#  TELÃO — página pública de projeção
# ══════════════════════════════════════════════════════════════

@vote_bp.route('/telao')
def telao():
    """Página de projeção — sem login, aberta no projetor."""
    return render_template('telao.html')


@vote_bp.route('/api/telao/estado')
def api_telao_estado():
    """Estado atual para o telão: sessão aberta + votos + ticker + oradores."""
    from models.news import News
    from models.delegation import Delegation
    session = VoteSession.query.filter_by(status='open')\
                               .order_by(VoteSession.created_at.desc()).first()
    news    = News.query.filter_by(published=True)\
                        .order_by(News.created_at.desc()).limit(6).all()

    oradores = Delegation.query.filter(Delegation.orador == True)\
                               .order_by(Delegation.country).all()

    return jsonify({
        'session': session.to_dict() if session else None,
        'ticker':  [n.title for n in news],
        'oradores': [{
            'id':        d.id,
            'country':   d.country or '?',
            'flag':      d.country_flag or '',
            'flag_url':  d.flag_url or '',
            'committee': d.committee or '',
        } for d in oradores],
    })