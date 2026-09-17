from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required, _ensure_participation_history
from models.inscription import Inscription
from models.inscription_member import InscriptionMember
from models.user import User
from models.student import Student
from models.delegation import Delegation
from models.theme import Theme
from models.system_config import SystemConfig
from extensions import db
import re
from datetime import datetime, timezone


@admin_bp.route('/inscricoes')
@login_required
@admin_required
def inscriptions_list():
    status_filter = request.args.get('status', 'all')
    formato_filter = request.args.get('formato', 'all')
    q = Inscription.query
    if status_filter != 'all':
        q = q.filter_by(status=status_filter)
    if formato_filter != 'all':
        q = q.filter_by(formato=formato_filter)
    inscriptions = q.order_by(Inscription.submitted_at.desc()).all()
    return render_template('admin/inscriptions_list.html',
                           inscriptions=inscriptions,
                           status_filter=status_filter,
                           formato_filter=formato_filter)


@admin_bp.route('/inscricoes/<int:id>')
@login_required
@admin_required
def inscription_detail(id):
    ins = Inscription.query.get_or_404(id)
    return render_template('admin/inscription_detail.html', ins=ins)


@admin_bp.route('/inscricoes/<int:id>/aprovar', methods=['POST'])
@login_required
@admin_required
def inscription_approve(id):
    ins = Inscription.query.get_or_404(id)
    ins.status      = 'approved'
    ins.reviewed_at = datetime.now(timezone.utc)
    ins.reviewed_by = current_user.id

    from models.system_config import SystemConfig
    from services.email_service import send_approval_email
    from services.whatsapp_service import send_approval_whatsapp
    import secrets, string

    # Coleta todos os participantes (inscrito principal + membros extras)
    participants = [{'name': ins.name, 'email': ins.email, 'phone': ins.phone, 'is_primary': True}]
    for m in ins.extra_members:
        participants.append({'name': m.name, 'email': m.email, 'phone': m.phone, 'is_primary': False})

    alphabet = string.ascii_letters + string.digits
    created_accounts = []

    for p in participants:
        existing_user = User.query.filter_by(email=p['email']).first()
        if existing_user:
            # Usuário já existe — garantir que tem Student profile
            student = Student.query.filter_by(email=p['email']).first()
            if not student:
                student = Student(user_id=existing_user.id, name=p['name'], email=p['email'])
                db.session.add(student)
                db.session.flush()
            created_accounts.append({
                'name': p['name'], 'email': p['email'],
                'password': '(já possui conta)', 'existed': True
            })
            continue

        # Criar nova conta
        password = ''.join(secrets.choice(alphabet) for _ in range(10))
        user = User(name=p['name'], email=p['email'], role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(user_id=user.id, name=p['name'], email=p['email'])
        db.session.add(student)
        db.session.flush()

        created_accounts.append({
            'name': p['name'], 'email': p['email'],
            'password': password, 'existed': False
        })

        # Enviar credenciais
        notificacoes = []
        auto_email    = SystemConfig.get('auto_email', '1') == '1'
        auto_whatsapp = SystemConfig.get('auto_whatsapp', '0') == '1'

        if auto_email:
            ok, msg = send_approval_email(
                SystemConfig.get,
                to_email=p['email'],
                student_name=p['name'],
                login_email=p['email'],
                password=password,
            )
            notificacoes.append(f'E-mail: {"✅" if ok else "❌"} {msg}')

        if auto_whatsapp and p.get('phone'):
            ok, msg = send_approval_whatsapp(
                SystemConfig.get,
                to_phone=p['phone'],
                student_name=p['name'],
                login_email=p['email'],
                password=password,
            )
            notificacoes.append(f'WhatsApp: {"✅" if ok else "❌"} {msg}')

    # Criar Delegation se inscrição em grupo ou se não existe ainda
    if not ins.delegation:
        primary_student = Student.query.filter_by(email=ins.email).first()
        if primary_student:
            deleg = Delegation(
                inscription_id = ins.id,
                user_id        = primary_student.user_id,
                edition_year   = datetime.now(timezone.utc).year,
                committee      = '',
                country        = '',
            )
            db.session.add(deleg)
            db.session.flush()

            # Vincular todos os students à delegação
            for p in created_accounts:
                s = Student.query.filter_by(email=p['email']).first()
                if s:
                    s.delegation_id = deleg.id
                    s.convened = True
                    _ensure_participation_history(s)
    else:
        # Delegação já existe — vincular membros extras
        for p in created_accounts:
            s = Student.query.filter_by(email=p['email']).first()
            if s and not s.delegation_id:
                s.delegation_id = ins.delegation.id
                s.convened = True
                _ensure_participation_history(s)

    db.session.commit()

    # Flash com credenciais
    if len(created_accounts) > 1:
        credenciais = '<br>'.join(
            f'• <b>{c["name"]}</b>: {c["email"]} | Senha: {c["password"]}'
            + (' <em>(já existia)</em>' if c['existed'] else '')
            for c in created_accounts
        )
        flash(f'✅ Inscrição aprovada! {len(created_accounts)} contas criadas:<br>{credenciais}', 'success')
    else:
        c = created_accounts[0]
        flash(
            f'✅ Inscricao de {c["name"]} aprovada! '
            f'Conta criada — Login: {c["email"]} | Senha: {c["password"]}',
            'success'
        )

    return redirect(url_for('admin.inscriptions_list'))


@admin_bp.route('/inscricoes/<int:id>/rejeitar', methods=['POST'])
@login_required
@admin_required
def inscription_reject(id):
    ins = Inscription.query.get_or_404(id)
    ins.status      = 'rejected'
    ins.reviewed_at = datetime.now(timezone.utc)
    ins.reviewed_by = current_user.id
    db.session.commit()
    flash(f'Inscricao de {ins.name} rejeitada.', 'info')
    return redirect(url_for('admin.inscriptions_list'))
