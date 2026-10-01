import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent / 'messages'

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p, data):
    raw = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    p.write_bytes(raw.encode('utf-8'))

# New keys: namespace -> {key: {locale: value or None}}
# Missing locales filled from pt then en in later pass

new_keys = {
    'home': {
        'next_debate_label': {
            'pt-BR': 'Próximo Debate', 'en': 'Next Debate', 'es': 'Próximo Debate',
            'fr': 'Prochain débat', 'de': 'Nächste Debatte', 'it': 'Prossimo dibattito',
            'nl': 'Volgend debat', 'id': 'Debat Berikutnya', 'ms': 'Debat Seterusnya',
        },
        'next_debate_title': {
            'pt-BR': 'A Escravidão do Passado ao Racismo do Presente',
            'en': 'From Slavery of the Past to Racism of the Present',
            'es': 'De la Esclavitud del Pasado al Racismo del Presente',
            'fr': "De l'Esclavage du Passé au Racisme du Présent",
            'de': 'Von der Sklaverei der Vergangenheit zum Rassismus der Gegenwart',
            'it': "Dalla Schiavitù del Passato al Razzismo del Presente",
            'nl': 'Van Slavernij van het Verleden naar Racisme van Nu',
            'id': 'Dari Perbudakan Masa Lalu hingga Rasisme Masa Kini',
            'ms': 'Dari Perhambaan Masa Lalu hingga Perkauman Kini',
        },
        'next_debate_theme': {
            'pt-BR': 'Desafiando o Futuro', 'en': 'Challenging the Future',
            'es': 'Desafiando el Futuro', 'fr': 'Défier l’Avenir',
            'de': 'Die Zukunft herausfordern', 'it': 'Sfidare il Futuro',
            'nl': 'De Toekomst uitdagen', 'id': 'Menantang Masa Depan',
            'ms': 'Mencabar Masa Depan',
        },
        'closes_in': {
            'pt-BR': 'As inscrições fecham em:', 'en': 'Registrations close in:',
            'es': 'Las inscripciones cierran en:', 'fr': 'Les inscriptions ferment dans :',
            'de': 'Anmeldungen enden in:', 'it': 'Le iscrizioni chiudono tra:',
            'nl': 'Inschrijvingen sluiten over:', 'id': 'Pendaftaran ditutup dalam:',
            'ms': 'Pendaftaran ditutup dalam:',
        },
        'registrations_closed': {
            'pt-BR': 'Inscrições encerradas!', 'en': 'Registrations closed!',
            'es': '¡Inscripciones cerradas!', 'fr': 'Inscriptions clôturées !',
            'de': 'Anmeldungen geschlossen!', 'it': 'Iscrizioni chiuse!',
            'nl': 'Inschrijvingen gesloten!', 'id': 'Pendaftaran ditutup!',
            'ms': 'Pendaftaran ditutup!',
        },
        'cta_register': {
            'pt-BR': 'Inscreva-se Agora', 'en': 'Register Now', 'es': 'Inscríbete Ahora',
            'fr': 'Inscrivez-vous', 'de': 'Jetzt anmelden', 'it': 'Iscriviti Ora',
            'nl': 'Schrijf je nu in', 'id': 'Daftar Sekarang', 'ms': 'Daftar Sekarang',
        },
        'unit_days': {
            'pt-BR': 'dias', 'en': 'days', 'es': 'días', 'fr': 'jours',
            'de': 'Tage', 'it': 'giorni', 'nl': 'dagen', 'id': 'hari', 'ms': 'hari',
        },
        'unit_hours': {
            'pt-BR': 'horas', 'en': 'hours', 'es': 'horas', 'fr': 'heures',
            'de': 'Stunden', 'it': 'ore', 'nl': 'uren', 'id': 'jam', 'ms': 'jam',
        },
        'gallery_archive_label': {
            'pt-BR': 'Arquivo', 'en': 'Archive', 'es': 'Archivo', 'fr': 'Archives',
            'de': 'Archiv', 'it': 'Archivio', 'nl': 'Archief', 'id': 'Arsip', 'ms': 'Arkib',
        },
        'gallery_editions_title': {
            'pt-BR': 'Edições Anteriores', 'en': 'Previous Editions',
            'es': 'Ediciones Anteriores', 'fr': 'Éditions Précédentes',
            'de': 'Frühere Ausgaben', 'it': 'Edizioni Precedenti',
            'nl': 'Eerdere edities', 'id': 'Edisi Sebelumnya', 'ms': 'Edisi Terdahulu',
        },
        'testimonials_next': {
            'pt-BR': 'Próximo', 'en': 'Next', 'es': 'Siguiente', 'fr': 'Suivant',
            'de': 'Weiter', 'it': 'Avanti', 'nl': 'Volgende', 'id': 'Berikutnya', 'ms': 'Seterusnya',
        },
    },
    'sobre': {
        'hero_label': {
            'pt-BR': 'A Liga', 'en': 'The League', 'es': 'La Liga', 'fr': 'La Ligue',
            'de': 'Die Liga', 'it': 'La Lega', 'nl': 'De Liga', 'id': 'Liga', 'ms': 'Liga',
        },
        'breadcrumb_about': {
            'pt-BR': 'Sobre', 'en': 'About', 'es': 'Sobre', 'fr': 'À propos',
            'de': 'Über uns', 'it': 'Chi siamo', 'nl': 'Over ons', 'id': 'Tentang', 'ms': 'Tentang',
        },
        'founding_badge': {
            'pt-BR': 'Fundação — 2024', 'en': 'Founded — 2024', 'es': 'Fundación — 2024',
            'fr': 'Fondation — 2024', 'de': 'Gegründet — 2024', 'it': 'Fondazione — 2024',
            'nl': 'Opgericht — 2024', 'id': 'Didirikan — 2024', 'ms': 'Ditubuhkan — 2024',
        },
        'history_p1': {
            'pt-BR': 'A SESI World Diplomacy League (SWDL) nasceu em 2024 da visão de estudantes do 1º ano do Ensino Médio do SESI CE-437, apaixonados por relações internacionais e diplomacia.',
            'en': 'The SESI World Diplomacy League (SWDL) was born in 2024 from the vision of first-year high school students at SESI CE-437, passionate about international relations and diplomacy.',
            'es': 'La SESI World Diplomacy League (SWDL) nació en 2024 de la visión de estudiantes de primer año de bachillerato del SESI CE-437, apasionados por las relaciones internacionales y la diplomacia.',
            'fr': 'La SESI World Diplomacy League (SWDL) est née en 2024 de la vision d’étudiants de première année de lycée du SESI CE-437, passionnés par les relations internationales et la diplomatie.',
            'de': 'Die SESI World Diplomacy League (SWDL) entstand 2024 aus der Vision von Schülern der ersten Oberstufenklasse der SESI CE-437, die sich für internationale Beziehungen und Diplomatie begeistern.',
            'it': 'La SESI World Diplomacy League (SWDL) è nata nel 2024 dalla visione di studenti del primo anno delle scuole superiori del SESI CE-437, appassionati di relazioni internazionali e diplomazia.',
            'nl': 'De SESI World Diplomacy League (SWDL) ontstond in 2024 vanuit de visie van leerlingen uit het eerste jaar van de bovenbouw van SESI CE-437, gepassioneerd door internationale betrekkingen en diplomatie.',
            'id': 'SESI World Diplomacy League (SWDL) lahir pada 2024 dari visi siswa kelas satu SMA SESI CE-437 yang bersemangat hubungan internasional dan diplomasi.',
            'ms': 'SESI World Diplomacy League (SWDL) lahir pada 2024 daripada visi pelajar tingkatan satu menengah SESI CE-437 yang bersemangat dengan hubungan antarabangsa dan diplomasi.',
        },
        'history_p2': {
            'pt-BR': 'O projeto começou como uma iniciativa para promover simulações realísticas da ONU, oferecendo aos estudantes a oportunidade de experimentar o trabalho diplomático em um ambiente educacional e envolvente.',
            'en': 'The project began as an initiative to promote realistic UN simulations, giving students the chance to experience diplomatic work in an educational and engaging environment.',
            'es': 'El proyecto comenzó como una iniciativa para promover simulaciones realistas de la ONU, ofreciendo a los estudiantes la oportunidad de experimentar el trabajo diplomático en un entorno educativo y atractivo.',
            'fr': "Le projet a commencé comme une initiative pour promouvoir des simulations réalistes de l'ONU, offrant aux étudiants l'occasion de vivre le travail diplomatique dans un environnement éducatif et stimulant.",
            'de': 'Das Projekt begann als Initiative zur Förderung realistischer UN-Simulationen und gab Schülerinnen und Schülern die Chance, diplomatische Arbeit in einer pädagogischen und mitreißenden Umgebung zu erleben.',
            'it': "Il progetto è iniziato come iniziativa per promuovere simulazioni realistiche dell'ONU, offrendo agli studenti l'opportunità di sperimentare il lavoro diplomatico in un ambiente educativo e coinvolgente.",
            'nl': 'Het project begon als initiatief om realistische VN-simulaties te bevorderen en bood leerlingen de kans diplomatiek werk te ervaren in een educatieve en boeiende omgeving.',
            'id': 'Proyek dimulai sebagai inisiatif untuk mempromosikan simulasi PBB yang realistis, memberi siswa kesempatan mengalami kerja diplomatik dalam lingkungan pendidikan yang menarik.',
            'ms': 'Projek bermula sebagai inisiatif untuk menggalakkan simulasi PBB yang realistik, memberi pelajar peluang mengalami kerja diplomatik dalam persekitaran pendidikan yang menarik.',
        },
        'history_p3': {
            'pt-BR': 'Hoje, a SWDL é reconhecida pela qualidade de suas simulações, contando com a participação de dezenas de delegados e com a parceria de instituições educacionais da região.',
            'en': 'Today, SWDL is recognized for the quality of its simulations, with dozens of delegates participating and partnerships with regional educational institutions.',
            'es': 'Hoy, la SWDL es reconocida por la calidad de sus simulaciones, con la participación de decenas de delegados y alianzas con instituciones educativas de la región.',
            "fr": "Aujourd'hui, la SWDL est reconnue pour la qualité de ses simulations, avec la participation de dizaines de délégués et des partenariats avec des institutions éducatives régionales.",
            'de': 'Heute ist die SWDL für die Qualität ihrer Simulationen anerkannt, mit dutzenden Delegierten und Partnerschaften mit regionalen Bildungseinrichtungen.',
            'it': 'Oggi la SWDL è riconosciuta per la qualità delle sue simulazioni, con decine di delegati e partenariati con istituzioni educative della regione.',
            'nl': 'Vandaag staat SWDL bekend om de kwaliteit van zijn simulaties, met tientallen delegaten en samenwerkingen met regionale onderwijsinstellingen.',
            'id': 'Hari ini, SWDL diakui karena kualitas simulasinya, dengan puluhan delegat berpartisipasi dan kemitraan dengan lembaga pendidikan regional.',
            'ms': 'Hari ini, SWDL diiktiraf kerana kualiti simulasinya, dengan penyertaan berpuluh delegat dan perkongsian dengan institusi pendidikan serantau.',
        },
    },
    'comites': {
        'breadcrumb_home': {
            'pt-BR': 'Home', 'en': 'Home', 'es': 'Inicio', 'fr': 'Accueil',
            'de': 'Startseite', 'it': 'Home', 'nl': 'Home', 'id': 'Beranda', 'ms': 'Utama',
        },
        'breadcrumb_themes': {
            'pt-BR': 'Temas', 'en': 'Themes', 'es': 'Temas', 'fr': 'Thèmes',
            'de': 'Themen', 'it': 'Temi', 'nl': "Thema's", 'id': 'Tema', 'ms': 'Tema',
        },
        'watermark': {
            'pt-BR': 'TEMAS', 'en': 'THEMES', 'es': 'TEMAS', 'fr': 'THÈMES',
            'de': 'THEMEN', 'it': 'TEMI', 'nl': "THEMA'S", 'id': 'TEMA', 'ms': 'TEMA',
        },
    },
    'footer': {
        'copyright_swdl': {
            'pt-BR': 'SESI World Diplomacy League', 'en': 'SESI World Diplomacy League',
            'es': 'SESI World Diplomacy League', 'fr': 'SESI World Diplomacy League',
            'de': 'SESI World Diplomacy League', 'it': 'SESI World Diplomacy League',
            'nl': 'SESI World Diplomacy League', 'id': 'SESI World Diplomacy League',
            'ms': 'SESI World Diplomacy League',
        },
    },
}

