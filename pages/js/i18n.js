/* ============================================================
   SWDL — i18n.js
   Sistema de internacionalização com dropdown + tradução
   ============================================================ */

const SWDL_I18N = {
  lang: 'pt-BR',
  available: [
    { code: 'pt-BR', label: 'Português (Brasil)', flag: '🇧🇷' },
    { code: 'en',    label: 'English',             flag: '🇬🇧' },
    { code: 'es',    label: 'Español',             flag: '🇪🇸' },
    { code: 'fr',    label: 'Français',            flag: '🇫🇷' },
    { code: 'de',    label: 'Deutsch',             flag: '🇩🇪' },
    { code: 'it',    label: 'Italiano',            flag: '🇮🇹' },
    { code: 'nl',    label: 'Nederlands',          flag: '🇳🇱' },
    { code: 'id',    label: 'Bahasa Indonesia',    flag: '🇮🇩' },
    { code: 'ms',    label: 'Bahasa Melayu',       flag: '🇲🇾' },
  ],

  dict: {
    // ── NAVEGAÇÃO ──────────────────────────────────────────────
    'nav.home': {
      'pt-BR': 'Home', 'en': 'Home', 'es': 'Inicio', 'fr': 'Accueil',
      'de': 'Start', 'it': 'Home', 'nl': 'Home', 'id': 'Beranda', 'ms': 'Laman Utama'
    },
    'nav.noticias': {
      'pt-BR': 'Notícias', 'en': 'News', 'es': 'Noticias', 'fr': 'Actualités',
      'de': 'Nachrichten', 'it': 'Notizie', 'nl': 'Nieuws', 'id': 'Berita', 'ms': 'Berita'
    },
    'nav.comites': {
      'pt-BR': 'Temas', 'en': 'Committees', 'es': 'Comités', 'fr': 'Comités',
      'de': 'Ausschüsse', 'it': 'Comitati', 'nl': 'Comités', 'id': 'Komite', 'ms': 'Jawatankuasa'
    },
    'nav.agenda': {
      'pt-BR': 'Agenda', 'en': 'Schedule', 'es': 'Agenda', 'fr': 'Agenda',
      'de': 'Zeitplan', 'it': 'Agenda', 'nl': 'Agenda', 'id': 'Jadwal', 'ms': 'Jadual'
    },
    'nav.sobre': {
      'pt-BR': 'Sobre', 'en': 'About', 'es': 'Acerca', 'fr': 'À propos',
      'de': 'Über uns', 'it': 'Informazioni', 'nl': 'Over ons', 'id': 'Tentang', 'ms': 'Tentang'
    },
    'nav.faca_parte': {
      'pt-BR': 'Faça Parte', 'en': 'Join Us', 'es': 'Participa', 'fr': 'Participer',
      'de': 'Mitmachen', 'it': 'Partecipa', 'nl': 'Doe Mee', 'id': 'Ikut Serta', 'ms': 'Sertai'
    },

    // ── CRISIS BANNER ──────────────────────────────────────────
    'crisis_banner.close': {
      'pt-BR': 'Fechar alerta', 'en': 'Close alert', 'es': 'Cerrar alerta',
      'fr': 'Fermer alerte', 'de': 'Alarm schließen', 'it': 'Chiudi avviso',
      'nl': 'Sluit waarschuwing', 'id': 'Tutup peringatan', 'ms': 'Tutup amaran'
    },

    // ── FOOTER ─────────────────────────────────────────────────
    'footer.brand_desc': {
      'pt-BR': 'A liga que transforma alunos em diplomatas.<br>SESI CE-437, Hortolândia.',
      'en': 'The league that turns students into diplomats.<br>SESI CE-437, Hortolândia.',
      'es': 'La liga que transforma alumnos en diplomáticos.<br>SESI CE-437, Hortolândia.',
      'fr': 'La ligue qui transforme les élèves en diplomates.<br>SESI CE-437, Hortolândia.',
      'de': 'Die Liga, die Schüler zu Diplomaten macht.<br>SESI CE-437, Hortolândia.',
      'it': 'La lega che trasforma gli studenti in diplomatici.<br>SESI CE-437, Hortolândia.',
      'nl': 'De competitie die studenten in diplomaten verandert.<br>SESI CE-437, Hortolândia.',
      'id': 'Liga yang mengubah siswa menjadi diplomat.<br>SESI CE-437, Hortolândia.',
      'ms': 'Liga yang mengubah pelajar menjadi diplomat.<br>SESI CE-437, Hortolândia.'
    },
    'footer.links_title': {
      'pt-BR': 'Links Rápidos', 'en': 'Quick Links', 'es': 'Enlaces Rápidos',
      'fr': 'Liens Rapides', 'de': 'Schnelllinks', 'it': 'Link Veloci',
      'nl': 'Snelle Links', 'id': 'Tautan Cepat', 'ms': 'Pautan Pantas'
    },
    'footer.sobre_link': {
      'pt-BR': 'Sobre', 'en': 'About', 'es': 'Acerca', 'fr': 'À propos',
      'de': 'Über uns', 'it': 'Informazioni', 'nl': 'Over ons', 'id': 'Tentang', 'ms': 'Tentang'
    },
    'footer.noticias_link': {
      'pt-BR': 'Notícias', 'en': 'News', 'es': 'Noticias', 'fr': 'Actualités',
      'de': 'Nachrichten', 'it': 'Notizie', 'nl': 'Nieuws', 'id': 'Berita', 'ms': 'Berita'
    },
    'footer.agenda_link': {
      'pt-BR': 'Agenda', 'en': 'Schedule', 'es': 'Agenda', 'fr': 'Agenda',
      'de': 'Zeitplan', 'it': 'Agenda', 'nl': 'Agenda', 'id': 'Jadwal', 'ms': 'Jadual'
    },
    'footer.comites_link': {
      'pt-BR': 'Recursos', 'en': 'Resources', 'es': 'Recursos', 'fr': 'Ressources',
      'de': 'Ressourcen', 'it': 'Risorse', 'nl': 'Bronnen', 'id': 'Sumber Daya', 'ms': 'Sumber'
    },
    'footer.faca_parte_link': {
      'pt-BR': 'Faça Parte', 'en': 'Join Us', 'es': 'Participa', 'fr': 'Participer',
      'de': 'Mitmachen', 'it': 'Partecipa', 'nl': 'Doe Mee', 'id': 'Ikut Serta', 'ms': 'Sertai'
    },
    'footer.contato_title': {
      'pt-BR': 'Contato', 'en': 'Contact', 'es': 'Contacto', 'fr': 'Contact',
      'de': 'Kontakt', 'it': 'Contatto', 'nl': 'Contact', 'id': 'Kontak', 'ms': 'Hubungi'
    },
    'footer.email_link': {
      'pt-BR': 'pedro.pereira63@portalsesisp.org.br',
      'en': 'pedro.pereira63@portalsesisp.org.br',
      'es': 'pedro.pereira63@portalsesisp.org.br',
      'fr': 'pedro.pereira63@portalsesisp.org.br',
      'de': 'pedro.pereira63@portalsesisp.org.br',
      'it': 'pedro.pereira63@portalsesisp.org.br',
      'nl': 'pedro.pereira63@portalsesisp.org.br',
      'id': 'pedro.pereira63@portalsesisp.org.br',
      'ms': 'pedro.pereira63@portalsesisp.org.br'
    },
    'footer.endereco_link': {
      'pt-BR': 'SESI CE-437, Hortolândia', 'en': 'SESI CE-437, Hortolândia',
      'es': 'SESI CE-437, Hortolândia', 'fr': 'SESI CE-437, Hortolândia',
      'de': 'SESI CE-437, Hortolândia', 'it': 'SESI CE-437, Hortolândia',
      'nl': 'SESI CE-437, Hortolândia', 'id': 'SESI CE-437, Hortolândia',
      'ms': 'SESI CE-437, Hortolândia'
    },
    'footer.copyright': {
      'pt-BR': '© 2025 SESI World Diplomacy League — Desenvolvido por <strong>Pedro Bonazzi</strong>',
      'en': '© 2025 SESI World Diplomacy League — Developed by <strong>Pedro Bonazzi</strong>',
      'es': '© 2025 SESI World Diplomacy League — Desarrollado por <strong>Pedro Bonazzi</strong>',
      'fr': '© 2025 SESI World Diplomacy League — Développé par <strong>Pedro Bonazzi</strong>',
      'de': '© 2025 SESI World Diplomacy League — Entwickelt von <strong>Pedro Bonazzi</strong>',
      'it': '© 2025 SESI World Diplomacy League — Sviluppato da <strong>Pedro Bonazzi</strong>',
      'nl': '© 2025 SESI World Diplomacy League — Ontwikkeld door <strong>Pedro Bonazzi</strong>',
      'id': '© 2025 SESI World Diplomacy League — Dikembangkan oleh <strong>Pedro Bonazzi</strong>',
      'ms': '© 2025 SESI World Diplomacy League — Dibangun oleh <strong>Pedro Bonazzi</strong>'
    },
    'footer.privacy_link': {
      'pt-BR': 'Política de Privacidade', 'en': 'Privacy Policy', 'es': 'Política de Privacidad',
      'fr': 'Politique de Confidentialité', 'de': 'Datenschutzrichtlinie', 'it': 'Informativa sulla Privacy',
      'nl': 'Privacybeleid', 'id': 'Kebijakan Privasi', 'ms': 'Dasar Privasi'
    },
    'footer.terms_link': {
      'pt-BR': 'Termos de Uso', 'en': 'Terms of Use', 'es': 'Términos de Uso',
      'fr': "Conditions d'Utilisation", 'de': 'Nutzungsbedingungen', 'it': 'Termini di Utilizzo',
      'nl': 'Gebruiksvoorwaarden', 'id': 'Ketentuan Penggunaan', 'ms': 'Syarat Penggunaan'
    },
    'footer.legal_title': {
      'pt-BR': 'Legal', 'en': 'Legal', 'es': 'Legal', 'fr': 'Mentions Légales',
      'de': 'Rechtliches', 'it': 'Note Legali', 'nl': 'Juridisch', 'id': 'Hukum', 'ms': 'Perundangan'
    },
    'footer.aviso_link': {
      'pt-BR': 'Aviso Legal', 'en': 'Legal Notice', 'es': 'Aviso Legal', 'fr': 'Mentions Légales',
      'de': 'Impressum', 'it': 'Avviso Legale', 'nl': 'Juridische Kennisgeving', 'id': 'Pemberitahuan Hukum', 'ms': 'Notis Undang-undang'
    },

    // ── HOME / INDEX ───────────────────────────────────────────
    'home.page_title': { 'pt-BR': 'SWDL — SESI World Diplomacy League', 'en': 'SWDL — SESI World Diplomacy League' },
    'home.hero_tag': { 'pt-BR': 'Edição 2026 — Em Andamento', 'en': '2026 Edition — In Progress' },
    'home.hero_title': { 'pt-BR': 'Diplomacia.\n        <em>Estratégia.</em>\n        Liderança.', 'en': 'Diplomacy.\n        <em>Strategy.</em>\n        Leadership.' },
    'home.hero_sub': { 'pt-BR': 'Fundação de Simulações da ONU do SESI CE-437 Hortolândia. Represente nações, estabeleça novas alianças, debata resoluções e construa acordos que moldam o mundo contemporâneo.', 'en': 'UN Simulation Foundation of SESI CE-437 Hortolândia. Represent nations, establish new alliances, debate resolutions and build agreements that shape the contemporary world.' },
    'home.hero_btn_parte': { 'pt-BR': 'Faça Parte →', 'en': 'Join Us →' },
    'home.hero_btn_temas': { 'pt-BR': 'Ver Temas', 'en': 'View Committees' },
    'home.hero_stat_temas': { 'pt-BR': 'Temas', 'en': 'Committees' },
    'home.hero_stat_delegados': { 'pt-BR': 'Delegados', 'en': 'Delegates' },
    'home.hero_stat_paises': { 'pt-BR': 'Países', 'en': 'Countries' },
    'home.hero_pais_brasil': { 'pt-BR': 'Brasil', 'en': 'Brazil', 'es': 'Brasil', 'fr': 'Brésil', 'de': 'Brasilien', 'it': 'Brasile', 'nl': 'Brazilië', 'id': 'Brasil', 'ms': 'Brazil' },
    'home.hero_pais_alemanha': { 'pt-BR': 'Alemanha', 'en': 'Germany', 'es': 'Alemania', 'fr': 'Allemagne', 'de': 'Deutschland', 'it': 'Germania', 'nl': 'Duitsland', 'id': 'Jerman', 'ms': 'Jerman' },
    'home.hero_pais_japao': { 'pt-BR': 'Japão', 'en': 'Japan', 'es': 'Japón', 'fr': 'Japon', 'de': 'Japan', 'it': 'Giappone', 'nl': 'Japan', 'id': 'Jepang', 'ms': 'Jepun' },
    'home.hero_pais_eua': { 'pt-BR': 'Estados Unidos', 'en': 'United States', 'es': 'Estados Unidos', 'fr': 'États-Unis', 'de': 'Vereinigte Staaten', 'it': 'Stati Uniti', 'nl': 'Verenigde Staten', 'id': 'Amerika Serikat', 'ms': 'Amerika Syarikat' },
    'home.hero_globe': { 'pt-BR': 'SWDL', 'en': 'SWDL' },
    'home.ticker_label': { 'pt-BR': '📡 Ao Vivo', 'en': '📡 Live' },
    'home.ticker_item': { 'pt-BR': 'SWDL 2025 — Aguardando notícias...', 'en': 'SWDL 2025 — Awaiting news...' },
    'home.stat_paises': { 'pt-BR': 'Países Representados', 'en': 'Countries Represented' },
    'home.stat_delegados': { 'pt-BR': 'Delegados Inscritos', 'en': 'Registered Delegates' },
    'home.stat_temas': { 'pt-BR': 'Temas', 'en': 'Committees' },
    'home.stat_edicoes': { 'pt-BR': 'Edições Realizadas', 'en': 'Editions Held' },
    'home.noticias_label': { 'pt-BR': 'Cobertura ao Vivo', 'en': 'Live Coverage' },
    'home.noticias_title': { 'pt-BR': 'Central de Notícias', 'en': 'News Center' },
    'home.noticia1_tag': { 'pt-BR': '🚨 Crise — CS', 'en': '🚨 Crisis — SC' },
    'home.noticia1_titulo': { 'pt-BR': 'Tensão no Conselho de Segurança: França e Rússia debatem intervenção humanitária em zona de conflito', 'en': 'Tension in the Security Council: France and Russia debate humanitarian intervention in conflict zone' },
    'home.noticia1_desc': { 'pt-BR': 'A sessão que começou com discussões sobre a Resolução 07 transformou-se em debate acalorado após a delegação francesa apresentar evidências de violações ao direito internacional.', 'en': 'The session that began with discussions on Resolution 07 turned into a heated debate after the French delegation presented evidence of violations of international law.' },
    'home.noticia1_meta': { 'pt-BR': 'Conselho de Segurança', 'en': 'Security Council' },
    'home.noticia1_tempo': { 'pt-BR': 'há 12 min', 'en': '12 min ago' },
    'home.noticia2_tag': { 'pt-BR': '📋 Oficial — MMA', 'en': '📋 Official — UNEP' },
    'home.noticia2_titulo': { 'pt-BR': 'Resolução 03 aprovada: metas climáticas ampliadas para 2030', 'en': 'Resolution 03 approved: climate targets expanded for 2030' },
    'home.noticia2_meta': { 'pt-BR': 'Meio Ambiente', 'en': 'Environment' },
    'home.noticia2_tempo': { 'pt-BR': 'há 34 min', 'en': '34 min ago' },
    'home.noticia3_tag': { 'pt-BR': '📰 Imprensa — DISEC', 'en': '📰 Press — DISEC' },
    'home.noticia3_titulo': { 'pt-BR': 'Bastidores: como a dupla Brasil chegou à proposta que mudou o debate sobre desarmamento', 'en': 'Behind the scenes: how the Brazilian duo reached the proposal that changed the disarmament debate' },
    'home.noticia3_meta': { 'pt-BR': 'Desarmamento', 'en': 'Disarmament' },
    'home.noticia3_tempo': { 'pt-BR': 'há 1h', 'en': '1h ago' },
    'home.news_ver_todas': { 'pt-BR': 'Ver todas as notícias →', 'en': 'View all news →' },
    'home.comites_label': { 'pt-BR': 'Estrutura do Evento', 'en': 'Event Structure' },
    'home.comites_title': { 'pt-BR': 'Temas', 'en': 'Committees' },
    'home.comites_desc': { 'pt-BR': 'Cada comitê simula um órgão real das Nações Unidas. Os delegados debatem temas contemporâneos, propõem resoluções e votam em tempo real.', 'en': 'Each committee simulates a real United Nations body. Delegates debate contemporary issues, propose resolutions and vote in real time.' },
    'home.comites_btn': { 'pt-BR': 'Ver todos os Temas →', 'en': 'View all Committees →' },
    'home.comite_guia_nome': { 'pt-BR': 'Guia do Delegado', 'en': "Delegate's Guide" },
    'home.comite_guia_desc': { 'pt-BR': 'Guia geral obrigatorio', 'en': 'Mandatory general guide' },
    'home.comite_guia_tag': { 'pt-BR': 'SWDL — SESI', 'en': 'SWDL — SESI' },
    'home.comite_ma_nome': { 'pt-BR': 'Meio Ambiente', 'en': 'Environment' },
    'home.comite_ma_desc': { 'pt-BR': 'Mudanças climáticas, biodiversidade e desenvolvimento sustentável', 'en': 'Climate change, biodiversity and sustainable development' },
    'home.comite_ma_tag': { 'pt-BR': 'MMA — UNEP', 'en': 'UNEP — UNEP' },
    'home.comite_dh_nome': { 'pt-BR': 'Direitos Humanos', 'en': 'Human Rights' },
    'home.comite_dh_desc': { 'pt-BR': 'Proteção de minorias, refugiados e liberdades fundamentais', 'en': 'Protection of minorities, refugees and fundamental freedoms' },
    'home.comite_dh_tag': { 'pt-BR': 'DHR — UNHCR', 'en': 'DHR — UNHCR' },
    'home.comite_eco_nome': { 'pt-BR': 'Desenvolvimento Econômico', 'en': 'Economic Development' },
    'home.comite_eco_desc': { 'pt-BR': 'Comércio internacional, combate à pobreza e finanças globais', 'en': 'International trade, poverty alleviation and global finance' },
    'home.comite_eco_tag': { 'pt-BR': 'ECOSOC', 'en': 'ECOSOC' },
    'home.comite_dis_nome': { 'pt-BR': 'Desarmamento', 'en': 'Disarmament' },
    'home.comite_dis_desc': { 'pt-BR': 'Não-proliferação nuclear, controle de armas e segurança cibernética', 'en': 'Nuclear non-proliferation, arms control and cybersecurity' },
    'home.comite_dis_tag': { 'pt-BR': 'DISEC — ONU', 'en': 'DISEC — UN' },
    'home.comite_saude_nome': { 'pt-BR': 'Saúde Global', 'en': 'Global Health' },
    'home.comite_saude_desc': { 'pt-BR': 'Pandemias, acesso universal à saúde e resposta a emergências', 'en': 'Pandemics, universal health access and emergency response' },
    'home.comite_saude_tag': { 'pt-BR': 'OMS — WHO', 'en': 'WHO — WHO' },
    'home.comite_acnur_nome': { 'pt-BR': 'Refugiados', 'en': 'Refugees' },
    'home.comite_acnur_desc': { 'pt-BR': 'Proteção de pessoas deslocadas por eventos climáticos extremos', 'en': 'Protection of people displaced by extreme climate events' },
    'home.comite_acnur_tag': { 'pt-BR': 'ACNUR — UNHCR', 'en': 'UNHCR — ACNUR' },
    'home.agenda_label': { 'pt-BR': 'Cronograma', 'en': 'Schedule' },
    'home.agenda_title': { 'pt-BR': 'Agenda<br>do Evento', 'en': 'Event<br>Schedule' },
    'home.agenda_desc': { 'pt-BR': 'O cronograma é atualizado em tempo real pelo painel administrativo, destacando sempre a atividade em curso.', 'en': 'The schedule is updated in real time by the administrative panel, always highlighting the current activity.' },
    'home.agenda_btn': { 'pt-BR': 'Ver cronograma completo', 'en': 'View full schedule' },
    'home.agenda_loading': { 'pt-BR': 'Carregando agenda...', 'en': 'Loading schedule...' },
    'home.galeria_label': { 'pt-BR': 'Arquivo', 'en': 'Archive' },
    'home.galeria_title': { 'pt-BR': 'Edições Anteriores', 'en': 'Previous Editions' },
    'home.galeria_btn': { 'pt-BR': 'Ver galeria completa →', 'en': 'View full gallery →' },
    'home.galeria_sessao': { 'pt-BR': 'Sessão Plenária', 'en': 'Plenary Session' },
    'home.galeria_conselho': { 'pt-BR': 'Conselho de Segurança', 'en': 'Security Council' },
    'home.galeria_negociacoes': { 'pt-BR': 'Negociações Bilaterais', 'en': 'Bilateral Negotiations' },
    'home.galeria_premiacao': { 'pt-BR': 'Premiação Final', 'en': 'Final Awards' },
    'home.galeria_oratoria': { 'pt-BR': 'Oratória em Destaque', 'en': 'Featured Oratory' },
    'home.galeria_item_ano1': { 'pt-BR': 'SWDL 2025', 'en': 'SWDL 2025' },
    'home.galeria_item_ano2': { 'pt-BR': 'SWDL 2025', 'en': 'SWDL 2025' },
    'home.galeria_item_ano3': { 'pt-BR': 'SWDL 2025', 'en': 'SWDL 2025' },
    'home.galeria_item_ano4': { 'pt-BR': 'SWDL 2025', 'en': 'SWDL 2025' },
    'home.galeria_item_ano5': { 'pt-BR': 'SWDL 2025', 'en': 'SWDL 2025' },

    // ── SOBRE ──────────────────────────────────────────────────
    'sobre.page_title': { 'pt-BR': 'Sobre — SWDL', 'en': 'About — SWDL' },
    'sobre.breadcrumb_home': { 'pt-BR': 'Home', 'en': 'Home' },
    'sobre.breadcrumb_current': { 'pt-BR': 'Sobre', 'en': 'About' },
    'sobre.hero_label': { 'pt-BR': 'A Liga', 'en': 'The League' },
    'sobre.hero_title': { 'pt-BR': 'Sobre a SWDL', 'en': 'About SWDL' },
    'sobre.hero_subtitle': { 'pt-BR': 'Conheça nossa história, missão e valores', 'en': 'Learn about our history, mission and values' },
    'sobre.missao_title': { 'pt-BR': 'Missão', 'en': 'Mission', 'es': 'Misión', 'fr': 'Mission', 'de': 'Mission', 'it': 'Missione', 'nl': 'Missie' },
    'sobre.missao_text': { 'pt-BR': 'Formar jovens líderes capacitados para enfrentar os desafios globais contemporâneos através de simulações realísticas da ONU, desenvolvendo habilidades diplomáticas, de negociação e pensamento crítico.', 'en': 'To train young leaders capable of facing contemporary global challenges through realistic UN simulations, developing diplomatic, negotiation and critical thinking skills.' },
    'sobre.visao_title': { 'pt-BR': 'Visão', 'en': 'Vision', 'es': 'Visión', 'fr': 'Vision', 'de': 'Vision', 'it': 'Visione', 'nl': 'Visie' },
    'sobre.visao_text': { 'pt-BR': 'Formar futuros membros que posteriormente ingressarão no comitê. Além disso, estabelecer parcerias com órgãos externos com a finalidade de criar um ambiente para ambos participantes internos e externos. Adicionalmente, inspirar novas gerações de líderes comprometidos com a paz, justiça e cooperação internacional.', 'en': 'Train future members who will later join the committee. Also, establish partnerships with external bodies to create an environment for both internal and external participants. Additionally, inspire new generations of leaders committed to peace, justice and international cooperation.' },
    'sobre.valores_label': { 'pt-BR': 'Nossos Pilares', 'en': 'Our Pillars' },
    'sobre.valores_title': { 'pt-BR': 'Valores', 'en': 'Values', 'es': 'Valores', 'fr': 'Valeurs', 'de': 'Werte', 'it': 'Valori', 'nl': 'Waarden' },
    'sobre.valor_diplomacia': { 'pt-BR': 'Diplomacia e Diálogo', 'en': 'Diplomacy and Dialogue' },
    'sobre.valor_respeito': { 'pt-BR': 'Respeito à Diversidade', 'en': 'Respect for Diversity' },
    'sobre.valor_excelencia': { 'pt-BR': 'Excelência Acadêmica', 'en': 'Academic Excellence' },
    'sobre.valor_cooperacao': { 'pt-BR': 'Cooperação Internacional', 'en': 'International Cooperation' },
    'sobre.valor_desenvolvimento': { 'pt-BR': 'Desenvolvimento Sustentável', 'en': 'Sustainable Development' },
    'sobre.historia_year': { 'pt-BR': 'Fundação — 2024 · SESI CE-437', 'en': 'Founded — 2024 · SESI CE-437' },
    'sobre.historia_text1': { 'pt-BR': 'A SESI World Diplomacy League (SWDL) nasceu em 2024 da visão de estudantes do 1º ano do Ensino Médio do SESI CE-437, apaixonados por relações internacionais e diplomacia.', 'en': 'The SESI World Diplomacy League (SWDL) was born in 2024 from the vision of 1st year high school students at SESI CE-437, passionate about international relations and diplomacy.' },
    'sobre.historia_text2': { 'pt-BR': 'O projeto começou como uma iniciativa para promover simulações realísticas da ONU, capacitando jovens a partir do 6º ano. Desde o primeiro debate, a SWDL tem crescido, impactando dezenas de estudantes com discussões sobre temas globais desde educação e igualdade de gênero, até disputas politicas e militares', 'en': 'The project began as an initiative to promote realistic UN simulations, empowering young people from 6th grade onward. Since the first debate, SWDL has grown, impacting dozens of students with discussions on global topics from education and gender equality to political and military disputes.' },
    'sobre.historia_text3': { 'pt-BR': 'Hoje, a SWDL é reconhecida pela qualidade de suas simulações e pelo comprometimento em formar jovens líderes preparados para os desafios do século XXI.', 'en': 'Today, SWDL is recognized for the quality of its simulations and its commitment to training young leaders prepared for the challenges of the 21st century.' },
    'sobre.historia_label_fundacao': { 'pt-BR': 'Ano de fundação', 'en': 'Year founded' },
    'sobre.historia_label_unidade': { 'pt-BR': 'Unidade SESI', 'en': 'SESI Unit' },
    'sobre.historia_label_ano': { 'pt-BR': 'A partir do ano', 'en': 'From grade' },
    'sobre.historia_section_label': { 'pt-BR': 'Nossa História', 'en': 'Our History' },
    'sobre.historia_title': { 'pt-BR': 'Uma liga criada<br>por estudantes', 'en': 'A league created<br>by students' },
    'sobre.historia_desc': { 'pt-BR': 'Do sonho de alunos do 1º EM à realidade: a SWDL prova que jovens têm o poder de criar experiências educacionais transformadoras para toda a comunidade escolar.', 'en': 'From the dream of 1st year high school students to reality: SWDL proves that young people have the power to create transformative educational experiences for the entire school community.' },
    'sobre.historia_cta': { 'pt-BR': 'Junte-se a nós →', 'en': 'Join us →' },
    'sobre.simulacao_label': { 'pt-BR': 'Como Funciona', 'en': 'How It Works' },
    'sobre.simulacao_title': { 'pt-BR': 'O que é uma Simulação da ONU?', 'en': 'What is a UN Simulation?' },
    'sobre.sim_card1_title': { 'pt-BR': 'Representação de Países', 'en': 'Country Representation' },
    'sobre.sim_card1_text': { 'pt-BR': 'Os participantes representam diferentes países em temas da ONU, defendendo suas posições e interesses nacionais.', 'en': 'Participants represent different countries in UN committees, defending their positions and national interests.' },
    'sobre.sim_card2_title': { 'pt-BR': 'Debates Realísticos', 'en': 'Realistic Debates' },
    'sobre.sim_card2_text': { 'pt-BR': 'Discussões sobre temas globais atuais seguindo os procedimentos oficiais das Nações Unidas.', 'en': 'Discussions on current global issues following official United Nations procedures.' },
    'sobre.sim_card3_title': { 'pt-BR': 'Negociação e Diplomacia', 'en': 'Negotiation and Diplomacy' },
    'sobre.sim_card3_text': { 'pt-BR': 'Desenvolvimento de habilidades diplomáticas através de negociações e busca por consenso entre delegações.', 'en': 'Development of diplomatic skills through negotiations and consensus-building among delegations.' },
    'sobre.sim_card4_title': { 'pt-BR': 'Produção de Resoluções', 'en': 'Resolution Production' },
    'sobre.sim_card4_text': { 'pt-BR': 'Elaboração de documentos oficiais que propõem soluções concretas para os problemas discutidos.', 'en': 'Drafting official documents proposing concrete solutions to the issues discussed.' },
    'sobre.equipe_label': { 'pt-BR': 'Quem faz acontecer', 'en': 'Who makes it happen' },
    'sobre.equipe_title': { 'pt-BR': 'Nossa Equipe', 'en': 'Our Team' },
    'sobre.equipe_desc': { 'pt-BR': 'A SWDL é conduzida por uma equipe dedicada de estudantes do Ensino Médio do SESI CE-437, apaixonados por relações internacionais e educação diplomática.', 'en': 'SWDL is led by a dedicated team of high school students from SESI CE-437, passionate about international relations and diplomatic education.' },
    'sobre.equipe_tab_atual': { 'pt-BR': 'Equipe Atual', 'en': 'Current Team' },
    'sobre.equipe_tab_2025': { 'pt-BR': 'Gestão 2025', 'en': '2025 Management' },
    'sobre.equipe_role_prof_orientadora': { 'pt-BR': 'Professora Orientadora', 'en': 'Advisor Teacher' },
    'sobre.equipe_role_secretario_geral': { 'pt-BR': 'Secretário-Geral', 'en': 'Secretary-General' },
    'sobre.equipe_role_diretora_eventos': { 'pt-BR': 'Diretora de Eventos e Logística', 'en': 'Director of Events and Logistics' },
    'sobre.equipe_role_diretora_rp': { 'pt-BR': 'Diretora de Relações Públicas', 'en': 'Director of Public Relations' },
    'sobre.equipe_role_diretora_rh': { 'pt-BR': 'Diretora de Recursos Humanos', 'en': 'Director of Human Resources' },
    'sobre.equipe_role_coordenadora_adm': { 'pt-BR': 'Coordenadora Administrativa', 'en': 'Administrative Coordinator' },
    'sobre.equipe_role_coord_staff_web': { 'pt-BR': 'Coord. da Staff & Desenvolvimento Web', 'en': 'Staff Coordinator & Web Development' },
    'sobre.equipe_role_novo_membro': { 'pt-BR': 'Novo membro ✨', 'en': 'New member ✨' },
    'sobre.equipe_desc_prof_orientadora': { 'pt-BR': 'Responsável por orientar e acompanhar todas as atividades da SWDL, garantindo a qualidade pedagógica e o desenvolvimento dos alunos.', 'en': 'Responsible for guiding and monitoring all SWDL activities, ensuring pedagogical quality and student development.' },
    'sobre.equipe_role_diretora_academica': { 'pt-BR': 'Diretora Acadêmica', 'en': 'Academic Director' },
    'sobre.equipe_role_diretora_comunicacao': { 'pt-BR': 'Diretora de Comunicação e Marketing', 'en': 'Director of Communication and Marketing' },
    'sobre.equipe_role_coordenacao_staff': { 'pt-BR': 'Coordenação da Staff', 'en': 'Staff Coordination' },

    // ── NOTÍCIAS ───────────────────────────────────────────────
    'noticias.page_title': { 'pt-BR': 'Notícias — SWDL', 'en': 'News — SWDL' },
    'noticias.categorias_panel_header': { 'pt-BR': 'Categorias', 'en': 'Categories' },
    'noticias.alertas': { 'pt-BR': 'ALERTAS', 'en': 'ALERTS' },
    'noticias.carregando_alertas': { 'pt-BR': 'Carregando alertas...', 'en': 'Loading alerts...' },
    'noticias.destaque': { 'pt-BR': 'Destaque', 'en': 'Featured' },
    'noticias.carregando': { 'pt-BR': 'Carregando...', 'en': 'Loading...' },
    'noticias.temas_title': { 'pt-BR': '🏛️ Temas', 'en': '🏛️ Committees' },
    'noticias.carregando_comites': { 'pt-BR': 'Carregando...', 'en': 'Loading...' },
    'noticias.carregando_noticias': { 'pt-BR': 'Carregando notícias...', 'en': 'Loading news...' },
    'noticias.ultimas': { 'pt-BR': '📡 Últimas', 'en': '📡 Latest' },
    'noticias.carregando_ultimas': { 'pt-BR': 'Carregando...', 'en': 'Loading...' },

    // ── AGENDA ─────────────────────────────────────────────────
    'agenda.hero_bg': { 'pt-BR': 'AGENDA', 'en': 'SCHEDULE' },
    'agenda.breadcrumb_home': { 'pt-BR': 'Home', 'en': 'Home' },
    'agenda.breadcrumb_current': { 'pt-BR': 'Agenda', 'en': 'Schedule' },
    'agenda.hero_label': { 'pt-BR': 'Cronograma', 'en': 'Schedule' },
    'agenda.hero_title': { 'pt-BR': 'Agenda do Evento', 'en': 'Event Schedule' },
    'agenda.hero_desc': { 'pt-BR': 'Acompanhe em tempo real o que está acontecendo agora. A atividade atual brilha em dourado.', 'en': 'Follow in real time what is happening now. The current activity shines in gold.' },
    'agenda.now_label': { 'pt-BR': 'Acontecendo agora', 'en': 'Happening now' },
    'agenda.now_next_label': { 'pt-BR': 'Próxima atividade', 'en': 'Next activity' },
    'agenda.countdown_min': { 'pt-BR': 'min', 'en': 'min' },
    'agenda.countdown_seg': { 'pt-BR': 'seg', 'en': 'sec' },
    'agenda.loading': { 'pt-BR': 'Carregando agenda...', 'en': 'Loading schedule...' },

    // ── COMITÊS ────────────────────────────────────────────────
    'comites.page_title': { 'pt-BR': 'Temas — SWDL', 'en': 'Committees — SWDL' },
    'comites.hero_bg': { 'pt-BR': 'Temas', 'en': 'COMMITTEES' },
    'comites.breadcrumb_temas': { 'pt-BR': 'Temas', 'en': 'Committees' },
    'comites.hero_section_label': { 'pt-BR': 'Estrutura', 'en': 'Structure' },
    'comites.hero_title': { 'pt-BR': 'Temas & Guias', 'en': 'Committees & Guides' },
    'comites.hero_desc': { 'pt-BR': 'Cada comitê simula um órgão real das Nações Unidas. Baixe o guia de estudos do seu comitê e prepare-se para representar sua nação.', 'en': 'Each committee simulates a real United Nations body. Download your committee study guide and prepare to represent your nation.' },

    // Estreito de Ormuz
    'comites.estreito_ormuz_edicao': { 'pt-BR': 'Edição de 2026', 'en': '2026 Edition' },
    'comites.estreito_ormuz_titulo': { 'pt-BR': 'Estreito de Ormuz: A Crise No Comércio Internacional e Escalada Militar', 'en': 'Strait of Hormuz: The Crisis in International Trade and Military Escalation' },
    'comites.estreito_ormuz_desc': { 'pt-BR': 'No contexto desta simulação, o Conselho de Segurança reúne-se em sessão de emergência diante do agravamento da guerra no Oriente Médio. A rápida escalada das hostilidades, o envolvimento de múltiplos atores regionais e internacionais e os riscos crescentes de expansão do conflito colocam sobre os delegados a responsabilidade de buscar respostas para uma crise que ultrapassa fronteiras nacionais e afeta a segurança global.', 'en': 'In the context of this simulation, the Security Council meets in an emergency session facing the worsening war in the Middle East. The rapid escalation of hostilities, the involvement of multiple regional and international actors, and the growing risks of conflict expansion place on delegates the responsibility to seek answers to a crisis that transcends national borders and affects global security.' },
    'comites.estreito_ormuz_topic_1': { 'pt-BR': 'Escalada Militar', 'en': 'Military Escalation' },
    'comites.estreito_ormuz_topic_2': { 'pt-BR': 'Comércio Internacional', 'en': 'International Trade' },
    'comites.estreito_ormuz_topic_3': { 'pt-BR': 'Arsenais Nucleares', 'en': 'Nuclear Arsenals' },
    'comites.estreito_ormuz_topic_4': { 'pt-BR': 'Petróleo', 'en': 'Oil' },
    'comites.estreito_ormuz_topic_5': { 'pt-BR': 'Sanções Internacionais', 'en': 'International Sanctions' },
    'comites.estreito_ormuz_topic_6': { 'pt-BR': 'Agentes Não-Estatais', 'en': 'Non-State Actors' },
    'comites.estreito_ormuz_delegados': { 'pt-BR': '16 delegações · 32 delegados', 'en': '16 delegations · 32 delegates' },
    'comites.estreito_ormuz_baixar_guia_geral': { 'pt-BR': '📥 Baixar Guia Geral', 'en': '📥 Download General Guide' },
    'comites.estreito_ormuz_manual_delegados': { 'pt-BR': 'Manual dos Delegados', 'en': 'Delegate Handbook' },

    // ACNUR
    'comites.acnur_edicao': { 'pt-BR': 'Edição de 2026', 'en': '2026 Edition' },
    'comites.acnur_titulo': { 'pt-BR': 'A Proteção Internacional de Pessoas Deslocadas em Decorrência de Eventos Climáticos Extremos', 'en': 'The International Protection of People Displaced by Extreme Climate Events' },
    'comites.acnur_desc': { 'pt-BR': 'Nesta simulação, os delegados do Alto Comissariado das Nações Unidas para os Refugiados (ACNUR) debaterão a crescente crise dos deslocamentos forçados provocados por eventos climáticos extremos — enchentes, secas, furacões e tempestades. O desafio será construir mecanismos internacionais de proteção, apoio humanitário e integração para as pessoas deslocadas, conciliando soberania nacional, financiamento internacional e responsabilidade compartilhada.', 'en': 'In this simulation, delegates of the United Nations High Commissioner for Refugees (UNHCR) will debate the growing crisis of forced displacement caused by extreme climate events — floods, droughts, hurricanes and storms. The challenge will be to build international mechanisms of protection, humanitarian support and integration for displaced people, reconciling national sovereignty, international financing and shared responsibility.' },
    'comites.acnur_topic_1': { 'pt-BR': 'Deslocamento Climático', 'en': 'Climate Displacement' },
    'comites.acnur_topic_2': { 'pt-BR': 'Refugiados Climáticos', 'en': 'Climate Refugees' },
    'comites.acnur_topic_3': { 'pt-BR': 'Ajuda Humanitária', 'en': 'Humanitarian Aid' },
    'comites.acnur_topic_4': { 'pt-BR': 'Mudanças Climáticas', 'en': 'Climate Change' },
    'comites.acnur_topic_5': { 'pt-BR': 'Responsabilidade Compartilhada', 'en': 'Shared Responsibility' },
    'comites.acnur_topic_6': { 'pt-BR': 'Financiamento Internacional', 'en': 'International Financing' },
    'comites.acnur_delegados': { 'pt-BR': '11 delegações · 34 estudantes', 'en': '11 delegations · 34 students' },
    'comites.acnur_baixar_guia': { 'pt-BR': '📥 Baixar Guia Geral', 'en': '📥 Download General Guide' },
    'comites.acnur_manual_delegados': { 'pt-BR': 'Manual dos Delegados', 'en': 'Delegate Handbook' },
    'comites.acnur_baixar_manual': { 'pt-BR': '📥 Baixar Manual', 'en': '📥 Download Handbook' },

    // Cannabis
    'comites.cannabis_edicao': { 'pt-BR': 'Edição de 2026', 'en': '2026 Edition' },
    'comites.cannabis_titulo': { 'pt-BR': 'Regulamentação da Canábis: Saúde Pública e Economia Global', 'en': 'Cannabis Regulation: Public Health and Global Economy' },
    'comites.cannabis_desc': { 'pt-BR': 'Este comitê debaterá os impactos da transição global nas políticas sobre a canábis. Os delegados enfrentarão o desafio de equilibrar a descriminalização e o uso medicinal com o controle do narcotráfico, analisando os reflexos socioeconômicos da legalização, a soberania dos Estados e o desenvolvimento de marcos regulatórios internacionais de saúde.', 'en': 'This committee will debate the impacts of the global transition on cannabis policies. Delegates will face the challenge of balancing decriminalization and medicinal use with the control of drug trafficking, analyzing the socioeconomic effects of legalization, State sovereignty and the development of international health regulatory frameworks.' },
    'comites.cannabis_topic_1': { 'pt-BR': 'Saúde Pública', 'en': 'Public Health' },
    'comites.cannabis_topic_2': { 'pt-BR': 'Uso Medicinal', 'en': 'Medicinal Use' },
    'comites.cannabis_topic_3': { 'pt-BR': 'Combate ao Narcotráfico', 'en': 'Fighting Drug Trafficking' },
    'comites.cannabis_topic_4': { 'pt-BR': 'Marcos Regulatórios', 'en': 'Regulatory Frameworks' },
    'comites.cannabis_topic_5': { 'pt-BR': 'Impacto Econômico', 'en': 'Economic Impact' },
    'comites.cannabis_topic_6': { 'pt-BR': 'Soberania Nacional', 'en': 'National Sovereignty' },
    'comites.cannabis_delegados': { 'pt-BR': '16 delegações · 32 delegados', 'en': '16 delegations · 32 delegates' },

    // Misoginia
    'comites.misoginia_edicao': { 'pt-BR': 'Edição de 2025', 'en': '2025 Edition' },
    'comites.misoginia_titulo': { 'pt-BR': 'Combate à Misoginia: Direitos Humanos e Violência de Gênero', 'en': 'Combating Misogyny: Human Rights and Gender Violence' },
    'comites.misoginia_desc': { 'pt-BR': 'Nesta simulação, os delegados debaterão estratégias globais para erradicar a misoginia estrutural e a violência baseada em gênero. O foco estará na criação de mecanismos internacionais de proteção, no combate ao discurso de ódio online e na garantia dos direitos fundamentais das mulheres, enfrentando retrocessos sociais e legislativos em escala global.', 'en': 'In this simulation, delegates will debate global strategies to eradicate structural misogyny and gender-based violence. The focus will be on creating international protection mechanisms, combating online hate speech and guaranteeing women\'s fundamental rights, facing social and legislative setbacks on a global scale.' },
    'comites.misoginia_topic_1': { 'pt-BR': 'Violência de Gênero', 'en': 'Gender Violence' },
    'comites.misoginia_topic_2': { 'pt-BR': 'Direitos Humanos', 'en': 'Human Rights' },
    'comites.misoginia_topic_3': { 'pt-BR': 'Discurso de Ódio Online', 'en': 'Online Hate Speech' },
    'comites.misoginia_topic_4': { 'pt-BR': 'Igualdade Salarial', 'en': 'Pay Equality' },
    'comites.misoginia_topic_5': { 'pt-BR': 'Mecanismos de Proteção', 'en': 'Protection Mechanisms' },
    'comites.misoginia_topic_6': { 'pt-BR': 'Legislação Internacional', 'en': 'International Legislation' },
    'comites.misoginia_delegados': { 'pt-BR': '16 delegações · 32 delegados', 'en': '16 delegations · 32 delegates' },
    'comites.misoginia_baixar_guia': { 'pt-BR': '📥 Baixar Guia Geral', 'en': '📥 Download General Guide' },

    // MMA
    'comites.mma_meta': { 'pt-BR': 'MMA — Meio Ambiente', 'en': 'UNEP — Environment' },
    'comites.mma_titulo': { 'pt-BR': 'Programa da ONU para o Meio Ambiente', 'en': 'UN Environment Programme' },
    'comites.mma_desc': { 'pt-BR': 'O principal órgão ambiental do sistema das Nações Unidas. Debate metas climáticas, preservação da biodiversidade e transição energética global.', 'en': 'The main environmental body of the United Nations system. Debates climate targets, biodiversity preservation and global energy transition.' },
    'comites.mma_topic_1': { 'pt-BR': 'Mudanças Climáticas', 'en': 'Climate Change' },
    'comites.mma_topic_2': { 'pt-BR': 'Biodiversidade', 'en': 'Biodiversity' },
    'comites.mma_topic_3': { 'pt-BR': 'Energia Renovável', 'en': 'Renewable Energy' },
    'comites.mma_topic_4': { 'pt-BR': 'Poluição dos Oceanos', 'en': 'Ocean Pollution' },
    'comites.mma_delegados': { 'pt-BR': '18 delegações · 36 delegados', 'en': '18 delegations · 36 delegates' },

    // DHR
    'comites.dhr_meta': { 'pt-BR': 'DHR — Direitos Humanos', 'en': 'DHR — Human Rights' },
    'comites.dhr_titulo': { 'pt-BR': 'Conselho de Direitos Humanos', 'en': 'Human Rights Council' },
    'comites.dhr_desc': { 'pt-BR': 'Órgão responsável pela promoção e proteção dos direitos humanos em todo o mundo.', 'en': 'Body responsible for promoting and protecting human rights worldwide.' },
    'comites.dhr_topic_1': { 'pt-BR': 'Proteção de Minorias', 'en': 'Minority Protection' },
    'comites.dhr_topic_2': { 'pt-BR': 'Refugiados', 'en': 'Refugees' },
    'comites.dhr_topic_3': { 'pt-BR': 'Liberdade de Expressão', 'en': 'Freedom of Expression' },
    'comites.dhr_topic_4': { 'pt-BR': 'Trabalho Infantil', 'en': 'Child Labor' },
    'comites.dhr_delegados': { 'pt-BR': '16 delegações · 32 delegados', 'en': '16 delegations · 32 delegates' },

    // ECOSOC
    'comites.ecosoc_meta': { 'pt-BR': 'ECOSOC — Econômico e Social', 'en': 'ECOSOC — Economic and Social' },
    'comites.ecosoc_titulo': { 'pt-BR': 'Conselho Econômico e Social', 'en': 'Economic and Social Council' },
    'comites.ecosoc_desc': { 'pt-BR': 'Principal fórum para debater questões econômicas, sociais e ambientais internacionais.', 'en': 'Main forum for debating international economic, social and environmental issues.' },
    'comites.ecosoc_topic_1': { 'pt-BR': 'Combate à Pobreza', 'en': 'Poverty Alleviation' },
    'comites.ecosoc_topic_2': { 'pt-BR': 'Comércio Internacional', 'en': 'International Trade' },
    'comites.ecosoc_topic_3': { 'pt-BR': 'Dívida Externa', 'en': 'External Debt' },
    'comites.ecosoc_topic_4': { 'pt-BR': 'ODS — Agenda 2030', 'en': 'SDGs — Agenda 2030' },
    'comites.ecosoc_delegados': { 'pt-BR': '14 delegações · 28 delegados', 'en': '14 delegations · 28 delegates' },

    // DISEC
    'comites.disec_meta': { 'pt-BR': 'DISEC — Desarmamento', 'en': 'DISEC — Disarmament' },
    'comites.disec_titulo': { 'pt-BR': 'Comitê de Desarmamento e Segurança', 'en': 'Disarmament and Security Committee' },
    'comites.disec_desc': { 'pt-BR': 'Primeiro Comitê da Assembleia Geral da ONU. Trata de questões de desarmamento e segurança internacional.', 'en': 'First Committee of the UN General Assembly. Deals with disarmament and international security issues.' },
    'comites.disec_topic_1': { 'pt-BR': 'Não-Proliferação Nuclear', 'en': 'Nuclear Non-Proliferation' },
    'comites.disec_topic_2': { 'pt-BR': 'Guerras Cibernéticas', 'en': 'Cyber Warfare' },
    'comites.disec_topic_3': { 'pt-BR': 'Armas Autônomas', 'en': 'Autonomous Weapons' },
    'comites.disec_topic_4': { 'pt-BR': 'Tratados de Paz', 'en': 'Peace Treaties' },
    'comites.disec_delegados': { 'pt-BR': '16 delegações · 32 delegados', 'en': '16 delegations · 32 delegates' },

    // OMS
    'comites.oms_meta': { 'pt-BR': 'OMS — Saúde Global', 'en': 'WHO — Global Health' },
    'comites.oms_titulo': { 'pt-BR': 'Organização Mundial da Saúde', 'en': 'World Health Organization' },
    'comites.oms_desc': { 'pt-BR': 'Agência especializada da ONU responsável pela saúde pública internacional.', 'en': 'UN specialized agency responsible for international public health.' },
    'comites.oms_topic_1': { 'pt-BR': 'Prevenção de Pandemias', 'en': 'Pandemic Prevention' },
    'comites.oms_topic_2': { 'pt-BR': 'Acesso a Vacinas', 'en': 'Vaccine Access' },
    'comites.oms_topic_3': { 'pt-BR': 'Saúde Mental Global', 'en': 'Global Mental Health' },
    'comites.oms_topic_4': { 'pt-BR': 'Resistência Antimicrobiana', 'en': 'Antimicrobial Resistance' },
    'comites.oms_delegados': { 'pt-BR': '16 delegações · 32 delegados', 'en': '16 delegations · 32 delegates' },

    // CS
    'comites.cs_meta': { 'pt-BR': 'CS — Conselho de Segurança', 'en': 'SC — Security Council' },
    'comites.cs_titulo': { 'pt-BR': 'Conselho de Segurança da ONU', 'en': 'UN Security Council' },
    'comites.cs_desc': { 'pt-BR': 'O órgão de maior responsabilidade da ONU para manutenção da paz e segurança internacionais.', 'en': 'The UN body with the greatest responsibility for maintaining international peace and security.' },
    'comites.cs_topic_1': { 'pt-BR': 'Conflitos Armados', 'en': 'Armed Conflicts' },
    'comites.cs_topic_2': { 'pt-BR': 'Manutenção da Paz', 'en': 'Peacekeeping' },
    'comites.cs_topic_3': { 'pt-BR': 'Sanções Internacionais', 'en': 'International Sanctions' },
    'comites.cs_topic_4': { 'pt-BR': 'Direito Humanitário', 'en': 'Humanitarian Law' },
    'comites.cs_delegados': { 'pt-BR': '15 delegações · 30 delegados', 'en': '15 delegations · 30 delegates' },
    'comites.cs_baixar_guia': { 'pt-BR': '📥 Baixar Guia Geral', 'en': '📥 Download General Guide' },

    // ── FAÇA PARTE ─────────────────────────────────────────────
    'faca_parte.hero_bg': { 'pt-BR': 'FAÇA PARTE', 'en': 'JOIN US' },
    'faca_parte.breadcrumb_current': { 'pt-BR': 'Faça Parte', 'en': 'Join Us' },
    'faca_parte.section_label': { 'pt-BR': 'Junte-se à Liga', 'en': 'Join the League' },
    'faca_parte.title': { 'pt-BR': 'Faça Parte da SWDL', 'en': 'Join SWDL' },
    'faca_parte.subtitle': { 'pt-BR': 'Junte-se a nós e desenvolva suas habilidades diplomáticas', 'en': 'Join us and develop your diplomatic skills' },
    'faca_parte.tab_delegado': { 'pt-BR': '🌍 Torne-se Delegado', 'en': '🌍 Become a Delegate' },
    'faca_parte.tab_voluntario': { 'pt-BR': '🤝 Seja Voluntário / Staff', 'en': '🤝 Be a Volunteer / Staff' },
    'faca_parte.delegado_title': { 'pt-BR': 'Torne-se um Delegado', 'en': 'Become a Delegate' },
    'faca_parte.delegado_desc': { 'pt-BR': 'Represente um país e participe dos debates mais importantes do mundo. Desenvolva oratória, diplomacia e visão global em uma experiência única.', 'en': 'Represent a country and participate in the world\'s most important debates. Develop oratory, diplomacy and global vision in a unique experience.' },

    // Why be a delegate
    'faca_parte.delegado_why_label': { 'pt-BR': 'Por que ser um Delegado SWDL?', 'en': 'Why be a SWDL Delegate?' },
    'faca_parte.delegado_why_1': { 'pt-BR': 'Desenvolva habilidades de oratória e argumentação', 'en': 'Develop oratory and argumentation skills' },
    'faca_parte.delegado_why_2': { 'pt-BR': 'Aprenda sobre questões globais contemporâneas', 'en': 'Learn about contemporary global issues' },
    'faca_parte.delegado_why_3': { 'pt-BR': 'Pratique negociação e diplomacia em situações reais', 'en': 'Practice negotiation and diplomacy in real situations' },
    'faca_parte.delegado_why_4': { 'pt-BR': 'Trabalhe em equipe com estudantes de diferentes turmas', 'en': 'Work in teams with students from different classes' },
    'faca_parte.delegado_why_5': { 'pt-BR': 'Ganhe experiência em pesquisa e análise crítica', 'en': 'Gain experience in research and critical analysis' },
    'faca_parte.delegado_why_6': { 'pt-BR': 'Construa um currículo diferenciado', 'en': 'Build a standout resume' },
    'faca_parte.delegado_why_7': { 'pt-BR': 'Faça networking com jovens interessados em política internacional', 'en': 'Network with young people interested in international politics' },

    // Requirements
    'faca_parte.delegado_req_label': { 'pt-BR': 'Requisitos para Participar', 'en': 'Requirements to Participate' },
    'faca_parte.delegado_req_escola_title': { 'pt-BR': 'Série Escolar', 'en': 'School Grade' },
    'faca_parte.delegado_req_escola_desc': { 'pt-BR': 'Estudantes a partir do 6° ano do SESI CE-437', 'en': 'Students from 6th grade at SESI CE-437' },
    'faca_parte.delegado_req_disponibilidade_title': { 'pt-BR': 'Disponibilidade', 'en': 'Availability' },
    'faca_parte.delegado_req_disponibilidade_desc': { 'pt-BR': 'Participação nos dias de debate e preparação prévia', 'en': 'Participation on debate days and prior preparation' },
    'faca_parte.delegado_req_comprometimento_title': { 'pt-BR': 'Comprometimento', 'en': 'Commitment' },
    'faca_parte.delegado_req_comprometimento_desc': { 'pt-BR': 'Estudo do país representado e dos temas em debate', 'en': 'Study of the represented country and topics under debate' },
    'faca_parte.delegado_req_equipe_title': { 'pt-BR': 'Trabalho em Equipe', 'en': 'Teamwork' },
    'faca_parte.delegado_req_equipe_desc': { 'pt-BR': 'Colaboração com outros delegados e respeito às regras', 'en': 'Collaboration with other delegates and respect for rules' },

    // Form
    'faca_parte.form_blur_title': { 'pt-BR': 'Inscrições Fechadas', 'en': 'Registration Closed' },
    'faca_parte.form_blur_desc': { 'pt-BR': 'As inscrições para delegados estão encerradas no momento.<br>Fique atento aos próximos eventos!', 'en': 'Delegate registrations are currently closed.<br>Stay tuned for upcoming events!' },
    'faca_parte.form_title': { 'pt-BR': 'Formulário de Inscrição', 'en': 'Registration Form' },
    'faca_parte.form_sub': { 'pt-BR': 'Formulário de Inscrição — Delegado', 'en': 'Registration Form — Delegate' },
    'faca_parte.form_label_nome': { 'pt-BR': 'Nome Completo *', 'en': 'Full Name *' },
    'faca_parte.form_placeholder_nome': { 'pt-BR': 'Seu nome completo', 'en': 'Your full name' },
    'faca_parte.form_label_email': { 'pt-BR': 'E-mail educacional *', 'en': 'Educational email *' },
    'faca_parte.form_placeholder_email': { 'pt-BR': 'seunome@portalsesisp.org.br', 'en': 'yourname@portalsesisp.org.br' },
    'faca_parte.form_email_hint': { 'pt-BR': 'Use seu e-mail @portalsesisp.org.br', 'en': 'Use your @portalsesisp.org.br email' },
    'faca_parte.form_email_error': { 'pt-BR': '✕ Apenas e-mail @portalsesisp.org.br é permitido', 'en': '✕ Only @portalsesisp.org.br email is allowed' },
    'faca_parte.form_label_telefone': { 'pt-BR': 'Telefone', 'en': 'Phone' },
    'faca_parte.form_placeholder_telefone': { 'pt-BR': '(00) 00000-0000', 'en': '(00) 00000-0000' },
    'faca_parte.form_label_serie': { 'pt-BR': 'Série / Ano *', 'en': 'Grade / Year *' },
    'faca_parte.form_option_serie_default': { 'pt-BR': 'Selecione sua série', 'en': 'Select your grade' },
    'faca_parte.form_option_6ano': { 'pt-BR': '6° Ano', 'en': '6th Grade' },
    'faca_parte.form_option_7ano': { 'pt-BR': '7° Ano', 'en': '7th Grade' },
    'faca_parte.form_option_8ano': { 'pt-BR': '8° Ano', 'en': '8th Grade' },
    'faca_parte.form_option_9ano': { 'pt-BR': '9° Ano', 'en': '9th Grade' },
    'faca_parte.form_option_1em': { 'pt-BR': '1° Ano EM', 'en': '1st Year HS' },
    'faca_parte.form_option_2em': { 'pt-BR': '2° Ano EM', 'en': '2nd Year HS' },
    'faca_parte.form_option_3em': { 'pt-BR': '3° Ano EM', 'en': '3rd Year HS' },
    'faca_parte.form_label_experiencia': { 'pt-BR': 'Experiência Anterior', 'en': 'Previous Experience' },
    'faca_parte.form_placeholder_experiencia': { 'pt-BR': 'Ex: participei de um MUN na escola X...', 'en': 'E.g. I participated in a MUN at school X...' },
    'faca_parte.form_label_motivacao': { 'pt-BR': 'Por que deseja participar? *', 'en': 'Why do you want to participate? *' },
    'faca_parte.form_placeholder_motivacao': { 'pt-BR': 'Conte brevemente sua motivação...', 'en': 'Briefly tell us your motivation...' },
    'faca_parte.form_label_interesses': { 'pt-BR': 'Temas de Interesse', 'en': 'Topics of Interest' },
    'faca_parte.form_placeholder_interesses': { 'pt-BR': 'Ex: Segurança Internacional, Direitos Humanos, Meio Ambiente...', 'en': 'E.g. International Security, Human Rights, Environment...' },
    'faca_parte.form_btn_submit': { 'pt-BR': 'Inscrições fechadas🔒', 'en': 'Registrations closed🔒' },
    'faca_parte.form_note': { 'pt-BR': '🔒 Dados usados apenas para o processo de seleção', 'en': '🔒 Data used only for the selection process' },
    'faca_parte.form_success_title': { 'pt-BR': 'Inscrição Enviada!', 'en': 'Registration Sent!' },
    'faca_parte.form_success_desc': { 'pt-BR': 'Nossa equipe entrará em contato em até 3 dias úteis.<br>Fique atento ao seu e-mail!', 'en': 'Our team will contact you within 3 business days.<br>Check your email!' },

    // Volunteer
    'faca_parte.voluntario_title': { 'pt-BR': 'Seja Voluntário / Staff', 'en': 'Be a Volunteer / Staff' },
    'faca_parte.voluntario_desc': { 'pt-BR': 'Ajude a organizar e conduzir as simulações da SWDL. Faça parte dos bastidores que tornam o evento possível.', 'en': 'Help organize and conduct SWDL simulations. Be part of the behind-the-scenes team that makes the event possible.' },
    'faca_parte.voluntario_roles_label': { 'pt-BR': 'Oportunidades de Voluntariado', 'en': 'Volunteer Opportunities' },
    'faca_parte.voluntario_role_mod_title': { 'pt-BR': 'Moderador de Debate', 'en': 'Debate Moderator' },
    'faca_parte.voluntario_role_mod_desc': { 'pt-BR': 'Conduza as sessões de debate e mantenha a ordem durante as discussões dos temas.', 'en': 'Lead debate sessions and maintain order during topic discussions.' },
    'faca_parte.voluntario_role_midia_title': { 'pt-BR': 'Equipe de Mídia', 'en': 'Media Team' },
    'faca_parte.voluntario_role_midia_desc': { 'pt-BR': 'Documente os eventos através de fotos, vídeos e cobertura nas redes sociais da SWDL.', 'en': 'Document events through photos, videos and coverage on SWDL social media.' },
    'faca_parte.voluntario_role_org_title': { 'pt-BR': 'Organização', 'en': 'Organization' },
    'faca_parte.voluntario_role_org_desc': { 'pt-BR': 'Auxilie na logística, preparação de materiais e coordenação geral dos eventos.', 'en': 'Assist with logistics, material preparation and general event coordination.' },
    'faca_parte.voluntario_role_mentor_title': { 'pt-BR': 'Mentor', 'en': 'Mentor' },
    'faca_parte.voluntario_role_mentor_desc': { 'pt-BR': 'Oriente novos delegados e compartilhe conhecimentos sobre diplomacia e procedimentos da ONU.', 'en': 'Guide new delegates and share knowledge about diplomacy and UN procedures.' },

    // Volunteer form
    'faca_parte.voluntario_form_title': { 'pt-BR': 'Formulário de Interesse', 'en': 'Interest Form' },
    'faca_parte.voluntario_form_sub': { 'pt-BR': 'Formulário de Interesse — Voluntário / Staff', 'en': 'Interest Form — Volunteer / Staff' },
    'faca_parte.voluntario_form_label_nome': { 'pt-BR': 'Nome Completo *', 'en': 'Full Name *' },
    'faca_parte.voluntario_form_placeholder_nome': { 'pt-BR': 'Seu nome completo', 'en': 'Your full name' },
    'faca_parte.voluntario_form_label_email': { 'pt-BR': 'E-mail educacional *', 'en': 'Educational email *' },
    'faca_parte.voluntario_form_placeholder_email': { 'pt-BR': 'seunome@portalsesisp.org.br', 'en': 'yourname@portalsesisp.org.br' },
    'faca_parte.voluntario_form_email_hint': { 'pt-BR': 'Use seu e-mail @portalsesisp.org.br', 'en': 'Use your @portalsesisp.org.br email' },
    'faca_parte.voluntario_form_email_error': { 'pt-BR': '✕ Apenas e-mail @portalsesisp.org.br é permitido', 'en': '✕ Only @portalsesisp.org.br email is allowed' },
    'faca_parte.voluntario_form_label_telefone': { 'pt-BR': 'Telefone', 'en': 'Phone' },
    'faca_parte.voluntario_form_placeholder_telefone': { 'pt-BR': '(00) 00000-0000', 'en': '(00) 00000-0000' },
    'faca_parte.voluntario_form_label_serie': { 'pt-BR': 'Série / Ano *', 'en': 'Grade / Year *' },
    'faca_parte.voluntario_form_option_serie_default': { 'pt-BR': 'Selecione sua série', 'en': 'Select your grade' },
    'faca_parte.voluntario_form_option_6ano': { 'pt-BR': '6° Ano', 'en': '6th Grade' },
    'faca_parte.voluntario_form_option_7ano': { 'pt-BR': '7° Ano', 'en': '7th Grade' },
    'faca_parte.voluntario_form_option_8ano': { 'pt-BR': '8° Ano', 'en': '8th Grade' },
    'faca_parte.voluntario_form_option_9ano': { 'pt-BR': '9° Ano', 'en': '9th Grade' },
    'faca_parte.voluntario_form_option_1em': { 'pt-BR': '1° Ano EM', 'en': '1st Year HS' },
    'faca_parte.voluntario_form_option_2em': { 'pt-BR': '2° Ano EM', 'en': '2nd Year HS' },
    'faca_parte.voluntario_form_option_3em': { 'pt-BR': '3° Ano EM', 'en': '3rd Year HS' },
    'faca_parte.voluntario_form_label_interesses': { 'pt-BR': 'Áreas de Interesse *', 'en': 'Areas of Interest *' },
    'faca_parte.voluntario_form_interesse_mod': { 'pt-BR': 'Moderação de Debates', 'en': 'Debate Moderation' },
    'faca_parte.voluntario_form_interesse_midia': { 'pt-BR': 'Equipe de Mídia', 'en': 'Media Team' },
    'faca_parte.voluntario_form_interesse_org': { 'pt-BR': 'Organização e Logística', 'en': 'Organization and Logistics' },
    'faca_parte.voluntario_form_interesse_mentor': { 'pt-BR': 'Mentoria de Novos Delegados', 'en': 'New Delegate Mentoring' },
    'faca_parte.voluntario_form_label_habilidades': { 'pt-BR': 'Habilidades e Experiências', 'en': 'Skills and Experiences' },
    'faca_parte.voluntario_form_placeholder_habilidades': { 'pt-BR': 'Descreva habilidades relevantes ou experiências anteriores...', 'en': 'Describe relevant skills or previous experiences...' },
    'faca_parte.voluntario_form_label_disponibilidade': { 'pt-BR': 'Disponibilidade *', 'en': 'Availability *' },
    'faca_parte.voluntario_form_placeholder_disponibilidade': { 'pt-BR': 'Ex: disponível nas tardes de quarta e sábados...', 'en': 'E.g. available on Wednesday afternoons and Saturdays...' },
    'faca_parte.voluntario_form_btn_submit': { 'pt-BR': 'Quero Ser Voluntário →', 'en': 'I Want to Volunteer →' },
    'faca_parte.voluntario_form_note': { 'pt-BR': '🔒 Dados usados apenas para o processo de seleção', 'en': '🔒 Data used only for the selection process' },
    'faca_parte.voluntario_form_success_title': { 'pt-BR': 'Interesse Registrado!', 'en': 'Interest Registered!' },
    'faca_parte.voluntario_form_success_desc': { 'pt-BR': 'Nossa equipe entrará em contato em até 3 dias úteis.<br>Obrigado por querer fazer parte da SWDL!', 'en': 'Our team will contact you within 3 business days.<br>Thank you for wanting to be part of SWDL!' },

    // Steps
    'faca_parte.steps_label': { 'pt-BR': 'O que vem a seguir', 'en': 'What\'s next' },
    'faca_parte.steps_title': { 'pt-BR': 'Próximos Passos', 'en': 'Next Steps' },
    'faca_parte.step_1_title': { 'pt-BR': 'Envie sua Inscrição', 'en': 'Submit your Application' },
    'faca_parte.step_1_desc': { 'pt-BR': 'Preencha o formulário acima com suas informações e motivações', 'en': 'Fill out the form above with your information and motivations' },
    'faca_parte.step_2_title': { 'pt-BR': 'Aguarde o Contato', 'en': 'Wait for Contact' },
    'faca_parte.step_2_desc': { 'pt-BR': 'Nossa equipe entrará em contato em até 3 dias úteis', 'en': 'Our team will contact you within 3 business days' },
    'faca_parte.step_3_title': { 'pt-BR': 'Participe da Preparação', 'en': 'Join Preparation' },
    'faca_parte.step_3_desc': { 'pt-BR': 'Compareça aos workshops e sessões de preparação', 'en': 'Attend workshops and preparation sessions' },
    'faca_parte.step_4_title': { 'pt-BR': 'Debate e Aprenda', 'en': 'Debate and Learn' },
    'faca_parte.step_4_desc': { 'pt-BR': 'Participe dos debates e desenvolva suas habilidades diplomáticas', 'en': 'Participate in debates and develop your diplomatic skills' },

    // ── AVISO LEGAL ────────────────────────────────────────────
    'aviso_legal.hero_bg_text': { 'pt-BR': 'AVISO LEGAL', 'en': 'LEGAL NOTICE' },
    'aviso_legal.breadcrumb_current': { 'pt-BR': 'Aviso Legal', 'en': 'Legal Notice' },
    'aviso_legal.hero_label': { 'pt-BR': 'Informações Oficiais', 'en': 'Official Information' },
    'aviso_legal.hero_title': { 'pt-BR': 'Aviso Legal', 'en': 'Legal Notice' },
    'aviso_legal.hero_desc': { 'pt-BR': 'Esclarecimentos sobre a natureza e finalidade do projeto SWDL.', 'en': 'Clarifications on the nature and purpose of the SWDL project.' },
    'aviso_legal.update_date': { 'pt-BR': 'Última atualização: 2025', 'en': 'Last updated: 2025' },
    'aviso_legal.title': { 'pt-BR': 'Aviso Legal — SESI World Diplomacy League (SWDL)', 'en': 'Legal Notice — SESI World Diplomacy League (SWDL)' },
    'aviso_legal.subtitle': { 'pt-BR': 'Este documento esclarece a natureza independente e educacional do projeto SWDL, bem como seus limites institucionais.', 'en': 'This document clarifies the independent and educational nature of the SWDL project, as well as its institutional limits.' },
    'aviso_legal.section1_title': { 'pt-BR': 'Natureza do Projeto', 'en': 'Project Nature' },
    'aviso_legal.section1_p1': { 'pt-BR': 'O SESI World Diplomacy League (SWDL) é um projeto estudantil desenvolvido por alunos do SESI CE-437...', 'en': 'SESI World Diplomacy League (SWDL) is a student project developed by students of SESI CE-437...' },
    'aviso_legal.section1_p2': { 'pt-BR': 'A SWDL consiste em uma simulação de órgãos diplomáticos, inspirada em modelos como Model United Nations (MUN)...', 'en': 'SWDL consists of a simulation of diplomatic bodies, inspired by models such as Model United Nations (MUN)...' },
    'aviso_legal.section2_title': { 'pt-BR': 'Ausência de Vínculo com a ONU', 'en': 'No Association with the UN' },
    'aviso_legal.section2_p1': { 'pt-BR': 'A SWDL não possui qualquer vínculo institucional, oficial ou não oficial com a Organização das Nações Unidas (ONU)...', 'en': 'SWDL has no institutional, official or unofficial link with the United Nations (UN)...' },
    'aviso_legal.section2_p2': { 'pt-BR': 'O uso de nomenclaturas, temas e procedimentos inspirados no sistema ONU tem finalidade estritamente pedagógica...', 'en': 'The use of names, themes and procedures inspired by the UN system is strictly for educational purposes...' },
    'aviso_legal.section3_title': { 'pt-BR': 'Limitação de Responsabilidade', 'en': 'Limitation of Liability' },
    'aviso_legal.section3_p1': { 'pt-BR': 'O SWDL é uma atividade extracurricular promovida no âmbito do SESI CE-437...', 'en': 'SWDL is an extracurricular activity promoted within SESI CE-437...' },
    'aviso_legal.section3_li1': { 'pt-BR': 'Todo o conteúdo publicado no portal é produzido para fins pedagógicos...', 'en': 'All content published on the portal is produced for educational purposes...' },
    'aviso_legal.section3_li2': { 'pt-BR': 'A participação no evento é voluntária e está sujeita às regras estabelecidas...', 'en': 'Participation in the event is voluntary and subject to the rules established...' },
    'aviso_legal.section3_li3': { 'pt-BR': 'Em caso de dúvidas sobre a natureza do projeto, entre em contato...', 'en': 'If you have questions about the nature of the project, please contact...' },
    'aviso_legal.section4_title': { 'pt-BR': 'Contato', 'en': 'Contact' },
    'aviso_legal.section4_p1': { 'pt-BR': 'Para esclarecimentos adicionais sobre este aviso legal ou sobre o projeto SWDL, entre em contato:', 'en': 'For further clarification on this legal notice or on the SWDL project, please contact:' },
    'aviso_legal.section4_email': { 'pt-BR': 'E-mail: pedro.pereira63@portalsesisp.org.br', 'en': 'Email: pedro.pereira63@portalsesisp.org.br' },
    'aviso_legal.section4_unidade': { 'pt-BR': 'Unidade: SESI CE-437, Hortolândia — SP', 'en': 'Unit: SESI CE-437, Hortolândia — SP' },
    'aviso_legal.back_link': { 'pt-BR': '← Voltar ao Início', 'en': '← Back to Home' },
    'aviso_legal.disclaimer': { 'pt-BR': 'SESI World Diplomacy League (SWDL) é um projeto estudantil desenvolvido no âmbito do SESI CE-437 com finalidade exclusivamente educacional. A SWDL não possui vínculo institucional com a Organização das Nações Unidas (ONU).', 'en': 'SESI World Diplomacy League (SWDL) is a student project developed within SESI CE-437 for exclusively educational purposes. SWDL has no institutional link with the United Nations (UN).' },

    // ── PRIVACIDADE ────────────────────────────────────────────
    'privacidade.crisis_text': { 'pt-BR': '🚨 CRISE: Sessão de emergência convocada.', 'en': '🚨 CRISIS: Emergency session called.' },
    'privacidade.hero_bg': { 'pt-BR': 'PRIVACIDADE', 'en': 'PRIVACY' },
    'privacidade.breadcrumb': { 'pt-BR': 'Política de Privacidade', 'en': 'Privacy Policy' },
    'privacidade.section_label': { 'pt-BR': 'Proteção de Dados', 'en': 'Data Protection' },
    'privacidade.title': { 'pt-BR': 'Política de Privacidade', 'en': 'Privacy Policy' },
    'privacidade.subtitle': { 'pt-BR': 'Em conformidade com a Lei Geral de Proteção de Dados — LGPD (Lei nº 13.709/2018).', 'en': 'In compliance with the General Data Protection Law — LGPD (Law nº 13.709/2018).' },
    'privacidade.update': { 'pt-BR': 'Última atualização: 2025 · Vigência: SWDL 2026', 'en': 'Last updated: 2025 · Validity: SWDL 2026' },
    'privacidade.legal_title': { 'pt-BR': 'Política de Privacidade e<br>Proteção de Dados — SWDL 2026', 'en': 'Privacy Policy and<br>Data Protection — SWDL 2026' },
    'privacidade.legal_desc': { 'pt-BR': 'A SWDL valoriza a sua privacidade e está comprometida com a proteção dos dados pessoais dos participantes, em conformidade com a Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018).', 'en': 'SWDL values your privacy and is committed to protecting participants\' personal data in compliance with the General Data Protection Law (LGPD — Law nº 13.709/2018).' },
    'privacidade.toc_title': { 'pt-BR': 'Índice', 'en': 'Table of Contents' },
    'privacidade.toc_1': { 'pt-BR': '1. Finalidade e Base Legal', 'en': '1. Purpose and Legal Basis' },
    'privacidade.toc_2': { 'pt-BR': '2. Tratamento de Dados de Menores', 'en': '2. Processing of Minors\' Data' },
    'privacidade.toc_3': { 'pt-BR': '3. Compartilhamento e Retenção', 'en': '3. Sharing and Retention' },
    'privacidade.toc_4': { 'pt-BR': '4. Segurança da Informação', 'en': '4. Information Security' },
    'privacidade.toc_5': { 'pt-BR': '5. Seus Direitos (Art. 18 da LGPD)', 'en': '5. Your Rights (Art. 18 of LGPD)' },
    'privacidade.toc_6': { 'pt-BR': '6. Cookies e Tecnologias', 'en': '6. Cookies and Technologies' },
    'privacidade.sec1_title': { 'pt-BR': 'Finalidade e Base Legal', 'en': 'Purpose and Legal Basis' },
    'privacidade.sec1_p1': { 'pt-BR': 'Ao se inscrever, você fornece dados voluntariamente para que possamos organizar sua participação na simulação.', 'en': 'When registering, you voluntarily provide data so we can organize your participation in the simulation.' },
    'privacidade.sec1_li1': { 'pt-BR': '<strong>Dados coletados:</strong> Nome, e-mail educacional, telefone, série e interesses temáticos.', 'en': '<strong>Data collected:</strong> Name, educational email, phone, grade and thematic interests.' },
    'privacidade.sec1_li2': { 'pt-BR': '<strong>Para que servem:</strong> Identificação oficial, alocação em temas (países), envio de Guias de Estudo e comunicações urgentes sobre o cronograma do evento.', 'en': '<strong>Purpose:</strong> Official identification, allocation to committees (countries), sending Study Guides and urgent communications about the event schedule.' },
    'privacidade.sec1_li3': { 'pt-BR': '<strong>Base legal:</strong> Tratamento necessário para a execução dos procedimentos relacionados à inscrição...', 'en': '<strong>Legal basis:</strong> Processing necessary for the execution of procedures related to registration...' },
    'privacidade.sec2_title': { 'pt-BR': 'Tratamento de Dados de Menores', 'en': 'Processing of Minors\' Data' },
    'privacidade.sec2_p1': { 'pt-BR': 'A SWDL integra atividades educacionais vinculadas ao SESI CE-437. O tratamento dos dados dos estudantes observa as políticas institucionais aplicáveis e a legislação vigente...', 'en': 'SWDL integrates educational activities linked to SESI CE-437. The processing of student data observes applicable institutional policies and current legislation...' },
    'privacidade.sec2_highlight': { 'pt-BR': '📌 Tratamento de dados de participantes menores de idade é realizado no contexto das atividades pedagógicas desenvolvidas pela unidade SESI CE-437, no âmbito de suas atribuições institucionais e educacionais.', 'en': '📌 Processing of data from underage participants is carried out in the context of pedagogical activities developed by SESI CE-437, within its institutional and educational attributions.' },
    'privacidade.sec3_title': { 'pt-BR': 'Compartilhamento e Retenção', 'en': 'Sharing and Retention' },
    'privacidade.sec3_li1': { 'pt-BR': '<strong>Não compartilhamento:</strong> Seus dados jamais serão vendidos ou compartilhados com terceiros fora do âmbito do projeto.', 'en': '<strong>No sharing:</strong> Your data will never be sold or shared with third parties outside the project scope.' },
    'privacidade.sec3_li2': { 'pt-BR': '<strong>Parceiros tecnológicos:</strong> Os dados poderão ser tratados por plataformas tecnológicas utilizadas para hospedagem do site...', 'en': '<strong>Technology partners:</strong> Data may be processed by technology platforms used for website hosting...' },
    'privacidade.sec3_li3': { 'pt-BR': '<strong>Acesso Restrito:</strong> Apenas a Mesa Diretora (Staff) e a Coordenação Pedagógica têm acesso à sua ficha de inscrição.', 'en': '<strong>Restricted Access:</strong> Only the Board (Staff) and Pedagogical Coordination have access to your registration form.' },
    'privacidade.sec3_li4': { 'pt-BR': '<strong>Prazo de Armazenamento:</strong> Seus dados serão mantidos apenas durante o ciclo do evento 2026...', 'en': '<strong>Storage Period:</strong> Your data will be kept only during the 2026 event cycle...' },
    'privacidade.sec4_title': { 'pt-BR': 'Segurança da Informação', 'en': 'Information Security' },
    'privacidade.sec4_p1': { 'pt-BR': 'São adotadas medidas técnicas e administrativas compatíveis com o porte do projeto para proteger os dados pessoais...', 'en': 'Technical and administrative measures compatible with the project size are adopted to protect personal data...' },
    'privacidade.sec4_li1': { 'pt-BR': 'Protocolo HTTPS para navegação segura no portal.', 'en': 'HTTPS protocol for secure browsing on the portal.' },
    'privacidade.sec4_li2': { 'pt-BR': 'Controle de acesso às informações e armazenamento em ambiente protegido.', 'en': 'Access control to information and storage in a protected environment.' },
    'privacidade.sec4_li3': { 'pt-BR': 'Monitoramento de logs para evitar vazamentos de informações.', 'en': 'Log monitoring to prevent information leaks.' },
    'privacidade.sec5_title': { 'pt-BR': 'Seus Direitos (Art. 18 da LGPD)', 'en': 'Your Rights (Art. 18 of LGPD)' },
    'privacidade.sec5_p1': { 'pt-BR': 'Você ou seus responsáveis podem, a qualquer momento, entrar em contato com a organização do SWDL para:', 'en': 'You or your guardians may at any time contact SWDL organization to:' },
    'privacidade.sec5_li1': { 'pt-BR': 'Confirmar se seus dados estão sendo processados.', 'en': 'Confirm whether your data is being processed.' },
    'privacidade.sec5_li2': { 'pt-BR': 'Corrigir dados incompletos ou errados.', 'en': 'Correct incomplete or incorrect data.' },
    'privacidade.sec5_li3': { 'pt-BR': 'Solicitar a exclusão de seus dados (o que cancelará sua participação no evento).', 'en': 'Request deletion of your data (which will cancel your participation in the event).' },
    'privacidade.sec5_li4': { 'pt-BR': 'Revogar eventual consentimento quando aplicável.', 'en': 'Revoke any consent when applicable.' },
    'privacidade.sec5_highlight': { 'pt-BR': '🔒 Para exercer seus direitos, entre em contato pelo e-mail: pedro.pereira63@portalsesisp.org.br', 'en': '🔒 To exercise your rights, contact us at: pedro.pereira63@portalsesisp.org.br' },
    'privacidade.sec6_title': { 'pt-BR': 'Cookies e Tecnologias', 'en': 'Cookies and Technologies' },
    'privacidade.sec6_p1': { 'pt-BR': 'O portal poderá utilizar cookies estritamente necessários ao funcionamento da plataforma...', 'en': 'The portal may use cookies strictly necessary for the platform operation...' },
    'privacidade.sec6_li1': { 'pt-BR': '<strong>Cookies essenciais:</strong> Necessários para o funcionamento básico do site, como sessão de login.', 'en': '<strong>Essential cookies:</strong> Necessary for basic site operation, such as login session.' },
    'privacidade.sec6_li2': { 'pt-BR': '<strong>Serviços integrados:</strong> O site pode fazer uso de serviços como Google Fonts, hospedagem em nuvem e outras tecnologias que processam dados de forma anonimizada.', 'en': '<strong>Integrated services:</strong> The site may use services such as Google Fonts, cloud hosting and other technologies that process data anonymously.' },
    'privacidade.cta_text': { 'pt-BR': 'Tem dúvidas sobre como seus dados são tratados?', 'en': 'Have questions about how your data is handled?' },
    'privacidade.cta_button': { 'pt-BR': '📧 Fale com a Organização', 'en': '📧 Contact the Organization' },
    'privacidade.disclaimer': { 'pt-BR': 'SESI World Diplomacy League (SWDL) é um projeto estudantil desenvolvido no âmbito do SESI CE-437 com finalidade exclusivamente educacional. A SWDL não possui vínculo institucional com a Organização das Nações Unidas (ONU).', 'en': 'SESI World Diplomacy League (SWDL) is a student project developed within SESI CE-437 for exclusively educational purposes. SWDL has no institutional link with the United Nations (UN).' },

    // ── TERMOS ─────────────────────────────────────────────────
    'termos.crisis_text': { 'pt-BR': '🚨 CRISE: Sessão de emergência convocada.', 'en': '🚨 CRISIS: Emergency session called.' },
    'termos.hero_bg': { 'pt-BR': 'TERMOS', 'en': 'TERMS' },
    'termos.breadcrumb': { 'pt-BR': 'Termos de Uso', 'en': 'Terms of Use' },
    'termos.section_label': { 'pt-BR': 'Diretrizes Oficiais', 'en': 'Official Guidelines' },
    'termos.page_title': { 'pt-BR': 'Termos de Uso', 'en': 'Terms of Use' },
    'termos.hero_desc': { 'pt-BR': 'Diretrizes oficiais para uso da plataforma digital SWDL 2026.', 'en': 'Official guidelines for using the SWDL 2026 digital platform.' },
    'termos.update': { 'pt-BR': 'Última atualização: 2025 · Vigência: Todo o ciclo SWDL 2026', 'en': 'Last updated: 2025 · Validity: Entire SWDL 2026 cycle' },
    'termos.legal_title': { 'pt-BR': 'Diretrizes Oficiais e\nTermos de Uso — SWDL 2026', 'en': 'Official Guidelines and\nTerms of Use — SWDL 2026' },
    'termos.legal_subtitle': { 'pt-BR': 'Ao utilizar a plataforma SWDL, você concorda com estas diretrizes. Leia com atenção — o descumprimento pode resultar em desclassificação do evento.', 'en': 'By using the SWDL platform, you agree to these guidelines. Read carefully — non-compliance may result in disqualification from the event.' },
    'termos.toc_title': { 'pt-BR': 'Índice', 'en': 'Table of Contents' },
    'termos.toc_sec1': { 'pt-BR': '1. Código de Conduta e Ética Digital', 'en': '1. Code of Conduct and Digital Ethics' },
    'termos.toc_sec2': { 'pt-BR': '2. Propriedade Intelectual e Direitos Autorais', 'en': '2. Intellectual Property and Copyright' },
    'termos.toc_sec3': { 'pt-BR': '3. Responsabilidade sobre o Conteúdo', 'en': '3. Content Responsibility' },
    'termos.toc_sec4': { 'pt-BR': '4. Disponibilidade do Sistema e Suporte Técnico', 'en': '4. System Availability and Technical Support' },
    'termos.toc_sec5': { 'pt-BR': '5. Vigência e Alterações', 'en': '5. Validity and Changes' },
    'termos.sec1_title': { 'pt-BR': '1 Código de Conduta e Ética Digital', 'en': '1 Code of Conduct and Digital Ethics' },
    'termos.sec1_intro': { 'pt-BR': 'A plataforma SWDL é um espaço de aprendizado e diplomacia. Ao utilizar o portal, o usuário compromete-se a:', 'en': 'The SWDL platform is a space for learning and diplomacy. By using the portal, the user agrees to:' },
    'termos.sec1_item1': { 'pt-BR': '<strong>Respeito Mútuo:</strong> Utilizar linguagem diplomática em todos os campos de texto e interações...', 'en': '<strong>Mutual Respect:</strong> Use diplomatic language in all text fields and interactions...' },
    'termos.sec1_item2': { 'pt-BR': '<strong>Integridade Acadêmica:</strong> Não utilizar ferramentas de automação para fraudar votações...', 'en': '<strong>Academic Integrity:</strong> Do not use automation tools to defraud votes...' },
    'termos.sec1_item3': { 'pt-BR': '<strong>Veracidade das Informações:</strong> O usuário é responsável pela veracidade das informações fornecidas...', 'en': '<strong>Truthfulness of Information:</strong> The user is responsible for the accuracy of the information provided...' },
    'termos.sec1_item4': { 'pt-BR': '<strong>Uso da Imagem:</strong> Estar ciente de que fotos e vídeos das sessões poderão ser utilizados...', 'en': '<strong>Image Use:</strong> Be aware that photos and videos of the sessions may be used...' },
    'termos.sec1_highlight': { 'pt-BR': '⚠️ Atenção: Qualquer tentativa de manipulação do sistema de votação... poderá resultar em desclassificação...', 'en': '⚠️ Attention: Any attempt to manipulate the voting system... may result in disqualification...' },
    'termos.sec2_title': { 'pt-BR': '2 Propriedade Intelectual e Direitos Autorais', 'en': '2 Intellectual Property and Copyright' },
    'termos.sec2_intro': { 'pt-BR': 'Todo o ecossistema tecnológico (código-fonte, design system, logotipos e arquitetura do site) é de propriedade dos seus desenvolvedores e da organização SWDL.', 'en': 'The entire technological ecosystem (source code, design system, logos and site architecture) is owned by its developers and the SWDL organization.' },
    'termos.sec2_item1': { 'pt-BR': '<strong>Uso autorizado:</strong> É proibido tentar copiar, modificar, explorar vulnerabilidades...', 'en': '<strong>Authorized use:</strong> It is forbidden to attempt to copy, modify, exploit vulnerabilities...' },
    'termos.sec2_item2': { 'pt-BR': '<strong>Conteúdo Acadêmico:</strong> Os Guias de Estudo e Documentos de Posição Oficial produzidos são para uso exclusivo dos participantes...', 'en': '<strong>Academic Content:</strong> Study Guides and Official Position Documents produced are for exclusive use of participants...' },
    'termos.sec3_title': { 'pt-BR': '3 Responsabilidade sobre o Conteúdo', 'en': '3 Content Responsibility' },
    'termos.sec3_item1': { 'pt-BR': '<strong>Narrativas Simuladas:</strong> O usuário compreende que as "Notícias de Crise" publicadas no portal são ficcionais...', 'en': '<strong>Simulated Narratives:</strong> The user understands that "Crisis News" published on the portal are fictional...' },
    'termos.sec3_item2': { 'pt-BR': '<strong>Uso de Fontes:</strong> As informações postadas por delegados em seus DPOs são de responsabilidade dos mesmos...', 'en': '<strong>Use of Sources:</strong> Information posted by delegates in their DPOs is their own responsibility...' },
    'termos.sec3_note': { 'pt-BR': '📰 Nota editorial: Todas as notícias publicadas no portal durante o evento são produzidas pela equipe SWDL...', 'en': '📰 Editorial note: All news published on the portal during the event is produced by the SWDL team...' },
    'termos.sec4_title': { 'pt-BR': '4 Disponibilidade do Sistema e Suporte Técnico', 'en': '4 System Availability and Technical Support' },
    'termos.sec4_item1': { 'pt-BR': '<strong>Manutenção:</strong> A organização poderá suspender temporariamente o portal para manutenção preventiva ou corretiva...', 'en': '<strong>Maintenance:</strong> The organization may temporarily suspend the portal for preventive or corrective maintenance...' },
    'termos.sec4_item2': { 'pt-BR': '<strong>Falhas de Conexão:</strong> O SWDL não se responsabiliza por problemas de conexão individuais...', 'en': '<strong>Connection Failures:</strong> SWDL is not responsible for individual connection issues...' },
    'termos.sec4_note': { 'pt-BR': '🛠️ Suporte técnico: Em caso de problemas com login, senha ou votação durante o evento...', 'en': '🛠️ Technical support: In case of problems with login, password or voting during the event...' },
    'termos.sec5_title': { 'pt-BR': '5 Vigência e Alterações', 'en': '5 Validity and Changes' },
    'termos.sec5_intro': { 'pt-BR': 'Estes termos são válidos durante todo o período de preparação e execução da simulação em 2026...', 'en': 'These terms are valid throughout the preparation and execution period of the 2026 simulation...' },
    'termos.sec5_note': { 'pt-BR': '📅 Vigência: 2026 — do período de inscrições até o encerramento oficial do evento...', 'en': '📅 Validity: 2026 — from the registration period until the official closing of the event...' },
    'termos.cta_question': { 'pt-BR': 'Dúvidas sobre estes termos?', 'en': 'Questions about these terms?' },
    'termos.cta_button': { 'pt-BR': '📧 Fale com a Organização', 'en': '📧 Contact the Organization' },
    'termos.disclaimer': { 'pt-BR': 'SESI World Diplomacy League (SWDL) é um projeto estudantil desenvolvido no âmbito do SESI CE-437 com finalidade exclusivamente educacional. A SWDL não possui vínculo institucional com a Organização das Nações Unidas (ONU).', 'en': 'SESI World Diplomacy League (SWDL) is a student project developed within SESI CE-437 for exclusively educational purposes. SWDL has no institutional link with the United Nations (UN).' },

    // ── 404 ────────────────────────────────────────────────────
    'page_404.meta_title': { 'pt-BR': 'Página não encontrada — SWDL', 'en': 'Page not found — SWDL' },
    'page_404.hero_tag': { 'pt-BR': 'Erro de Navegação', 'en': 'Navigation Error' },
    'page_404.hero_title': { 'pt-BR': 'Resolução não encontrada', 'en': 'Resolution not found' },
    'page_404.hero_sub': { 'pt-BR': 'A página que você procura foi movida, não existe ou ainda está em deliberação nos comitês. Tente voltar ao plenário principal.', 'en': 'The page you are looking for has been moved, does not exist or is still being discussed in committees. Try returning to the main hall.' },
    'page_404.hero_back_btn': { 'pt-BR': '← Voltar ao Início', 'en': '← Back to Home' },
    'page_404.hero_agenda_btn': { 'pt-BR': 'Ver Agenda', 'en': 'View Schedule' },
    'page_404.link_noticias': { 'pt-BR': 'Notícias', 'en': 'News' },
    'page_404.link_comites': { 'pt-BR': 'Comitês', 'en': 'Committees' },
    'page_404.link_agenda': { 'pt-BR': 'Agenda', 'en': 'Schedule' },
    'page_404.link_sobre': { 'pt-BR': 'Sobre', 'en': 'About' },
    'page_404.link_inscricao': { 'pt-BR': 'Inscrição', 'en': 'Registration' },
  },

  init() {
    const saved = localStorage.getItem('swdl_lang');
    if (saved && this.available.some(l => l.code === saved)) {
      this.lang = saved;
    }
    document.documentElement.lang = this.lang;
    this.injectDropdown();
    this.apply();
  },

  getFlag(code) {
    const lang = this.available.find(l => l.code === code);
    return lang ? lang.flag : '';
  },

  getLabel(code) {
    const lang = this.available.find(l => l.code === code);
    return lang ? lang.label : code;
  },

  setLang(code) {
    if (code === this.lang) return;
    this.lang = code;
    localStorage.setItem('swdl_lang', code);
    document.documentElement.lang = code;
    this.updateDropdownLabel();
    this.apply();
  },

  t(key) {
    const entry = this.dict[key];
    if (!entry) return '';
    return entry[this.lang] || entry['pt-BR'] || '';
  },

  apply() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      const text = this.t(key);
      if (text) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = text;
        } else if (el.tagName === 'META') {
          el.content = text;
        } else if (/<[a-z][\s\S]*>/i.test(text)) {
          el.innerHTML = text;
        } else {
          el.textContent = text;
        }
      }
    });
  },

  injectDropdown() {
    const container = document.querySelector('.footer-langs');
    if (!container) return;
    container.innerHTML = '';

    const current = this.available.find(l => l.code === this.lang) || this.available[0];

    const btn = document.createElement('button');
    btn.className = 'lang-dropdown-btn';
    btn.setAttribute('aria-label', this.t('crisis_banner.close') || 'Select language');
    btn.innerHTML = `${current.flag} ${current.label} <span class="lang-arrow">▾</span>`;

    const list = document.createElement('div');
    list.className = 'lang-dropdown-list';

    this.available.forEach(lang => {
      const item = document.createElement('button');
      item.className = 'lang-option' + (lang.code === this.lang ? ' active' : '');
      item.textContent = `${lang.flag} ${lang.label}`;
      item.dataset.code = lang.code;
      item.addEventListener('click', () => {
        this.setLang(lang.code);
        list.classList.remove('open');
      });
      list.appendChild(item);
    });

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      list.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!container.contains(e.target)) {
        list.classList.remove('open');
      }
    });

    container.appendChild(btn);
    container.appendChild(list);
  },

  updateDropdownLabel() {
    const btn = document.querySelector('.lang-dropdown-btn');
    if (!btn) return;
    const current = this.available.find(l => l.code === this.lang) || this.available[0];
    btn.innerHTML = `${current.flag} ${current.label} <span class="lang-arrow">▾</span>`;

    document.querySelectorAll('.lang-option').forEach(opt => {
      opt.classList.toggle('active', opt.dataset.code === this.lang);
    });
  },
};

document.addEventListener('DOMContentLoaded', () => SWDL_I18N.init());
