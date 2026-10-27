from extensions import db
from datetime import datetime, timezone
import hmac, hashlib, secrets, string


CERT_TYPES = {
    'participation':   'Participação',
    'best_delegation': 'Melhor Delegação',
    'best_speaker':    'Melhor Orador(a)',
    'best_dress':      'Melhor Vestimenta',
    'organizer':       'Organizador',
    'external':        'SWDL com Portas Abertas',
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

    Para certificados externos (Sem aluno vinculado), ``student_id`` e NULL e
    os dados ficam nos campos livres ``name``/``email`` do próprio registro.
    """
    __tablename__ = 'certificates'
    __table_args__ = (
        # Um certificado por aluno/edicao/tipo — dedupe no proprio banco.
        # student_id NULL (externos) permite multiplas linhas (NULLs sao
        # considerados distintos pelo SQL), entao nao bloqueia externos.
        db.Index('uq_cert_student_year_type', 'student_id', 'edition_year',
                 'type', unique=True),
    )

    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(db.Integer, db.ForeignKey('students.id'),
                               nullable=True, index=True)
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

    # Campos livres para certificados SEM aluno vinculado (externos / orgs).
    name           = db.Column(db.String(120), nullable=True)
    email          = db.Column(db.String(120), nullable=True)

    # ── SNAPSHOT (autocontido) ──────────────────────────────────────
    # Copiado do aluno/delegacao na emissao: o certificado nao depende de
    # JOIN com students/delegations, o que era emitido fica registrado
    # mesmo se o aluno for renomeado ou trocar de delegacao, e o HMAC
    # (que cobre esses campos) continua valido depois de editar o cadastro.
    student_name   = db.Column(db.String(120), nullable=True)
    global_id      = db.Column(db.String(36), nullable=True)
    country        = db.Column(db.String(80), nullable=True)
    country_flag   = db.Column(db.String(10), nullable=True)
    committee      = db.Column(db.String(300), nullable=True)
    committee_name = db.Column(db.String(120), nullable=True)

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

    @property
    def display_name(self):
        """Nome mostrado nas telas — snapshot, com fallback ao cadastro."""
        if self.student_name:
            return self.student_name
        if self.name:
            return self.name
        if self.student:
            return self.student.name
        return '---'

    def fill_snapshot(self, student=None, delegation=None, theme=None,
                      name=None, country=None, country_flag=None,
                      committee=None, committee_name=None):
        """Copia nome/pais/comitie para dentro do certificado.

        Aceita objetos (student/delegation/theme) OU valores diretos, para
        suportar certificados externos sem aluno vinculado. Chamado na
        geracao do codigo e de novo no upload (momento em que o certificado
        vira oficial) — assim o snapshot casa com o PDF assinado.
        """
        s = student or self.student
        deleg = delegation or (s.delegation if s else None)
        th = theme or (deleg.theme if deleg else None)

        self.student_name   = name or (s.name if s else None)
        self.global_id      = s.global_id if s else None
        self.email          = s.email if s else (self.email or None)
        self.country        = country or (deleg.country if deleg else None)
        self.country_flag   = country_flag or (deleg.country_flag if deleg else None)
        self.committee      = committee or (deleg.committee if deleg else None)
        self.committee_name = committee_name or (th.name if th else None)
        return self

    def _signature_parts(self):
        # Pelo snapshot, nao pelo cadastro: editar o aluno depois de emitido
        # nao pode invalidar a assinatura (nem trocar o que a pagina mostra).
        return [
            self.global_id or '',
            self.student_name or '',
            self.name or '',
            self.email or '',
            self.country or '',
            self.committee or '',
            self.committee_name or '',
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
