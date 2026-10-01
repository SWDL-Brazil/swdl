import json
import pathlib
import copy

ROOT = pathlib.Path(__file__).resolve().parent / 'messages'
BASE = ROOT / 'pt-BR.json'

# Extra English-style defaults only used when filling EN gaps from structure;
# other locales get fallbacks from pt-BR then EN then the key name.

def load(p: pathlib.Path):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p: pathlib.Path, data):
    raw = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    had_bom = p.read_bytes().startswith(b'\xef\xbb\xbf')
    enc = raw.encode('utf-8')
    if had_bom:
        enc = b'\xef\xbb\xbf' + enc
    p.write_bytes(enc)

def leaf_keys(obj, prefix=''):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f'{prefix}.{k}' if prefix else k
            if isinstance(v, dict):
                out |= leaf_keys(v, key)
            else:
                out.add(key)
    return out

def get_path(obj, path):
    cur = obj
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

def set_path(obj, path, value):
    parts = path.split('.')
    cur = obj
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value

def list_len(path):
    # arrays are not leaf keys in leaf_keys if we skip them - handle separately
    return path

base = load(BASE)
base_keys = leaf_keys(base)

# Also collect array-containing paths
def array_paths(obj, prefix=''):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f'{prefix}.{k}' if prefix else k
            if isinstance(v, list):
                out.append(key)
            elif isinstance(v, dict):
                out.extend(array_paths(v, key))
    return out

base_arrays = array_paths(base)

files = sorted(ROOT.glob('*.json'))
loaded = {p.stem: load(p) for p in files}

# Fix accidental dotted flat keys like "stats.days" inside home
for loc, data in list(loaded.items()):
    home = data.get('home')
    if isinstance(home, dict):
        for k in list(home.keys()):
            if '.' in k:
                val = home.pop(k)
                set_path(data, f'home.{k}', val)

# Ensure EN has keys from PT (fill with EN translations where we know, else PT)
en_fill = {
    'home.stats_editions': 'Editions',
    'home.stats_editions_desc': 'Held since 2024',
    'home.testimonials_label': 'Testimonials',
    'home.testimonials_title': 'Those who lived it tell it better',
    'home.gallery_label': 'Gallery',
    'home.gallery_title': 'SWDL Moments',
    'footer.address': 'SESI CE-437, Hortolândia',
    'footer.developed_by': 'Developed by Pedro Bonazzi',
    'sobre.mission_desc': 'To form young leaders equipped to face contemporary global challenges through realistic UN simulations, developing diplomatic, negotiation and critical thinking skills.',
    'sobre.history_desc': 'From a high school dream to reality',
    'sobre.representacao': 'Country Representation',
    'sobre.representacao_desc': 'Participants represent different countries on UN themes, defending their national positions and interests.',
    'sobre.debates': 'Realistic Debates',
    'sobre.debates_desc': 'Discussions on current global topics following official United Nations procedures.',
    'sobre.negociacao': 'Negotiation and Diplomacy',
    'sobre.negociacao_desc': 'Developing diplomatic skills through negotiation and consensus-building.',
    'sobre.fundacao_ano': 'Founding year',
    'sobre.unidade': 'SESI Unit',
    'sobre.edicoes_realizadas': 'From the year',
    'faca_parte.why_delegate': 'Why become a SWDL Delegate?',
    'faca_parte.why_reasons': [
        'Develop public speaking and argumentation skills',
        'Learn about contemporary global issues',
        'Practice negotiation and diplomacy in real situations',
        'Work as a team with students from different grades',
        'Gain research and critical analysis experience',
        'Build a differentiated resume',
        'Network with young people interested in international politics',
    ],
    'faca_parte.req_school': 'School Grade',
    'faca_parte.req_school_desc': 'Students from 6th grade at SESI CE-437',
    'faca_parte.req_disponibilidade': 'Availability',
    'faca_parte.req_disponibilidade_desc': 'Participation on debate days and prior preparation',
    'faca_parte.req_comprometimento': 'Commitment',
    'faca_parte.req_comprometimento_desc': 'Study of the represented country and debate themes',
    'faca_parte.req_equipe': 'Teamwork',
    'faca_parte.req_equipe_desc': 'Collaboration with other delegates and respect for the rules',
    'faca_parte.form_experience': 'Previous Experience',
    'faca_parte.form_experience_placeholder': 'e.g. I participated in a MUN at school X...',
    'faca_parte.form_interests': 'Topics of Interest',
    'faca_parte.form_interests_placeholder': 'e.g. International Security, Human Rights, Environment...',
    'faca_parte.tab_delegado': 'Become a Delegate',
    'faca_parte.tab_voluntario': 'Be a Volunteer',
    'faca_parte.volunteer_roles': 'Areas of Work',
    'faca_parte.role_moderador': 'Debate Moderator',
    'faca_parte.role_moderador_desc': 'Lead debate sessions and keep order during theme discussions.',
    'faca_parte.role_midia': 'Media Team',
    'faca_parte.role_midia_desc': 'Document events through photos, videos and social media coverage of SWDL.',
    'faca_parte.role_organizacao': 'Organization',
    'faca_parte.role_organizacao_desc': 'Help with logistics, material preparation and overall event coordination.',
    'faca_parte.role_mentor': 'Mentor',
    'faca_parte.role_mentor_desc': 'Guide new delegates and share knowledge about diplomacy and UN procedures.',
    'faca_parte.next_steps': 'Next Steps',
    'faca_parte.step_1': 'Submit Your Registration',
    'faca_parte.step_1_desc': 'Fill in the form above with your information and motivations',
    'faca_parte.step_2': 'Wait for Contact',
    'faca_parte.step_2_desc': 'We will respond after the registration period ends',
    'faca_parte.step_3': 'Join Preparation',
    'faca_parte.step_3_desc': 'Attend workshops and preparation sessions',
    'faca_parte.step_4': 'Debate and Learn',
    'faca_parte.step_4_desc': 'Take part in debates and develop your diplomatic skills',
    'faca_parte.hero_label': 'Join the League',
    'faca_parte.closed_title': 'Registrations Closed',
    'faca_parte.closed_desc': 'Registrations for SWDL 2026 are temporarily closed.',
    'faca_parte.form_success_msg': 'Your registration was received successfully. We will contact you soon!',
    'faca_parte.form_grade_select': 'Select',
    'faca_parte.form_motivation_volunteer': 'Why do you want to be a volunteer?',
    'faca_parte.form_submit_volunteer': 'I Want to Be a Volunteer',
    'common.back_home': 'Back to home',
    'common.read_testimonial': 'Read testimonial',
    'sobre.values_title': 'What We Believe',
    'sobre_values.diplomacy': 'Diplomacy and Dialogue',
}

