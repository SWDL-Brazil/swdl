import os, sys, shutil, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models.theme import Theme
from models.document import Document
from models.agenda import AgendaItem
from extensions import db
from config import Config

THEME_NAME = "A Proteção Internacional de Pessoas Deslocadas em Decorrência de Eventos Climáticos Extremos"
PDF_SOURCE = os.path.join(os.path.dirname(__file__), 'pages', 'assent', 'PDF', 'Guia de Comitê - ACNUR.pdf')

app = create_app()
with app.app_context():
    theme = Theme.query.filter_by(name=THEME_NAME).first()
    if not theme:
        theme = Theme(name=THEME_NAME)
        from extensions import db
        db.session.add(theme)
        db.session.flush()
        print(f'[OK] Tema criado (id={theme.id})')
    else:
        print(f'[OK] Tema já existe (id={theme.id})')

    doc = Document.query.filter_by(title=f'Guia de Estudos - {THEME_NAME}').first()
    if not doc:
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'documentos')
        os.makedirs(upload_dir, exist_ok=True)
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        safe_name = f'doc_{ts}_Guia de Comitê - ACNUR.pdf'
        filepath = os.path.join(upload_dir, safe_name)
        shutil.copyfile(PDF_SOURCE, filepath)

        doc = Document(
            title=f'Guia de Estudos - {THEME_NAME}',
            description='Guia de estudos do comitê ACNUR sobre a proteção internacional de pessoas deslocadas em decorrência de eventos climáticos extremos.',
            file_path=filepath,
            category='guias',
            theme_id=theme.id,
        )
        from extensions import db
        db.session.add(doc)
        print(f'[OK] Documento cadastrado -> {safe_name}')
    else:
        print('[OK] Documento já existia')

    item = AgendaItem.query.filter(AgendaItem.event_date == '2026-09-02',
                                   AgendaItem.committee == 'ACNUR').first()
    if not item:
        item = AgendaItem(
            day         = 1,
            event_date  = '2026-09-02',
            start_time  = '07:00',
            end_time    = '12:00',
            title       = THEME_NAME,
            description = 'Debate do comitê ACNUR — proteção internacional de pessoas deslocadas em decorrência de eventos climáticos extremos.',
            location    = 'LMT',
            status      = 'auto',
            committee   = 'ACNUR',
            order       = 1,
        )
        db.session.add(item)
        print('[OK] Item de agenda criado (02/09/2026, 07:00–12:00)')
    else:
        print('[OK] Item de agenda já existia')

    from extensions import db
    db.session.commit()
    print('[OK] Pronto!')