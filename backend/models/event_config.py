from extensions import db

class EventConfig(db.Model):
    __tablename__ = 'event_config'

    id                 = db.Column(db.Integer, primary_key=True)
    phase              = db.Column(db.String(10), nullable=False, default='pre')
    inscricoes_abertas = db.Column(db.Boolean, default=False)
    invoke_url         = db.Column(db.String(500), default='')
    invoke_active      = db.Column(db.Boolean, default=False)
    invoke_label       = db.Column(db.String(100), default='')
    invoke_at          = db.Column(db.DateTime, nullable=True)

    @classmethod
    def _ensure(cls):
        cfg = cls.query.first()
        if not cfg:
            cfg = cls(phase='pre', inscricoes_abertas=False)
            db.session.add(cfg)
            db.session.commit()
        return cfg

    @classmethod
    def get_phase(cls):
        return cls._ensure().phase

    @classmethod
    def set_phase(cls, phase):
        cfg = cls._ensure()
        cfg.phase = phase
        db.session.commit()

    @classmethod
    def get_inscricoes_abertas(cls):
        return cls._ensure().inscricoes_abertas

    @classmethod
    def set_inscricoes_abertas(cls, value):
        cfg = cls._ensure()
        cfg.inscricoes_abertas = value
        db.session.commit()

    @classmethod
    def get_invoke(cls):
        cfg = cls._ensure()
        if cfg.invoke_active and cfg.invoke_url:
            return {
                'url': cfg.invoke_url,
                'label': cfg.invoke_label or cfg.invoke_url,
                'at': cfg.invoke_at,
            }
        return None

    @classmethod
    def set_invoke(cls, url, label=''):
        from datetime import datetime
        cfg = cls._ensure()
        cfg.invoke_url = url
        cfg.invoke_label = label
        cfg.invoke_active = True
        cfg.invoke_at = datetime.utcnow()
        db.session.commit()

    @classmethod
    def clear_invoke(cls):
        cfg = cls._ensure()
        cfg.invoke_url = ''
        cfg.invoke_label = ''
        cfg.invoke_active = False
        cfg.invoke_at = None
        db.session.commit()
