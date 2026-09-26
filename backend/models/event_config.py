from extensions import db

class EventConfig(db.Model):
    __tablename__ = 'event_config'

    id                 = db.Column(db.Integer, primary_key=True)
    inscricoes_abertas = db.Column(db.Boolean, default=False)
    invoke_url         = db.Column(db.String(500), default='')
    invoke_active      = db.Column(db.Boolean, default=False)
    invoke_label       = db.Column(db.String(100), default='')
    invoke_at          = db.Column(db.DateTime, nullable=True)
    phase_override     = db.Column(db.String(20), nullable=True, default=None)

    @classmethod
    def _ensure(cls):
        from flask import g
        if hasattr(g, '_event_config'):
            return g._event_config
        cfg = cls.query.first()
        if not cfg:
            cfg = cls(inscricoes_abertas=False)
            db.session.add(cfg)
            db.session.flush()
        g._event_config = cfg
        return cfg

    @classmethod
    def get_state(cls):
        """Estado completo (phase/invoke/inscrições) em 1 única query.

        Tabela de linha única lida em TODA tela do admin via context processor.
        Cache de processo: 1 query a cada TTL, 0 nas requests seguintes.
        """
        from perf_cache import cache_get, cache_set
        st = cache_get('event_config_state', ttl=60.0)
        if st is None:
            cfg = cls._ensure()
            st = {
                'phase_override': cfg.phase_override or '',
                'inscricoes_abertas': bool(cfg.inscricoes_abertas),
                'invoke': ({
                    'url': cfg.invoke_url,
                    'label': cfg.invoke_label or cfg.invoke_url,
                    'at': cfg.invoke_at,
                } if cfg.invoke_active and cfg.invoke_url else None),
            }
            cache_set('event_config_state', st, ttl=60.0)
        return st

    @classmethod
    def get_inscricoes_abertas(cls):
        return cls.get_state()['inscricoes_abertas']

    @classmethod
    def set_inscricoes_abertas(cls, value):
        from perf_cache import cache_clear
        cfg = cls._ensure()
        cfg.inscricoes_abertas = value
        db.session.commit()
        cache_clear('event_config_state')
        cache_clear('inscricoes_abertas')

    @classmethod
    def get_invoke(cls):
        return cls.get_state()['invoke']

    @classmethod
    def set_invoke(cls, url, label=''):
        from datetime import datetime, timezone
        from perf_cache import cache_clear
        cfg = cls._ensure()
        cfg.invoke_url = url
        cfg.invoke_label = label
        cfg.invoke_active = True
        cfg.invoke_at = datetime.now(timezone.utc)
        db.session.commit()
        cache_clear('event_config_state')
        cache_clear('active_invoke')

    @classmethod
    def clear_invoke(cls):
        from perf_cache import cache_clear
        cfg = cls._ensure()
        cfg.invoke_url = ''
        cfg.invoke_label = ''
        cfg.invoke_active = False
        cfg.invoke_at = None
        db.session.commit()
        cache_clear('event_config_state')
        cache_clear('active_invoke')

    @classmethod
    def get_phase_override(cls):
        return cls.get_state()['phase_override'] or None

    @classmethod
    def set_phase_override(cls, value):
        from perf_cache import cache_clear
        cfg = cls._ensure()
        cfg.phase_override = value
        db.session.commit()
        cache_clear('event_config_state')
        cache_clear('phase_override')
