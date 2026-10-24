from extensions import db
from datetime import datetime, timezone
import uuid


class Student(db.Model):
    __tablename__ = 'students'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    global_id      = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name           = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)

    delegation_id  = db.Column(db.Integer, db.ForeignKey('delegations.id'), nullable=True, index=True)

    # ── LEGADO (pré-Certificate) — mantidos como backup; não escrever mais ──
    verification_code   = db.Column(db.String(12), unique=True, nullable=True, index=True)
    certificate_url     = db.Column(db.String(500))
    certificate_released = db.Column(db.Boolean, default=False, index=True)
    certificate_hash    = db.Column(db.String(128), unique=True)
    digital_signature = db.Column(db.Text, nullable=True)
    signed_at         = db.Column(db.DateTime, nullable=True)

    read_only       = db.Column(db.Boolean, default=False, index=True)
    adapted_device  = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    convened    = db.Column(db.Boolean, default=False, index=True)

    user       = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    delegation = db.relationship('Delegation', backref=db.backref('students', lazy=True))

    participations = db.relationship('ParticipationHistory', backref='student', lazy=True,
                                     cascade='all, delete-orphan',
                                     order_by='ParticipationHistory.year.desc()')

    def latest_released_certificate(self):
        """Certificado liberado mais recente (edicao desc, criado desc)."""
        released = [c for c in self.certificates if c.released]
        if not released:
            return None
        return max(released,
                   key=lambda c: (c.edition_year,
                                  c.created_at.timestamp() if c.created_at else 0))

    def to_dict(self):
        cert = self.latest_released_certificate()
        return {
            'id': self.id,
            'global_id': self.global_id,
            'name': self.name,
            'email': self.email,
            'has_delegation': self.delegation_id is not None,
            'verification_code': cert.verification_code if cert else None,
            'certificate_released': bool(cert),
            'digital_signature': bool(cert and cert.digital_signature),
            'signed_at': cert.signed_at.isoformat() if cert and cert.signed_at else None,
            'read_only': self.read_only,
            'adapted_device': self.adapted_device,
        }

    def __repr__(self):
        return f'<Student {self.name} [{self.global_id[:8]}]>'
