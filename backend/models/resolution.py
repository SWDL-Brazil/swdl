# =============================================================
#  SWDL — models/resolution.py
#  Resoluções com cláusulas, emendas e votação por artigo
# =============================================================
from extensions import db
from datetime import datetime, timezone


class Resolution(db.Model):
    __tablename__ = 'resolutions'

    id              = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(200), nullable=False)
    committee       = db.Column(db.String(30), nullable=False, index=True)
    preambulatory   = db.Column(db.Text, default='')
    operative       = db.Column(db.Text, default='')
    proposer_id     = db.Column(db.Integer, db.ForeignKey('delegations.id'),
                                nullable=False, index=True)
    co_sponsors     = db.Column(db.Text, default='')  # CSV de delegation IDs
    status          = db.Column(db.String(20), default='draft', index=True)
    # draft | submitted | voting | passed | rejected
    vote_session_id = db.Column(db.Integer, db.ForeignKey('vote_sessions.id'), nullable=True)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at    = db.Column(db.DateTime)
    voted_at        = db.Column(db.DateTime)

    proposer     = db.relationship('Delegation', backref='resolutions_proposed')
    vote_session = db.relationship('VoteSession', backref='resolution', uselist=False)
    amendments   = db.relationship('Amendment', backref='resolution',
                                   lazy=True, cascade='all, delete-orphan',
                                   order_by='Amendment.created_at')

    def co_sponsor_ids(self):
        if not self.co_sponsors:
            return []
        return [int(x.strip()) for x in self.co_sponsors.split(',') if x.strip()]

    def add_co_sponsor(self, delegation_id):
        ids = self.co_sponsor_ids()
        if delegation_id not in ids:
            ids.append(delegation_id)
            self.co_sponsors = ','.join(str(i) for i in ids)

    def remove_co_sponsor(self, delegation_id):
        ids = self.co_sponsor_ids()
        if delegation_id in ids:
            ids.remove(delegation_id)
            self.co_sponsors = ','.join(str(i) for i in ids)

    def preambulatory_clauses(self):
        return [c.strip() for c in self.preambulatory.split('\n') if c.strip()]

    def operative_clauses(self):
        return [c.strip() for c in self.operative.split('\n') if c.strip()]

    def pending_amendments(self):
        return [a for a in self.amendments if a.status == 'pending']

    def to_dict(self):
        p = self.proposer
        return {
            'id':              self.id,
            'title':           self.title,
            'committee':       self.committee,
            'preambulatory':   self.preambulatory,
            'operative':       self.operative,
            'proposer_id':     self.proposer_id,
            'proposer_country': p.country if p else '?',
            'proposer_flag':   p.country_flag if p else '',
            'proposer_flag_url': p.flag_url if p else '',
            'co_sponsors':     self.co_sponsors,
            'co_sponsor_ids':  self.co_sponsor_ids(),
            'status':          self.status,
            'vote_session_id': self.vote_session_id,
            'amendments_count': len(self.amendments),
            'pending_amendments': len(self.pending_amendments()),
            'created_at':      self.created_at.isoformat() if self.created_at else None,
            'submitted_at':    self.submitted_at.isoformat() if self.submitted_at else None,
            'voted_at':        self.voted_at.isoformat() if self.voted_at else None,
        }

    @staticmethod
    def for_committee(committee, status=None):
        q = Resolution.query.filter_by(committee=committee)
        if status:
            q = q.filter_by(status=status)
        return q.order_by(Resolution.created_at.desc()).all()


class Amendment(db.Model):
    __tablename__ = 'amendments'

    id              = db.Column(db.Integer, primary_key=True)
    resolution_id   = db.Column(db.Integer, db.ForeignKey('resolutions.id'),
                                nullable=False, index=True)
    proposer_id     = db.Column(db.Integer, db.ForeignKey('delegations.id'),
                                nullable=False)
    amendment_type  = db.Column(db.String(20), default='friendly')
    # friendly | unfriendly
    target_section  = db.Column(db.String(20), nullable=False)
    # preambulatory | operative
    target_index    = db.Column(db.Integer, default=0)
    original_text   = db.Column(db.Text, default='')
    proposed_text   = db.Column(db.Text, default='')
    status          = db.Column(db.String(20), default='pending', index=True)
    # pending | accepted | rejected
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    decided_at      = db.Column(db.DateTime)

    proposer = db.relationship('Delegation', backref='amendments_proposed')

    def to_dict(self):
        p = self.proposer
        return {
            'id':             self.id,
            'resolution_id':  self.resolution_id,
            'proposer_id':    self.proposer_id,
            'proposer_country': p.country if p else '?',
            'proposer_flag':  p.country_flag if p else '',
            'amendment_type': self.amendment_type,
            'target_section': self.target_section,
            'target_index':   self.target_index,
            'original_text':  self.original_text,
            'proposed_text':  self.proposed_text,
            'status':         self.status,
            'created_at':     self.created_at.isoformat() if self.created_at else None,
            'decided_at':     self.decided_at.isoformat() if self.decided_at else None,
        }