# gallery items as nested keys under home.gallery_items
gallery_pt = [
    ('g1', 'Sessão Plenária', 'Delegados de todos os comitês reunidos para a sessão de abertura e debates plenários.'),
    ('g2', 'Conselho de Segurança', 'Negociações intensas sobre conflitos internacionais e manutenção da paz.'),
    ('g3', 'Negociações Bilaterais', 'Acordos diplomáticos sendo firmados entre delegações de diferentes nações.'),
    ('g4', 'Premiação Final', 'Reconhecimento dos melhores delegados e delegações da conferência.'),
    ('g5', 'Oratória em Destaque', 'Discursos memoráveis e habilidades de oratória dos delegados.'),
]
gallery_en = [
    ('g1', 'Plenary Session', 'Delegates from all committees gathered for the opening session and plenary debates.'),
    ('g2', 'Security Council', 'Intense negotiations on international conflicts and peacekeeping.'),
    ('g3', 'Bilateral Negotiations', 'Diplomatic agreements being reached between delegations of different nations.'),
    ('g4', 'Final Awards', 'Recognition of the conference’s best delegates and delegations.'),
    ('g5', 'Public Speaking Spotlight', 'Memorable speeches and public speaking skills from the delegates.'),
]

# static committees preview
comm_preview_pt = [
    ('guide', 'Guia do Delegado', 'SWDL — SESI', 'Guia geral obrigatório para todos os delegados.'),
    ('mma', 'Meio Ambiente', 'MMA — UNEP', 'Mudanças climáticas, biodiversidade e desenvolvimento sustentável'),
    ('dhr', 'Direitos Humanos', 'DHR — UNHCR', 'Proteção de minorias, refugiados e liberdades fundamentais'),
    ('ecosoc', 'Desenvolvimento Econômico', 'ECOSOC', 'Comércio internacional, combate à pobreza e finanças globais'),
    ('disec', 'Desarmamento', 'DISEC — ONU', 'Não-proliferação nuclear, controle de armas e segurança cibernética'),
    ('oms', 'Saúde Global', 'OMS — WHO', 'Pandemias, acesso universal à saúde e resposta a emergências'),
    ('acnur', 'Refugiados', 'ACNUR — UNHCR', 'Proteção de pessoas deslocadas por eventos climáticos extremos'),
]
comm_preview_en = [
    ('guide', 'Delegate Guide', 'SWDL — SESI', 'Mandatory general guide for all delegates.'),
    ('mma', 'Environment', 'MMA — UNEP', 'Climate change, biodiversity and sustainable development'),
    ('dhr', 'Human Rights', 'DHR — UNHCR', 'Protection of minorities, refugees and fundamental freedoms'),
    ('ecosoc', 'Economic Development', 'ECOSOC', 'International trade, poverty reduction and global finance'),
    ('disec', 'Disarmament', 'DISEC — UN', 'Nuclear non-proliferation, arms control and cybersecurity'),
    ('oms', 'Global Health', 'OMS — WHO', 'Pandemics, universal health coverage and emergency response'),
    ('acnur', 'Refugees', 'ACNUR — UNHCR', 'Protection of people displaced by extreme climate events'),
]

