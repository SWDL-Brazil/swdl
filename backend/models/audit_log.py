from extensions import db
from datetime import datetime


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id             = db.Column(db.Integer, primary_key=True)
    action         = db.Column(db.String(50), nullable=False)
    target_type    = db.Column(db.String(50), nullable=False)
    target_id      = db.Column(db.Integer, nullable=True)
    target_name    = db.Column(db.String(200), default='')
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_name      = db.Column(db.String(120), default='')
    details        = db.Column(db.Text, default='')
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.target_type}#{self.target_id}>'