from extensions import db
from datetime import datetime


class ParticipationHistory(db.Model):
    __tablename__ = 'participation_history'

    id                = db.Column(db.Integer, primary_key=True)
    student_id        = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    year              = db.Column(db.Integer, nullable=False)
    committee         = db.Column(db.String(30))
    committee_name    = db.Column(db.String(120))
    country           = db.Column(db.String(80))
    country_flag      = db.Column(db.String(10))
    flag_url          = db.Column(db.String(300))
    role              = db.Column(db.String(30), default='delegate')
    delegation_name   = db.Column(db.String(120))

    details           = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'committee': self.committee,
            'committee_name': self.committee_name,
            'country': self.country,
            'country_flag': self.country_flag,
            'flag_url': self.flag_url,
            'role': self.role,
            'delegation_name': self.delegation_name,
        }

    def __repr__(self):
        return f'<ParticipationHistory {self.year} - {self.country} @ {self.committee}>'
