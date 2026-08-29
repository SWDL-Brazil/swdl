# =============================================================
#  SWDL — models/delegation.py
# =============================================================
from extensions import db
from datetime import datetime, timezone


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
    members         = db.Column(db.Text)

    accepted        = db.Column(db.Boolean, default=False)
    dpo_uploaded    = db.Column(db.Boolean, default=False, index=True)
    dpo_path        = db.Column(db.String(300))

    presence_status = db.Column(db.String(20), default='ausente', index=True)

    orador          = db.Column(db.Boolean, default=False, index=True)

    theme_id        = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True, index=True)
    theme           = db.relationship('Theme', backref=db.backref('delegations', lazy=True))

    flag_animation  = db.Column(db.Boolean, default=True)

    assigned_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    edition_year    = db.Column(db.Integer, default=lambda: datetime.now(timezone.utc).year, index=True)

    def _extra_members(self):
        """Nomes extras além dos alunos vinculados (membros sem conta)."""
        extras = []
        if self.members:
            extras = [m.strip() for m in self.members.split(',') if m.strip()]
        if not extras and self.pair_name:
            extras.append(self.pair_name.strip())
        return extras

    def member_names(self):
        """Lista de todos os membros (candidato da inscrição + alunos vinculados + extras)."""
        names = [s.name for s in self.students] if self.students else []
        if self.inscription and self.inscription.name not in names:
            names.insert(0, self.inscription.name)
        names.extend(self._extra_members())
        return names

    def member_count(self):
        return len(self.member_names())

    def group_label(self):
        """Formato derivado da quantidade de membros."""
        n = self.member_count()
        if n <= 1:
            return 'Individual'
        if n == 2:
            return 'Dupla'
        if n == 3:
            return 'Trio'
        return 'Grupo'

    def __repr__(self):
        return f'<Delegation {self.country} @ {self.committee}>'