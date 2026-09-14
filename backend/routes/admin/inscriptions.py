from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required
from models.inscription import Inscription
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
    q = Inscription.query
    if status_filter != 'all':
        q = q.filter_by(status=status_filter)
    inscriptions = q.order_by(Inscription.submitted_at.desc()).all()
    return render_template('admin/inscriptions_list.html',
                           inscriptions=inscriptions,
                           status_filter=status_filter)


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

    # Cria conta de usuario + perfil de aluno automaticamente
    from models.user import User
    from models.student import Student
    from models.system_config import SystemConfig
    from services.email_service import send_approval_email
    from services.whatsapp_service import send_approval_whatsapp
    import re

    existing_user = User.query.filter_by(email=ins.email).first()
    if not existing_user:
        import secrets, string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(10))

        user = User(name=ins.name, email=ins.email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id = user.id,
            name    = ins.name,
            email   = ins.email,
        )
        db.session.add(student)
        db.session.flush()

        # Vincula delegacao existente, se houver
        if ins.delegation:
            ins.delegation.user_id = user.id

        db.session.commit()

        # -- Envio automatico de notificacoes --------
        notificacoes = []
        auto_email    = SystemConfig.get('auto_email', '1') == '1'
        auto_whatsapp = SystemConfig.get('auto_whatsapp', '0') == '1'

        if auto_email:
            ok, msg = send_approval_email(
                SystemConfig.get,
                to_email=ins.email,
                student_name=ins.name,
                login_email=ins.email,
                password=password,
            )
            notificacoes.append(f'E-mail: {"✅" if ok else "❌"} {msg}')

        if auto_whatsapp and ins.phone:
            ok, msg = send_approval_whatsapp(
                SystemConfig.get,
                to_phone=ins.phone,
                student_name=ins.name,
                login_email=ins.email,
                password=password,
            )
            notificacoes.append(f'WhatsApp: {"✅" if ok else "❌"} {msg}')

        msg_notificacoes = ' | '.join(notificacoes) if notificacoes else 'Notificacoes desabilitadas'

        flash(
            f'✅ Inscricao de {ins.name} aprovada! '
            f'Conta criada — Login: {ins.email} | Senha: {password}'
            f'<br><small style="color:var(--muted)">{msg_notificacoes}</small>',
            'success'
        )
    else:
        flash(f'✅ Inscricao de {ins.name} aprovada! (Usuario ja existia)', 'success')
        db.session.commit()

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
