from extensions import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    file_path   = db.Column(db.String(500), nullable=False)
    category    = db.Column(db.String(50), default='guias')
    theme_id    = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    theme = db.relationship('Theme', backref='documents', lazy=True)

    def filename(self):
        return self.file_path.split('\\')[-1].split('/')[-1] if self.file_path else ''

    def __repr__(self):
        return f'<Document {self.title}>'
