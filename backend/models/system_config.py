from extensions import db

class SystemConfig(db.Model):
    __tablename__ = 'system_config'

    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @classmethod
    def get(cls, key, default=None):
        # Cache de processo: cada query custa ~180ms em produção (Fase 0).
        # Na primeira leitura carrega TODAS as chaves em 1 query e popula
        # o cache — a página de notificações lê ~8 chaves por request.
        from perf_cache import cache_get, cache_set
        ck = 'syscfg:' + key
        cached = cache_get(ck, ttl=30.0)
        if cached is None:
            if cache_get('syscfg:_all', ttl=30.0) is None:
                for e in cls.query.all():
                    cache_set('syscfg:' + e.key, (True, e.value), ttl=30.0)
                cache_set('syscfg:_all', True, ttl=30.0)
            cached = cache_get(ck, ttl=30.0) or (False, None)
            cache_set(ck, cached, ttl=30.0)
        found, value = cached
        return value if found else default

    @classmethod
    def set(cls, key, value):
        from perf_cache import cache_clear
        entry = cls.query.filter_by(key=key).first()
        if entry:
            entry.value = value
        else:
            entry = cls(key=key, value=value)
            db.session.add(entry)
        db.session.commit()
        cache_clear('syscfg:')

    @classmethod
    def get_bool(cls, key, default=False):
        val = cls.get(key, str(default))
        return val and val.lower() in ('1', 'true', 'yes', 'on')

    def __repr__(self):
        return f'<SystemConfig {self.key}>'