# Remove invalid EN-only structures that don't exist in PT
en_only_remove = [
    'faca_parte.format_volunteer',
    'faca_parte.requirements_list',
    'home.stats.days',
    'home.stats.days_desc',
]
# home.stats.days is nested under stats namespace differently

for loc, data in loaded.items():
    for key in base_keys:
        if get_path(data, key) is None:
            if loc == 'en' and key in en_fill:
                set_path(data, key, en_fill[key])
            else:
                # fallback: EN value if present else PT
                en_val = get_path(loaded.get('en', {}), key)
                pt_val = get_path(base, key)
                if en_val is not None and loc != 'en':
                    # prefer existing language if we only need structure fill from PT
                    set_path(data, key, pt_val if pt_val is not None else en_val)
                elif pt_val is not None:
                    set_path(data, key, pt_val)
                elif en_val is not None:
                    set_path(data, key, en_val)
                else:
                    set_path(data, key, key)

    # arrays: copy length from base if missing/wrong type
    for apath in base_arrays:
        bval = get_path(base, apath)
        dval = get_path(data, apath)
        if dval is None or not isinstance(dval, list) or len(dval) != len(bval):
            if loc == 'en' and apath in en_fill:
                set_path(data, apath, en_fill[apath])
            else:
                set_path(data, apath, copy.deepcopy(bval))

    # drop keys not in base (except we keep everything that's in base)
    def prune(obj, base_obj):
        if not isinstance(obj, dict):
            return
        for k in list(obj.keys()):
            if k not in base_obj:
                # allow nested only if base has dict there - else drop
                del obj[k]
            elif isinstance(base_obj[k], dict) and isinstance(obj[k], dict):
                prune(obj[k], base_obj[k])
            elif isinstance(base_obj[k], list) and not isinstance(obj[k], list):
                obj[k] = copy.deepcopy(base_obj[k])

    prune(data, base)

