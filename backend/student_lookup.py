"""Diagnostico (e reparo opcional) de alunos sumidos do painel.

Uso:
    python student_lookup.py                     # relatorio dos 3 nomes do chamado
    python student_lookup.py --names "Fulano de Tal"
    python student_lookup.py --apply             # recria o Student que faltar
    python student_lookup.py --apply --dry-run   # mostra o que faria

Roda contra o banco configurado em DATABASE_URL (producao no Render) ou, sem
ela, contra o backend/swdl.db local. Nada e escrito sem --apply.

Por que existe: a aba Alunos lista `Student.query.all()` sem filtro, entao um
aluno ausente dali nao tem linha em `students`. Ele pode continuar existindo em
`users` / `inscriptions` / `inscription_members` / `participation_history` — o
que permite recriar o vinculo sem redigitar nada.
"""
from __future__ import annotations

import argparse
import os
import sys
import unicodedata

DEFAULT_NAMES = (
    'Guilherme Santiago Pereira',
    'Gabrielly Viana Munhoz',
    'Isaac Lauro de Moura',
)

STOPWORDS = {'de', 'da', 'do', 'das', 'dos', 'e'}


def _norm(text):
    """Minusculo, sem acento e sem espacos duplicados (para comparar nomes)."""
    if not text:
        return ''
    text = unicodedata.normalize('NFKD', str(text))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return ' '.join(text.lower().split())


def _tokens(name):
    return [t for t in _norm(name).split() if t not in STOPWORDS and len(t) > 2]


def _levenshtein(a, b):
    if a == b:
        return 0
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _same_token(a, b):
    """Igual, ou parecido o bastante para tolerar erro de digitacao
    (Isac/Isaac, Viana/Vianna...)."""
    if a == b:
        return True
    if min(len(a), len(b)) < 4:
        return False
    limit = 2 if min(len(a), len(b)) >= 7 else 1
    return _levenshtein(a, b) <= limit


def _match_score(person_tokens, candidate_name):
    """Quantos tokens do nome procurado aparecem no candidato."""
    c = _norm(candidate_name)
    if not c:
        return 0
    words = c.split()
    score = 0
    for token in person_tokens:
        if token in c:
            score += 1
        elif any(_same_token(token, word) for word in words):
            score += 1
    return score


def _row_dict(obj, fields):
    return {f: getattr(obj, f, None) for f in fields}


def _print_rows(title, rows, fields):
    if not rows:
        return
    print(f'    {title}: {len(rows)}')
    for row in rows:
        parts = []
        for f in fields:
            val = getattr(row, f, None)
            if val is None or val == '':
                continue
            parts.append(f'{f}={val}')
        print(f'      - id={getattr(row, "id", "?")} | ' + ' | '.join(parts))


def collect_matches(name, models):
    """Devolve {tabela: [linhas]} com candidatos encontrados para o nome."""
    tokens = _tokens(name)
    found = {}

    def scan(model, fields):
        try:
            rows = model.query.all()
        except Exception as exc:  # tabela ausente no banco
            print(f'    (aviso) {model.__tablename__}: {exc}')
            return []
        hits = []
        for row in rows:
            for f in fields:
                value = getattr(row, f, None)
                if value and _match_score(tokens, value) >= max(2, len(tokens) - 1):
                    hits.append(row)
                    break
        return hits

    found['students'] = scan(models['Student'], ('name', 'email'))
    found['users'] = scan(models['User'], ('name', 'email'))
    found['inscriptions'] = scan(models['Inscription'], ('name', 'email'))
    found['inscription_members'] = scan(models['InscriptionMember'], ('name', 'email'))
    found['certificates'] = scan(models['Certificate'], ('name', 'email', 'student_name'))
    found['participation_history'] = []
    for student in found['students']:
        try:
            found['participation_history'].extend(
                models['ParticipationHistory'].query.filter_by(student_id=student.id).all()
            )
        except Exception:
            pass
    return found


def _ensure_models(app):
    import importlib
    names = [
        ('models.student', 'Student'),
        ('models.user', 'User'),
        ('models.inscription', 'Inscription'),
        ('models.inscription_member', 'InscriptionMember'),
        ('models.delegation', 'Delegation'),
        ('models.certificate', 'Certificate'),
        ('models.participation', 'ParticipationHistory'),
    ]
    models = {}
    for module_name, cls_name in names:
        try:
            module = importlib.import_module(module_name)
            models[cls_name] = getattr(module, cls_name)
        except Exception as exc:
            print(f'    (aviso) {module_name}.{cls_name} indisponivel: {exc}')
    return models


