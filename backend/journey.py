# ── JORNADA DO ALUNO ───────────────────────────────────────────
# Estado dos passos exibidos no card "Sua Jornada" do dashboard.
# Função pura (sem Flask/DB) — testada em test_journey.py.

def build_journey(delegation, event_started, event_ended, cert_released):
    """Monta a lista de passos da jornada do aluno.

    delegation      — objeto Delegation (ou None); usa .country/.dpo_uploaded
    event_started   — fase 'during' ou 'post'
    event_ended     — fase 'post'
    cert_released   — student.certificate_released

    Cada passo: {key, label, state, status, icon, endpoint, line_done}
      state    — 'done' | 'current' | 'warn' | 'locked'
      endpoint — nome de rota Flask para o passo ser clicável (ou None)
      line_done— a linha ANTERIOR ao passo fica verde quando o passo
                 anterior está 'done' (nunca "cedo", como no template antigo
                 em que a linha do DPO ficava verde justamente com o DPO
                 pendente via prep_warn).
    """
    designated = bool(delegation and getattr(delegation, 'country', None))
    dpo_ok = designated and bool(getattr(delegation, 'dpo_uploaded', False))
    prep_warn = designated and event_started and not dpo_ok
    sim_now = designated and event_started and not event_ended
    sim_done = designated and event_ended

    if dpo_ok:
        prep_status, prep_icon = 'DPO Enviado', 'check'
    elif prep_warn:
        prep_status, prep_icon = 'DPO pendente', 'alert-triangle'
    elif designated:
        prep_status, prep_icon = 'Aguardando DPO', 'clock'
    else:
        prep_status, prep_icon = 'Bloqueada', 'lock'

    if sim_done:
        sim_status, sim_icon = 'Concluído', 'check'
    elif sim_now:
        sim_status, sim_icon = 'Ao Vivo', 'radio'
    else:
        sim_status, sim_icon = 'Bloqueada', 'lock'

    if sim_done and cert_released:
        pos_status, pos_icon = 'Certificado Emitido', 'check'
    elif sim_done:
        pos_status, pos_icon = 'Certificado pendente', 'clock'
    else:
        pos_status, pos_icon = 'Bloqueada', 'lock'

    steps = [
        dict(key='cadastro', label='Cadastro', state='done',
             status='Concluído', icon='check', endpoint=None),
        dict(key='designacao', label='Designação',
             state='done' if designated else 'current',
             status='Concluído' if designated else 'Aguardando',
             icon='check' if designated else 'clock',
             endpoint=None),
        dict(key='preparacao', label='Preparação',
             state=('done' if dpo_ok else
                    'warn' if prep_warn else
                    'current' if designated else 'locked'),
             status=prep_status, icon=prep_icon,
             endpoint='student.profile' if designated else None),
        dict(key='simulacao', label='Simulação',
             state='done' if sim_done else ('current' if sim_now else 'locked'),
             status=sim_status, icon=sim_icon,
             endpoint='student.attendance' if sim_now else None),
        dict(key='pos_evento', label='Pós-Evento',
             state='done' if sim_done and cert_released else
                   ('current' if sim_done else 'locked'),
             status=pos_status, icon=pos_icon,
             endpoint='student.certificados' if sim_done else None),
    ]

    prev_done = False
    for s in steps:
        s['line_done'] = prev_done
        prev_done = s['state'] == 'done'
    return steps
