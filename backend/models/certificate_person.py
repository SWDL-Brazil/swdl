from extensions import db
from datetime import datetime, timezone


PERSON_KINDS = {
    'external': 'SWDL com Portas Abertas',
    'organizer': 'Organizador',
}

# Ocupacoes do organizador (lista fixa — vai no certificado/relatorio)
PERSON_OCCUPATIONS = [
    'Diretor(a)',
    'Mesa diretora',
    'Staff',
    'Assessoria',
    'Secretariado',
    'RH',
    'Mídias',
    'Imprensa',
    'Outro',
]


class CertificatePerson(db.Model):
    """Pessoa sem cadastro de aluno que recebe certificado.

    Serve de "agenda" para externos (SWDL com Portas Abertas) e membros da
    organizacao: cadastra-se uma vez e depois basta escolher na hora de
    gerar o certificado, sem digitar nome/e-mail de novo.

    Formulario enxuto por tipo:
      * organizador -> nome, e-mail, tema/comite e ocupacao (lista fixa)
      * externo     -> nome, e-mail, instituicao, edicao e tema assistido
    """
    __tablename__ = 'certificate_people'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(120), nullable=False, index=True)
    email          = db.Column(db.String(120), nullable=True)
    kind           = db.Column(db.String(20), nullable=False, default='external',
                               index=True)  # external | organizer
    committee      = db.Column(db.String(300), nullable=True)
    committee_name = db.Column(db.String(120), nullable=True)
    country        = db.Column(db.String(80), nullable=True)
    country_flag   = db.Column(db.String(10), nullable=True)
    notes          = db.Column(db.Text, nullable=True)
    # Organizador: cargo/funcao (Diretor, Mesa diretora, Staff, ...)
    occupation     = db.Column(db.String(60), nullable=True)
    # Portas Abertas: de onde veio (escola/instituicao)
    institution    = db.Column(db.String(120), nullable=True)
    # Portas Abertas: edicao em que assistiu
    edition_year   = db.Column(db.Integer, nullable=True, index=True)
    created_at     = db.Column(db.DateTime,
                               default=lambda: datetime.now(timezone.utc))
    updated_at     = db.Column(db.DateTime,
                               default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))

    certificates = db.relationship('Certificate', backref='person', lazy=True)

    @property
    def kind_label(self):
        return PERSON_KINDS.get(self.kind, self.kind)

    @property
    def theme_label(self):
        if self.committee_name and self.committee:
            return f'{self.committee_name} ({self.committee})'
        return self.committee_name or self.committee or '---'

    @property
    def detail_label(self):
        """Coluna unica na lista: ocupacao (organizador) ou instituicao."""
        if self.kind == 'organizer':
            return self.occupation or '---'
        return self.institution or '---'

    def fill_certificate(self, cert):
        """Copia os dados da pessoa para o certificado (nome/snapshot)."""
        cert.name = self.name
        cert.email = self.email
        cert.fill_snapshot(
            name=self.name,
            country=self.country,
            country_flag=self.country_flag,
            committee=self.committee,
            committee_name=self.committee_name,
        )
        return cert

    def __repr__(self):
        return f'<CertificatePerson {self.name} [{self.kind}]>'
