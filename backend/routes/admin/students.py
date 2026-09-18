from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required, _ensure_participation_history, _cleanup_orphan_delegation
from models.user import User
from models.student import Student
from models.delegation import Delegation
from models.theme import Theme
from models.inscription import Inscription
from models.participation import ParticipationHistory
from extensions import db
import re
from datetime import datetime, timezone


@admin_bp.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def delegate_create():
    """Step 1: cria apenas a conta do aluno (name + email).
    A designação de país/tema/formato é feita depois em /alunos."""
    from models.system_config import SystemConfig
    from services.email_service import send_approval_email
    from services.whatsapp_service import send_approval_whatsapp

    error = None

    if request.method == 'POST':
        name  = request.form['name'].strip()
        email = request.form['email'].strip()

        if User.query.filter_by(email=email).first():
            error = f'Já existe um usuário com o e-mail {email}.'
        else:
            import secrets, string
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(10))

            ins = Inscription(
                name        = name,
                email       = email,
                phone       = request.form.get('phone', ''),
                type        = 'delegate',
                status      = 'approved',
                reviewed_at = datetime.now(timezone.utc),
                reviewed_by = current_user.id,
            )
            db.session.add(ins)

            user = User(name=name, email=email, role='student')
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id = user.id,
                name    = name,
                email   = email,
            )
            db.session.add(student)
            db.session.commit()

            notificacoes = []
            if SystemConfig.get('auto_email', '1') == '1':
                ok, msg = send_approval_email(SystemConfig.get, email, name, email, password)
                notificacoes.append(f'E-mail: {"✅" if ok else "❌"} {msg}')

            if SystemConfig.get('auto_whatsapp', '0') == '1' and ins.phone:
                ok, msg = send_approval_whatsapp(SystemConfig.get, ins.phone, name, email, password)
                notificacoes.append(f'WhatsApp: {"✅" if ok else "❌"} {msg}')

            msg_notif = ' | '.join(notificacoes) if notificacoes else ''
            flash(
                f'✅ Conta de aluno criada! '
                f'Login: {email} | Senha: {password} | '
                f'ID Global: {student.global_id[:12]}...'
                + (f'<br><small style="color:var(--muted)">{msg_notif}</small>' if msg_notif else ''),
                'success'
            )
            return redirect(url_for('admin.students_list'))

    return render_template('admin/delegate_create.html', error=error)


@admin_bp.route('/alunos')
@login_required
@admin_required
def students_list():
    """Lista todos os alunos cadastrados com status da designação."""
    from sqlalchemy.orm import joinedload
    students = Student.query.options(
        joinedload(Student.delegation)
    ).order_by(Student.created_at.desc()).all()
    return render_template('admin/students_list.html', students=students)


@admin_bp.route('/alunos/<int:id>/designar', methods=['GET', 'POST'])
@login_required
@admin_required
def student_assign(id):
    """Step 2: atribui país, tema e formato (individual, dupla, trio ou grupo) a um aluno existente."""
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        country  = request.form.get('country', '').strip()
        flag     = request.form.get('flag', '').strip()
        flag_url = request.form.get('flag_url', '').strip()
        theme_id = request.form.get('theme_id', type=int)
        members   = request.form.get('members', '').strip()

        if not country:
            flash('O país é obrigatório.', 'error')
            themes = Theme.query.order_by(Theme.name).all()
            joinable = Student.query.filter(Student.id != student.id).order_by(Student.name).all()
            return render_template('admin/student_assign.html', student=student,
                                   available_themes=themes,
                                   all_students=Student.query.order_by(Student.name).all(),
                                   joinable_students=joinable)

        extra_ids = request.form.getlist('extra_ids', type=int)
        deleg = student.delegation
        if not deleg and student.user_id:
            deleg = Delegation.query.filter_by(user_id=student.user_id).first()
        if not deleg:
            for i in extra_ids:
                s = Student.query.get(i)
                if s and s.delegation_id:
                    deleg = s.delegation
                    break
        if not deleg:
            ins = Inscription.query.filter_by(email=student.email, status='approved').first()
            if not ins:
                flash('Inscrição não encontrada para este aluno.', 'error')
                return redirect(url_for('admin.students_list'))

            deleg = Delegation(
                inscription_id=ins.id,
                user_id=student.user_id,
                edition_year=datetime.now(timezone.utc).year,
            )
            db.session.add(deleg)
            db.session.flush()
        else:
            deleg.edition_year = datetime.now(timezone.utc).year
            if not deleg.inscription_id:
                ins = Inscription.query.filter_by(email=student.email, status='approved').first()
                if ins:
                    deleg.inscription_id = ins.id
            if not deleg.user_id and student.user_id:
                deleg.user_id = student.user_id

        theme = Theme.query.get(theme_id) if theme_id else None
        deleg.theme_id    = theme.id if theme else None
        deleg.country      = country
        deleg.country_flag = flag
        deleg.flag_url     = flag_url
        deleg.committee    = theme.name if theme else ''
        deleg.members      = members
        deleg.flag_animation = bool(request.form.get('flag_animation'))
        db.session.flush()

        member_ids = [student.id] + [i for i in extra_ids if i != student.id]

        old_deleg_ids = set()
        for sid in member_ids:
            s = Student.query.get(sid)
            if s and s.delegation_id and s.delegation_id != deleg.id:
                old_deleg_ids.add(s.delegation_id)

        for sid in member_ids:
            s = Student.query.get(sid)
            if not s:
                continue
            s.delegation_id = deleg.id
            s.convened = True
            if not deleg.user_id and s.user_id:
                deleg.user_id = s.user_id
            _ensure_participation_history(s)
        for s in deleg.students:
            _ensure_participation_history(s)

        db.session.flush()

        for old_id in old_deleg_ids:
            _cleanup_orphan_delegation(old_id)

        db.session.commit()

        nomes = ', '.join(s.name for s in (Student.query.get(i) for i in member_ids) if s)
        flash(f'🌍 {country} designado para {nomes}!', 'success')
        return redirect(url_for('admin.students_list'))

    themes = Theme.query.order_by(Theme.name).all()
    joinable = Student.query.filter(Student.id != student.id).order_by(Student.name).all()
    return render_template('admin/student_assign.html', student=student,
                           available_themes=themes,
                           all_students=Student.query.order_by(Student.name).all(),
                           joinable_students=joinable)


