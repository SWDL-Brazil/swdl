from extensions import db
from datetime import datetime, timezone
import uuid, hmac, hashlib, secrets, string


def generate_verification_code():
    """Gera codigo curto no formato SWDL-XXXXXX (6 chars alfanumericos)."""
    alphabet = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(alphabet) for _ in range(6))
    return f'SWDL-{code}'


class Student(db.Model):
    __tablename__ = 'students'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    global_id      = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name           = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)

    delegation_id  = db.Column(db.Integer, db.ForeignKey('delegations.id'), nullable=True, index=True)

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

    def _signature_parts(self):
        deleg = self.delegation
        return [
            self.global_id,
            self.name,
            deleg.country if deleg else '',
            deleg.committee if deleg else '',
            self.verification_code or self.certificate_hash or '',
        ]

    def compute_signature(self, secret):
        raw = '::'.join(self._signature_parts())
        return hmac.new(
            secret.encode('utf-8'),
            raw.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()

    def verify_signature(self, secret):
        if not self.digital_signature:
            return False
        expected = self.compute_signature(secret)
        return hmac.compare_digest(self.digital_signature, expected)

    def to_dict(self):
        return {
            'id': self.id,
            'global_id': self.global_id,
            'name': self.name,
            'email': self.email,
            'has_delegation': self.delegation_id is not None,
            'verification_code': self.verification_code,
            'certificate_released': self.certificate_released,
            'digital_signature': bool(self.digital_signature),
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'read_only': self.read_only,
            'adapted_device': self.adapted_device,
        }

    def __repr__(self):
        return f'<Student {self.name} [{self.global_id[:8]}]>'
