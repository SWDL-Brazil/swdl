"""Estado da tela ativa no telao — para restaurar apos F5/reboot.

Os botoes "Exibir no Telao" dos painéis admin gravam aqui qual tela foi
solicitada (feature + args). GET /api/telao/estado reconstrói o payload na
hora da leitura (sempre dados frescos) e o telão reaplica quando o `ts`
muda — assim uma recarga do navegador do projetor volta a exibir a tela
certa sem depender de novo clique do admin.
"""
import json
from datetime import datetime, timezone

KEY = 'telao_state'


def set_telao_state(feature, args=None):
    """Grava a tela ativa. feature=None limpa (tela oculta)."""
    from models.system_config import SystemConfig
    if not feature:
        SystemConfig.set(KEY, None)
        return
    data = {
        'feature': feature,
        'args': args or {},
        'ts': datetime.now(timezone.utc).isoformat(),
    }
    SystemConfig.set(KEY, json.dumps(data))


def get_telao_state():
    """Retorna {'feature','args','ts'} ou None."""
    from models.system_config import SystemConfig
    raw = SystemConfig.get(KEY)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict) or not data.get('feature'):
        return None
    return data


def build_telao_display(state):
    """Reconstrói o payload da tela indicada, com dados atuais do banco."""
    from flask import current_app
    from extensions import db
    if not state:
        return None
    feature = state.get('feature')
    args = state.get('args') or {}
    committee = args.get('committee', 'all')
    builders = {
        'chamada': _build_chamada,
        'oradores': _build_oradores,
        'speaker_queue': _build_speaker_queue,
        'motion': _build_motion,
        'resolution': _build_resolution,
    }
    builder = builders.get(feature)
    if not builder:
        return None
    try:
        payload = builder(committee)
    except Exception:
        current_app.logger.error('[TELAO] falha ao montar display %s', feature,
                                 exc_info=True)
        db.session.rollback()
        return None
    return {
        'feature': feature,
        'args': args,
        'ts': state.get('ts'),
        'payload': payload,
    }


def _delegation_row(d, status=None):
    row = {
        'id':        d.id,
        'country':   d.country or '?',
        'flag':      d.country_flag or '',
        'flag_url':  d.flag_url or '',
        'committee': d.committee or '',
    }
    if status is not None:
        row['status'] = status
    return row


def _build_chamada(committee):
    from models.delegation import Delegation
    q = Delegation.query
    if committee != 'all':
        q = q.filter_by(committee=committee)
    delegations = q.order_by(Delegation.country).all()
    return {
        'committee': committee,
        'delegations': [
            _delegation_row(d, d.presence_status or 'ausente')
            for d in delegations
        ],
    }


def _build_oradores(committee):
    from models.delegation import Delegation
    q = Delegation.query.filter(Delegation.orador == True)  # noqa: E712
    if committee != 'all':
        q = q.filter_by(committee=committee)
    oradores = q.order_by(Delegation.country).all()
    return {
        'committee': committee,
        'oradores': [_delegation_row(d) for d in oradores],
    }


def _build_speaker_queue(committee):
    from models.speaker import SpeakerEntry
    c = committee if committee != 'all' else None
    queue = SpeakerEntry.current_queue(c)
    active = SpeakerEntry.active_speaker(c)
    return {
        'committee': committee,
        'queue': [e.to_dict() for e in queue],
        'active': active.to_dict() if active else None,
    }


def _build_motion(committee):
    from models.motion import Motion
    c = committee if committee != 'all' else None
    pending = Motion.pending_for_committee(c)
    active = Motion.active_for_committee(c)
    return {
        'committee': committee,
        'pending': [m.to_dict() for m in pending],
        'active': active.to_dict() if active else None,
    }


def _build_resolution(committee):
    from models.resolution import Resolution
    q_active = Resolution.query.filter_by(status='voting')
    q_submitted = Resolution.query.filter_by(status='submitted')
    if committee and committee != 'all':
        q_active = q_active.filter_by(committee=committee)
        q_submitted = q_submitted.filter_by(committee=committee)
    active = q_active.first()
    submitted = q_submitted.order_by(Resolution.submitted_at.desc()).all()
    return {
        'committee': committee,
        'active': active.to_dict() if active else None,
        'submitted': [r.to_dict() for r in submitted[:5]],
    }
