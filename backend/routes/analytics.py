# =============================================================
#  SWDL — routes/analytics.py
#  Dashboard analítico com timeline e estatísticas
# =============================================================
from flask import (Blueprint, render_template, request, jsonify, abort)
from flask_login import login_required
from extensions import db
from models.delegation import Delegation
from models.speech_log import SpeechLog
from models.motion import Motion
from models.resolution import Resolution

analytics_bp = Blueprint('analytics', __name__)


def moderator_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or not current_user.is_moderator():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@analytics_bp.route('/admin/analytics')
@login_required
@moderator_required
def analytics_panel():
    committee_filter = request.args.get('committee', 'all')

    committees_query = db.session.query(Delegation.committee).filter(
        Delegation.committee.isnot(None),
        Delegation.committee != ''
    ).distinct().all()
    available_committees = sorted([c[0] for c in committees_query])

    if committee_filter != 'all':
        stats = SpeechLog.committee_stats(committee_filter)
    else:
        stats = SpeechLog.committee_stats(None)

    timeline = SpeechLog.timeline(
        committee_filter if committee_filter != 'all' else None
    )

    return render_template('admin/analytics.html',
                           stats=stats,
                           timeline=timeline,
                           committee_filter=committee_filter,
                           available_committees=available_committees)


@analytics_bp.route('/admin/analytics/<committee>')
@login_required
@moderator_required
def analytics_committee(committee):
    stats = SpeechLog.committee_stats(committee)
    timeline = SpeechLog.timeline(committee)
    return render_template('admin/analytics.html',
                           stats=stats,
                           timeline=timeline,
                           committee_filter=committee,
                           available_committees=[committee])


@analytics_bp.route('/admin/analytics/export/<committee>')
@login_required
@moderator_required
def analytics_export(committee):
    stats = SpeechLog.committee_stats(committee)
    timeline = SpeechLog.timeline(committee, limit=500)

    export = {
        'committee': committee,
        'stats': stats,
        'timeline': [t.to_dict() for t in timeline],
    }
    return jsonify(export)