# legal sections
legal = {
    'aviso_legal': {
        'sections': [
            {
                'title': '1. Propriedade Intelectual',
                'body': 'Todo o conteúdo presente neste site, incluindo textos, imagens, gráficos, marcas, logotipos e demais materiais, são de propriedade da SWDL — SESI World Diplomacy League ou de seus parceiros, sendo protegidos pelas leis de propriedade intelectual brasileiras e internacionais.',
            },
            {
                'title': '2. Uso do Site',
                'body': 'O uso deste site implica na aceitação dos presentes termos legais. O usuário se compromete a utilizar o site de forma ética e em conformidade com a legislação vigente.',
            },
            {
                'title': '3. Links Externos',
                'body': 'Este site pode conter links para sites de terceiros. A SWDL não se responsabiliza pelo conteúdo, políticas de privacidade ou práticas de sites externos.',
            },
            {
                'title': '4. Isenção de Responsabilidade',
                'body': 'As informações contidas neste site são fornecidas "como estão", sem garantias de qualquer tipo, expressas ou implícitas. A SWDL não se responsabiliza por danos diretos ou indiretos decorrentes do uso deste site.',
            },
            {
                'title': '5. Alterações',
                'body': 'A SWDL reserva-se o direito de alterar estes termos legais a qualquer momento, sem aviso prévio. As alterações entram em vigor imediatamente após a publicação no site.',
            },
            {
                'title': '6. Contato',
                'body': 'Em caso de dúvidas sobre estes termos legais, entre em contato pelo e-mail: pedro.pereira63@portalsesisp.org.br',
            },
        ],
        'sections_en': [
            {
                'title': '1. Intellectual Property',
                'body': 'All content on this site, including texts, images, graphics, trademarks, logos and other materials, is owned by SWDL — SESI World Diplomacy League or its partners, and is protected by Brazilian and international intellectual property laws.',
            },
            {
                'title': '2. Use of the Site',
                'body': 'Use of this site implies acceptance of these legal terms. The user agrees to use the site ethically and in compliance with applicable legislation.',
            },
            {
                'title': '3. External Links',
                'body': 'This site may contain links to third-party sites. SWDL is not responsible for the content, privacy policies or practices of external sites.',
            },
            {
                'title': '4. Disclaimer',
                'body': 'The information on this site is provided "as is", without warranties of any kind, express or implied. SWDL is not liable for direct or indirect damages arising from the use of this site.',
            },
            {
                'title': '5. Changes',
                'body': 'SWDL reserves the right to change these legal terms at any time without prior notice. Changes take effect immediately after publication on the site.',
            },
            {
                'title': '6. Contact',
                'body': 'If you have questions about these legal terms, contact us at: pedro.pereira63@portalsesisp.org.br',
            },
        ],
    },
    'privacidade': {
        'sections': [
            {'title': '1. Dados Coletados', 'body': 'Para participar da SWDL, coletamos os seguintes dados pessoais durante o processo de inscrição: nome completo, e-mail, telefone, Instagram, nome da escola, série escolar e motivação para participação.'},
            {'title': '2. Finalidade dos Dados', 'body': 'Os dados coletados são utilizados exclusivamente para: (a) processamento de inscrições; (b) comunicação sobre o evento; (c) emissão de certificados; e (d) melhoria da experiência dos participantes.'},
            {'title': '3. Base Legal (LGPD)', 'body': 'O tratamento de dados é realizado com base no consentimento do titular (Art. 7º, I da Lei 13.709/2018) e na execução de contrato ou de procedimentos preliminares relacionados a contrato (Art. 7º, V).'},
            {'title': '4. Compartilhamento de Dados', 'body': 'Seus dados pessoais não serão compartilhados com terceiros, exceto quando necessário para cumprimento de obrigação legal ou regulatória, ou mediante consentimento expresso do titular.'},
            {'title': '5. Retenção de Dados', 'body': 'Os dados serão mantidos pelo período necessário para cumprir as finalidades para as quais foram coletados, ou pelo período exigido pela legislação aplicável.'},
            {'title': '6. Direitos do Titular', 'body': 'Conforme a LGPD, você tem direito a: acesso aos dados, correção de dados incompletos ou desatualizados, anonimização, bloqueio ou eliminação de dados desnecessários, portabilidade, e eliminação dos dados tratados com consentimento.'},
            {'title': '7. Segurança dos Dados', 'body': 'Adotamos medidas técnicas e administrativas adequadas para proteger os dados pessoais contra acessos não autorizados e situações acidentais ou ilícitas de destruição, perda, alteração ou comunicação indevida.'},
            {'title': '8. Contato', 'body': 'Para exercer seus direitos ou esclarecer dúvidas sobre esta política, entre em contato: pedro.pereira63@portalsesisp.org.br'},
        ],
        'sections_en': [
            {'title': '1. Data Collected', 'body': 'To participate in SWDL, we collect the following personal data during registration: full name, email, phone, Instagram, school name, grade and motivation for participating.'},
            {'title': '2. Purpose of Data', 'body': 'Collected data is used exclusively for: (a) processing registrations; (b) event communications; (c) issuing certificates; and (d) improving the participant experience.'},
            {'title': '3. Legal Basis (LGPD)', 'body': 'Data processing is based on the data subject’s consent (Art. 7, I of Law 13.709/2018) and on the performance of a contract or preliminary procedures related to a contract (Art. 7, V).'},
            {'title': '4. Data Sharing', 'body': 'Your personal data will not be shared with third parties, except when necessary to comply with a legal or regulatory obligation, or with the data subject’s express consent.'},
            {'title': '5. Data Retention', 'body': 'Data will be kept for the period necessary to fulfill the purposes for which it was collected, or for the period required by applicable legislation.'},
            {'title': '6. Data Subject Rights', 'body': 'Under the LGPD, you have the right to: access data, correct incomplete or outdated data, anonymize, block or delete unnecessary data, portability, and deletion of data processed with consent.'},
            {'title': '7. Data Security', 'body': 'We adopt appropriate technical and administrative measures to protect personal data against unauthorized access and accidental or unlawful destruction, loss, alteration or disclosure.'},
            {'title': '8. Contact', 'body': 'To exercise your rights or ask questions about this policy, contact: pedro.pereira63@portalsesisp.org.br'},
        ],
    },
    'termos': {
        'sections': [
            {'title': '1. Aceitação dos Termos', 'body': 'Ao acessar e utilizar o site da SWDL — SESI World Diplomacy League, você concorda com estes Termos de Uso. Caso não concorde, não utilize o site.'},
            {'title': '2. Uso do Site', 'body': 'O site é fornecido para fins informativos e de inscrição no evento SWDL. Você concorda em utilizar o site de forma ética e em conformidade com a legislação vigente.'},
            {'title': '3. Inscrições', 'body': 'Ao se inscrever na SWDL, você declara que: (a) as informações fornecidas são verdadeiras; (b) possui entre 14 e 19 anos de idade; (c) é estudante do SESI ou de escola parceira; e (d) aceita as regras e regulamentos do evento.'},
            {'title': '4. Conduta dos Participantes', 'body': 'Os participantes devem manter um comportamento respeitoso durante o evento. A organização reserva-se o direito de desqualificar participantes que descumprirem as regras de conduta.'},
            {'title': '5. Propriedade Intelectual', 'body': 'Todo o conteúdo produzido durante o evento (resoluções, discursos, trabalhos) é de propriedade dos autores, sendo concedida à SWDL uma licença não exclusiva para uso em materiais promocionais.'},
            {'title': '6. Limitação de Responsabilidade', 'body': 'A SWDL não se responsabiliza por danos diretos ou indiretos decorrentes da participação no evento, incluindo mas não se limitando a: cancelamento do evento, alterações de programação, ou force majeure.'},
            {'title': '7. Cancelamento e Devolução', 'body': 'Em caso de cancelamento do evento pela organização, os inscritos serão notificados por e-mail. Não há previsão de devolução de valores, uma vez que o evento é gratuito.'},
            {'title': '8. Alterações nos Termos', 'body': 'A SWDL reserva-se o direito de alterar estes Termos de Uso a qualquer momento. As alterações entram em vigor imediatamente após a publicação no site.'},
            {'title': '9. Contato', 'body': 'Em caso de dúvidas sobre estes Termos, entre em contato: pedro.pereira63@portalsesisp.org.br'},
        ],
        'sections_en': [
            {'title': '1. Acceptance of Terms', 'body': 'By accessing and using the SWDL — SESI World Diplomacy League website, you agree to these Terms of Use. If you do not agree, do not use the site.'},
            {'title': '2. Use of the Site', 'body': 'The site is provided for informational and SWDL event registration purposes. You agree to use the site ethically and in compliance with applicable legislation.'},
            {'title': '3. Registrations', 'body': 'By registering for SWDL, you declare that: (a) the information provided is true; (b) you are between 14 and 19 years old; (c) you are a student of SESI or a partner school; and (d) you accept the event rules and regulations.'},
            {'title': '4. Participant Conduct', 'body': 'Participants must behave respectfully during the event. The organization reserves the right to disqualify participants who break the code of conduct.'},
            {'title': '5. Intellectual Property', 'body': 'All content produced during the event (resolutions, speeches, papers) belongs to the authors, with SWDL granted a non-exclusive license for use in promotional materials.'},
            {'title': '6. Limitation of Liability', 'body': 'SWDL is not liable for direct or indirect damages arising from participation in the event, including but not limited to: event cancellation, schedule changes, or force majeure.'},
            {'title': '7. Cancellation and Refunds', 'body': 'If the event is cancelled by the organization, registrants will be notified by email. There is no refund, as the event is free of charge.'},
            {'title': '8. Changes to Terms', 'body': 'SWDL reserves the right to change these Terms of Use at any time. Changes take effect immediately after publication on the site.'},
            {'title': '9. Contact', 'body': 'If you have questions about these Terms, contact: pedro.pereira63@portalsesisp.org.br'},
        ],
    },
}

