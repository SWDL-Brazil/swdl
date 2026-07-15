# =============================================================
#  SWDL — models/delegation.py
# =============================================================
from extensions import db
from datetime import datetime


class Delegation(db.Model):
    __tablename__ = 'delegations'

    id              = db.Column(db.Integer, primary_key=True)
    inscription_id  = db.Column(db.Integer, db.ForeignKey('inscriptions.id'), index=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    country         = db.Column(db.String(80))
    country_flag    = db.Column(db.String(10))
    flag_url        = db.Column(db.String(300))
    committee       = db.Column(db.String(30), index=True)
    pair_name       = db.Column(db.String(120))

    accepted        = db.Column(db.Boolean, default=False)
    dpo_uploaded    = db.Column(db.Boolean, default=False, index=True)
    dpo_path        = db.Column(db.String(300))

    presence_status = db.Column(db.String(20), default='ausente', index=True)

    orador          = db.Column(db.Boolean, default=False, index=True)

    theme_id        = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True, index=True)
    theme           = db.relationship('Theme', backref=db.backref('delegations', lazy=True))

    flag_animation  = db.Column(db.Boolean, default=True)

    assigned_at     = db.Column(db.DateTime, default=datetime.utcnow)
    edition_year    = db.Column(db.Integer, default=lambda: datetime.utcnow().year, index=True)

    def __repr__(self):
        return f'<Delegation {self.country} @ {self.committee}>'