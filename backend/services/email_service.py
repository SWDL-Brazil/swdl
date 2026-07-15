import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_approval_email(config_get, to_email, student_name, login_email, password):
    smtp_server = config_get('smtp_server', '')
    smtp_port   = config_get('smtp_port', '587')
    smtp_user   = config_get('smtp_user', '')
    smtp_pass   = config_get('smtp_pass', '')
    from_email  = config_get('from_email', '')

    if not all([smtp_server, smtp_port, smtp_user, smtp_pass, from_email]):
        logger.warning('Email config incompleto — notificação não enviada')
        return False, 'Configuração de e-mail incompleta'

    subject = 'Sua inscricao no SWDL 2026 foi aprovada!'
    body = (
        f'Ola {student_name},\n\n'
        f'Sua inscricao no SESI World Diplomacy League (SWDL) 2026 foi aprovada!\n\n'
        f'Acesse o portal com suas credenciais:\n\n'
        f'Login: {login_email}\n'
        f'Senha: {password}\n\n'
        f'Link: https://swdl2026.com/student/login\n\n'
        f'Bons debates!\n'
        f'Equipe SWDL'
    )

    try:
        msg = MIMEMultipart()
        msg['From']    = from_email
        msg['To']      = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logger.info(f'E-mail enviado para {to_email}')
        return True, 'E-mail enviado com sucesso'
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail para {to_email}: {e}')
        return False, str(e)
