from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required
from models.system_config import SystemConfig
from extensions import db


@admin_bp.route('/notificacoes', methods=['GET', 'POST'])
@login_required
@admin_required
def notifications_config():
    if request.method == 'POST':
        section = request.form.get('section', '')

        if section == 'email':
            SystemConfig.set('smtp_server', request.form.get('smtp_server', ''))
            SystemConfig.set('smtp_port',   request.form.get('smtp_port', '587'))
            SystemConfig.set('smtp_user',   request.form.get('smtp_user', ''))
            SystemConfig.set('smtp_pass',   request.form.get('smtp_pass', ''))
            SystemConfig.set('from_email',  request.form.get('from_email', ''))
            flash('Configuracoes de e-mail salvas!', 'success')

        elif section == 'whatsapp':
            SystemConfig.set('whatsapp_api_url', request.form.get('whatsapp_api_url', ''))
            SystemConfig.set('whatsapp_api_key', request.form.get('whatsapp_api_key', ''))
            flash('Configuracoes de WhatsApp salvas!', 'success')

        elif section == 'general':
            SystemConfig.set('auto_email',    '1' if request.form.get('auto_email') else '0')
            SystemConfig.set('auto_whatsapp', '1' if request.form.get('auto_whatsapp') else '0')
            flash('Preferencias de disparo salvas!', 'success')

        return redirect(url_for('admin.notifications_config'))

    configs = {
        'smtp_server': SystemConfig.get('smtp_server', ''),
        'smtp_port':   SystemConfig.get('smtp_port', '587'),
        'smtp_user':   SystemConfig.get('smtp_user', ''),
        'smtp_pass':   SystemConfig.get('smtp_pass', ''),
        'from_email':  SystemConfig.get('from_email', ''),
        'whatsapp_api_url': SystemConfig.get('whatsapp_api_url', ''),
        'whatsapp_api_key': SystemConfig.get('whatsapp_api_key', ''),
        'auto_email':    SystemConfig.get('auto_email', '1'),
        'auto_whatsapp': SystemConfig.get('auto_whatsapp', '0'),
    }
    return render_template('admin/notifications_config.html', configs=configs)


@admin_bp.route('/notificacoes/testar-email', methods=['POST'])
@login_required
@admin_required
def test_email_config():
    from services.email_service import send_approval_email

    success, msg = send_approval_email(
        SystemConfig.get,
        to_email=current_user.email,
        student_name=current_user.name,
        login_email='teste@exemplo.com',
        password='teste_swdl',
    )
    if success:
        flash(f'E-mail de teste enviado para {current_user.email}! Verifique sua caixa de entrada.', 'success')
    else:
        flash(f'Falha ao enviar e-mail de teste: {msg}', 'error')
    return redirect(url_for('admin.notifications_config'))
