# =============================================================
#  SWDL — models/speech_log.py
#  Registro de atividades para analytics
# =============================================================
from extensions import db
from datetime import datetime, timezone
from sqlalchemy import func


class SpeechLog(db.Model):
    __tablename__ = 'speech_log'

    id             = db.Column(db.Integer, primary_key=True)
    delegation_id  = db.Column(db.Integer, db.ForeignKey('delegations.id'),
                               nullable=False, index=True)
    committee      = db.Column(db.String(30), index=True)
    log_type       = db.Column(db.String(30), nullable=False, index=True)
    # speech | motion_proposed | motion_seconded | motion_activated |
    # vote_cast | amendment_proposed | amendment_decided | resolution_created | resolution_voted
    duration_sec   = db.Column(db.Integer, default=0)
    topic          = db.Column(db.String(300))
    reference_id   = db.Column(db.Integer)  # ID da moção/voto/resolução referenciado
    reference_type = db.Column(db.String(30))  # motion | vote | resolution | amendment
    details        = db.Column(db.Text)  # JSON extra
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    delegation = db.relationship('Delegation', backref='activity_logs')

    def to_dict(self):
        d = self.delegation
        return {
            'id':            self.id,
            'delegation_id': self.delegation_id,
            'country':       d.country if d else '?',
            'flag':          d.country_flag if d else '',
            'flag_url':      d.flag_url if d else '',
            'committee':     self.committee,
            'log_type':      self.log_type,
            'duration_sec':  self.duration_sec,
            'topic':         self.topic or '',
            'reference_id':  self.reference_id,
            'reference_type': self.reference_type,
            'details':       self.details or '',
            'created_at':    self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def log(delegation_id, committee, log_type, **kwargs):
        entry = SpeechLog(
            delegation_id=delegation_id,
            committee=committee,
            log_type=log_type,
            duration_sec=kwargs.get('duration_sec', 0),
            topic=kwargs.get('topic', ''),
            reference_id=kwargs.get('reference_id'),
            reference_type=kwargs.get('reference_type'),
            details=kwargs.get('details', ''),
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def committee_stats(committee):
        logs = SpeechLog.query.filter_by(committee=committee).all()

        speeches = [l for l in logs if l.log_type == 'speech']
        motions = [l for l in logs if l.log_type.startswith('motion_')]
        votes = [l for l in logs if l.log_type == 'vote_cast']
        amendments = [l for l in logs if l.log_type.startswith('amendment_')]

        total_speech_time = sum(l.duration_sec for l in speeches)

        delegation_activity = {}
        for l in logs:
            did = l.delegation_id
            if did not in delegation_activity:
                delegation_activity[did] = {
                    'delegation_id': did,
                    'country': l.delegation.country if l.delegation else '?',
                    'flag': l.delegation.country_flag if l.delegation else '',
                    'flag_url': l.delegation.flag_url if l.delegation else '',
                    'speeches': 0,
                    'total_time': 0,
                    'motions': 0,
                    'votes': 0,
                    'amendments': 0,
                }
            if l.log_type == 'speech':
                delegation_activity[did]['speeches'] += 1
                delegation_activity[did]['total_time'] += l.duration_sec
            elif l.log_type.startswith('motion_'):
                delegation_activity[did]['motions'] += 1
            elif l.log_type == 'vote_cast':
                delegation_activity[did]['votes'] += 1
            elif l.log_type.startswith('amendment_'):
                delegation_activity[did]['amendments'] += 1

        return {
            'total_speeches': len(speeches),
            'total_speech_time': total_speech_time,
            'total_motions': len(motions),
            'total_votes': len(votes),
            'total_amendments': len(amendments),
            'delegations': sorted(delegation_activity.values(),
                                  key=lambda x: x['total_time'], reverse=True),
        }

    @staticmethod
    def delegation_stats(delegation_id):
        logs = SpeechLog.query.filter_by(delegation_id=delegation_id).all()
        speeches = [l for l in logs if l.log_type == 'speech']
        return {
            'total_speeches': len(speeches),
            'total_time': sum(l.duration_sec for l in speeches),
            'motions_proposed': sum(1 for l in logs if l.log_type == 'motion_proposed'),
            'votes_cast': sum(1 for l in logs if l.log_type == 'vote_cast'),
            'amendments': sum(1 for l in logs if l.log_type.startswith('amendment_')),
        }

    @staticmethod
    def timeline(committee=None, limit=50):
        q = SpeechLog.query
        if committee and committee != 'all':
            q = q.filter_by(committee=committee)
        return q.order_by(SpeechLog.created_at.desc()).limit(limit).all()
