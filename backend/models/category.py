from extensions import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'categories'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(80), nullable=False, unique=True)
    slug       = db.Column(db.String(80), unique=True, nullable=False)
    icon       = db.Column(db.String(20), default='')      # emoji
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    news = db.relationship('News', backref='category_obj', lazy='select')

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'slug':       self.slug,
            'icon':       self.icon or '',
            'sort_order': self.sort_order,
        }

    def __repr__(self):
        return f'<Category {self.id}: {self.name}>'