def deep_set(obj, path, value):
    parts = path.split('.')
    cur = obj
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value

for p in sorted(ROOT.glob('*.json')):
    loc = p.stem
    data = load(p)

    for ns, keys in new_keys.items():
        data.setdefault(ns, {})
        for k, by_loc in keys.items():
            if k not in data[ns]:
                data[ns][k] = by_loc.get(loc) or by_loc.get('pt-BR') or by_loc.get('en') or k

    # gallery items
    data.setdefault('home', {}).setdefault('gallery_items', {})
    for i, (key, title, desc) in enumerate(gallery_pt):
        if loc == 'en':
            title, desc = gallery_en[i][1], gallery_en[i][2]
        node = data['home']['gallery_items'].setdefault(key, {})
        node.setdefault('title', title)
        node.setdefault('desc', desc)

    # committee preview
    data['home'].setdefault('committee_preview', {})
    for i, (key, name, tag, desc) in enumerate(comm_preview_pt):
        if loc == 'en':
            name, tag, desc = comm_preview_en[i][1], comm_preview_en[i][2], comm_preview_en[i][3]
        node = data['home']['committee_preview'].setdefault(key, {})
        node.setdefault('name', name)
        node.setdefault('tag', tag)
        node.setdefault('desc', desc)

    # legal sections
    for ns, pack in legal.items():
        data.setdefault(ns, {})
        sections = pack['sections_en'] if loc == 'en' else pack['sections']
        # for non-pt non-en use en if available else pt
        if loc not in ('pt-BR', 'en'):
            sections = pack.get('sections_en') or pack['sections']
        if 'sections' not in data[ns] or not isinstance(data[ns].get('sections'), list) or len(data[ns].get('sections') or []) != len(sections):
            data[ns]['sections'] = sections
        elif loc == 'en':
            data[ns]['sections'] = sections

    save(p, data)
    print('updated', loc)

print('done')
