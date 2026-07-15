from extensions import db

class SystemConfig(db.Model):
    __tablename__ = 'system_config'

    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @classmethod
    def get(cls, key, default=None):
        entry = cls.query.filter_by(key=key).first()
        return entry.value if entry else default

    @classmethod
    def set(cls, key, value):
        entry = cls.query.filter_by(key=key).first()
        if entry:
            entry.value = value
        else:
            entry = cls(key=key, value=value)
            db.session.add(entry)
        db.session.commit()

    @classmethod
    def get_bool(cls, key, default=False):
        val = cls.get(key, str(default))
        return val and val.lower() in ('1', 'true', 'yes', 'on')

    def __repr__(self):
        return f'<SystemConfig {self.key}>'
