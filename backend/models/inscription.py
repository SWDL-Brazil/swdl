# =============================================================
#  SWDL — models/inscription.py
# =============================================================
from extensions import db
from datetime import datetime, timezone


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
    submitted_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    reviewed_at   = db.Column(db.DateTime)
    reviewed_by   = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Campos novos — inscrição em grupo
    instagram     = db.Column(db.String(100))
    formato       = db.Column(db.String(20), default='individual')  # individual / dupla / trio

    # Se aprovado, gera uma delegação
    delegation    = db.relationship('Delegation', backref='inscription', uselist=False)

    # Membros adicionais (dupla/trio)
    extra_members = db.relationship('InscriptionMember', backref='inscription',
                                    cascade='all, delete-orphan', lazy=True)

    def member_count(self):
        """Número total de participantes (inscrito + membros extras)."""
        return 1 + len(self.extra_members)

    def __repr__(self):
        return f'<Inscription {self.name} [{self.status}]>'