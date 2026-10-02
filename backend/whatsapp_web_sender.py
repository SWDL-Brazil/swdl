# =============================================================
#  SWDL — whatsapp_web_sender.py
#  Envia mensagens via WhatsApp Web (Playwright), sem API paga.
#
#  Uso:
#    pip install playwright
#    python -m playwright install chromium
#    python whatsapp_web_sender.py contatos.csv
#
#  O CSV deve ter colunas: nome, email, telefone, pais, comite, tema
#  (exportar em Admin > Alunos > "Exportar contatos (CSV)")
# =============================================================
import csv
import re
import sys
import time
import unicodedata

MESSAGE_TEMPLATE = (
    "*SWDL 2026 — Sua conta*\n\n"
    "Olá {nome}!\n\n"
    "Segue seu acesso e delegação:\n\n"
    "*Login:* {email}\n"
    "*Senha:* {senha}\n"
    "{delegacao_linha}"
    "\nLink: https://swdl.onrender.com/student/login\n\n"
    "Bons debates!\nEquipe SWDL"
)


def first_name_password(name):
    fn = (name.strip().split()[0] if name.strip() else '')
    fn = unicodedata.normalize('NFKD', fn).encode('ascii', 'ignore').decode('ascii')
    fn = fn.capitalize()
    return f'{fn}@2026' if fn else 'Delegado@2026'


def build_message(row):
    deleg = ''
    pais = (row.get('pais') or '').strip()
    comite = (row.get('comite') or '').strip()
    tema = (row.get('tema') or '').strip()
    if pais or comite or tema:
        partes = []
        if comite: partes.append(comite)
        if pais: partes.append(pais)
        if tema: partes.append(tema)
        deleg = '*Delegação:* ' + ' — '.join(partes) + '\n'
    return MESSAGE_TEMPLATE.format(
        nome=row['nome'],
        email=row['email'],
        senha=first_name_password(row['nome']),
        delegacao_linha=deleg,
    )


def normalize_phone(phone):
    digits = re.sub(r'\D', '', phone or '')
    if not digits:
        return None
    if not digits.startswith('55'):
        digits = '55' + digits
    return digits


def main():
    if len(sys.argv) < 2:
        print('Uso: python whatsapp_web_sender.py <contatos.csv>')
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('Instale: pip install playwright && python -m playwright install chromium')
        sys.exit(1)

    rows = []
    with open(sys.argv[1], newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            phone = normalize_phone(row.get('telefone', ''))
            if phone:
                rows.append((row, phone))

    if not rows:
        print('Nenhum contato com telefone encontrado no CSV.')
        sys.exit(1)

    print(f'{len(rows)} contatos com telefone.')

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir='.whatsapp_session',
            headless=False,
        )
        page = browser.new_page()
        page.goto('https://web.whatsapp.com/')
        print('Aguardando WhatsApp Web carregar (escaneie o QR se for a 1a vez)...')
        try:
            page.wait_for_selector('div#pane-side', timeout=120000)
        except Exception:
            print('Timeout esperando WhatsApp Web. Tente novamente.')
            browser.close()
            sys.exit(1)

        for row, phone in rows:
            msg = build_message(row)
            print(f'Enviando para {row["nome"]} ({phone})...')
            import urllib.parse
            try:
                page.goto('https://web.whatsapp.com/send?phone=' + phone + '&text=' + urllib.parse.quote(msg))
                try:
                    page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=20000)
                except Exception:
                    page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
                time.sleep(2)
                page.keyboard.press('Enter')
                time.sleep(3)
                print('  OK')
            except Exception as e:
                print(f'  FALHOU: {e}')
            time.sleep(5)

        browser.close()
        print('Concluido.')


if __name__ == '__main__':
    main()