@admin_bp.route('/alunos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def student_edit(id):
    """Edita nome e e-mail de um aluno (atualiza User e Inscription tambem)."""
    student = Student.query.get_or_404(id)
    error = None

    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not name or not email:
            error = 'Nome e e-mail sao obrigatorios.'
        elif email != student.email and User.query.filter_by(email=email).first():
            error = f'Ja existe um usuario com o e-mail {email}.'
        else:
            old_email = student.email
            student.name  = name
            student.email = email

            if student.user_id:
                user = User.query.get(student.user_id)
                if user:
                    user.name  = name
                    user.email = email

            ins = Inscription.query.filter_by(email=old_email, status='approved').first()
            if ins:
                ins.name  = name
                ins.email = email

            if student.delegation and student.delegation.inscription:
                dins = student.delegation.inscription
                if dins.email == old_email:
                    dins.name  = name
                    dins.email = email

            db.session.commit()
            flash(f'✅ Dados de {name} atualizados!', 'success')
            return redirect(url_for('admin.students_list'))

    return render_template('admin/student_edit.html', student=student, error=error)


@admin_bp.route('/alunos/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def student_delete(id):
    """Deleta um aluno e limpa registros relacionados."""
    from models.vote import Vote
    student = Student.query.get_or_404(id)

    deleg = student.delegation
    user_to_delete = None
    if student.user_id:
        user_to_delete = User.query.get(student.user_id)

    ins_to_delete = Inscription.query.filter_by(
        email=student.email, status='approved'
    ).first()

    Vote.query.filter_by(delegation_id=deleg.id).delete() if deleg else None

    db.session.delete(student)

    if deleg and not deleg.students:
        db.session.delete(deleg)

    if user_to_delete and user_to_delete.role != 'admin':
        has_other_students = Student.query.filter(
            Student.user_id == user_to_delete.id,
            Student.id != student.id
        ).first()
        if not has_other_students:
            db.session.delete(user_to_delete)

    if ins_to_delete:
        db.session.delete(ins_to_delete)

    db.session.commit()
    flash(f'🗑️ Aluno {student.name} deletado.', 'success')
    return redirect(url_for('admin.students_list'))


@admin_bp.route('/alunos/<int:id>/desdesignar', methods=['POST'])
@login_required
@admin_required
def student_unassign(id):
    """Remove o aluno da delegacao sem deletar."""
    student = Student.query.get_or_404(id)
    deleg = student.delegation

    student.delegation_id = None
    student.convened = False

    if deleg:
        _cleanup_orphan_delegation(deleg.id)

    db.session.commit()
    flash(f'↩️ {student.name} removido da delegação.', 'success')
    return redirect(url_for('admin.students_list'))


@admin_bp.route('/alunos/<int:id>/membro/remover/<int:member_id>', methods=['POST'])
@login_required
@admin_required
def student_remove_member(id, member_id):
    """Remove um membro da delegacao (desvincula sem deletar)."""
    student = Student.query.get_or_404(id)
    member = Student.query.get_or_404(member_id)

    if student.delegation_id and member.delegation_id == student.delegation_id:
        deleg = student.delegation
        member.delegation_id = None
        member.convened = False
        _cleanup_orphan_delegation(deleg.id)
        db.session.commit()
        flash(f'↩️ {member.name} removido da delegação de {student.name}.', 'success')
    else:
        flash('Aluno nao encontrado nesta delegacao.', 'error')

    return redirect(url_for('admin.student_assign', id=student.id))


@admin_bp.route('/alunos/travar', methods=['POST'])
@login_required
@admin_required
def students_lock_all():
    """Trava todos os alunos (read_only = True)."""
    count = Student.query.update({Student.read_only: True})
    db.session.commit()
    flash(f'🔒 {count} alunos travados. Eles não poderão mais registrar presença ou votar.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/alunos/destravar', methods=['POST'])
@login_required
@admin_required
def students_unlock_all():
    """Destrava todos os alunos (read_only = False)."""
    count = Student.query.update({Student.read_only: False})
    db.session.commit()
    flash(f'🔓 {count} alunos destravados.', 'success')
    return redirect(url_for('admin.dashboard'))
