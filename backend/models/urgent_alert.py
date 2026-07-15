from extensions import db
from datetime import datetime


class UrgentAlert(db.Model):
    __tablename__ = 'urgent_alerts'

    id         = db.Column(db.Integer, primary_key=True)
    message    = db.Column(db.String(300), nullable=False)
    active     = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {
            'id':      self.id,
            'message': self.message,
            'active':  self.active,
        }

    def __repr__(self):
        return f'<UrgentAlert {self.id}: {self.message[:40]}>'
