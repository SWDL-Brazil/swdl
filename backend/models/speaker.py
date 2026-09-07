# =============================================================
#  SWDL — models/speaker.py
#  Fila de oradores com tracking de discursos
# =============================================================
from extensions import db
from datetime import datetime, timezone


class SpeakerEntry(db.Model):
    __tablename__ = 'speaker_queue'

    id             = db.Column(db.Integer, primary_key=True)
    delegation_id  = db.Column(db.Integer, db.ForeignKey('delegations.id'),
                               nullable=False, index=True)
    committee      = db.Column(db.String(30), index=True)
    topic          = db.Column(db.String(300))
    speaking_time  = db.Column(db.Integer, default=60)
    position       = db.Column(db.Integer, default=0)
    status         = db.Column(db.String(20), default='pending', index=True)
    # pending | speaking | done | skipped
    started_at     = db.Column(db.DateTime)
    ended_at       = db.Column(db.DateTime)
    duration_used  = db.Column(db.Integer, default=0)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    delegation = db.relationship('Delegation', backref='speaker_entries')

    def to_dict(self):
        d = self.delegation
        return {
            'id':            self.id,
            'delegation_id': self.delegation_id,
            'country':       d.country if d else '?',
            'flag':          d.country_flag if d else '',
            'flag_url':      d.flag_url if d else '',
            'committee':     self.committee or (d.committee if d else ''),
            'topic':         self.topic or '',
            'speaking_time': self.speaking_time,
            'position':      self.position,
            'status':        self.status,
            'started_at':    self.started_at.isoformat() if self.started_at else None,
            'ended_at':      self.ended_at.isoformat() if self.ended_at else None,
            'duration_used': self.duration_used,
            'created_at':    self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def current_queue(committee=None):
        q = SpeakerEntry.query.filter_by(status='pending')
        if committee and committee != 'all':
            q = q.filter_by(committee=committee)
        return q.order_by(SpeakerEntry.position, SpeakerEntry.created_at).all()

    @staticmethod
    def active_speaker(committee=None):
        q = SpeakerEntry.query.filter_by(status='speaking')
        if committee and committee != 'all':
            q = q.filter_by(committee=committee)
        return q.first()

    @staticmethod
    def today_log(committee=None):
        q = SpeakerEntry.query.filter(SpeakerEntry.status.in_(['done', 'skipped']))
        if committee and committee != 'all':
            q = q.filter_by(committee=committee)
        return q.order_by(SpeakerEntry.ended_at.desc()).all()