# Write common UI keys for switcher into all locales
common_ui = {
    'pt-BR': {'common.back': 'Voltar', 'common.close': 'Fechar', 'common.language': 'Idioma', 'common.home': 'Home', 'common.back_home': 'Voltar para o início', 'common.read_testimonial': 'Ler depoimento', 'ticker.live': 'AO VIVO', 'ticker.alerts': '{n} ALERTAS', 'crisis_banner.label': 'CRISE —', 'crisis_banner.close_aria': 'Fechar alerta'},
    'en': {'common.back': 'Back', 'common.close': 'Close', 'common.language': 'Language', 'common.home': 'Home', 'common.back_home': 'Back to home', 'common.read_testimonial': 'Read testimonial', 'ticker.live': 'LIVE', 'ticker.alerts': '{n} ALERTS', 'crisis_banner.label': 'CRISIS —', 'crisis_banner.close_aria': 'Close alert'},
    'es': {'common.back': 'Volver', 'common.close': 'Cerrar', 'common.language': 'Idioma', 'common.home': 'Inicio', 'common.back_home': 'Volver al inicio', 'common.read_testimonial': 'Leer testimonio', 'ticker.live': 'EN VIVO', 'ticker.alerts': '{n} ALERTAS', 'crisis_banner.label': 'CRISIS —', 'crisis_banner.close_aria': 'Cerrar alerta'},
    'fr': {'common.back': 'Retour', 'common.close': 'Fermer', 'common.language': 'Langue', 'common.home': 'Accueil', 'common.back_home': "Retour à l'accueil", 'common.read_testimonial': 'Lire le témoignage', 'ticker.live': 'EN DIRECT', 'ticker.alerts': '{n} ALERTES', 'crisis_banner.label': 'CRISE —', 'crisis_banner.close_aria': 'Fermer alerte'},
    'de': {'common.back': 'Zurück', 'common.close': 'Schließen', 'common.language': 'Sprache', 'common.home': 'Startseite', 'common.back_home': 'Zurück zur Startseite', 'common.read_testimonial': 'Referenz lesen', 'ticker.live': 'LIVE', 'ticker.alerts': '{n} ALARME', 'crisis_banner.label': 'KRISE —', 'crisis_banner.close_aria': 'Alarm schließen'},
    'it': {'common.back': 'Indietro', 'common.close': 'Chiudi', 'common.language': 'Lingua', 'common.home': 'Home', 'common.back_home': 'Torna alla home', 'common.read_testimonial': 'Leggi testimonianza', 'ticker.live': 'DIRETTA', 'ticker.alerts': '{n} ALLARMI', 'crisis_banner.label': 'CRISI —', 'crisis_banner.close_aria': 'Chiudi avviso'},
    'nl': {'common.back': 'Terug', 'common.close': 'Sluiten', 'common.language': 'Taal', 'common.home': 'Home', 'common.back_home': 'Terug naar home', 'common.read_testimonial': 'Getuigenis lezen', 'ticker.live': 'LIVE', 'ticker.alerts': '{n} ALARMS', 'crisis_banner.label': 'CRISIS —', 'crisis_banner.close_aria': 'Sluit waarschuwing'},
    'id': {'common.back': 'Kembali', 'common.close': 'Tutup', 'common.language': 'Bahasa', 'common.home': 'Beranda', 'common.back_home': 'Kembali ke beranda', 'common.read_testimonial': 'Baca testimoni', 'ticker.live': 'LANGSUNG', 'ticker.alerts': '{n} PERINGATAN', 'crisis_banner.label': 'KRISIS —', 'crisis_banner.close_aria': 'Tutup peringatan'},
    'ms': {'common.back': 'Kembali', 'common.close': 'Tutup', 'common.language': 'Bahasa', 'common.home': 'Utama', 'common.back_home': 'Kembali ke utama', 'common.read_testimonial': 'Baca testimoni', 'ticker.live': 'LANGSUNG', 'ticker.alerts': '{n} AMARAN', 'crisis_banner.label': 'KRISIS —', 'crisis_banner.close_aria': 'Tutup amaran'},
}

