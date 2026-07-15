# =============================================================
#  SWDL — models/delegation.py
# =============================================================
from extensions import db
from datetime import datetime


class Delegation(db.Model):
    __tablename__ = 'delegations'

    id              = db.Column(db.Integer, primary_key=True)
    inscription_id  = db.Column(db.Integer, db.ForeignKey('inscriptions.id'))
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'))

    country         = db.Column(db.String(80))
    country_flag    = db.Column(db.String(10))    # emoji fallback
    flag_url        = db.Column(db.String(300))   # URL da bandeira (restcountries)
    committee       = db.Column(db.String(30))
    pair_name       = db.Column(db.String(120))

    # Status de preparação
    accepted        = db.Column(db.Boolean, default=False)
    dpo_uploaded    = db.Column(db.Boolean, default=False)
    dpo_path        = db.Column(db.String(300))

    # Chamada / Presença: 'ausente', 'presente', 'votante'
    presence_status = db.Column(db.String(20), default='ausente')

    # Lista de Oradores
    orador = db.Column(db.Boolean, default=False)

    theme_id        = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True)
    theme           = db.relationship('Theme', backref=db.backref('delegations', lazy=True))

    # Preferências do delegado
    flag_animation  = db.Column(db.Boolean, default=True)  # animação ativada?

    assigned_at     = db.Column(db.DateTime, default=datetime.utcnow)
    edition_year    = db.Column(db.Integer, default=lambda: datetime.utcnow().year)

    def __repr__(self):
        return f'<Delegation {self.country} @ {self.committee}>'