# =============================================================
#  SWDL — models/vote.py
# =============================================================
from extensions import db
from datetime import datetime


class VoteSession(db.Model):
    __tablename__ = 'vote_sessions'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(240), nullable=False)
    description  = db.Column(db.Text)
    committee    = db.Column(db.String(30), default='geral')
    status       = db.Column(db.String(20), default='open')  # open | closed
    duration_sec = db.Column(db.Integer, default=120)        # cronômetro em segundos
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at    = db.Column(db.DateTime)
    created_by   = db.Column(db.Integer, db.ForeignKey('users.id'))

    votes = db.relationship('Vote', backref='session', lazy=True,
                            cascade='all, delete-orphan')

    def count(self):
        favor     = sum(1 for v in self.votes if v.choice == 'favor')
        contra    = sum(1 for v in self.votes if v.choice == 'contra')
        abstencao = sum(1 for v in self.votes if v.choice == 'abstencao')
        return {'favor': favor, 'contra': contra, 'abstencao': abstencao,
                'total': len(self.votes)}

    def vote_details(self):
        """Retorna lista de votos com dados da delegação."""
        from models.delegation import Delegation
        details = []
        for v in self.votes:
            d = Delegation.query.get(v.delegation_id)
            details.append({
                'choice':    v.choice,
                'country':   d.country   if d else '?',
                'flag':      d.country_flag if d else '',
                'flag_url':  d.flag_url  if d else '',
                'voted_at':  v.voted_at.isoformat(),
            })
        return details

    def to_dict(self):
        c = self.count()
        return {
            'id':           self.id,
            'title':        self.title,
            'description':  self.description,
            'committee':    self.committee,
            'status':       self.status,
            'duration_sec': self.duration_sec,
            'counts':       c,
            'votes':        self.vote_details(),
            'created_at':   self.created_at.isoformat(),
        }


class Vote(db.Model):
    __tablename__ = 'votes'

    id             = db.Column(db.Integer, primary_key=True)
    session_id     = db.Column(db.Integer, db.ForeignKey('vote_sessions.id'),
                               nullable=False)
    delegation_id  = db.Column(db.Integer, db.ForeignKey('delegations.id'),
                               nullable=False)
    choice         = db.Column(db.String(20), nullable=False)
    voted_at       = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'delegation_id', name='one_vote_per_session'),
    )

    def to_dict(self):
        return {
            'id':            self.id,
            'session_id':    self.session_id,
            'delegation_id': self.delegation_id,
            'choice':        self.choice,
            'voted_at':      self.voted_at.isoformat(),
        }