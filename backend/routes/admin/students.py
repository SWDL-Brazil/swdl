from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import (admin_bp, admin_required,
                                   _ensure_participation_history,
                                   _cleanup_orphan_delegation,
                                   _country_taken)
from models.user import User
from models.student import Student
from models.delegation import Delegation
from models.theme import Theme
from models.inscription import Inscription
from models.inscription_member import InscriptionMember
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
            import unicodedata
            first_name = (name.strip().split()[0] if name.strip() else '')
            first_name = unicodedata.normalize('NFKD', first_name).encode('ascii', 'ignore').decode('ascii')
            first_name = first_name.capitalize()
            password = f'{first_name}@2026' if first_name else 'Delegado@2026'

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
            # Etapa 2: designar pais/tema direto (evita voltar pela lista)
            return redirect(url_for('admin.student_assign', id=student.id))

    return render_template('admin/delegate_create.html', error=error)


@admin_bp.route('/alunos')
@login_required
@admin_required
def students_list():
    """Lista todos os alunos cadastrados com status da designação."""
    from sqlalchemy.orm import joinedload, selectinload
    # Eager: template chama s.delegation.member_names() por linha (N+1)
    students = Student.query.options(
        selectinload(Student.delegation).options(
            selectinload(Delegation.students),
            joinedload(Delegation.inscription),
        )
    ).order_by(Student.created_at.desc()).all()
    return render_template('admin/students_list.html', students=students)


@admin_bp.route('/alunos/exportar-contatos')
@login_required
@admin_required
def students_export_contacts():
    """Exporta CSV (nome, email, telefone, pais, comite, tema, membros) para envio via WhatsApp Web."""
    import csv, io
    from flask import Response
    from sqlalchemy.orm import joinedload, selectinload
    students = Student.query.options(
        selectinload(Student.delegation).options(
            selectinload(Delegation.students),
            joinedload(Delegation.inscription),
        )
    ).order_by(Student.name).all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['nome', 'email', 'telefone', 'pais', 'comite', 'tema', 'membros'])
    for s in students:
        ins = (s.delegation.inscription if s.delegation and s.delegation.inscription else None)
        phone = ''
        if s.delegation and s.delegation.inscription:
            try:
                member = next((m for m in s.delegation.inscription.extra_members
                               if (m.email or '').lower() == s.email.lower()), None)
                phone = (member.phone if member and member.phone else '') or ''
            except Exception:
                phone = ''
        if not phone and ins:
            phone = ins.phone or ''
        w.writerow([
            s.name, s.email, phone,
            s.delegation.country if s.delegation else '',
            s.delegation.committee if s.delegation else '',
            (s.delegation.theme.name if s.delegation and s.delegation.theme else ''),
            ('; '.join(s.delegation.member_names()) if s.delegation else ''),
        ])
    return Response(
        '﻿' + buf.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=alunos_contatos.csv'},
    )


