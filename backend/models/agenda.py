# =============================================================
#  SWDL — models/agenda.py
# =============================================================
from extensions import db
from datetime import datetime, date


class AgendaItem(db.Model):
    __tablename__ = 'agenda_items'

    id          = db.Column(db.Integer, primary_key=True)
    event_date  = db.Column(db.String(20), index=True)
    start_time  = db.Column(db.String(10), nullable=False)
    end_time    = db.Column(db.String(10))
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location    = db.Column(db.String(120))
    status      = db.Column(db.String(20), default='auto', index=True)
    committee   = db.Column(db.String(60))
    order       = db.Column(db.Integer, default=0, index=True)
    day         = db.Column(db.Integer, default=1, index=True)

    __table_args__ = (
        db.Index('ix_agenda_date_time', 'event_date', 'start_time'),
    )

    def compute_status(self):
        if self.status in ('break', 'crisis', 'vote', 'award'):
            return self.status
        today = date.today().isoformat()
        if self.event_date and self.event_date != today:
            return 'done' if self.event_date < today else 'next'
        now_str = datetime.now().strftime('%H:%M')
        start   = self.start_time or '00:00'
        end     = self.end_time   or '23:59'
        if now_str >= end:   return 'done'
        if now_str >= start: return 'now'
        return 'next'

    def to_dict(self, mode='auto'):
        today = date.today().isoformat()
        if mode == 'archive':
            status = self.status if self.status != 'auto' else 'archive'
        elif mode == 'live':
            status = self.compute_status()
        else:
            is_today = self.event_date and self.event_date == today
            is_past  = self.event_date and self.event_date < today
            if is_today: status = self.compute_status()
            elif is_past: status = 'done'
            else: status = self.compute_status()

        return {
            'id':          self.id,
            'event_date':  self.event_date or '',
            'day':         self.day,
            'start_time':  self.start_time,
            'end_time':    self.end_time or '',
            'title':       self.title,
            'description': self.description or '',
            'location':    self.location or '',
            'status':      status,
            'committee':   self.committee or '',
            'order':       self.order,
        }