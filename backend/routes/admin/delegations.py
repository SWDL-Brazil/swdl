from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import (admin_bp, admin_required,
                                   _ensure_participation_history,
                                   _cleanup_orphan_delegation,
                                   _country_taken)
from models.delegation import Delegation
from models.inscription import Inscription
from models.user import User
from models.student import Student
from models.theme import Theme
from models.event_config import EventConfig
from extensions import db
import re
from datetime import datetime, timezone


@admin_bp.route('/delegacoes')
@login_required
@admin_required
def delegations_list():
    from sqlalchemy.orm import joinedload
    delegations = Delegation.query.options(
        joinedload(Delegation.inscription),
        joinedload(Delegation.students),
        joinedload(Delegation.theme),
    ).all()
    return render_template('admin/delegations_list.html',
                           delegations=delegations,
                           inscricoes_abertas=EventConfig.get_inscricoes_abertas())


@admin_bp.route('/delegacoes/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def delegation_create():
    """Cria uma nova delegacao do zero (tema, pais, alunos)."""
    from models.theme import Theme
    from models.student import Student
    from models.inscription import Inscription
    from models.user import User
    import re

    if request.method == 'POST':
        theme_id = request.form.get('theme_id', type=int)
        country  = request.form.get('country', '').strip()
        flag     = request.form.get('flag', '').strip()
        flag_url = request.form.get('flag_url', '').strip()
        committee_name = request.form.get('committee_name', '').strip()
        student_ids = request.form.getlist('student_ids', type=int)

        if not country:
            flash('O pais e obrigatorio.', 'error')
            return redirect(url_for('admin.delegation_create'))

        if not student_ids:
            flash('Selecione pelo menos um aluno.', 'error')
            return redirect(url_for('admin.delegation_create'))

        theme = Theme.query.get(theme_id) if theme_id else None

        if _country_taken(country, theme, committee=committee_name):
            flash(f'⚠️ {country} já foi designado neste tema/comitê. '
                  f'Escolha outro país.', 'error')
            return redirect(url_for('admin.delegation_create'))

        # Cria Inscription para cada aluno, mas usa a primeira como principal
        first_student = Student.query.get(student_ids[0])
        if not first_student:
            flash('Aluno nao encontrado.', 'error')
            return redirect(url_for('admin.delegation_create'))

        ins = Inscription.query.filter_by(email=first_student.email, status='approved').first()
        if not ins:
            ins = Inscription(
                name=first_student.name,
                email=first_student.email,
                phone='',
                grade='',
                motivation='',
                interests='',
                type='delegate',
                status='approved',
                reviewed_at=datetime.now(timezone.utc),
            )
            db.session.add(ins)
            db.session.flush()

        pair_name = request.form.get('pair_name', '').strip()
        members   = request.form.get('members', '').strip()

        deleg = Delegation(
            inscription_id=ins.id,
            edition_year=datetime.now(timezone.utc).year,
            theme_id=theme.id if theme else None,
            country=country,
            country_flag=flag,
            flag_url=flag_url,
            committee=committee_name or (theme.name if theme else ''),
            pair_name=pair_name,
            members=members,
        )
        db.session.add(deleg)
        db.session.flush()

        # Vincula todos os alunos selecionados a esta delegacao
        for sid in student_ids:
            student = Student.query.get(sid)
            if student:
                student.delegation_id = deleg.id
                student.convened = True
                # Garante ParticipationHistory
                _ensure_participation_history(student)

                # Checa se ja tem User; se nao, cria
                if not student.user_id:
                    existing = User.query.filter_by(email=student.email).first()
                    if not existing:
                        import secrets, string
                        alphabet = string.ascii_letters + string.digits
                        password = ''.join(secrets.choice(alphabet) for _ in range(10))
                        user = User(name=student.name, email=student.email, role='student')
                        user.set_password(password)
                        db.session.add(user)
                        db.session.flush()
                        student.user_id = user.id
                    else:
                        student.user_id = existing.id

        # Vincula a delegacao ao usuario do aluno principal (para login/votacao)
        if not deleg.user_id and first_student.user_id:
            deleg.user_id = first_student.user_id

        db.session.commit()
        flash(f'🌍 Delegacao {country} criada com {len(student_ids)} aluno(s)!', 'success')
        return redirect(url_for('admin.delegations_list'))

    themes = Theme.query.all()
    # Alunos que ainda nao tem delegacao
    unassigned = Student.query.filter(Student.delegation_id.is_(None)).order_by(Student.name).all()
    return render_template('admin/delegation_create.html',
                           themes=themes,
                           unassigned_students=unassigned,
                           all_students=Student.query.order_by(Student.name).all())


@admin_bp.route('/delegacoes/<int:id>/designar', methods=['GET', 'POST'])
@login_required
@admin_required
def delegation_assign(id):
    from models.theme import Theme
    from models.student import Student
    deleg = Delegation.query.get_or_404(id)
    if request.method == 'POST':
        country = request.form.get('country', '').strip()
        if not country:
            flash('O país é obrigatório.', 'error')
            return redirect(url_for('admin.delegation_assign', id=id))

        theme_id = request.form.get('theme_id', type=int)
        theme = Theme.query.get(theme_id) if theme_id else None

        if _country_taken(country, theme, exclude_id=deleg.id):
            flash(f'⚠️ {country} já foi designado neste tema/comitê. '
                  f'Escolha outro país.', 'error')
            return redirect(url_for('admin.delegation_assign', id=id))

        committee_name = request.form.get('committee_name', '').strip()
        prev_theme_id  = deleg.theme_id
        prev_committee = deleg.committee or ''

        deleg.theme_id    = theme.id if theme else None
        deleg.country      = country
        deleg.country_flag = request.form.get('flag', '')
        deleg.flag_url     = request.form.get('flag_url', '').strip()
        if committee_name:
            deleg.committee = committee_name
        elif theme and (theme.id != prev_theme_id or not prev_committee):
            deleg.committee = theme.name
        elif not theme:
            prev_theme = db.session.get(Theme, prev_theme_id) if prev_theme_id else None
            if not prev_theme or prev_committee == prev_theme.name:
                deleg.committee = ''
        deleg.members      = request.form.get('members', '').strip()
        deleg.flag_animation = bool(request.form.get('flag_animation'))

        # Convoca todos os alunos da delegacao e sincroniza o historico
        for student in deleg.students:
            if not student.convened:
                student.convened = True
            if not deleg.user_id and student.user_id:
                deleg.user_id = student.user_id
            _ensure_participation_history(student)

        db.session.commit()
        flash(f'Pais {deleg.country} designado com sucesso!', 'success')
        return redirect(url_for('admin.delegations_list'))
    available_themes = Theme.query.all()
    return render_template('admin/delegation_assign.html', deleg=deleg,
                           available_themes=available_themes,
                           all_students=Student.query.order_by(Student.name).all())


@admin_bp.route('/delegacoes/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def delegation_delete(id):
    from models.vote import Vote
    deleg = Delegation.query.get_or_404(id)

    # 1. Deleta votos
    Vote.query.filter_by(delegation_id=deleg.id).delete()

    user_to_delete = None
    if deleg.user_id:
        user_to_delete = User.query.get(deleg.user_id)

    ins_to_delete = None
    if deleg.inscription_id:
        ins_to_delete = Inscription.query.get(deleg.inscription_id)

    # 2. Desvincula students da delegacao (limpa FK antes de deletar)
    students_to_delete = list(deleg.students) if deleg.students else []
    for s in students_to_delete:
        s.delegation_id = None

    db.session.flush()

    # 3. Deleta students (ParticipationHistory cascade)
    for s in students_to_delete:
        db.session.delete(s)

    # 4. Deleta delegacao
    db.session.delete(deleg)

    # 5. Deleta user (sem mais student referenciando)
    if user_to_delete:
        db.session.delete(user_to_delete)

    # 6. Deleta inscricao
    if ins_to_delete:
        db.session.delete(ins_to_delete)

    db.session.commit()
    flash('Delegacao e login deletados com sucesso.', 'success')
    return redirect(url_for('admin.delegations_list'))


@admin_bp.route('/delegacoes/<int:id>/credenciais', methods=['POST'])
@login_required
@admin_required
def delegation_create_credentials(id):
    """Cria login para o delegado acessar o portal."""
    from models.user import User
    deleg = Delegation.query.get_or_404(id)

    if not deleg.inscription:
        flash('Delegacao sem inscricao vinculada.', 'error')
        return redirect(url_for('admin.delegations_list'))

    ins = deleg.inscription

    # Verifica se ja tem conta (independente de role)
    existing = User.query.filter_by(email=ins.email).first()
    if existing:
        flash(f'Delegado {ins.name} ja possui credenciais.', 'info')
        return redirect(url_for('admin.delegations_list'))

    # Gera senha aleatoria forte
    import secrets, string
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(10))

    user = User(name=ins.name, email=ins.email, role='student')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # garante o user.id

    deleg.user_id = user.id

    # Vincula o perfil de aluno (se houver) ao novo login.
    # NOTA: Todos os students da delegacao compartilham o mesmo User
    # (login compartilhado para votacao). Criacao de contas individuais
    # e feita em delegation_create ou delegate_create.
    from models.student import Student
    for s in deleg.students:
        if s and not s.user_id:
            s.user_id = user.id

    db.session.commit()

    flash(
        f'Credenciais criadas para {ins.name} → '
        f'Login: {ins.email} | Senha: {password}',
        'success'
    )
    return redirect(url_for('admin.delegations_list'))


@admin_bp.route('/delegacoes/<int:id>/membros-contas', methods=['POST'])
@login_required
@admin_required
def delegation_members_accounts(id):
    """Cria login + perfil de aluno para membros da delegacao sem conta.

    Cobre o caso de quem aparece em member_names() (candidato da inscricao,
    extra_members ou nome digitado no campo 'membros') mas nao tem Student —
    sem isso a pessoa nao aparece em /alunos e nao da para resetar a senha.
    Idempotente: membros ja com conta sao pulados.
    """
    import unicodedata
    from sqlalchemy.orm import joinedload, selectinload
    from models.inscription_member import InscriptionMember

    deleg = Delegation.query.options(
        joinedload(Delegation.inscription).selectinload(Inscription.extra_members),
        joinedload(Delegation.students),
    ).filter(Delegation.id == id).first_or_404()

    def _norm(s):
        return ' '.join((s or '').strip().lower().split())

    # Participantes com e-mail: inscricao principal + extras
    participants = []  # (name, email)
    seen_emails = set()

    def _add(name, email):
        name = (name or '').strip()
        email = (email or '').strip().lower()
        if not name or not email or email in seen_emails:
            return
        seen_emails.add(email)
        participants.append((name, email))

    if deleg.inscription:
        _add(deleg.inscription.name, deleg.inscription.email)
        for m in deleg.inscription.extra_members:
            _add(m.name, m.email)

    # Nomes digitados no campo 'membros' que casem com inscricao aprovada
    student_names = {_norm(s.name) for s in (deleg.students or [])}
    for raw in deleg._extra_members():
        if _norm(raw) in student_names:
            continue
        ins2 = Inscription.query.filter(
            db.func.lower(Inscription.name) == _norm(raw),
            Inscription.status == 'approved',
        ).first()
        if ins2:
            _add(ins2.name, ins2.email)

    created, updated, skipped = [], [], []
    for name, email in participants:
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user and user.role == 'admin':
            skipped.append(f'{name} (e-mail é de um admin)')
            continue
        password = None
        if not user:
            first = unicodedata.normalize('NFKD', name.split()[0])\
                .encode('ascii', 'ignore').decode('ascii').capitalize()
            password = f'{first}@2026' if first else 'Delegado@2026'
            user = User(name=name, email=email, role='student')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

        student = Student.query.filter(db.func.lower(Student.email) == email).first()
        if not student:
            student = Student(user_id=user.id, name=name, email=email)
            db.session.add(student)
            db.session.flush()
            created.append(f'{name} <{email}> — Senha: {password or "(conta já existia)"}')
        else:
            if not student.user_id:
                student.user_id = user.id
            if password:
                created.append(f'{name} <{email}> — Senha: {password}')
            else:
                updated.append(name)

        student.delegation_id = deleg.id
        student.convened = True
        _ensure_participation_history(student)

    if deleg.inscription and not deleg.user_id:
        main = User.query.filter(
            db.func.lower(User.email) == deleg.inscription.email.strip().lower()
        ).first()
        if main and main.role != 'admin':
            deleg.user_id = main.id

    db.session.commit()

    if not created and not updated:
        flash('✅ Todos os membros desta delegação já possuem conta.', 'info')
    else:
        parts = []
        if created:
            parts.append('Contas criadas — ' + ' · '.join(created))
        if updated:
            parts.append('Já vinculados — ' + ', '.join(updated))
        if skipped:
            parts.append('Pulados — ' + ', '.join(skipped))
        flash('👥 ' + ' | '.join(parts), 'success')
    return redirect(url_for('admin.delegations_list'))


@admin_bp.route('/config/inscricoes/toggle', methods=['POST'])
@login_required
@admin_required
def inscricoes_toggle():
    """Abre/fecha inscricoes de delegados."""
    current = EventConfig.get_inscricoes_abertas()
    EventConfig.set_inscricoes_abertas(not current)
    status = 'abertas' if not current else 'fechadas'
    flash(f'📋 Inscricoes de delegados {status}!', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))
