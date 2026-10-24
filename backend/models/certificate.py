from extensions import db
from datetime import datetime, timezone
import hmac, hashlib, secrets, string


CERT_TYPES = {
    'participation':   'Participação',
    'best_delegation': 'Melhor Delegação',
    'best_speaker':    'Melhor Orador(a)',
    'best_dress':      'Melhor Vestimenta',
}


def generate_verification_code():
    """Gera codigo curto no formato SWDL-XXXXXX (6 chars alfanumericos)."""
    alphabet = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(alphabet) for _ in range(6))
    return f'SWDL-{code}'


class Certificate(db.Model):
    """Certificado escopado por edicao + tipo.

    Um aluno pode ter N certificados (um por edicao/tipo). O codigo de
    verificacao e unico globalmente (SWDL-XXXXXX).
    """
    __tablename__ = 'certificates'
    __table_args__ = (
        # Um certificado por aluno/edicao/tipo — dedupe no proprio banco,
        # nao so em Python (dois admins simultaneos criariam duplicata).
        db.Index('uq_cert_student_year_type', 'student_id', 'edition_year',
                 'type', unique=True),
    )

    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(db.Integer, db.ForeignKey('students.id'),
                               nullable=False, index=True)
    edition_year   = db.Column(db.Integer, nullable=False, index=True,
                               default=lambda: datetime.now(timezone.utc).year)
    type           = db.Column(db.String(30), nullable=False, index=True,
                               default='participation')
    title          = db.Column(db.String(120), nullable=True)
    verification_code = db.Column(db.String(12), unique=True, nullable=False, index=True)
    # PDF no BANCO (bytea/BLOB): o Render free nao tem disco persistente e o
    # FS some a cada deploy. pdf_path guarda so o nome original do upload.
    pdf_data       = db.Column(db.LargeBinary, nullable=True)
    pdf_path       = db.Column(db.String(300), nullable=True)
    released       = db.Column(db.Boolean, default=False, index=True)
    digital_signature = db.Column(db.Text, nullable=True)
    signed_at      = db.Column(db.DateTime, nullable=True)
    awarded_by     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime,
                               default=lambda: datetime.now(timezone.utc))

    student = db.relationship(
        'Student',
        backref=db.backref('certificates', lazy=True, cascade='all, delete-orphan'),
    )

    @property
    def type_label(self):
        return CERT_TYPES.get(self.type, self.type)

    @property
    def display_title(self):
        return self.title or self.type_label

    @property
    def has_pdf(self):
        """Tem PDF de verdade? (pdf_path so guarda o nome do arquivo)."""
        return bool(self.pdf_data)

    def _signature_parts(self):
        s = self.student
        deleg = s.delegation if s else None
        return [
            s.global_id if s else '',
            s.name if s else '',
            deleg.country if deleg else '',
            deleg.committee if deleg else '',
            self.type,
            str(self.edition_year),
            self.verification_code,
        ]

    def compute_signature(self, secret):
        raw = '::'.join(self._signature_parts())
        return hmac.new(secret.encode('utf-8'), raw.encode('utf-8'),
                        hashlib.sha256).hexdigest()

    def verify_signature(self, secret):
        if not self.digital_signature:
            return False
        return hmac.compare_digest(self.digital_signature,
                                   self.compute_signature(secret))

    def __repr__(self):
        return f'<Certificate {self.verification_code} {self.type} {self.edition_year}>'
