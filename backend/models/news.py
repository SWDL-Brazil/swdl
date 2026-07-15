# =============================================================
#  SWDL — models/news.py
# =============================================================
from extensions import db
from datetime import datetime
import re, unicodedata


def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:80]


class News(db.Model):
    __tablename__ = 'news'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(240), nullable=False)
    slug        = db.Column(db.String(100), unique=True)
    excerpt     = db.Column(db.String(300))          # resumo para o card
    body        = db.Column(db.Text, nullable=False)  # HTML rico (Quill)
    cover_image = db.Column(db.String(300))           # URL da imagem de capa
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    committee   = db.Column(db.String(30), default='geral')
    tags        = db.Column(db.String(300), default='')    # "diplomacia,cs,resolucao"
    is_crisis   = db.Column(db.Boolean, default=False)
    published   = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)
    author_id   = db.Column(db.Integer, db.ForeignKey('users.id'))
    author      = db.relationship('User', backref='news')

    def save(self):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            i = 1
            while News.query.filter_by(slug=slug).filter(News.id != self.id).first():
                slug = f'{base}-{i}'; i += 1
            self.slug = slug
        db.session.add(self)
        db.session.commit()

    def time_ago(self):
        delta = datetime.utcnow() - self.created_at
        s = int(delta.total_seconds())
        if s < 60:    return 'agora mesmo'
        if s < 3600:  return f'há {s//60} min'
        if s < 86400: return f'há {s//3600}h'
        return self.created_at.strftime('%d/%m/%Y')

    def tags_list(self):
        return [t.strip() for t in (self.tags or '').split(',') if t.strip()]

    def to_dict(self):
        return {
            'id':          self.id,
            'title':       self.title,
            'slug':        self.slug,
            'excerpt':     self.excerpt or '',
            'cover_image': self.cover_image or '',
            'category':    self.category_obj.name if self.category_obj else 'geral',
            'category_slug': self.category_obj.slug if self.category_obj else 'geral',
            'category_icon': self.category_obj.icon if self.category_obj else '',
            'committee':   self.committee,
            'tags':        self.tags_list(),
            'is_crisis':   self.is_crisis,
            'published':   self.published,
            'time_ago':    self.time_ago(),
            'created_at':  self.created_at.strftime('%d/%m/%Y'),
            'author':      self.author.name if self.author else 'SWDL',
        }

    def __repr__(self):
        return f'<News {self.id}: {self.title[:40]}>'