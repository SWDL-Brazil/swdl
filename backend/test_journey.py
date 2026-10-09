"""Teste da lógica da jornada do aluno (backend/journey.py).

Cobre: estados por fase (sem designação, designado sem DPO, durante o
evento, pós-evento com/sem certificado), linhas que só ficam verdes quando
o passo ANTERIOR conclui, e endpoints dos passos clicáveis.

Uso: python test_journey.py
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from journey import build_journey  # noqa: E402

FAILURES = []
COUNT = 0


def check(name, cond, extra=''):
    global COUNT
    COUNT += 1
    status = 'OK ' if cond else 'FAIL'
    print(f'[{status}] {name}' + (f'  {extra}' if extra and not cond else ''))
    if not cond:
        FAILURES.append(name)


def steps_by_key(delegation, started, ended, cert):
    return {s['key']: s for s in build_journey(delegation, started, ended, cert)}


def states(d, started, ended, cert):
    return {k: s['state'] for k, s in steps_by_key(d, started, ended, cert).items()}


def main():
    deleg = SimpleNamespace(country='Brasil', dpo_uploaded=False)
    deleg_ok = SimpleNamespace(country='Brasil', dpo_uploaded=True)
    other = SimpleNamespace(country=None, dpo_uploaded=False)

    # ── 1. Sem designação ────────────────────────────────────
    st = states(None, False, False, False)
    check('sem delegação: cadastro done', st['cadastro'] == 'done')
    check('sem delegação: designação current (aguardando)',
          st['designacao'] == 'current')
    check('sem delegação: preparação locked', st['preparacao'] == 'locked')
    check('sem delegação: simulação locked', st['simulacao'] == 'locked')
    check('sem delegação: pós-evento locked', st['pos_evento'] == 'locked')

    st = states(other, True, False, False)
    check('designação em branco não destrava nada', st['preparacao'] == 'locked'
          and st['simulacao'] == 'locked')

    # ── 2. Designado, antes do evento, sem DPO ───────────────
    st = states(deleg, False, False, False)
    check('designado: designação done', st['designacao'] == 'done')
    check('designado s/ DPO antes do evento: preparação current',
          st['preparacao'] == 'current')
    check('designado antes do evento: simulação locked', st['simulacao'] == 'locked')

    # ── 3. Designado, durante o evento, DPO pendente ─────────
    steps = build_journey(deleg, True, False, False)
    st = {s['key']: s for s in steps}
    check('durante evento s/ DPO: preparação warn',
          st['preparacao']['state'] == 'warn')
    check('durante evento s/ DPO: linha até simulação NÃO verde (bug antigo)',
          st['simulacao']['line_done'] is False)
    check('durante evento s/ DPO: simulação current (Ao Vivo)',
          st['simulacao']['state'] == 'current'
          and st['simulacao']['status'] == 'Ao Vivo')

    # ── 4. Designado, durante o evento, DPO enviado ──────────
    steps = build_journey(deleg_ok, True, False, False)
    st = {s['key']: s for s in steps}
    check('durante evento c/ DPO: preparação done', st['preparacao']['state'] == 'done')
    check('durante evento c/ DPO: linha até simulação verde',
          st['simulacao']['line_done'] is True)
    check('durante evento c/ DPO: pós-evento locked',
          st['pos_evento']['state'] == 'locked')

    # ── 5. Pós-evento ────────────────────────────────────────
    s = steps_by_key(deleg_ok, False, True, False)
    check('pós-evento s/ certificado: pós current (pendente)',
          s['pos_evento']['state'] == 'current'
          and s['pos_evento']['status'] == 'Certificado pendente')
    check('pós-evento: simulação done', s['simulacao']['state'] == 'done')

    s = steps_by_key(deleg_ok, False, True, True)
    check('pós-evento c/ certificado: done', s['pos_evento']['state'] == 'done')

    # ── 6. Linhas: só verdes com o passo anterior done ───────
    steps = build_journey(deleg, True, False, False)   # DPO pendente, evento rolando
    lines = [(s['key'], s['line_done']) for s in steps]
    check('linhas: primeira sem linha (line_done False)',
          lines[0] == ('cadastro', False))
    check('linhas: designação verdes (cadastro done)',
          dict(lines)['designacao'] is True)
    check('linhas: preparação verdes (designação done)',
          dict(lines)['preparacao'] is True)
    check('linhas: pós-evento cinza (simulação não concluída)',
          dict(lines)['pos_evento'] is False)

    # ── 7. Passos clicáveis (endpoints) ──────────────────────
    s = steps_by_key(deleg, False, False, False)
    check('preparação clicável → perfil (upload de DPO)',
          s['preparacao']['endpoint'] == 'student.profile')
    check('simulação sem link antes do evento', s['simulacao']['endpoint'] is None)
    check('cadastro/designação sem link', s['cadastro']['endpoint'] is None
          and s['designacao']['endpoint'] is None)

    s = steps_by_key(deleg_ok, True, False, False)
    check('simulação durante evento → presença',
          s['simulacao']['endpoint'] == 'student.attendance')

    s = steps_by_key(deleg_ok, False, True, True)
    check('pós-evento → certificados', s['pos_evento']['endpoint'] == 'student.certificados')
    check('simulação pós-evento sem link (read-only)',
          s['simulacao']['endpoint'] is None)

    s = steps_by_key(None, True, False, False)
    check('sem designação: nenhum link em preparação/simulação/pós',
          s['preparacao']['endpoint'] is None and s['simulacao']['endpoint'] is None
          and s['pos_evento']['endpoint'] is None)

    # ── 8. Ordem e completude ────────────────────────────────
    order = [x['key'] for x in build_journey(None, False, False, False)]
    check('5 passos na ordem canônica',
          order == ['cadastro', 'designacao', 'preparacao', 'simulacao', 'pos_evento'])

    print()
    if FAILURES:
        print(f'FALHOU: {len(FAILURES)} checagem(s): {FAILURES}', file=sys.stderr)
        return 1
    print(f'OK: todas as {COUNT} checagens passaram.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
