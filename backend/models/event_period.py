# =============================================================
#  SWDL — models/event_period.py
# =============================================================
from extensions import db


class EventPeriod(db.Model):
    __tablename__ = 'event_periods'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date   = db.Column(db.String(20), nullable=False)
    order      = db.Column(db.Integer, default=0)
    color      = db.Column(db.String(20), default='navy')

    items = db.relationship('AgendaItem', backref='period', lazy='dynamic')

    __table_args__ = (
        db.Index('ix_period_dates', 'start_date', 'end_date'),
    )

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'start_date': self.start_date,
            'end_date':   self.end_date,
            'order':      self.order,
            'color':      self.color,
        }
