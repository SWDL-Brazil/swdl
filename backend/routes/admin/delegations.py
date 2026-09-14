from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required, _ensure_participation_history, _cleanup_orphan_delegation
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
                           delegations=delegations)


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
        theme_id = request.form.get('theme_id', type=int)
        theme = Theme.query.get(theme_id) if theme_id else None
        deleg.theme_id    = theme.id if theme else None
        deleg.country      = request.form.get('country', '').strip()
        deleg.country_flag = request.form.get('flag', '')
        deleg.flag_url     = request.form.get('flag_url', '').strip()
        deleg.committee    = theme.name if theme else ''
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


@admin_bp.route('/config/inscricoes/toggle', methods=['POST'])
@login_required
@admin_required
def inscricoes_toggle():
    """Abre/fecha inscricoes de delegados."""
    current = EventConfig.get_inscricoes_abertas()
    EventConfig.set_inscricoes_abertas(not current)
    status = 'abertas' if not current else 'fechadas'
    flash(f'📋 Inscricoes de delegados {status}!', 'success')
    return redirect(url_for('admin.dashboard'))
