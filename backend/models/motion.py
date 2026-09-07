# =============================================================
#  SWDL — models/motion.py
#  Fila de moções do debate (Moderated Caucus, Unmoderated, etc.)
# =============================================================
from extensions import db
from datetime import datetime, timezone


MOTION_TYPES = {
    'moderated_caucus':   {'label': 'Moderated Caucus',   'icon': '🎤', 'default_total': 900, 'default_speaking': 60},
    'unmoderated_caucus': {'label': 'Unmoderated Caucus', 'icon': '🗣️', 'default_total': 600, 'default_speaking': 0},
    'round_table':        {'label': 'Round Table',         'icon': '📋', 'default_total': 1200, 'default_speaking': 90},
    'formal_speech':      {'label': 'Formal Speech',       'icon': '📜', 'default_total': 1800, 'default_speaking': 120},
    'close_debate':       {'label': 'Close Debate',        'icon': '🔒', 'default_total': 0, 'default_speaking': 0},
    'other':              {'label': 'Outro',               'icon': '📌', 'default_total': 600, 'default_speaking': 60},
}


class Motion(db.Model):
    __tablename__ = 'motions'

    id              = db.Column(db.Integer, primary_key=True)
    proposer_id     = db.Column(db.Integer, db.ForeignKey('delegations.id'),
                                nullable=False, index=True)
    committee       = db.Column(db.String(30), nullable=False, index=True)
    motion_type     = db.Column(db.String(30), nullable=False, default='moderated_caucus')
    topic           = db.Column(db.String(300), nullable=False)
    total_time      = db.Column(db.Integer, default=900)
    speaking_time   = db.Column(db.Integer, default=60)
    status          = db.Column(db.String(20), default='pending', index=True)
    # pending | approved | rejected | active | completed
    priority        = db.Column(db.Integer, default=0)
    seconded_by_id  = db.Column(db.Integer, db.ForeignKey('delegations.id'), nullable=True)
    chair_notes     = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    decided_at      = db.Column(db.DateTime)
    completed_at    = db.Column(db.DateTime)

    proposer   = db.relationship('Delegation', foreign_keys=[proposer_id], backref='motions_proposed')
    seconded_by = db.relationship('Delegation', foreign_keys=[seconded_by_id], backref='motions_seconded')

    def type_info(self):
        return MOTION_TYPES.get(self.motion_type, MOTION_TYPES['other'])

    def to_dict(self):
        p = self.proposer
        s = self.seconded_by
        info = self.type_info()
        return {
            'id':            self.id,
            'proposer_id':   self.proposer_id,
            'proposer_country': p.country if p else '?',
            'proposer_flag': p.country_flag if p else '',
            'proposer_flag_url': p.flag_url if p else '',
            'committee':     self.committee,
            'motion_type':   self.motion_type,
            'type_label':    info['label'],
            'type_icon':     info['icon'],
            'topic':         self.topic,
            'total_time':    self.total_time,
            'speaking_time': self.speaking_time,
            'status':        self.status,
            'priority':      self.priority,
            'seconded_by_id': self.seconded_by_id,
            'seconded_by_country': s.country if s else None,
            'chair_notes':   self.chair_notes or '',
            'created_at':    self.created_at.isoformat() if self.created_at else None,
            'decided_at':    self.decided_at.isoformat() if self.decided_at else None,
            'completed_at':  self.completed_at.isoformat() if self.completed_at else None,
        }

    @staticmethod
    def pending_for_committee(committee):
        return Motion.query.filter_by(
            committee=committee, status='pending'
        ).order_by(Motion.priority.desc(), Motion.created_at).all()

    @staticmethod
    def active_for_committee(committee):
        return Motion.query.filter_by(
            committee=committee, status='active'
        ).first()

    @staticmethod
    def today_log(committee=None):
        q = Motion.query.filter(Motion.status.in_(['approved', 'rejected', 'active', 'completed']))
        if committee and committee != 'all':
            q = q.filter_by(committee=committee)
        return q.order_by(Motion.decided_at.desc()).all()
