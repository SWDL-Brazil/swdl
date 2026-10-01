"""Revisa texto legal PT e gera sections + metadados nos 9 idiomas."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent / 'messages'
UPDATED = '23/09/2026'

# UI chrome for LegalPage
LEGAL_UI = {
    'pt-BR': {'label': 'Jurídico', 'toc': 'Nesta página', 'updated': 'Última atualização'},
    'en': {'label': 'Legal', 'toc': 'On this page', 'updated': 'Last updated'},
    'es': {'label': 'Legal', 'toc': 'En esta página', 'updated': 'Última actualización'},
    'fr': {'label': 'Juridique', 'toc': 'Sur cette page', 'updated': 'Dernière mise à jour'},
    'de': {'label': 'Rechtliches', 'toc': 'Auf dieser Seite', 'updated': 'Zuletzt aktualisiert'},
    'it': {'label': 'Legale', 'toc': 'In questa pagina', 'updated': 'Ultimo aggiornamento'},
    'nl': {'label': 'Juridisch', 'toc': 'Op deze pagina', 'updated': 'Laatst bijgewerkt'},
    'id': {'label': 'Hukum', 'toc': 'Di halaman ini', 'updated': 'Terakhir diperbarui'},
    'ms': {'label': 'Undang-undang', 'toc': 'Di halaman ini', 'updated': 'Kemas kini terakhir'},
}

# Reviewed/improved PT sections + full translations
PAGES = {
    'termos': {
        'page_title': {
            'pt-BR': 'Termos de Uso — SWDL', 'en': 'Terms of Use — SWDL',
            'es': 'Términos de Uso — SWDL', 'fr': "Conditions d'utilisation — SWDL",
            'de': 'Nutzungsbedingungen — SWDL', 'it': 'Termini di utilizzo — SWDL',
            'nl': 'Gebruiksvoorwaarden — SWDL', 'id': 'Syarat Penggunaan — SWDL',
            'ms': 'Syarat Penggunaan — SWDL',
        },
        'hero_title': {
            'pt-BR': 'Termos de Uso', 'en': 'Terms of Use', 'es': 'Términos de Uso',
            'fr': "Conditions d'utilisation", 'de': 'Nutzungsbedingungen',
            'it': 'Termini di utilizzo', 'nl': 'Gebruiksvoorwaarden',
            'id': 'Syarat Penggunaan', 'ms': 'Syarat Penggunaan',
        },
        'content': {
            'pt-BR': 'Condições de uso do site e dos serviços da SWDL — SESI World Diplomacy League.',
            'en': 'Terms for using the SWDL — SESI World Diplomacy League website and services.',
            'es': 'Condiciones de uso del sitio y de los servicios de la SWDL — SESI World Diplomacy League.',
            'fr': "Conditions d'utilisation du site et des services de la SWDL — SESI World Diplomacy League.",
            'de': 'Bedingungen für die Nutzung der Website und Dienste der SWDL — SESI World Diplomacy League.',
            'it': 'Condizioni d’uso del sito e dei servizi SWDL — SESI World Diplomacy League.',
            'nl': 'Voorwaarden voor het gebruik van de website en diensten van SWDL — SESI World Diplomacy League.',
            'id': 'Syarat penggunaan situs dan layanan SWDL — SESI World Diplomacy League.',
            'ms': 'Syarat penggunaan laman web dan perkhidmatan SWDL — SESI World Diplomacy League.',
        },
        'sections': [
            {
                'title': '1. Aceitação dos Termos',
                'body': 'Ao acessar e utilizar este site, você concorda com estes Termos de Uso da SWDL — SESI World Diplomacy League. Caso não concorde com alguma condição, não utilize o site ou os serviços nele oferecidos.',
                'en': 'By accessing and using this site, you agree to these Terms of Use of SWDL — SESI World Diplomacy League. If you do not agree with any condition, do not use the site or its services.',
                'es': 'Al acceder y utilizar este sitio, usted acepta estos Términos de Uso de la SWDL — SESI World Diplomacy League. Si no está de acuerdo con alguna condición, no utilice el sitio.',
                'fr': "En accédant à ce site et en l'utilisant, vous acceptez les présentes Conditions d'utilisation de la SWDL — SESI World Diplomacy League. Si vous n'acceptez pas une condition, n'utilisez pas le site.",
                'de': 'Indem Sie auf diese Website zugreifen und sie nutzen, stimmen Sie diesen Nutzungsbedingungen der SWDL — SESI World Diplomacy League zu. Wenn Sie einer Bedingung nicht zustimmen, nutzen Sie die Website bitte nicht.',
                'it': 'Accedendo e utilizzando questo sito, accetti i presenti Termini di utilizzo della SWDL — SESI World Diplomacy League. Se non accetti una condizione, non utilizzare il sito.',
                'nl': 'Door deze website te bezoeken en te gebruiken, ga je akkoord met deze Gebruiksvoorwaarden van SWDL — SESI World Diplomacy League. Als je niet met een voorwaarde akkoord gaat, gebruik de website dan niet.',
                'id': 'Dengan mengakses dan menggunakan situs ini, Anda menyetujui Syarat Penggunaan SWDL — SESI World Diplomacy League. Jika Anda tidak setuju, jangan gunakan situs ini.',
                'ms': 'Dengan mengakses dan menggunakan laman web ini, anda bersetuju dengan Syarat Penggunaan SWDL — SESI World Diplomacy League. Jika anda tidak bersetuju, jangan gunakan laman web ini.',
            },
            {
                'title': '2. Uso do Site',
                'body': 'O site é fornecido para fins informativos, institucionais e de inscrição no evento SWDL. Você se compromete a usá-lo de forma ética, respeitosa e em conformidade com a legislação vigente, sem praticar qualquer atividade ilícita ou que viole direitos de terceiros.',
                'en': 'The site is provided for informational, institutional and SWDL event registration purposes. You agree to use it ethically, respectfully and in compliance with applicable legislation, without engaging in any unlawful activity or violating third-party rights.',
                'es': 'El sitio se ofrece con fines informativos, institucionales e de inscripción al evento SWDL. Usted se compromete a usarlo de forma ética, respetuosa y conforme a la legislación vigente, sin realizar actividades ilícitas ni violar derechos de terceros.',
                'fr': "Le site est fourni à des fins informatives, institutionnelles et d'inscription à l'événement SWDL. Vous vous engagez à l'utiliser de manière éthique, respectueuse et conformément à la législation applicable, sans activité illicite ni atteinte aux droits des tiers.",
                'de': 'Die Website dient informativen, institutionellen und Anmeldezwecken für die SWDL-Veranstaltung. Sie verpflichten sich, sie ethisch, respektvoll und konform mit geltendem Recht zu nutzen, ohne unerlaubte Aktivitäten oder Rechtsverletzungen Dritter.',
                'it': 'Il sito è fornito a fini informativi, istitutivi e di iscrizione all’evento SWDL. Ti impegni a utilizzarlo in modo etico, rispettoso e conforme alla legge, senza attività illecite o violazioni di diritti di terzi.',
                'nl': 'De website is bedoeld voor informatie, institutie en inschrijving voor het SWDL-evenement. Je gebruikt de site op een ethische, respectvolle en wettelijke manier, zonder onwettige activiteiten of inbreuk op rechten van derden.',
                'id': 'Situs disediakan untuk tujuan informasi, institusional dan pendaftaran acara SWDL. Anda setuju menggunakannya secara etis, sopan dan sesuai hukum, tanpa aktivitas ilegal atau pelanggaran hak pihak lain.',
                'ms': 'Laman web disediakan untuk tujuan maklumat, institusi dan pendaftaran acara SWDL. Anda bersetuju menggunakannya secara etik, sopan dan mematuhi undang-undang, tanpa aktiviti haram atau pelanggaran hak pihak ketiga.',
            },
            {
                'title': '3. Inscrições',
                'body': 'Ao se inscrever na SWDL, você declara que: (a) as informações fornecidas são verdadeiras e atualizadas; (b) possui idade compatível com a faixa etária do evento; (c) é estudante do SESI ou de escola parceira, quando aplicável; e (d) aceita as regras, o código de conduta e os regulamentos do evento.',
                'en': 'By registering for SWDL, you declare that: (a) the information provided is true and up to date; (b) you meet the event’s age requirements; (c) you are a student at SESI or a partner school, where applicable; and (d) you accept the event rules, code of conduct and regulations.',
                'es': 'Al inscribirse en la SWDL, declara que: (a) la información proporcionada es verdadera y actualizada; (b) cumple con la edad requerida para el evento; (c) es estudiante del SESI o de una escuela asociada, cuando aplique; y (d) acepta las reglas, el código de conducta y los reglamentos del evento.',
                'fr': "En vous inscrivant à la SWDL, vous déclarez que : (a) les informations fournies sont exactes et à jour ; (b) vous répondez aux critères d'âge de l'événement ; (c) vous êtes élève du SESI ou d'une école partenaire, le cas échéant ; et (d) vous acceptez les règles, le code de conduite et le règlement de l'événement.",
                'de': 'Mit Ihrer Anmeldung bei der SWDL erklären Sie, dass: (a) die angegebenen Informationen wahr und aktuell sind; (b) Sie die Altersanforderungen der Veranstaltung erfüllen; (c) Sie Schüler der SESI oder einer Partnerschule sind, sofern zutreffend; und (d) Sie die Regeln, den Verhaltenskodex und die Bestimmungen der Veranstaltung akzeptieren.',
                'it': 'Iscrivendoti alla SWDL, dichiari che: (a) le informazioni fornite sono vere e aggiornate; (b) rispetti i requisiti di età dell’evento; (c) sei studente del SESI o di una scuola partner, ove applicabile; e (d) accetti regole, codice di condotta e regolamenti dell’evento.',
                'nl': 'Door je in te schrijven bij SWDL verklaar je dat: (a) de verstrekte informatie waar en actueel is; (b) je voldoet aan de leeftijdseisen van het evenement; (c) je leerling bent van SESI of een partnerschool, indien van toepassing; en (d) je de regels, gedragscode en voorschriften van het evenement accepteert.',
                'id': 'Dengan mendaftar di SWDL, Anda menyatakan bahwa: (a) informasi yang diberikan benar dan terkini; (b) Anda memenuhi persyaratan usia acara; (c) Anda siswa SESI atau sekolah mitra, jika berlaku; dan (d) Anda menerima aturan, kode etik dan peraturan acara.',
                'ms': 'Dengan mendaftar di SWDL, anda mengisytiharkan bahawa: (a) maklumat yang diberikan adalah benar dan terkini; (b) anda memenuhi syarat umur acara; (c) anda pelajar SESI atau sekolah rakan kongsi, jika berkenaan; dan (d) anda menerima peraturan, kod etik dan garis panduan acara.',
            },
            {
                'title': '4. Conduta dos Participantes',
                'body': 'Os participantes devem manter comportamento respeitoso, inclusivo e profissional durante todo o evento — presencial e online. A organização reserva-se o direito de advertir, suspender ou desqualificar quem violar o código de conduta, incluindo assédio, discriminação, desinformação ou uso indevido do nome e da marca SWDL.',
                'en': 'Participants must behave respectfully, inclusively and professionally throughout the event — in person and online. The organization reserves the right to warn, suspend or disqualify anyone who violates the code of conduct, including harassment, discrimination, misinformation or misuse of the SWDL name and brand.',
                'es': 'Los participantes deben mantener una conducta respetuosa, inclusiva y profesional durante todo el evento — presencial y en línea. La organización se reserva el derecho de advertir, suspender o descalificar a quien viole el código de conducta, incluido acoso, discriminación, desinformación o uso indebido de la marca SWDL.',
                'fr': "Les participants doivent adopter un comportement respectueux, inclusif et professionnel tout au long de l'événement — en présentiel et en ligne. L'organisation se réserve le droit d'avertir, de suspendre ou de disqualifier toute personne violant le code de conduite, y compris harcèlement, discrimination, désinformation ou usage abusif de la marque SWDL.",
                'de': 'Teilnehmende müssen während der gesamten Veranstaltung — vor Ort und online — respektvoll, inklusiv und professionell auftreten. Die Organisation behält sich das Recht vor, Personen bei Verstößen gegen den Verhaltenskodex zu verwarnen, auszusetzen oder zu disqualifizieren, einschließlich Belästigung, Diskriminierung, Falschinformationen oder Missbrauchs des SWDL-Namens und -Marken.',
                'it': 'I partecipanti devono mantenere un comportamento rispettoso, inclusivo e professionale per tutta l’evento — in presenza e online. L’organizzazione si riserva il diritto di avvertire, sospendere o squalificare chi violi il codice di condotta, incluse molestie, discriminazioni, disinformazione o uso improprio del marchio SWDL.',
                'nl': 'Deelnemers gedragen zich tijdens het hele evenement — online en offline — respectvol, inclusief en professioneel. De organisatie behoudt het recht om iedereen die de gedragscode schendt te waarschuren, schorsen of diskwalificeren, inclusief pesterijen, discriminatie, desinformatie of misbruik van de SWDL-merknaam.',
                'id': 'Peserta harus menjaga perilaku sopan, inklusif dan profesional sepanjang acara — luring dan daring. Penyelenggara berhak memperingatkan, menangguhkan atau mendiskualifikasi pelanggar kode etik, termasuk pelecehan, diskriminasi, disinformasi atau penyalahgunaan merek SWDL.',
                'ms': 'Peserta mesti mengekalkan tingkah laku hormat, inklusif dan profesional sepanjang acara — bersemuka dan dalam talian. Penganjur berhak memberi amaran, menggantung atau mendiskualifikasi sesiapa yang melanggar kod etik termasuk gangguan, diskriminasi, salah maklumat atau salah guna jenama SWDL.',
            },
            {
                'title': '5. Propriedade Intelectual',
                'body': 'Todo o conteúdo produzido durante o evento (resoluções, discursos, trabalhos, fotos e gravações) pertence aos seus autores. Ao participar, você concede à SWDL uma licença não exclusiva, gratuita e mundial para uso desses materiais em comunicação institucional e materiais promocionais, com crédito ao autor quando aplicável.',
                'en': 'All content produced during the event (resolutions, speeches, papers, photos and recordings) belongs to its authors. By participating, you grant SWDL a non-exclusive, free and worldwide license to use such materials in institutional communication and promotional materials, with credit to the author where applicable.',
                'es': 'Todo el contenido producido durante el evento (resoluciones, discursos, trabajos, fotos y grabaciones) pertenece a sus autores. Al participar, usted concede a la SWDL una licencia no exclusiva, gratuita y mundial para usar esos materiales en comunicación institucional y promocional, con crédito al autor cuando corresponda.',
                'fr': "Tout le contenu produit pendant l'événement (résolutions, discours, travaux, photos et enregistrements) appartient à ses auteurs. En participant, vous accordez à la SWDL une licence non exclusive, gratuite et mondiale pour utiliser ces supports en communication institutionnelle et promotionnelle, avec mention de l'auteur le cas échéant.",
                'de': 'Alle während der Veranstaltung erstellten Inhalte (Resolutionen, Reden, Arbeiten, Fotos und Aufnahmen) gehören den jeweiligen Urhebern. Mit der Teilnahme gewähren Sie der SWDL eine nicht-exklusive, kostenlose und weltweite Lizenz zur Nutzung dieser Materialien in institutioneller und werblicher Kommunikation, mit Urhebernennung, soweit zutreffend.',
                'it': 'Tutto il contenuto prodotto durante l’evento (risoluzioni, discorsi, lavori, foto e registrazioni) appartiene ai rispettivi autori. Partecipando, concedi alla SWDL una licenza non esclusiva, gratuita e mondiale per usare tali materiali in comunicazione istituzionale e promozionale, con credito all’autore ove applicabile.',
                'nl': 'Alle tijdens het evenement geproduceerde inhoud (resoluties, toespraken, werkstukken, foto’s en opnames) behoort tot de auteurs. Door deel te nemen, verleen je SWDL een niet-exclusieve, gratis en wereldwijde licentie om dit materiaal te gebruiken in institutionele en promotionele communicatie, met bronvermelding waar van toepassing.',
                'id': 'Semua konten yang diproduksi selama acara (resolusi, pidato, karya, foto dan rekaman) adalah milik para penulisnya. Dengan berpartisipasi, Anda memberi SWDL lisensi non-eksklusif, gratis dan global untuk menggunakan materi tersebut dalam komunikasi institusional dan promosi, dengan kredit penulis jika berlaku.',
                'ms': 'Semua kandungan yang dihasilkan semasa acara (resolusi, ucapan, karya, foto dan rakaman) adalah milik penulisnya. Dengan menyertai, anda memberi SWDL lesen tidak eksklusif, percuma dan sejagat untuk menggunakan bahan tersebut dalam komunikasi institusi dan promosi, dengan kredit penulis jika berkenaan.',
            },
            {
                'title': '6. Limitação de Responsabilidade',
                'body': 'A SWDL não se responsabiliza por danos diretos ou indiretos decorrentes da participação no evento ou do uso do site, incluindo — sem limitação — cancelamento ou adiamento do evento, mudanças de programação, falhas técnicas, força maior ou atos de terceiros. O site é fornecido "como está", na medida do permitido pela lei.',
                'en': 'SWDL is not liable for direct or indirect damages arising from participation in the event or use of the site, including — without limitation — event cancellation or postponement, schedule changes, technical failures, force majeure or acts of third parties. The site is provided "as is", to the extent permitted by law.',
                'es': 'La SWDL no se responsabiliza por daños directos o indirectos derivados de la participación en el evento o del uso del sitio, incluyendo — sin limitación — cancelación o aplazamiento del evento, cambios de programación, fallas técnicas, fuerza mayor o actos de terceros. El sitio se ofrece "tal cual", en la medida permitida por la ley.',
                'fr': "La SWDL n'est pas responsable des dommages directs ou indirects résultant de la participation à l'événement ou de l'utilisation du site, y compris — sans limitation — annulation ou report de l'événement, modifications de programme, pannes techniques, force majeure ou actes de tiers. Le site est fourni « en l'état », dans la limite autorisée par la loi.",
                'de': 'Die SWDL haftet nicht für direkte oder indirekte Schäden aus der Teilnahme an der Veranstaltung oder der Nutzung der Website, einschließlich — ohne Einschränkung — Absage oder Verschiebung der Veranstaltung, Programmänderungen, technischer Störungen, höhere Gewalt oder Handlungen Dritter. Die Website wird "wie besehen" bereitgestellt, soweit gesetzlich zulässig.',
                'it': 'La SWDL non è responsabile per danni diretti o indiretti derivanti dalla partecipazione all’evento o dall’uso del sito, inclusi — senza limitazione — annullamento o rinvio dell’evento, modifiche di programma, guasti tecnici, forza maggiore o atti di terzi. Il sito è fornito “così com’è”, nei limiti di legge.',
                'nl': 'SWDL is niet aansprakelijk voor directe of indirecte schade door deelname aan het evenement of het gebruik van de website, inclusief — zonder beperking — afgelasting of uitstel, programmacwijzigingen, technische storingen, overmacht of handelingen van derden. De website wordt "zoals deze is" aangeboden, voor zover de wet dat toestaat.',
                'id': 'SWDL tidak bertanggung jawab atas kerugian langsung atau tidak langsung akibat partisipasi dalam acara atau penggunaan situs, termasuk — tanpa batasan — pembatalan atau penundaan acara, perubahan jadwal, kegagalan teknis, force majeure atau perbuatan pihak ketiga. Situs disediakan "sebagaimana adanya", sejauh diizinkan hukum.',
                'ms': 'SWDL tidak bertanggungjawab atas kerosakan langsung atau tidak langsung akibat penyertaan dalam acara atau penggunaan laman web, termasuk — tanpa batasan — pembatalan atau penundaan acara, perubahan jadual, kegagalan teknikal, force majeure atau perbuatan pihak ketiga. Laman web disediakan "sebagaimana adanya", setakat yang dibenarkan oleh undang-undang.',
            },
            {
                'title': '7. Cancelamento e Devolução',
                'body': 'Em caso de cancelamento do evento por decisão da organização, os inscritos serão notificados por e-mail ou canais oficiais da SWDL. Como o evento é gratuito, não há devolução de valores. Eventuais custos de deslocamento ou hospedagem correm por conta do participante.',
                'en': 'If the event is cancelled by the organization, registrants will be notified by email or official SWDL channels. As the event is free of charge, there are no refunds. Any travel or accommodation costs are the participant’s responsibility.',
                'es': 'En caso de cancelación del evento por decisión de la organización, los inscritos serán notificados por correo o canales oficiales de la SWDL. Como el evento es gratuito, no hay reembolso. Cualquier costo de viaje o alojamiento corre por cuenta del participante.',
                "fr": "En cas d'annulation de l'événement par l'organisation, les inscrits seront notifiés par e-mail ou les canaux officiels de la SWDL. L'événement étant gratuit, aucun remboursement n'est prévu. Les frais de voyage ou d'hébergement restent à la charge du participant.",
                'de': 'Bei Absage der Veranstaltung durch die Organisation werden die Angemeldeten per E-Mail oder offiziellen SWDL-Kanälen informiert. Da die Veranstaltung kostenlos ist, erfolgt keine Rückerstattung. Reise- oder Übernachtungskosten trägen die Teilnehmenden selbst.',
                "it": "In caso di annullamento dell’evento per decisione dell’organizzazione, gli iscritti saranno informati via e-mail o canali ufficiali SWDL. Essendo l’evento gratuito, non sono previsti rimborsi. Eventuali costi di viaggio o alloggio sono a carico del partecipante.",
                "nl": "Als het evenement door de organisatie wordt afgelast, worden deelnemers geïnformeerd via e-mail of officiële SWDL-kanalen. Omdat het evenement gratis is, is er geen restitutie. Reis- of verblijfkosten zijn voor eigen rekening.",
                "id": "Jika acara dibatalkan oleh penyelenggara, peserta akan diberi tahu melalui e-mail atau kanal resmi SWDL. Karena acara gratis, tidak ada pengembalian dana. Biaya perjalanan atau penginapan menjadi tanggung jawab peserta.",
                "ms": "Sekiranya acara dibatalkan oleh penganjur, peserta akan dimaklumkan melalui e-mel atau saluran rasmi SWDL. Memandangkan acara adalah percuma, tiada bayaran balik. Kos penginapan atau perjalanan ditanggung oleh peserta.",
            },
            {
                "title": "8. Alterações nos Termos",
                'body': 'A SWDL pode alterar estes Termos de Uso a qualquer momento. As alterações entram em vigor imediatamente após a publicação nesta página. Recomenda-se revisar periodicamente o conteúdo. O uso continuado do site após mudanças implica aceitação da nova versão.',
                'en': 'SWDL may change these Terms of Use at any time. Changes take effect immediately after publication on this page. We recommend reviewing the content periodically. Continued use of the site after changes constitutes acceptance of the new version.',
                'es': 'La SWDL puede modificar estos Términos de Uso en cualquier momento. Los cambios entran en vigor inmediatamente después de su publicación en esta página. Se recomienda revisar el contenido periódicamente. El uso continuado del sitio tras los cambios implica aceptación de la nueva versión.',
                'fr': "La SWDL peut modifier les présentes Conditions d'utilisation à tout moment. Les changements prennent effet immédiatement après leur publication sur cette page. Il est recommandé de relire le contenu périodiquement. La poursuite de l'utilisation du site après modification vaut acceptation de la nouvelle version.",
                'de': 'Die SWDL kann diese Nutzungsbedingungen jederzeit ändern. Änderungen treten mit der Veröffentlichung auf dieser Seite sofort in Kraft. Es empfiehlt sich, den Inhalt regelmäßig zu prüfen. Die fortgesetzte Nutzung der Website nach Änderungen gilt als Zustimmung zur neuen Fassung.',
                'it': 'La SWDL può modificare i presenti Termini di utilizzo in qualsiasi momento. Le modifiche hanno effetto immediatamente dopo la pubblicazione su questa pagina. Si consiglia di rivedere periodicamente il contenuto. L’uso continuato del sito dopo le modifiche implica accettazione della nuova versione.',
                'nl': 'SWDL kan deze Gebruiksvoorwaarden altijd wijzigen. Wijzigingen treden onmiddellijk in werking na publicatie op deze pagina. Het wordt aanbevolen de inhoud periodiek te controleren. Door de website na wijzigingen blijven te gebruiken, accepteer je de nieuwe versie.',
                'id': 'SWDL dapat mengubah Syarat Penggunaan ini kapan saja. Perubahan berlaku segera setelah dipublikasikan di halaman ini. Disarankan meninjau isi secara berkala. Penggunaan situs yang berlanjut setelah perubahan berarti penerimaan versi baru.',
                'ms': 'SWDL boleh mengubah Syarat Penggunaan ini pada bila-bila masa. Perubahan berkuat kuasa serta-merta selepas diterbitkan di halaman ini. Disarankan menyemak kandungan secara berkala. Penggunaan laman web yang berterusan selepas perubahan bermakna penerimaan versi baharu.',
            },
            {
                'title': '9. Contato',
                'body': 'Em caso de dúvidas sobre estes Termos de Uso, entre em contato pelo e-mail: pedro.pereira63@portalsesisp.org.br',
                'en': 'If you have questions about these Terms of Use, contact us at: pedro.pereira63@portalsesisp.org.br',
                'es': 'Si tiene dudas sobre estos Términos de Uso, contáctenos en: pedro.pereira63@portalsesisp.org.br',
                'fr': "Pour toute question sur ces Conditions d'utilisation, contactez-nous à : pedro.pereira63@portalsesisp.org.br",
                'de': 'Bei Fragen zu diesen Nutzungsbedingungen kontaktieren Sie uns unter: pedro.pereira63@portalsesisp.org.br',
                'it': 'Per domande sui presenti Termini di utilizzo, scrivi a: pedro.pereira63@portalsesisp.org.br',
                'nl': 'Vragen over deze Gebruiksvoorwaarden? Neem contact op via: pedro.pereira63@portalsesisp.org.br',
                'id': 'Pertanyaan tentang Syarat Penggunaan ini? Hubungi: pedro.pereira63@portalsesisp.org.br',
                'ms': 'Soalan mengenai Syarat Penggunaan ini? Hubungi: pedro.pereira63@portalsesisp.org.br',
            },
        ],
    },
    'privacidade': {
        'page_title': {
            'pt-BR': 'Privacidade — SWDL', 'en': 'Privacy — SWDL', 'es': 'Privacidad — SWDL',
            'fr': 'Confidentialité — SWDL', 'de': 'Datenschutz — SWDL', 'it': 'Privacy — SWDL',
            'nl': 'Privacy — SWDL', 'id': 'Privasi — SWDL', 'ms': 'Privasi — SWDL',
        },
        'hero_title': {
            'pt-BR': 'Política de Privacidade', 'en': 'Privacy Policy', 'es': 'Política de Privacidad',
            'fr': 'Politique de Confidentialité', 'de': 'Datenschutzerklärung',
            'it': 'Informativa sulla Privacy', 'nl': 'Privacybeleid',
            'id': 'Kebijakan Privasi', 'ms': 'Dasar Privasi',
        },
        'content': {
            'pt-BR': 'Como coletamos, usamos e protegemos seus dados pessoais conforme a LGPD.',
            'en': 'How we collect, use and protect your personal data under applicable privacy law.',
            'es': 'Cómo recopilamos, usamos y protegemos sus datos personales conforme la legislación de privacidad.',
            'fr': "Comment nous collectons, utilisons et protégeons vos données personnelles selon la législation applicable.",
            'de': 'Wie wir Ihre personenbezogenen Daten gemäß geltendem Datenschutzrecht erheben, nutzen und schützen.',
            'it': 'Come raccogliamo, utilizziamo e proteggiamo i tuoi dati personali secondo la normativa privacy.',
            'nl': 'Hoe we je persoonsgegevens verzamelen, gebruiken en beschermen volgens de privacywetgeving.',
            'id': 'Bagaimana kami mengumpulkan, menggunakan dan melindungi data pribadi Anda menurut hukum privasi.',
            'ms': 'Bagaimana kami mengumpul, guna dan lindungi data peribadi anda mengikut undang-undang privasi.',
        },
        'sections': [
            {
                'title': '1. Dados Coletados',
                'body': 'Para participar da SWDL, coletamos apenas os dados necessários à inscrição: nome completo, e-mail, telefone, Instagram (opcional), nome da escola, série/ano e motivação para participação. Não solicitamos dados sensíveis além do necessário para organizar o evento.',
                'en': 'To participate in SWDL, we collect only the data needed for registration: full name, email, phone, Instagram (optional), school name, grade and motivation for participating. We do not request sensitive data beyond what is needed to organize the event.',
                'es': 'Para participar en la SWDL, recopilamos solo los datos necesarios para la inscripción: nombre completo, correo, teléfono, Instagram (opcional), nombre de la escuela, curso y motivación de participación. No solicitamos datos sensibles más allá de lo necesario para organizar el evento.',
                'fr': "Pour participer à la SWDL, nous collectons uniquement les données nécessaires à l'inscription : nom complet, e-mail, téléphone, Instagram (facultatif), nom de l'école, niveau scolaire et motivation. Nous ne demandons pas de données sensibles au-delà du nécessaire à l'organisation de l'événement.",
                'de': 'Um an der SWDL teilzunehmen, erheben wir nur die für die Anmeldung erforderlichen Daten: vollständiger Name, E-Mail, Telefon, Instagram (optional), Schulname, Klassenstufe und Motivation. Wir fragen keine sensiblen Daten über das für die Veranstaltung Notwendige hinaus ab.',
                'it': 'Per partecipare alla SWDL raccogliamo solo i dati necessari all’iscrizione: nome completo, e-mail, telefono, Instagram (facoltativo), nome della scuola, classe e motivazione. Non richiediamo dati sensibili oltre il necessario per organizzare l’evento.',
                'nl': 'Om deel te nemen aan SWDL verzamelen we alleen de gegevens die nodig zijn voor inschrijving: volledige naam, e-mail, telefoon, Instagram (optioneel), schoolnaam, leerjaar en motivatie. We vragen geen gevoelige gegevens buiten het nodige voor de organisatie.',
                'id': 'Untuk berpartisipasi di SWDL, kami hanya mengumpulkan data yang diperlukan untuk pendaftaran: nama lengkap, email, telepon, Instagram (opsional), nama sekolah, kelas dan motivasi. Kami tidak meminta data sensitif di luar kebutuhan penyelenggaraan acara.',
                'ms': 'Untuk menyertai SWDL, kami hanya mengumpul data yang diperlukan untuk pendaftaran: nama penuh, e-mel, telefon, Instagram (pilihan), nama sekolah, tingkatan dan motivasi. Kami tidak meminta data sensitif selain keperluan penganjuran acara.',
            },
            {
                'title': '2. Finalidade dos Dados',
                'body': 'Os dados são usados exclusivamente para: (a) processar inscrições e conferir elegibilidade; (b) comunicar informações sobre o evento; (c) emitir certificados de participação; e (d) melhorar a experiência dos participantes. Não usamos seus dados para publicidade de terceiros sem consentimento.',
                'en': 'Data is used exclusively to: (a) process registrations and verify eligibility; (b) communicate event information; (c) issue participation certificates; and (d) improve the participant experience. We do not use your data for third-party advertising without consent.',
                'es': 'Los datos se usan exclusivamente para: (a) procesar inscripciones y verificar elegibilidad; (b) comunicar información del evento; (c) emitir certificados de participación; y (d) mejorar la experiencia de los participantes. No usamos sus datos para publicidad de terceros sin consentimiento.',
                'fr': "Les données sont utilisées exclusivement pour : (a) traiter les inscriptions et vérifier l'éligibilité ; (b) communiquer les informations sur l'événement ; (c) délivrer les certificats de participation ; et (d) améliorer l'expérience des participants. Nous n'utilisons pas vos données pour la publicité de tiers sans consentement.",
                'de': 'Die Daten werden ausschließlich verwendet, um: (a) Anmeldegerechtigkeit zu prüfen; (b) Veranstaltungsinformationen zu übermitteln; (c) Teilnahmezertifikate auszustellen; und (d) die Teilnehmererfahrung zu verbessern. Ohne Einwilligung nutzen wir Ihre Daten nicht für Werbung Dritter.',
                'it': 'I dati sono usati esclusivamente per: (a) elaborare le iscrizioni e verificare i requisiti; (b) comunicare informazioni sull’evento; (c) rilasciare certificati di partecipazione; e (d) migliorare l’esperienza dei partecipanti. Non usiamo i tuoi dati per pubblicità di terzi senza consenso.',
                'nl': 'Gegevens worden uitsluitend gebruikt om: (a) inschrijvingen te verwerken en deelname te controleren; (b) evenementsinformatie te versturen; (c) deelnamecertificaten af te geven; en (d) de deelnemerservaring te verbeteren. We gebruiken je gegevens niet voor advertenties van derden zonder toestemming.',
                'id': 'Data digunakan secara eksklusif untuk: (a) memproses pendaftaran dan memeriksa kelayakan; (b) mengomunikasikan informasi acara; (c) menerbitkan sertifikat partisipasi; dan (d) meningkatkan pengalaman peserta. Kami tidak memakai data Anda untuk iklan pihak ketiga tanpa persetujuan.',
                'ms': 'Data digunakan secara eksklusif untuk: (a) memproses pendaftaran dan menyemak kelayakan; (b) menyampaikan maklumat acara; (c) mengeluarkan sijil penyertaan; dan (d) meningkatkan pengalaman peserta. Kami tidak menggunakan data anda untuk iklan pihak ketiga tanpa kebenaran.',
            },
            {
                'title': '3. Base Legal (LGPD)',
                'body': 'O tratamento de dados é baseado no consentimento do titular (Art. 7º, I da Lei nº 13.709/2018 — LGPD) e, quando aplicável, na execução de contrato ou de procedimentos preliminares relacionados a contrato (Art. 7º, V). Você pode revogar o consentimento a qualquer momento.',
                'en': 'Data processing is based on the data subject’s consent (Art. 7, I of Law No. 13,709/2018 — LGPD) and, where applicable, on the performance of a contract or preliminary procedures related to a contract (Art. 7, V). You may withdraw consent at any time.',
                'es': 'El tratamiento de datos se basa en el consentimiento del titular (Art. 7, I de la Ley nº 13.709/2018 — LGPD) y, cuando corresponda, en la ejecución de un contrato o de procedimientos preliminares relacionados (Art. 7, V). Puede revocar el consentimiento en cualquier momento.',
                'fr': "Le traitement des données repose sur le consentement de la personne concernée (art. 7, I de la loi n° 13.709/2018 — LGPD) et, le cas échéant, sur l'exécution d'un contrat ou de procédures préliminaires liées à un contrat (art. 7, V). Vous pouvez retirer votre consentement à tout moment.",
                'de': 'Die Datenverarbeitung stützt sich auf die Einwilligung der betroffenen Person (Art. 7, I des Gesetzes Nr. 13.709/2018 — LGPD) und, wo anwendbar, auf die Vertragserfüllung oder vorvertragliche Maßnahmen (Art. 7, V). Sie können die Einwilligung jederzeit widerrufen.',
                'it': 'Il trattamento si basa sul consenso dell’interessato (art. 7, I della legge n. 13.709/2018 — LGPD) e, ove applicabile, sull’esecuzione di un contratto o di procedure preliminari (art. 7, V). Puoi revocare il consenso in qualsiasi momento.',
                'nl': 'Gegevensverwerking berust op toestemming van de betrokkene (art. 7, I van wet nr. 13.709/2018 — LGPD) en, waar van toepassing, op de uitvoering van een overeenkomst of daaraan voorafgaande handelingen (art. 7, V). Je kunt toestemming altijd intrekken.',
                'id': 'Pemrosesan data berdasarkan persetujuan subjek data (Pasal 7 ayat (1) UU No. 13.709/2018 — LGPD) dan, jika berlaku, pelaksanaan kontrak atau prosedur preliminer terkait kontrak (Pasal 7 ayat (5)). Anda dapat menarik persetujuan kapan saja.',
                'ms': 'Pemprosesan data berasaskan kebenaran subjek data (Perkara 7, I Akta No. 13.709/2018 — LGPD) dan, jika berkenaan, pelaksanaan kontrak atau prosedur awal berkaitan kontrak (Perkara 7, V). Anda boleh menarik balik kebenaran pada bila-bila masa.',
            },
            {
                'title': '4. Compartilhamento de Dados',
                'body': 'Seus dados pessoais não são vendidos nem compartilhados com terceiros para marketing. Podem ser compartilhados apenas quando necessário para cumprir obrigação legal ou regulatória, com prestadores de serviço que atuam sob contrato (hospedagem, e-mail) ou mediante consentimento expresso seu.',
                'en': 'Your personal data is not sold or shared with third parties for marketing. It may be shared only when required by law or regulation, with service providers acting under contract (hosting, email) or with your express consent.',
                'es': 'Sus datos personales no se venden ni se comparten con terceros para marketing. Solo pueden compartirse cuando sea obligación legal o reguladora, con proveedores de servicio bajo contrato (alojamiento, correo) o con su consentimiento expreso.',
                'fr': "Vos données personnelles ne sont ni vendues ni partagées avec des tiers à des fins marketing. Elles peuvent être partagées uniquement si la loi l'exige, avec des prestataires de services sous contrat (hébergement, e-mail) ou avec votre consentement explicite.",
                'de': 'Ihre personenbezogenen Daten werden nicht verkauft und nicht zu Marketingzwecken an Dritte weitergegeben. Eine Weitergabe erfolgt nur, wenn gesetzlich oder regulatorisch erforderlich, an Dienstleister im Rahmen eines Vertrags (Hosting, E-Mail) oder mit Ihrer ausdrücklichen Einwilligung.',
                'it': 'I tuoi dati personali non sono venduti né condivisi con terzi per marketing. Possono essere condivisi solo quando richiesto dalla legge, con fornitori di servizi sotto contratto (hosting, e-mail) o con il tuo consenso espresso.',
                'nl': 'Je persoonsgegevens worden niet verkocht of gedeeld met derden voor marketing. Delen gebeurt alleen wanneer wettelijk verplicht, met dienstverleners onder contract (hosting, e-mail) of met je uitdrukkelijke toestemming.',
                'id': 'Data pribadi Anda tidak dijual atau dibagikan ke pihak ketiga untuk pemasaran. Hanya dibagikan jika diwajibkan hukum/regulasi, dengan penyedia layanan berdasarkan kontrak (hosting, email) atau dengan persetujuan tegas Anda.',
                'ms': 'Data peribadi anda tidak dijual atau dikongsi dengan pihak ketiga untuk pemasaran. Ia mungkin dikongsi hanya apabila diwajibkan undang-undang, dengan penyedia perkhidmatan di bawah kontrak (hosting, e-mel) atau dengan kebenaran tegas anda.',
            },
            {
                'title': '5. Retenção de Dados',
                'body': 'Os dados são mantidos pelo período necessário para cumprir as finalidades para as quais foram coletados ou pelo prazo exigido pela legislação aplicável. Encerrada a finalidade, os dados são eliminados ou anonimizados de forma segura.',
                'en': 'Data is kept for the period necessary to fulfill the purposes for which it was collected or for the term required by applicable law. Once the purpose ends, data is securely deleted or anonymized.',
                'es': 'Los datos se conservan por el período necesario para cumplir las finalidades para las que fueron recabados o por el plazo que exija la legislación aplicable. Finalizada la finalidad, los datos se eliminan o se anonimizan de forma segura.',
                'fr': "Les données sont conservées pendant la durée nécessaire aux finalités pour lesquelles elles ont été collectées ou selon le délai exigé par la législation applicable. Une fois la finalité atteinte, les données sont supprimées ou anonymisées de manière sécurisée.",
                'de': 'Die Daten werden so lange aufbewahrt, wie es für die Zwecke, für die sie erhoben wurden, erforderlich ist, oder wie es das geltende Recht verlangt. Nach Wegfall des Zwecks werden die Daten sicher gelöscht oder anonymisiert.',
                'it': 'I dati sono conservati per il periodo necessario alle finalità per cui sono stati raccolti o per il termine previsto dalla legge. Esaurita la finalità, i dati vengono eliminati o anonimizzati in modo sicuro.',
                'nl': 'Gegevens worden bewaard zolang nodig voor de doeleinden waarvoor ze zijn verzameld of volgens de wettelijke bewaartermijn. Na het vervallen van het doel worden gegevens veilig verwijderd of geanonimiseerd.',
                'id': 'Data disimpan selama diperlukan untuk mencapai tujuan pengumpulan atau sesuai jangka waktu hukum yang berlaku. Setelah tujuan tercapai, data dihapus atau dianonimkan dengan aman.',
                'ms': 'Data disimpan untuk tempoh yang diperlukan bagi mencapai tujuan pengumpulan atau mengikut tempoh undang-undang. Selepas tujuan tamat, data dipadam atau dianonimkan dengan selamat.',
            },
            {
                'title': '6. Direitos do Titular',
                'body': 'Conforme a LGPD, você tem direito a: confirmação e acesso aos dados; correção de dados incompletos ou desatualizados; anonimização, bloqueio ou eliminação de dados desnecessários; portabilidade; e eliminação de dados tratados com consentimento. Para exercer esses direitos, use o e-mail da seção Contato.',
                'en': 'Under the LGPD, you have the right to: confirmation and access to data; correction of incomplete or outdated data; anonymization, blocking or deletion of unnecessary data; portability; and deletion of data processed with consent. To exercise these rights, use the email in the Contact section.',
                'es': 'Según la LGPD, usted tiene derecho a: confirmación y acceso a los datos; corrección de datos incompletos o desactualizados; anonimización, bloqueo o eliminación de datos innecesarios; portabilidad; y eliminación de datos tratados con consentimiento. Para ejercer estos derechos, use el correo de la sección Contacto.',
                'fr': "Selon la LGPD, vous avez droit à : la confirmation et l'accès aux données ; la correction de données incomplètes ou obsolètes ; l'anonymisation, le blocage ou la suppression de données inutiles ; la portabilité ; et la suppression des données traitées avec consentement. Pour exercer ces droits, utilisez l'e-mail de la section Contact.",
                'de': 'Nach der LGPD haben Sie das Recht auf: Bestätigung und Zugang zu Daten; Berichtigung unvollständiger oder veralteter Daten; Anonymisierung, Sperrung oder Löschung unnötiger Daten; Portabilität; und Löschung einwilligungsbasierter Daten. Zur Ausübung nutzen Sie die E-Mail-Adresse im Abschnitt Kontakt.',
                'it': 'Secondo la LGPD hai diritto a: conferma e accesso ai dati; correzione di dati incompleti o obsoleti; anonimizzazione, blocco o cancellazione di dati non necessari; portabilità; e cancellazione dei dati trattati con consenso. Per esercitare i diritti usa l’e-mail nella sezione Contatto.',
                'nl': 'Onder de LGPD heb je recht op: bevestiging en toegang tot gegevens; correctie van onvolledige of verouderde gegevens; anonymisering, blokkering of verwijdering van onnodige gegevens; overdraagbaarheid; en verwijdering van gegevens op basis van toestemming. Gebruik het e-mailadres in de sectie Contact.',
                'id': 'Menurut LGPD, Anda berhak atas: konfirmasi dan akses data; koreksi data tidak lengkap atau kedaluwarsa; anonimisasi, pemblokiran atau penghapusan data tidak perlu; portabilitas; dan penghapusan data yang diproses dengan persetujuan. Untuk menggunakan hak tersebut, gunakan e-mail pada bagian Kontak.',
                'ms': 'Mengikut LGPD, anda berhak mendapat: pengesahan dan akses kepada data; pembetulan data tidak lengkap atau lapuk; anonimisasi, penyekatan atau pembuangan data tidak perlu; kebolehpindahan; dan pembuangan data yang diproses dengan kebenaran. Untuk menggunakan hak tersebut, gunakan e-mel pada bahagian Hubungi.',
            },
            {
                'title': '7. Segurança dos Dados',
                'body': 'Adotamos medidas técnicas e administrativas adequadas para proteger dados pessoais contra acesso não autorizado e situações acidentais ou ilícitas de destruição, perda, alteração ou comunicação indevida. Nenhum sistema é 100% seguro; em caso de incidente relevante, informaremos os titulares afetados conforme a lei.',
                'en': 'We take appropriate technical and administrative measures to protect personal data against unauthorized access and accidental or unlawful destruction, loss, alteration or disclosure. No system is 100% secure; in the event of a relevant incident, we will notify affected data subjects as required by law.',
                'es': 'Adoptamos medidas técnicas y administrativas adecuadas para proteger los datos personales contra accesos no autorizados y situaciones accidentales o ilícitas de destrucción, pérdida, alteración o comunicación indebida. Ningún sistema es 100% seguro; ante un incidente relevante, informaremos a los titulares afectados según la ley.',
                'fr': "Nous prenons des mesures techniques et administratives appropriées pour protéger les données personnelles contre tout accès non autorisé et toute destruction, perte, altération ou communication illicites. Aucun système n'est sûr à 100 % ; en cas d'incident pertinent, nous informerons les personnes concernées conformément à la loi.",
                'de': 'Wir treffen angemessene technische und organisatorische Maßnahmen zum Schutz personenbezogener Daten vor unbefugtem Zugriff und vor unrechtmäßiger Zerstörung, Verlust, Veränderung oder Offenlegung. Kein System ist zu 100 % sicher; bei relevanten Vorfällen informieren wir die Betroffenen gesetzeskonform.',
                'it': 'Adottiamo misure tecniche e amministrative adeguate per proteggere i dati personali da accessi non autorizzati e da distruzione, perdita, alterazione o comunicazione illecite accidentali. Nessun sistema è al 100% sicuro; in caso di incidente rilevante, informeremo gli interessati secondo la legge.',
                'nl': 'We nemen passende technische en organisatorische maatregelen om persoonsgegevens te beschermen tegen onbevoegde toegang en toevallige of onrechtmatige vernietiging, verlies, wijziging of openbaarmaking. Geen enkel systeem is 100% veilig; bij een relevant incident stellen we betrokkenen volgens de wet op de hoogte.',
                'id': 'Kami menerapkan langkah teknis dan administratif yang tepat untuk melindungi data pribadi dari akses tak sah serta penghacuran, kehilangan, perubahan atau pengungkapan tidak sah secara kebetulan atau melanggar hukum. Tidak ada sistem yang 100% aman; bila ada insiden relevan, kami akan memberi tahu subjek data sesuai hukum.',
                'ms': 'Kami mengambil langkah teknikal dan pentadbiran yang sesuai untuk melindungi data peribadi daripada capaian tanpa kebenaran serta pemusnahan, kehilangan, perubahan atau pendedahan melanggar hukum secara sengaja atau kebetulan. Tiada sistem 100% selamat; dalam insiden berkaitan, kami akan memaklumkan subjek data mengikut undang-undang.',
            },
            {
                'title': '8. Contato',
                'body': 'Para exercer seus direitos ou esclarecer dúvidas sobre esta política, entre em contato: pedro.pereira63@portalsesisp.org.br',
                'en': 'To exercise your rights or ask questions about this policy, contact: pedro.pereira63@portalsesisp.org.br',
                'es': 'Para ejercer sus derechos o aclarar dudas sobre esta política, contáctenos en: pedro.pereira63@portalsesisp.org.br',
                'fr': "Pour exercer vos droits ou poser des questions sur cette politique, contactez : pedro.pereira63@portalsesisp.org.br",
                'de': 'Zur Ausübung Ihrer Rechte oder bei Fragen zu dieser Richtlinie: pedro.pereira63@portalsesisp.org.br',
                'it': 'Per esercitare i tuoi diritti o chiarire dubbi su questa policy: pedro.pereira63@portalsesisp.org.br',
                'nl': 'Om je rechten uit te oefenen of vragen over dit beleid: pedro.pereira63@portalsesisp.org.br',
                'id': 'Untuk menggunakan hak Anda atau bertanya tentang kebijakan ini: pedro.pereira63@portalsesisp.org.br',
                'ms': 'Untuk menggunakan hak anda atau bertanya tentang dasar ini: pedro.pereira63@portalsesisp.org.br',
            },
        ],
    },
    'aviso_legal': {
        'page_title': {
            'pt-BR': 'Aviso Legal — SWDL', 'en': 'Legal Notice — SWDL', 'es': 'Aviso Legal — SWDL',
            'fr': 'Mentions légales — SWDL', 'de': 'Impressum — SWDL', 'it': 'Note legali — SWDL',
            'nl': 'Juridische kennisgeving — SWDL', 'id': 'Pernyataan Hukum — SWDL',
            'ms': 'Pemberitahuan Undang-undang — SWDL',
        },
        'hero_title': {
            'pt-BR': 'Aviso Legal', 'en': 'Legal Notice', 'es': 'Aviso Legal',
            'fr': 'Mentions légales', 'de': 'Impressum', 'it': 'Note legali',
            'nl': 'Juridische kennisgeving', 'id': 'Pernyataan Hukum',
            'ms': 'Pemberitahuan Undang-undang',
        },
        'content': {
            'pt-BR': 'Informações legais sobre propriedade, uso e responsabilidades do site SWDL.',
            'en': 'Legal information about ownership, use and responsibilities of the SWDL website.',
            'es': 'Información legal sobre propiedad, uso y responsabilidades del sitio SWDL.',
            'fr': "Informations juridiques sur la propriété, l'utilisation et les responsabilités du site SWDL.",
            'de': 'Rechtliche Informationen zu Eigentum, Nutzung und Verantwortlichkeiten der SWDL-Website.',
            'it': 'Informazioni legali su proprietà, uso e responsabilità del sito SWDL.',
            'nl': 'Juridische informatie over eigendom, gebruik en verantwoordelijkheden van de SWDL-website.',
            'id': 'Informasi hukum tentang kepemilikan, penggunaan dan tanggung jawab situs SWDL.',
            'ms': 'Maklumat undang-undang tentang pemilikan, penggunaan dan tanggungjawab laman web SWDL.',
        },
        'sections': [
            {
                'title': '1. Propriedade Intelectual',
                'body': 'Todo o conteúdo deste site — textos, imagens, gráficos, marcas, logotipos e demais materiais — é de propriedade da SWDL — SESI World Diplomacy League ou de seus parceiros e é protegido pelas leis brasileiras e internacionais de propriedade intelectual. É proibida a reprodução total ou parcial sem autorização prévia, salvo os limites da lei.',
                'en': 'All content on this site — texts, images, graphics, trademarks, logos and other materials — belongs to SWDL — SESI World Diplomacy League or its partners and is protected by Brazilian and international intellectual property laws. Full or partial reproduction without prior authorization is prohibited, except as permitted by law.',
                'es': 'Todo el contenido de este sitio — textos, imágenes, gráficos, marcas, logotipos y demás materiales — es propiedad de la SWDL — SESI World Diplomacy League o sus socios y está protegido por las leis brasileñas e internacionales de propiedad intelectual. Se prohíbe la reproducción total o parcial sin autorización previa, salvo los límites de la ley.',
                'fr': "Tout le contenu de ce site — textes, images, graphiques, marques, logos et autres matériaux — appartient à la SWDL — SESI World Diplomacy League ou à ses partenaires et est protégé par les lois brésiliennes et internationales sur la propriété intellectuelle. Toute reproduction totale ou partielle sans autorisation préalable est interdite, sauf les limites de la loi.",
                'de': 'Sämtliche Inhalte dieser Website — Texte, Bilder, Grafiken, Marken, Logos und sonstige Materialien — gehören der SWDL — SESI World Diplomacy League oder ihren Partnern und sind durch brasilianische und internationale Gesetze zum Schutz des geistigen Eigentums geschützt. Vervielfältigung ganz oder teilweise ohne vorherige Genehmigung ist untersagt, soweit das Gesetz nicht anderes vorsieht.',
                'it': 'Tutti i contenuti di questo sito — testi, immagini, grafiche, marchi, loghi e altri materiali — sono di proprietà della SWDL — SESI World Diplomacy League o dei suoi partner e sono tutelati dalle leggi brasiliane e internazionali sulla proprietà intellettuale. È vietata la riproduzione totale o parziale senza autorizzazione preventiva, nei limiti di legge.',
                'nl': 'Alle inhoud van deze website — teksten, afbeeldingen, grafieken, merken, logo’s en andere materialen — is eigendom van SWDL — SESI World Diplomacy League of haar partners en wordt beschermd door Braziliaanse en internationale wetten op intellectueel eigendom. Volledige of gedeeltelijke reproductie zonder voorafgaande toestemming is verboden, behoudens wettelijke uitzonderingen.',
                'id': 'Seluruh isi situs ini — teks, gambar, grafis, merek, logo dan materi lain — adalah milik SWDL — SESI World Diplomacy League atau mitranya dan dilindungi hukum kekayaan intelektual Brasil dan internasional. Dilarang memproduksi seluruh atau sebagian tanpa izin terlebih dahulu, sejauh diizinkan hukum.',
                'ms': 'Semua kandungan laman web ini — teks, imej, grafik, tanda dagangan, logo dan bahan lain — adalah milik SWDL — SESI World Diplomacy League atau rakan kongsi dan dilindungi undang-undang harta intelek Brazil dan antarabangsa. Pembiakan keseluruhan atau sebahagian tanpa kebenaran terdahulu adalah dilarang, melainkan setakat yang dibenarkan undang-undang.',
            },
            {
                'title': '2. Uso do Site',
                'body': 'O uso deste site implica a aceitação dos presentes termos legais e, quando aplicável, dos Termos de Uso. Você se compromete a utilizar o site de forma ética e em conformidade com a legislação vigente, sem prejudicar o funcionamento da plataforma ou direitos de terceiros.',
                'en': 'Using this site implies acceptance of these legal terms and, where applicable, the Terms of Use. You agree to use the site ethically and in compliance with applicable legislation, without harming the platform or third-party rights.',
                'es': 'El uso de este sitio implica la aceptación de los presentes términos legales y, cuando corresponda, de los Términos de Uso. Usted se compromete a utilizar el sitio de forma ética y conforme a la legislación vigente, sin perjudicar la plataforma ni derechos de terceros.',
                'fr': "L'utilisation de ce site implique l'acceptation des présents termes légaux et, le cas échéant, des Conditions d'utilisation. Vous vous engagez à utiliser le site de manière éthique et conforme à la législation applicable, sans nuire à la plateforme ni aux droits des tiers.",
                'de': 'Die Nutzung dieser Website gilt als Annahme dieser rechtlichen Hinweise und, soweit anwendbar, der Nutzungsbedingungen. Sie verpflichten sich, die Website ethisch und rechtmäßig zu nutzen, ohne die Plattform oder Rechte Dritter zu beeinträchtigen.',
                'it': 'L’uso di questo sito implica l’accettazione dei presenti termini legali e, ove applicabile, dei Termini di utilizzo. Ti impegni a usare il sito in modo etico e conforme alla legge, senza danneggiare la piattaforma o i diritti di terzi.',
                'nl': 'Het gebruik van deze website betekent acceptatie van deze juridische voorwaarden en, waar van toepassing, de Gebruiksvoorwaarden. Je gebruikt de site ethisch en volgens de wet, zonder het platform of rechten van derden te schaden.',
                'id': 'Penggunaan situs ini berarti penerimaan persyaratan hukum ini dan, jika berlaku, Syarat Penggunaan. Anda setuju menggunakan situs secara etis dan sesuai hukum, tanpa merugikan platform atau hak pihak lain.',
                'ms': 'Penggunaan laman web ini bermakna penerimaan syarat undang-undang ini dan, jika berkenaan, Syarat Penggunaan. Anda bersetuju menggunakannya secara etik dan mematuhi undang-undang, tanpa memudaratkan platform atau hak pihak ketiga.',
            },
            {
                'title': '3. Links Externos',
                'body': 'Este site pode conter links para sites de terceiros. A SWDL não controla nem se responsabiliza pelo conteúdo, políticas de privacidade, disponibilidade ou práticas desses sites. A inclusão de um link não implica endosso ou parceria.',
                'en': 'This site may contain links to third-party sites. SWDL does not control and is not responsible for the content, privacy policies, availability or practices of those sites. Including a link does not imply endorsement or partnership.',
                'es': 'Este sitio puede contener enlaces a sitios de terceros. La SWDL no controla ni se responsabiliza por el contenido, políticas de privacidad, disponibilidad o prácticas de dichos sitios. Incluir un enlace no implica respaldo ni alianza.',
                'fr': "Ce site peut contenir des liens vers des sites tiers. La SWDL ne contrôle pas et n'est pas responsable du contenu, des politiques de confidentialité, de la disponibilité ou des pratiques de ces sites. L'inclusion d'un lien n'implique pas approbation ni partenariat.",
                'de': 'Diese Website kann Links zu Websites Dritter enthalten. Die SWDL kontrolliert deren Inhalte, Datenschutzrichtlinien, Verfügbarkeit oder Praktiken nicht und haftet nicht dafür. Die Aufnahme eines Links bedeutet keine Zustimmung oder Partnerschaft.',
                'it': 'Questo sito può contenere link a siti di terzi. La SWDL non controlla e non è responsabile del contenuto, delle privacy policy, della disponibilità o delle pratiche di tali siti. L’inserimento di un link non implica approvazione o partnership.',
                'nl': 'Deze website kan links naar sites van derden bevatten. SWDL controleert de inhoud, privacybeleid, beschikbaarheid of praktijken van die sites niet en is daar niet verantwoordelijk voor. Een link impliceert geen steun of partnerschap.',
                'id': 'Situs ini mungkin berisi tautan ke situs pihak ketiga. SWDL tidak mengontrol dan tidak bertanggung jawab atas isi, kebijakan privasi, ketersediaan atau praktik situs tersebut. Sertanya tautan tidak berarti dukungan atau kemitraan.',
                'ms': 'Laman web ini mungkin mengandungi pautan ke laman web pihak ketiga. SWDL tidak mengawal dan tidak bertanggungjawab ke atas kandungan, dasar privasi, ketersediaan atau amalan laman tersebut. Sertanya pautan tidak bermakna sokongan atau perkongsian.',
            },
            {
                'title': '4. Isenção de Responsabilidade',
                'body': 'As informações deste site são fornecidas "como estão", sem garantias expressas ou implícitas de qualquer tipo. A SWDL não garante disponibilidade ininterrupta, ausência de erros ou adequação a um propósito específico, nem se responsabiliza por danos diretos ou indiretos decorrentes do uso ou da impossibilidade de uso do site.',
                'en': 'Information on this site is provided "as is", without express or implied warranties of any kind. SWDL does not guarantee uninterrupted availability, error-free operation or fitness for a particular purpose, and is not liable for direct or indirect damages arising from use or inability to use the site.',
                'es': 'La información de este sitio se ofrece "tal cual", sin garantías expresas o implícitas de ningún tipo. La SWDL no garantiza disponibilidad ininterrumpida, ausencia de errores ni idoneidad para un propósito específico, ni responde por daños directos o indirectos derivados del uso o la imposibilidad de uso del sitio.',
                'fr': "Les informations de ce site sont fournies « en l'état », sans garanties expresses ou implicites d'aucune sorte. La SWDL ne garantit ni disponibilité continue, ni absence d'erreurs, ni adéquation à un objectif particulier, et n'est pas responsable des dommages directs ou indirects liés à l'utilisation ou à l'impossibilité d'utilisation du site.",
                'de': 'Die Informationen auf dieser Website werden "wie besehen" bereitgestellt, ohne ausdrückliche oder stillschweigende Gewährleistungen. Die SWDL garantiet keine ununterbrochene Verfügbarkeit, fehlerfreien Betrieb oder Eignung für einen bestimmten Zweck und haftet nicht für direkte oder indirekte Schäden aus der Nutzung oder Nichtnutzung der Website.',
                'it': 'Le informazioni su questo sito sono fornite “così com’è”, senza garanzie esplicite o implicite di alcun tipo. La SWDL non garantisce disponibilità ininterrotta, assenza di errori o adeguatezza a uno scopo specifico e non è responsabile di danni diretti o indiretti derivanti dall’uso o dall’impossibilità di usare il sito.',
                'nl': 'De informatie op deze website wordt "zoals deze is" aangeboden, zonder uitdrukkelijke of stilzwijgende garanties. SWDL garandeert geen ononderbroken beschikbaarheid, foutloze werking of geschiktheid voor een bepaald doel en is niet aansprakelijk voor directe of indirecte schade door gebruik of onbruik van de website.',
                'id': 'Informasi di situs ini disediakan "sebagaimana adanya", tanpa jaminan tersirat atau tersurat apa pun. SWDL tidak menjamin ketersediaan tanpa gangguan, bebas kesalahan atau kesesuaian untuk tujuan tertentu, dan tidak bertanggung jawab atas kerugian langsung atau tidak langsung akibat penggunaan atau ketidakmungkinan menggunakan situs.',
                'ms': 'Maklumat di laman web ini disediakan "sebagaimana adanya", tanpa sebarang jaminan tersurat atau tersirat. SWDL tidak menjamin ketersediaan tanpa gangguan, ketiadaan ralat atau kesesuaian untuk tujuan tertentu, dan tidak bertanggungjawab atas kerosakan langsung atau tidak langsung akibat penggunaan atau ketidakbolehan menggunakan laman web.',
            },
            {
                'title': '5. Alterações',
                'body': 'A SWDL reserva-se o direito de alterar estes termos legais a qualquer momento, sem aviso prévio. As alterações entram em vigor imediatamente após a publicação nesta página. O uso continuado do site após alterações constitui aceitação da nova versão.',
                'en': 'SWDL reserves the right to change these legal terms at any time without prior notice. Changes take effect immediately after publication on this page. Continued use of the site after changes constitutes acceptance of the new version.',
                'es': 'La SWDL se reserva el derecho de modificar estos términos legales en cualquier momento, sin aviso previo. Los cambios entran en vigor inmediatamente después de su publicación en esta página. El uso continuado del sitio tras los cambios implica aceptación de la nueva versión.',
                'fr': "La SWDL se réserve le droit de modifier ces termes légaux à tout moment, sans préavis. Les changements prennent effet immédiatement après publication sur cette page. La poursuite de l'utilisation du site après modification vaut acceptation de la nouvelle version.",
                'de': 'Die SWDL behält sich das Recht vor, diese rechtlichen Hinweise jederzeit ohne Vorankündigung zu ändern. Änderungen treten mit der Veröffentlichung auf dieser Seite sofort in Kraft. Die fortgesetzte Nutzung der Website nach Änderungen gilt als Zustimmung zur neuen Fassung.',
                'it': 'La SWDL si riserva il diritto di modificare i presenti termini legali in qualsiasi momento, senza preavviso. Le modifiche hanno effetto immediato dopo la pubblicazione su questa pagina. L’uso continuato del sito dopo le modifiche implica accettazione della nuova versione.',
                'nl': 'SWDL behoudt zich het recht voor deze juridische voorwaarden altijd zonder voorafgaande kennisgeving te wijzigen. Wijzigingen treden direct in werking na publicatie op deze pagina. Door de website na wijzigingen te blijven gebruiken, accepteer je de nieuwe versie.',
                'id': 'SWDL berhak mengubah persyaratan hukum ini kapan saja, tanpa pemberitahuan sebelumnya. Perubahan berlaku segera setelah dipublikasikan di halaman ini. Penggunaan situs yang berlanjut setelah perubahan berarti penerimaan versi baru.',
                'ms': 'SWDL berhak mengubah syarat undang-undang ini pada bila-bila masa, tanpa notis awal. Perubahan berkuat kuasa serta-merta selepas diterbitkan di halaman ini. Penggunaan laman web yang berterusan selepas perubahan bermakna penerimaan versi baharu.',
            },
            {
                'title': '6. Contato',
                'body': 'Em caso de dúvidas sobre estes termos legais, entre em contato: pedro.pereira63@portalsesisp.org.br',
                'en': 'If you have questions about these legal terms, contact: pedro.pereira63@portalsesisp.org.br',
                'es': 'Si tiene dudas sobre estos términos legales, contáctenos en: pedro.pereira63@portalsesisp.org.br',
                'fr': "Pour toute question sur ces termes légaux, contactez : pedro.pereira63@portalsesisp.org.br",
                'de': 'Bei Fragen zu diesen rechtlichen Hinweisen: pedro.pereira63@portalsesisp.org.br',
                'it': 'Per domande sui presenti termini legali: pedro.pereira63@portalsesisp.org.br',
                'nl': 'Vragen over deze juridische voorwaarden: pedro.pereira63@portalsesisp.org.br',
                'id': 'Pertanyaan tentang persyaratan hukum ini: pedro.pereira63@portalsesisp.org.br',
                'ms': 'Soalan mengenai syarat undang-undang ini: pedro.pereira63@portalsesisp.org.br',
            },
        ],
    },
}

LOCALES = ['pt-BR', 'en', 'es', 'fr', 'de', 'it', 'nl', 'id', 'ms']


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(p, data):
    raw = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    p.write_bytes(raw.encode('utf-8'))


# Ensure every section has all locale keys
for page in PAGES.values():
    for s in page['sections']:
        for loc in LOCALES:
            if loc not in s:
                s[loc] = s.get('en') or s.get('pt-BR')

# Localized section titles (non-PT); applied after bodies are written
TITLES = {
    'termos': {
        'en': ['Acceptance of Terms', 'Use of the Site', 'Registrations', 'Participant Conduct',
               'Intellectual Property', 'Limitation of Liability', 'Cancellation and Refunds',
               'Changes to Terms', 'Contact'],
        'es': ['Aceptación de los Términos', 'Uso del Sitio', 'Inscripciones', 'Conducta de los Participantes',
               'Propiedad Intelectual', 'Limitación de Responsabilidad', 'Cancelación y Reembolsos',
               'Cambios en los Términos', 'Contacto'],
        'fr': ['Acceptation des Conditions', 'Utilisation du Site', 'Inscriptions', 'Conduite des Participants',
               'Propriété Intellectuelle', 'Limitation de Responsabilité', 'Annulation et Remboursements',
               'Modification des Conditions', 'Contact'],
        'de': ['Akzeptanz der Bedingungen', 'Nutzung der Website', 'Anmeldungen', 'Teilnehmerverhalten',
               'Geistiges Eigentum', 'Haftungsbeschränkung', 'Stornierung und Rückerstattung',
               'Änderungen der Bedingungen', 'Kontakt'],
        'it': ['Accettazione dei Termini', 'Utilizzo del Sito', 'Iscrizioni', 'Condotta dei Partecipanti',
               'Proprietà Intellettuale', 'Limitazione di Responsabilità', 'Annullamento e Rimborsi',
               'Modifiche ai Termini', 'Contatto'],
        'nl': ['Acceptatie van de Voorwaarden', 'Gebruik van de Website', 'Inschrijvingen', 'Deelnemersgedrag',
               'Intellectueel Eigendom', 'Beperking van Aansprakelijkheid', 'Afgelasting en Restitutie',
               'Wijzigingen van de Voorwaarden', 'Contact'],
        'id': ['Penerimaan Persyaratan', 'Penggunaan Situs', 'Pendaftaran', 'Perilaku Peserta',
               'Kekayaan Intelektual', 'Pembatasan Tanggung Jawab', 'Pembatalan dan Pengembalian',
               'Perubahan Persyaratan', 'Kontak'],
        'ms': ['Penerimaan Syarat', 'Penggunaan Laman Web', 'Pendaftaran', 'Tingkah Laku Peserta',
               'Harta Intelek', 'Pembatasan Liabiliti', 'Pembatalan dan Pemulangan',
               'Perubahan Syarat', 'Hubungi'],
    },
    'privacidade': {
        'en': ['Data Collected', 'Purpose of Data', 'Legal Basis (LGPD)', 'Data Sharing',
               'Data Retention', 'Data Subject Rights', 'Data Security', 'Contact'],
        'es': ['Datos Recopilados', 'Finalidad de los Datos', 'Base Legal (LGPD)', 'Compartición de Datos',
               'Retención de Datos', 'Derechos del Titular', 'Seguridad de los Datos', 'Contacto'],
        'fr': ['Données Collectées', 'Finalité des Données', 'Base Légale (LGPD)', 'Partage des Données',
               'Conservation des Données', 'Droits de la Personne Concernée', 'Sécurité des Données', 'Contact'],
        'de': ['Erhobene Daten', 'Zweck der Daten', 'Rechtsgrundlage (LGPD)', 'Datenweitergabe',
               'Datenaufbewahrung', 'Rechte der Betroffenen', 'Datensicherheit', 'Kontakt'],
        'it': ['Dati Raccolti', 'Finalità dei Dati', 'Base Giuridica (LGPD)', 'Condivisione Dati',
               'Conservazione Dati', 'Diritti dell’Interessato', 'Sicurezza dei Dati', 'Contatto'],
        'nl': ['Verzamelde Gegevens', 'Doel van Gegevens', 'Rechtsgrondslag (LGPD)', 'Delen van Gegevens',
               'Bewaartermijn', 'Rechten van de Betrokkene', 'Gegevensbeveiliging', 'Contact'],
        'id': ['Data yang Dikumpulkan', 'Tujuan Data', 'Dasar Hukum (LGPD)', 'Berbagi Data',
               'Penyimpanan Data', 'Hak Subjek Data', 'Keamanan Data', 'Kontak'],
        'ms': ['Data yang Dikumpul', 'Tujuan Data', 'Asas Undang-undang (LGPD)', 'Perkongsian Data',
               'Penyimpanan Data', 'Hak Subjek Data', 'Keselamatan Data', 'Hubungi'],
    },
    'aviso_legal': {
        'en': ['Intellectual Property', 'Use of the Site', 'External Links', 'Disclaimer',
               'Changes', 'Contact'],
        'es': ['Propiedad Intelectual', 'Uso del Sitio', 'Enlaces Externos', 'Exención de Responsabilidad',
               'Cambios', 'Contacto'],
        'fr': ['Propriété Intellectuelle', 'Utilisation du Site', 'Liens Externes', 'Avertissement',
               'Modifications', 'Contact'],
        'de': ['Geistiges Eigentum', 'Nutzung der Website', 'Externe Links', 'Haftungsausschluss',
               'Änderungen', 'Kontakt'],
        'it': ['Proprietà Intellettuale', 'Utilizzo del Sito', 'Link Esterni', 'Disclaimer',
               'Modifiche', 'Contatto'],
        'nl': ['Intellectueel Eigendom', 'Gebruik van de Website', 'Externe Links', 'Afwijzing',
               'Wijzigingen', 'Contact'],
        'id': ['Kekayaan Intelektual', 'Penggunaan Situs', 'Tautan Eksternal', 'Penafian',
               'Perubahan', 'Kontak'],
        'ms': ['Harta Intelek', 'Penggunaan Laman Web', 'Pautan Luar', 'Penafian',
               'Perubahan', 'Hubungi'],
    },
}

# Write section bodies (PT titles first; TITLES pass overwrites non-PT titles below)
for loc in LOCALES:
    path = ROOT / f'{loc}.json'
    data = load(path)

    data['legal'] = LEGAL_UI[loc]

    for ns, pack in PAGES.items():
        data.setdefault(ns, {})
        data[ns]['page_title'] = pack['page_title'][loc]
        data[ns]['hero_title'] = pack['hero_title'][loc]
        data[ns]['content'] = pack['content'][loc]
        data[ns]['updated_date'] = UPDATED
        data[ns]['sections'] = [
            {'title': s['title'], 'body': s[loc]}
            for s in pack['sections']
        ]

    save(path, data)
    print('updated', loc)

for loc in LOCALES:
    if loc == 'pt-BR':
        continue
    path = ROOT / f'{loc}.json'
    data = load(path)
    for ns, by_loc in TITLES.items():
        titles = by_loc[loc]
        secs = data[ns]['sections']
        assert len(secs) == len(titles), (loc, ns, len(secs), len(titles))
        for i, title in enumerate(titles):
            secs[i]['title'] = f'{i + 1}. {title}'
    save(path, data)
    print('titles', loc)

print('done')