# sobre_values labels (en fill first via structure; other locales copy PT then OK for now)
sobre_values_fill = {
    'pt-BR': {
        'diplomacia': 'Diplomacia e Diálogo',
        'diversidade': 'Respeito à Diversidade',
        'excelencia': 'Excelência Acadêmica',
        'cooperacao': 'Cooperação Internacional',
        'sustentavel': 'Desenvolvimento Sustentável',
    },
    'en': {
        'diplomacia': 'Diplomacy and Dialogue',
        'diversidade': 'Respect for Diversity',
        'excelencia': 'Academic Excellence',
        'cooperacao': 'International Cooperation',
        'sustentavel': 'Sustainable Development',
    },
    'es': {
        'diplomacia': 'Diplomacia y Diálogo',
        'diversidade': 'Respeto a la Diversidad',
        'excelencia': 'Excelencia Académica',
        'cooperacao': 'Cooperación Internacional',
        'sustentavel': 'Desarrollo Sostenible',
    },
    'fr': {
        'diplomacia': 'Diplomatie et Dialogue',
        'diversidade': 'Respect de la Diversité',
        'excelencia': 'Excellence Académique',
        'cooperacao': 'Coopération Internationale',
        'sustentavel': 'Développement Durable',
    },
    'de': {
        'diplomacia': 'Diplomatie und Dialog',
        'diversidade': 'Respekt vor Vielfalt',
        'excelencia': 'Akademische Exzellenz',
        'cooperacao': 'Internationale Zusammenarbeit',
        'sustentavel': 'Nachhaltige Entwicklung',
    },
    'it': {
        'diplomacia': 'Diplomazia e Dialogo',
        'diversidade': 'Rispetto per la Diversità',
        'excelencia': 'Eccellenza Accademica',
        'cooperacao': 'Cooperazione Internazionale',
        'sustentavel': 'Sviluppo Sostenibile',
    },
    'nl': {
        'diplomacia': 'Diplomatie en Dialoog',
        'diversidade': 'Respect voor Diversiteit',
        'excelencia': 'Academische Uitmuntendheid',
        'cooperacao': 'Internationale Samenwerking',
        'sustentavel': 'Duurzame Ontwikkeling',
    },
    'id': {
        'diplomacia': 'Diplomasi dan Dialog',
        'diversidade': 'Menghargai Keragaman',
        'excelencia': 'Keunggulan Akademik',
        'cooperacao': 'Kerja Sama Internasional',
        'sustentavel': 'Pembangunan Berkelanjutan',
    },
    'ms': {
        'diplomasi': 'Diplomasi dan Dialog',
        'diversidade': 'Menghargai Kepelbagaian',
        'excelencia': 'Kecemerlangan Akademik',
        'cooperacao': 'Kerjasama Antarabangsa',
        'sustentavel': 'Pembangunan Mampan',
    },
}

# fix typo key in ms
sobre_values_fill['ms']['diplomacia'] = sobre_values_fill['ms'].pop('diplomasi')

for p in files:
    loc = p.stem
    data = loaded[loc]
    ui = common_ui[loc]
    # nest common
    data.setdefault('common', {})
    data['common'].update({k.split('.', 1)[1]: v for k, v in ui.items() if k.startswith('common.')})
    data.setdefault('crisis_banner', {})
    data['crisis_banner']['close_aria'] = ui['crisis_banner.close_aria']
    data['crisis_banner']['label'] = ui['crisis_banner.label']
    data.setdefault('ticker', {})
    data['ticker']['live'] = ui['ticker.live']
    data['ticker']['alerts'] = ui['ticker.alerts']
    # sobre_values from PT structure with fills
    if isinstance(base.get('sobre_values'), dict):
        data['sobre_values'] = {}
        for k in base['sobre_values'].keys():
            data['sobre_values'][k] = sobre_values_fill.get(loc, {}).get(k) or sobre_values_fill['en'].get(k) or base['sobre_values'][k]
    # ensure faca_parte new keys
    for key in ['hero_label', 'closed_title', 'closed_desc', 'form_success_msg', 'form_grade_select', 'form_motivation_volunteer', 'form_submit_volunteer']:
        if key not in data.get('faca_parte', {}):
            data.setdefault('faca_parte', {})[key] = base.get('faca_parte', {}).get(key, key)
        elif loc != 'pt-BR' and key in en_fill:
            data['faca_parte'][key] = en_fill[f'faca_parte.{key}']
    if 'values_title' not in data.get('sobre', {}):
        data.setdefault('sobre', {})['values_title'] = base.get('sobre', {}).get('values_title', 'values_title')
    elif loc != 'pt-BR' and 'sobre.values_title' in en_fill:
        data['sobre']['values_title'] = en_fill['sobre.values_title']
    save(p, data)
    keys = leaf_keys(data)
    print(f'{loc}: {len(keys)} leaf keys')

# verify parity
ref = leaf_keys(load(BASE))
for p in files:
    keys = leaf_keys(load(p))
    miss = sorted(ref - keys)
    extra = sorted(keys - ref)
    status = 'OK' if not miss and not extra else f'miss={miss[:5]} extra={extra[:5]}'
    print(p.stem, status)
print('done')