def restore_student(app, models, name, matches, dry_run=False):
    """Cria o Student que falta usando User/Inscription ja existentes."""
    from extensions import db
    from datetime import datetime, timezone

    Student = models['Student']
    User = models['User']
    Inscription = models['Inscription']
    Delegation = models.get('Delegation')

    email = None
    ins = None
    user = None

    # 1) O e-mail mais confiavel: inscricao aprovada que casa com o nome.
    for cand in matches['inscriptions']:
        if cand.status == 'approved':
            ins = cand
            email = cand.email
            break
    if not email:
        for cand in matches['inscriptions']:
            ins = cand
            email = cand.email
            break
    if not email:
        for cand in matches['users']:
            user = cand
            email = cand.email
            break

    if not email:
        print('    !! nenhum e-mail encontrado em inscricoes/users — '
              'cadastre pelo painel (Alunos > Novo Aluno).')
        return False

    if not user:
        user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
    if not ins:
        ins = Inscription.query.filter(
            db.func.lower(Inscription.email) == email.lower()
        ).order_by(Inscription.id.desc()).first()

    deleg = None
    if Delegation is not None:
        if ins:
            deleg = Delegation.query.filter_by(inscription_id=ins.id).first()
        if not deleg and user:
            deleg = Delegation.query.filter_by(user_id=user.id).first()

    print(f'    email={email} | user_id={getattr(user, "id", None)} | '
          f'inscription_id={getattr(ins, "id", None)} | '
          f'delegation_id={getattr(deleg, "id", None)}'
          + (f' ({deleg.country_flag} {deleg.country})' if deleg else ''))

    if dry_run:
        print('    (dry-run) criaria Student' + (' + User' if not user else '')
              + (' + ParticipationHistory' if deleg else ''))
        return True

    if not user:
        first = _norm(name).split()[0].capitalize() if _norm(name) else 'Delegado'
        password = f'{first}@2026'
        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        print(f'    + User criado (senha {password})')

    student = Student(user_id=user.id, name=name, email=email,
                      delegation_id=deleg.id if deleg else None)
    db.session.add(student)
    db.session.flush()

    if deleg and deleg.user_id is None:
        deleg.user_id = user.id

    if deleg:
        from routes.admin._helpers import _ensure_participation_history
        _ensure_participation_history(student)
        print(f'    + ParticipationHistory ({datetime.now(timezone.utc).year})')

    db.session.commit()
    print(f'    OK: Student id={student.id} criado'
          + (f' na delegacao {deleg.id}' if deleg else ' (sem delegacao)'))
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--names', default='|'.join(DEFAULT_NAMES),
                        help='nomes separados por |')
    parser.add_argument('--apply', action='store_true', help='recria o que faltar')
    parser.add_argument('--dry-run', action='store_true', help='nao grava nada')
    args = parser.parse_args()

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)

    # A config exige SECRET_KEY mesmo em leitura; nao precisa ser a de producao.
    os.environ.setdefault('SECRET_KEY', 'student-lookup-local')

    from app import create_app
    app = create_app()
    models = _ensure_models(app)

    print(f'DB: {app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1]}')
    print()

    names = [n.strip() for n in args.names.split('|') if n.strip()]
    with app.app_context():
        try:
            print(f'Alunos na tabela students: {models["Student"].query.count()}')
            print()
        except Exception as exc:
            print(f'(aviso) contagem de students falhou: {exc}')
        missing = []
        for name in names:
            print('=' * 70)
            print(f'>>> {name}')
            matches = collect_matches(name, models)
            _print_rows('students', matches['students'],
                        ('name', 'email', 'delegation_id', 'global_id'))
            _print_rows('users', matches['users'], ('name', 'email', 'role', 'is_active'))
            _print_rows('inscriptions', matches['inscriptions'],
                        ('name', 'email', 'status', 'type', 'formato', 'submitted_at'))
            _print_rows('inscription_members', matches['inscription_members'],
                        ('inscription_id', 'name', 'email'))
            _print_rows('participation_history', matches['participation_history'],
                        ('year', 'country', 'committee', 'role'))
            _print_rows('certificates', matches['certificates'],
                        ('year', 'type', 'name', 'email', 'student_id', 'released_at'))

            if matches['students']:
                st = matches['students'][0]
                print(f'    >>> JA EXISTE em students (id={st.id}, '
                      f'delegation_id={st.delegation_id}) — nada a fazer.')
                continue

            if not any(matches[k] for k in
                       ('users', 'inscriptions', 'inscription_members')):
                print('    >>> NAO encontrado em nenhuma tabela de origem.')
                print('        (precisa de cadastro manual: Alunos > Novo Aluno)')
                missing.append(name)
                continue

            if args.apply:
                ok = restore_student(app, models, name, matches,
                                     dry_run=args.dry_run)
                if not ok:
                    missing.append(name)
            else:
                print('    >>> sem Student. Rode com --apply (ou --apply --dry-run).')
        print('=' * 70)
        if missing:
            print('Sem dados de origem (cadastro manual necessario):')
            for name in missing:
                print(f'  - {name}')


if __name__ == '__main__':
    main()