@admin_bp.route('/alunos/<int:id>/designar', methods=['GET', 'POST'])
@login_required
@admin_required
def student_assign(id):
    """Step 2: atribui país, tema e formato (individual, dupla, trio ou grupo) a um aluno existente."""
    from sqlalchemy.orm import selectinload
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        country  = request.form.get('country', '').strip()
        flag     = request.form.get('flag', '').strip()
        flag_url = request.form.get('flag_url', '').strip()
        theme_id = request.form.get('theme_id', type=int)

        if not country:
            flash('O país é obrigatório.', 'error')
            themes = Theme.query.order_by(Theme.name).all()
            joinable = Student.query.filter(Student.id != student.id).order_by(Student.name).all()
            return render_template('admin/student_assign.html', student=student,
                                   available_themes=themes,
                                   all_students=Student.query.options(selectinload(Student.delegation)).order_by(Student.name).all(),
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
                # Membro de dupla/trio criado na aprovacao nao tem inscricao
                # propria — cria uma para permitir a designacao/re-designacao.
                ins = Inscription(
                    name=student.name,
                    email=student.email,
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

        if _country_taken(country, theme, exclude_id=deleg.id):
            flash(f'⚠️ {country} já foi designado neste tema/comitê. '
                  f'Escolha outro país (ou corrija a designação existente).', 'error')
            return redirect(url_for('admin.student_assign', id=student.id))

        prev_theme_id   = deleg.theme_id
        prev_committee  = deleg.committee or ''
        committee_name  = request.form.get('committee_name', '').strip()

        deleg.theme_id    = theme.id if theme else None
        deleg.country      = country
        deleg.country_flag = flag
        deleg.flag_url     = flag_url
        if committee_name:
            deleg.committee = committee_name
        elif theme and (theme.id != prev_theme_id or not prev_committee):
            deleg.committee = theme.name
        elif not theme:
            # Sem tema: limpa so se o comitê atual era o nome do tema antigo
            # (preserva comitê customizado).
            prev_theme = db.session.get(Theme, prev_theme_id) if prev_theme_id else None
            if not prev_theme or prev_committee == prev_theme.name:
                deleg.committee = ''
        if 'members' in request.form:
            # campo texto livre (formularios antigos) — preserva se ausente
            deleg.members = request.form.get('members', '').strip()
        deleg.flag_animation = bool(request.form.get('flag_animation'))
        db.session.flush()

        # ── Companheiros de equipe (nome + e-mail) ──────────────────
        # Cria login na hora (User + Student) e vincula a esta delegacao.
        import unicodedata
        from models.system_config import SystemConfig
        from services.email_service import send_approval_email
        from services.whatsapp_service import send_approval_whatsapp

        teammate_notes = []
        teammate_old_ids = set()
        nm_names  = request.form.getlist('nm_name')
        nm_emails = request.form.getlist('nm_email')
        for tname, temail in zip(nm_names, nm_emails):
            tname  = tname.strip()
            temail = temail.strip().lower()
            if not tname and not temail:
                continue
            if not tname or not temail:
                teammate_notes.append(f'⚠ linha de companheiro incompleta ({tname or temail}) — ignorada')
                continue
            if temail == (student.email or '').strip().lower():
                teammate_notes.append(f'⚠ {temail} é o e-mail do aluno designado — ignorado')
                continue

            tuser = User.query.filter(db.func.lower(User.email) == temail).first()
            if tuser and tuser.role == 'admin':
                teammate_notes.append(f'⚠ {temail} é de um admin — ignorado')
                continue

            tpassword = None
            if not tuser:
                first = (tname.split()[0] if tname.split() else '')
                first = unicodedata.normalize('NFKD', first)\
                    .encode('ascii', 'ignore').decode('ascii').capitalize()
                tpassword = f'{first}@2026' if first else 'Delegado@2026'
                tuser = User(name=tname, email=temail, role='student')
                tuser.set_password(tpassword)
                db.session.add(tuser)
                db.session.flush()

                if SystemConfig.get('auto_email', '1') == '1':
                    ok, m = send_approval_email(SystemConfig.get, temail, tname, temail, tpassword)
                    teammate_notes.append(f'{tname} — e-mail: {"✅" if ok else "❌"}')
                if SystemConfig.get('auto_whatsapp', '0') == '1':
                    tins = Inscription.query.filter_by(email=temail, status='approved').first()
                    if tins and tins.phone:
                        ok, m = send_approval_whatsapp(SystemConfig.get, tins.phone, tname, temail, tpassword)
                        teammate_notes.append(f'{tname} — WhatsApp: {"✅" if ok else "❌"}')

            tstudent = Student.query.filter(db.func.lower(Student.email) == temail).first()
            if not tstudent:
                tstudent = Student(user_id=tuser.id, name=tname, email=temail)
                db.session.add(tstudent)
                db.session.flush()
            elif not tstudent.user_id:
                tstudent.user_id = tuser.id

            if tstudent.delegation_id and tstudent.delegation_id != deleg.id:
                teammate_old_ids.add(tstudent.delegation_id)
            tstudent.delegation_id = deleg.id
            tstudent.convened = True
            if not deleg.user_id and tuser:
                deleg.user_id = tuser.id
            _ensure_participation_history(tstudent)
            if tstudent.id not in extra_ids and tstudent.id != student.id:
                extra_ids = extra_ids + [tstudent.id]
            teammate_notes.append(
                f'✅ {tname} <{temail}> — Login: {temail} | Senha: {tpassword or "(conta já existia)"}'
            )

        member_ids = [student.id] + [i for i in extra_ids if i != student.id]

        old_deleg_ids = set(teammate_old_ids)
        for sid in member_ids:
            s = Student.query.get(sid)
            if s and s.delegation_id and s.delegation_id != deleg.id:
                old_deleg_ids.add(s.delegation_id)
        moved = []
        for oid in old_deleg_ids:
            od = db.session.get(Delegation, oid)
            if od:
                moved.append(od.country or 'sem país')

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
        extra = f' (movidos de: {", ".join(sorted(moved))})' if moved else ''
        flash(f'🌍 {country} designado para {nomes}!{extra}', 'success')
        for note in teammate_notes:
            flash(note, 'success' if note.startswith('✅') else 'warning')
        return redirect(url_for('admin.students_list'))

    themes = Theme.query.order_by(Theme.name).all()
    joinable = Student.query.filter(Student.id != student.id).order_by(Student.name).all()
    return render_template('admin/student_assign.html', student=student,
                           available_themes=themes,
                           all_students=Student.query.options(selectinload(Student.delegation)).order_by(Student.name).all(),
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
        phone = request.form.get('phone', '').strip()
        instagram = request.form.get('instagram', '').strip()
        school = request.form.get('school', '').strip()
        grade = request.form.get('grade', '').strip()

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

            ins = (student.delegation.inscription
                   if student.delegation and student.delegation.inscription
                   else Inscription.query.filter_by(email=old_email, status='approved').first())
            if ins:
                member_of_ins = InscriptionMember.query.filter(
                    InscriptionMember.inscription_id == ins.id,
                    db.func.lower(InscriptionMember.email) == old_email.lower(),
                ).first()
                if member_of_ins:
                    member_of_ins.name = name
                    member_of_ins.email = email
                    member_of_ins.phone = phone
                    member_of_ins.instagram = instagram
                    member_of_ins.grade = grade
                    member_of_ins.school = school
                else:
                    ins.name = name
                    ins.email = email
                    ins.phone = phone
                    ins.instagram = instagram
                    ins.school = school
                    ins.grade = grade

            db.session.commit()
            flash(f'✅ Dados de {name} atualizados!', 'success')
            return redirect(url_for('admin.students_list'))

    ins = (student.delegation.inscription
           if student.delegation and student.delegation.inscription
           else Inscription.query.filter_by(email=student.email).first())
    member = None
    if ins:
        member = InscriptionMember.query.filter(
            InscriptionMember.inscription_id == ins.id,
            db.func.lower(InscriptionMember.email) == student.email.lower(),
        ).first()
    contact = member or ins
    return render_template('admin/student_edit.html', student=student, error=error,
                           inscription=ins, contact=contact, is_member=member is not None)


@admin_bp.route('/alunos/<int:id>/resetar-senha', methods=['POST'])
@login_required
@admin_required
def student_reset_password(id):
    """Gera uma nova senha aleatoria para o login do aluno e mostra na tela.

    Exige a senha-mestre de operacao (Bonazzi@2022) no campo 'master_password'.
    Observacao: senhas sao guardadas com hash, entao a senha atual do aluno
    nunca pode ser exibida — apenas uma nova senha gerada.
    """
    student = Student.query.get_or_404(id)
    if not student.user_id:
        flash('Este aluno nao possui login vinculado.', 'error')
        return redirect(url_for('admin.student_edit', id=student.id))

    import hmac
    if not hmac.compare_digest(request.form.get('master_password', ''), 'Bonazzi@2022'):
        flash('Senha-mestre incorreta.', 'error')
        return redirect(url_for('admin.student_edit', id=student.id))

    user = User.query.get(student.user_id)
    if not user:
        flash('Usuario de login nao encontrado.', 'error')
        return redirect(url_for('admin.student_edit', id=student.id))

    import unicodedata
    first_name = (student.name or '').strip().split()[0] if student.name else ''
    first_name = unicodedata.normalize('NFKD', first_name).encode('ascii', 'ignore').decode('ascii')
    first_name = first_name.capitalize()
    new_password = f'{first_name}@2026' if first_name else 'Delegado@2026'
    user.set_password(new_password)
    db.session.commit()
    flash(f'Nova senha gerada para {user.email}.', 'success')
    ins = (student.delegation.inscription
           if student.delegation and student.delegation.inscription
           else Inscription.query.filter_by(email=student.email).first())
    member = None
    if ins:
        member = InscriptionMember.query.filter(
            InscriptionMember.inscription_id == ins.id,
            db.func.lower(InscriptionMember.email) == student.email.lower(),
        ).first()
    return render_template('admin/student_edit.html', student=student, error=None,
                           inscription=ins, contact=member or ins, is_member=member is not None,
                           new_password=new_password)


@admin_bp.route('/alunos/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def student_delete(id):
    """Deleta um aluno sem perder dados do resto do grupo.

    Regras (antes as excluicoes apagavam votos/inscricao/delegacao inteiros
    mesmo quando o grupo ainda tinha membros):
      - Votos: nunca sao apagados aqui. A delegacao so e removida pelo
        _cleanup_orphan_delegation (que exige vazio + sem votos/DPO/presenca).
      - Inscricao: so sai se nenhum outro aluno usa o email e nenhuma
        delegacao referencia inscription_id.
      - Usuario login: so sai se nao restou outro aluno nem delegacao dele.
    """
    student = Student.query.get_or_404(id)

    deleg = student.delegation
    user_to_delete = User.query.get(student.user_id) if student.user_id else None
    ins_to_delete = Inscription.query.filter_by(
        email=student.email, status='approved'
    ).first()

    # Contagens ANTES do delete (referencias que devem sobreviver)
    others_in_deleg = 0
    if deleg:
        others_in_deleg = Student.query.filter(
            Student.delegation_id == deleg.id,
            Student.id != student.id,
        ).count()
    others_of_user = 0
    if user_to_delete:
        others_of_user = Student.query.filter(
            Student.user_id == user_to_delete.id,
            Student.id != student.id,
        ).count()

    db.session.delete(student)
    db.session.flush()

    if deleg:
        db.session.expire(deleg)  # releitura: students ja nao inclui o apagado
        if others_in_deleg == 0:
            # mantem a delegacao se tiver votos/DPO/presenca (evita perda)
            _cleanup_orphan_delegation(deleg.id)

    if ins_to_delete:
        same_email = Student.query.filter(Student.email == ins_to_delete.email).count()
        ins_referenced = Delegation.query.filter_by(
            inscription_id=ins_to_delete.id
        ).count()
        if same_email == 0 and ins_referenced == 0:
            db.session.delete(ins_to_delete)

    if user_to_delete and user_to_delete.role != 'admin' and others_of_user == 0:
        user_still_owner = Delegation.query.filter_by(
            user_id=user_to_delete.id
        ).count()
        if user_still_owner == 0:
            db.session.delete(user_to_delete)

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
