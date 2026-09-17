# =============================================================
#  SWDL — models/inscription_member.py
#  Membros adicionais de uma inscrição (dupla/trio)
# =============================================================
from extensions import db
from datetime import datetime, timezone


class InscriptionMember(db.Model):
    __tablename__ = 'inscription_members'

    id              = db.Column(db.Integer, primary_key=True)
    inscription_id  = db.Column(db.Integer, db.ForeignKey('inscriptions.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    name            = db.Column(db.String(120), nullable=False)
    email           = db.Column(db.String(120), nullable=False)
    grade           = db.Column(db.String(30))
    instagram       = db.Column(db.String(100))
    phone           = db.Column(db.String(30))
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<InscriptionMember {self.name} ({self.email})>'
