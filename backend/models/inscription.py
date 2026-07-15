# =============================================================
#  SWDL — models/inscription.py
# =============================================================
from extensions import db
from datetime import datetime


class Inscription(db.Model):
    __tablename__ = 'inscriptions'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), nullable=False, index=True)
    phone         = db.Column(db.String(30))
    school        = db.Column(db.String(120))
    grade         = db.Column(db.String(30))
    partner_name  = db.Column(db.String(120))
    motivation    = db.Column(db.Text)
    interests     = db.Column(db.String(300))
    status        = db.Column(db.String(20), default='pending', index=True)
    type          = db.Column(db.String(20), default='delegate')
    submitted_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reviewed_at   = db.Column(db.DateTime)
    reviewed_by   = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Se aprovado, gera uma delegação
    delegation    = db.relationship('Delegation', backref='inscription', uselist=False)

    def __repr__(self):
        return f'<Inscription {self.name} [{self.status}]>'