import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


def send_approval_whatsapp(config_get, to_phone, student_name, login_email, password):
    api_url = config_get('whatsapp_api_url', '')
    api_key = config_get('whatsapp_api_key', '')

    if not all([api_url, api_key]):
        logger.warning('WhatsApp config incompleto — notificação não enviada')
        return False, 'Configuração de WhatsApp incompleta'

    if not to_phone:
        logger.warning('Telefone não informado — WhatsApp não enviado')
        return False, 'Telefone não informado'

    message = (
        f'*SWDL 2026 — Inscricao Aprovada!*\n\n'
        f'Ola {student_name}!\n\n'
        f'Seu cadastro foi aprovado. Acesse o portal:\n\n'
        f'*Login:* {login_email}\n'
        f'*Senha:* {password}\n\n'
        f'Link: https://swdl2026.com/student/login\n\n'
        f'Bons debates!\n'
        f'Equipe SWDL'
    )

    payload = json.dumps({
        'number': to_phone,
        'message': message,
        'api_key': api_key,
    }).encode('utf-8')

    try:
        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = resp.read().decode()
            logger.info(f'WhatsApp enviado para {to_phone}: {result[:100]}')
            return True, 'WhatsApp enviado com sucesso'
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        logger.error(f'Erro HTTP ao enviar WhatsApp: {e.code} {body[:200]}')
        return False, f'HTTP {e.code}: {body[:200]}'
    except Exception as e:
        logger.error(f'Erro ao enviar WhatsApp para {to_phone}: {e}')
        return False, str(e)
