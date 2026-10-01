"""Phase 3: seed Sobre / Comites / Testimonials / Gallery i18n keys into all 9 locales."""
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent / "messages"
LOCALES = ["pt-BR", "en", "es", "fr", "de", "it", "nl", "id", "ms"]

# key -> {locale: value}  (pt-BR included for new keys)
T: dict[str, dict[str, str]] = {
    # ── sobre UI leftovers ─────────────────────────────────
    "sobre.history_body": {
        "pt-BR": "Do sonho de alunos do 1º EM à realidade de uma liga que inspira jovens diplomatas em todo o estado. A SWDL cresceu ano após ano, mantendo seu compromisso com a excelência educacional e a formação de cidadãos globais.",
        "en": "From a dream of 1st-year high-school students to a league that inspires young diplomats across the state. SWDL has grown year after year, keeping its commitment to educational excellence and the formation of global citizens.",
        "es": "Del sueño de alumnos de 1º de bachillerato a una liga que inspira a jóvenes diplomáticos de todo el estado. La SWDL ha crecido año tras año, manteniendo su compromiso con la excelencia educativa y la formación de ciudadanos globales.",
        "fr": "D'un rêve d'élèves de 1re année de lycée à une ligue qui inspire de jeunes diplomates dans tout l'État. La SWDL a grandi d'année en année, conservant son engagement en faveur de l'excellence éducative et de la formation de citoyens du monde.",
        "de": "Vom Traum von Schülerinnen und Schülern der Q1 zur Liga, die junge Diplomaten im ganzen Staat inspiriert. Die SWDL ist Jahr für Jahr gewachsen und bleibt ihrer Verpflichtung zu exzellenter Bildung und globaler Bürgerbildung treu.",
        "it": "Dal sogno degli studenti della prima superiore a una lega che ispira giovani diplomati in tutto lo stato. La SWDL è cresciuta anno dopo anno, mantenendo l'impegno per l'eccellenza educativa e la formazione di cittadini globali.",
        "nl": "Van een droom van leerlingen van klas 1 naar een liga die jonge diplomaten in heel de staat inspireert. SWDL is jaar na jaar gegroeid en blijft trouw aan onderwijskwaliteit en mondiale burgerschapsvorming.",
        "id": "Dari mimpi siswa SMA kelas 1 menuju liga yang menginspirasi diplomat muda di seluruh negara bagian. SWDL tumbuh tahun demi tahun, memegang komitmen pada keunggulan pendidikan dan pembentukan warga global.",
        "ms": "Dari impian pelajar tingkatan 1 kepada liga yang menginspirasi diplomat muda di seluruh negeri. SWDL berkembang tahun demi tahun, kekal komitmen kepada kecemerlangan pendidikan dan pembentukan warganegara global.",
    },
    "sobre.watermark": {
        "pt-BR": "SOBRE", "en": "ABOUT", "es": "SOBRE", "fr": "À PROPOS",
        "de": "ÜBER UNS", "it": "CHI SIAMO", "nl": "OVER ONS", "id": "TENTANG", "ms": "MENGENAI",
    },
    "sobre.team_who": {
        "pt-BR": "Quem Faz Acontecer", "en": "Who Makes It Happen", "es": "Quienes Lo Hacen Posible",
        "fr": "Ceux Qui Rendent Cela Possible", "de": "Wer Es Möglich Macht",
        "it": "Chi Lo Rende Possibile", "nl": "Wie Het Mogelijk Maakt",
        "id": "Siapa Yang Mewujudkannya", "ms": "Siapa Yang Merealisasikannya",
    },
    "sobre.tab_current": {
        "pt-BR": "Equipe Atual", "en": "Current Team", "es": "Equipo Actual",
        "fr": "Équipe Actuelle", "de": "Aktuelles Team", "it": "Squadra Attuale",
        "nl": "Huidig Team", "id": "Tim Saat Ini", "ms": "Pasukan Semasa",
    },
    "sobre.tab_2025": {
        "pt-BR": "Gestão 2025", "en": "2025 Leadership", "es": "Gestión 2025",
        "fr": "Direction 2025", "de": "Leitung 2025", "it": "Direzione 2025",
        "nl": "Leiding 2025", "id": "Kepemimpinan 2025", "ms": "Kepimpinan 2025",
    },
    "sobre.testimonial_of": {
        "pt-BR": "Depoimento de {name}", "en": "Testimonial from {name}",
        "es": "Testimonio de {name}", "fr": "Témoignage de {name}",
        "de": "Referenz von {name}", "it": "Testimonianza di {name}",
        "nl": "Getuigenis van {name}", "id": "Testimoni dari {name}",
        "ms": "Testimoni daripada {name}",
    },
    "sobre.role_professora": {
        "pt-BR": "Professora Orientadora", "en": "Faculty Advisor",
        "es": "Asesora Docente", "fr": "Conseillère Pédagogique",
        "de": "Fachbetreuung", "it": "Consulente Docente",
        "nl": "Faculty Advisor", "id": "Penasihat Fakultas",
        "ms": "Penasihat Fakulti",
    },
    "sobre.role_diretora_academica": {
        "pt-BR": "Diretora Acadêmica", "en": "Academic Director",
        "es": "Directora Académica", "fr": "Directrice Académique",
        "de": "Akademische Direktorin", "it": "Direttrice Accademica",
        "nl": "Academisch Directeur", "id": "Direktur Akademik",
        "ms": "Pengarah Akademik",
    },
    "sobre.role_diretora_eventos": {
        "pt-BR": "Diretora de Eventos", "en": "Events Director",
        "es": "Directora de Eventos", "fr": "Directrice des Événements",
        "de": "Veranstaltungsdirektorin", "it": "Direttrice Eventi",
        "nl": "Evenementendirecteur", "id": "Direktur Acara",
        "ms": "Pengarah Acara",
    },
    "sobre.role_diretora_rp": {
        "pt-BR": "Diretora de Relações Públicas", "en": "Public Relations Director",
        "es": "Directora de Relaciones Públicas", "fr": "Directrice des Relations Publiques",
        "de": "Direktorin für Öffentlichkeitsarbeit", "it": "Direttrice Relazioni Pubbliche",
        "nl": "Directeur Public Relations", "id": "Direktur Hubungan Masyarakat",
        "ms": "Pengarah Hubungan Awam",
    },
    "sobre.role_membro": {
        "pt-BR": "Membro", "en": "Member", "es": "Miembro", "fr": "Membre",
        "de": "Mitglied", "it": "Membro", "nl": "Lid", "id": "Anggota", "ms": "Ahli",
    },
    "sobre.role_hr": {
        "pt-BR": "Diretora de Recursos Humanos", "en": "Director of Human Resources",
        "es": "Directora de Recursos Humanos", "fr": "Directrice des Ressources Humaines",
        "de": "Direktorin für Personal", "it": "Direttrice Risorse Umane",
        "nl": "Directeur Personeelszaken", "id": "Direktur Sumber Daya Manusia",
        "ms": "Pengarah Sumber Manusia",
    },
    "sobre.role_admin": {
        "pt-BR": "Coordenadora Administrativa", "en": "Administrative Coordinator",
        "es": "Coordinadora Administrativa", "fr": "Coordonnatrice Administrative",
        "de": "Administrative Koordinatorin", "it": "Coordinatrice Amministrativa",
        "nl": "Administratief Coördinator", "id": "Koordinator Administrasi",
        "ms": "Penyelaras Pentadbiran",
    },
    "sobre.role_staff_web": {
        "pt-BR": "Coord. da Staff & Desenvolvimento Web", "en": "Staff Coord. & Web Development",
        "es": "Coord. de Staff y Desarrollo Web", "fr": "Coord. Staff et Développement Web",
        "de": "Staff-Koord. & Webentwicklung", "it": "Coord. Staff e Sviluppo Web",
        "nl": "Staff-coord. & Webontwikkeling", "id": "Koord. Staf & Pengembangan Web",
        "ms": "Penyelaras Staf & Pembangunan Web",
    },
    "sobre.role_comm": {
        "pt-BR": "Diretora de Comunicação e Marketing", "en": "Director of Communication and Marketing",
        "es": "Directora de Comunicación y Marketing", "fr": "Directrice de la Communication et du Marketing",
        "de": "Direktorin für Kommunikation und Marketing", "it": "Direttrice Comunicazione e Marketing",
        "nl": "Directeur Communicatie en Marketing", "id": "Direktur Komunikasi dan Pemasaran",
        "ms": "Pengarah Komunikasi dan Pemasaran",
    },
    "sobre.role_staff_coord": {
        "pt-BR": "Coordenação da Staff", "en": "Staff Coordination",
        "es": "Coordinación del Staff", "fr": "Coordination du Staff",
        "de": "Staff-Koordination", "it": "Coordinazione Staff",
        "nl": "Staff-coördinatie", "id": "Koordinasi Staf", "ms": "Penyelarasan Staf",
    },
    # ── sobre team quotes (current) ────────────────────────
    "sobre.team_current.0.quote": {
        "pt-BR": "Como Secretário-Geral, aprendi que diplomacia não é só discurso: é escuta, timing e coragem de decisões difíceis pela equipe.",
        "en": "As Secretary-General, I learned that diplomacy is not only speeches: it is listening, timing and the courage to make hard decisions for the team.",
        "es": "Como Secretario General, aprendí que la diplomacia no es solo discurso: es escucha, timing y valentía para decisiones difíciles por el equipo.",
        "fr": "En tant que Secrétaire général, j'ai appris que la diplomatie n'est pas que discours : c'est écouter, le bon timing et le courage des décisions difficiles pour l'équipe.",
        "de": "Als Generalsekretär habe ich gelernt: Diplomatie ist nicht nur Rede — sie ist Zuhören, Timing und den Mut, schwere Entscheidungen für das Team zu treffen.",
        "it": "Da Segretario Generale ho imparato che la diplomazia non è solo discorso: è ascolto, timing e coraggio di decisioni difficili per la squadra.",
        "nl": "Als Secretaris-Generaal leerde ik dat diplomatie niet alleen toespraken zijn: luisteren, timing en de moeilijke beslissingen voor het team.",
        "id": "Sebagai Sekretaris Jenderal, saya belajar bahwa diplomasi bukan hanya pidato: mendengarkan, timing, dan keberanian mengambil keputusan sulit untuk tim.",
        "ms": "Sebagai Setiausaha Agung, saya belajar bahawa diplomasi bukan sekadar ucapan: mendengar, masa dan keberanian membuat keputusan sukar untuk pasukan.",
    },
    "sobre.team_current.1.quote": {
        "pt-BR": "Cada edição parece impossível até o momento em que as portas abrem e tudo flui. Logística é diplomacia nos bastidores.",
        "en": "Each edition seems impossible until the doors open and everything flows. Logistics is diplomacy behind the scenes.",
        "es": "Cada edición parece imposible hasta que se abren las puertas y todo fluye. La logística es diplomacia entre bastidores.",
        "fr": "Chaque édition semble impossible jusqu'à l'ouverture des portes, où tout s'enchaîne. La logistique est la diplomatie en coulisses.",
        "de": "Jede Ausgabe scheint unmöglich, bis die Türen aufgehen und alles fließt. Logistik ist Diplomatie hinter den Kulissen.",
        "it": "Ogni edizione sembra impossibile finché le porte si aprono e tutto scorre. La logistica è diplomazia dietro le quinte.",
        "nl": "Elke editie lijkt onmogelijk tot de deuren opengaan en alles stroomt. Logistiek is diplomatie achter de schermen.",
        "id": "Setiap edisi tampak mustahil sampai pintu terbuka dan semuanya mengalir. Logistik adalah diplomasi di balik layar.",
        "ms": "Setiap edisi nampak mustahil sehingga pintu dibuka dan semuanya mengalir. Logistik adalah diplomasi di sebalik tabir.",
    },
    "sobre.team_current.2.quote": {
        "pt-BR": "Contar a SWDL para fora é fazer a comunidade escolar entender que diplomacia começa no corredor da escola.",
        "en": "Telling the SWDL story outside is helping the school community understand that diplomacy starts in the school corridor.",
        "es": "Contar la SWDL al exterior es hacer que la comunidad escolar entienda que la diplomacia comienza en el pasillo de la escuela.",
        "fr": "Raconter la SWDL à l'extérieur, c'est faire comprendre à la communauté scolaire que la diplomatie commence dans les couloirs de l'école.",
        "de": "Die SWDL nach außen zu erzählen, heißt, der Schulgemeinschaft zu zeigen, dass Diplomatie im Schulflur beginnt.",
        "it": "Raccontare la SWDL al di fuori significa far capire alla comunità scolastica che la diplomazia inizia nel corridoio della scuola.",
        "nl": "Het SWDL-verhaal naar buiten brengen is de schoolgemeenschap laten zien dat diplomatie begint in de schoolgang.",
        "id": "Menceritakan SWDL ke luar adalah membantu komunitas sekolah memahami bahwa diplomasi dimulai di koridor sekolah.",
        "ms": "Menceritakan SWDL ke luar adalah membantu komunitas sekolah memahami bahawa diplomasi bermula di koridor sekolah.",
    },
    "sobre.team_current.3.quote": {
        "pt-BR": "Formar time é como formar delegação: cada pessoa precisa saber seu papel e confiar nas outras. É isso que sustenta a liga.",
        "en": "Building a team is like building a delegation: everyone needs to know their role and trust the others. That is what sustains the league.",
        "es": "Formar un equipo es como formar una delegación: cada persona debe saber su papel y confiar en las demás. Eso sostiene a la liga.",
        "fr": "Former une équipe, c'est former une délégation : chacun doit connaître son rôle et faire confiance aux autres. C'est ce qui fait tenir la ligue.",
        "de": "Ein Team aufbauen ist wie eine Delegation formen: Jede Person muss ihre Rolle kennen und den anderen vertrauen. Das trägt die Liga.",
        "it": "Formare una squadra è come formare una delegazione: ognuno deve sapere il proprio ruolo e fidarsi degli altri. È ciò che sostiene la lega.",
        "nl": "Een team opbouwen is als een delegatie vormen: iedereen moet zijn rol kennen en de anderen vertrouwen. Dat draagt de liga.",
        "id": "Membangun tim sama seperti membentuk delegasi: setiap orang harus tahu perannya dan saling percaya. Itulah yang menopang liga.",
        "ms": "Membina pasukan sama seperti membina delegasi: setiap orang perlu tahu peranan dan saling percaya. Itu yang menyokong liga.",
    },
    "sobre.team_current.4.quote": {
        "pt-BR": "Por trás de cada debate impecável existe organização. Eu gosto de ser a razão pela qual ninguém precisa se preocupar com o “e agora?”.",
        "en": "Behind every flawless debate there is organization. I like being the reason no one has to worry about “what now?”.",
        "es": "Detrás de cada debate impecable hay organización. Me gusta ser la razón por la que nadie se preocupa por el “¿y ahora?”.",
        "fr": "Derrière chaque débat impeccable, il y a de l'organisation. J'aime être la raison pour laquelle personne ne se demande « et maintenant ? ».",
        "de": "Hinter jedem makellosen Debatt liegt Organisation. Ich mag es der Grund zu sein, warum niemand „Und nun?“ fürchten muss.",
        "it": "Dietro ogni dibattito impeccabile c'è organizzazione. Mi piace essere la ragione per cui nessuno deve chiedersi “e adesso?”.",
        "nl": "Achter elk perfect debat zit organisatie. Ik wil de reden zijn dat niemand zich „en nu?” hoeft af te vragen.",
        "id": "Di balik setiap debat yang sempurna ada organisasi. Saya suka menjadi alasan tak ada yang perlu bingung “lalu apa?”.",
        "ms": "Di sebalik setiap debat yang sempurna ada organisasi. Saya suka menjadi sebab tiada siapa perlu risau “sekarang apa?”.",
    },
    "sobre.team_current.5.quote": {
        "pt-BR": "Construir a plataforma da SWDL foi minha forma de servir a liga: transformar caos operacional em experiência fluida para delegados e staff.",
        "en": "Building the SWDL platform was my way of serving the league: turning operational chaos into a smooth experience for delegates and staff.",
        "es": "Construir la plataforma de la SWDL fue mi forma de servir a la liga: convertir el caos operativo en una experiencia fluida para delegados y staff.",
        "fr": "Construire la plateforme de la SWDL a été ma façon de servir la ligue : transformer le chaos opérationnel en expérience fluide pour délégués et staff.",
        "de": "Die SWDL-Plattform zu bauen war meine Art, der Liga zu dienen: operativen Chaos in ein reibungsloses Erlebnis für Delegierte und Staff zu verwandeln.",
        "it": "Costruire la piattaforma della SWDL è stato il mio modo di servire la lega: trasformare il caos operativo in un'esperienza fluida per delegati e staff.",
        "nl": "Het SWDL-platform bouwen was mijn manier om de liga te dienen: operationele chaos omzetten in een soepele ervaring voor afgevaardigden en staff.",
        "id": "Membangun platform SWDL adalah cara saya melayuni liga: mengubah kekacauan operasional menjadi pengalaman lancar bagi delegasi dan staf.",
        "ms": "Membina platform SWDL adalah cara saya menyampaikan jasa kepada liga: mengubah huru-hara operasi menjadi pengalaman lancar untuk wakil dan staf.",
    },
    "sobre.team_current.6.quote": {
        "pt-BR": "Entrar na SWDL foi descobrir que opinião bem pesquisada pesa mais que berro.",
        "en": "Joining SWDL meant discovering that a well-researched opinion weighs more than shouting.",
        "es": "Entrar en la SWDL fue descubrir que una opinión bien investigada pesa más que el grito.",
        "fr": "Rejoindre la SWDL, c'est découvrir qu'un avis bien étudié pèse plus qu'un cri.",
        "de": "In die SWDL zu kommen hieß zu entdecken, dass eine gut recherchierte Meinung mehr wiegt als Lärm.",
        "it": "Entrare nella SWDL ha significato scoprire che un'opinione ben studiata pesa più che un urlo.",
        "nl": "Bij SWDL ontdekte ik dat een goed onderbouwde mening zwaarder weegt dan lawaai.",
        "id": "Masuk SWDL berarti menemukan bahwa opini yang terresearch dengan baik lebih berbobot daripada teriakan.",
        "ms": "Menyertai SWDL bermakna mendapati bahawa pendapat yang baik dikaji lebih berat daripada jeritan.",
    },
    "sobre.team_current.7.quote": {
        "pt-BR": "Aprendi que representar um país é, antes de tudo, entender o outro lado da mesa.",
        "en": "I learned that representing a country is, above all, understanding the other side of the table.",
        "es": "Aprendí que representar un país es, ante todo, entender el otro lado de la mesa.",
        "fr": "J'ai appris que représenter un pays, c'est avant tout comprendre l'autre côté de la table.",
        "de": "Ich lernte, dass ein Land zu vertreten vor allem bedeutet, die andere Seite des Tisches zu verstehen.",
        "it": "Ho imparato che rappresentare un paese è, prima di tutto, capire l'altro lato del tavolo.",
        "nl": "Ik leerde dat een land vertegenwoordigen bovenal de andere kant van de tafel begrijpen is.",
        "id": "Saya belajar bahwa mewakili negara adalah, di atas segalanya, memahami sisi lain meja.",
        "ms": "Saya belajar bahawa mewakili negara adalah, di atas segalanya, memahami sisi lain meja.",
    },
    "sobre.team_current.8.quote": {
        "pt-BR": "Meu primeiro debate me tirou da zona de conforto — e foi exatamente ali que eu cresci.",
        "en": "My first debate took me out of my comfort zone — and that is exactly where I grew.",
        "es": "Mi primer debate me sacó de la zona de conforto — y fue exactamente allí donde crecí.",
        "fr": "Mon premier débat m'a fait sortir de ma zone de confort — et c'est précisément là que j'ai grandi.",
        "de": "Mein erstes Debatt brachte mich aus meiner Komfortzone — und genau dort wuchs ich.",
        "it": "Il mio primo dibattito mi ha tirato fuori dalla zona di comfort — ed è lì che sono cresciuto.",
        "nl": "Mijn eerste debat bracht me uit mijn comfortzone — en daar groeide ik juist.",
        "id": "Debat pertama saya mengeluarkan saya dari zona nyaman — dan di situlah saya berkembang.",
        "ms": "Debat pertama saya mengeluarkan saya dari zon selesa — dan di situ saya berkembang.",
    },
    "sobre.team_current.9.quote": {
        "pt-BR": "Na SWDL encontrei gente que leva o futuro a sério. Isso me deu coragem de fazer o mesmo.",
        "en": "At SWDL I found people who take the future seriously. That gave me the courage to do the same.",
        "es": "En la SWDL encontré gente que se toma el futuro en serio. Eso me dio coraje para hacer lo mismo.",
        "fr": "À la SWDL, j'ai trouvé des gens qui prennent l'au sérieux. Cela m'a donné le courage d'en faire autant.",
        "de": "In der SWDL traf ich Menschen, die die Zukunft ernst nehmen. Das gab mir den Mut, dasselbe zu tun.",
        "it": "Nella SWDL ho trovato persone che prendono sul serio il futuro. Questo mi ha dato il coraggio di fare altrettanto.",
        "nl": "Bij SWDL vond ik mensen die de serieus nemen. Dat gaf mij de moed hetzelfde te doen.",
        "id": "Di SWDL saya menemukan orang-orang yang menganggap masa depan serius. Itu memberi saya keberanian melakukan hal yang sama.",
        "ms": "Di SWDL saya menemui orang yang memandang masa depan dengan serius. Itu memberi saya keberanian berbuat demikian.",
    },
    "sobre.team_current.10.quote": {
        "pt-BR": "Negociar na ONU simulada me ensinou a negociar melhor na vida real — inclusive comigo.",
        "en": "Negotiating in the simulated UN taught me to negotiate better in real life — including with myself.",
        "es": "Negociar en la ONU simulada me enseñó a negociar mejor en la vida real — incluso conmigo mismo.",
        "fr": "Négocier dans l'ONU simulée m'a appris à mieux négocier dans la vie réelle — y compris avec moi-même.",
        "de": "Verhandeln im simulierten UNO hat mich gelehrt, im echten Leben besser zu verhandeln — auch mit mir selbst.",
        "it": "Negociare nelle Nazioni Unite simulate mi ha insegnato a negoziare meglio nella vita reale — anche con me stesso.",
        "nl": "Onderhandelen in de gesimuleerde VN leerde me beter te onderhandelen in het echte leven — ook met mezelf.",
        "id": "BNegosiasi di PBB simulasi mengajarkan saya bernegosiasi lebih baik dalam kehidupan nyata — termasuk dengan diri sendiri.",
        "ms": "Berpakatan dalam PBB simulasi mengajar saya berunding dengan lebih baik dalam kehidupan sebenar — termasuk dengan diri sendiri.",
    },
    "sobre.team_current.11.quote": {
        "pt-BR": "Pesquisar posição nacional virou paixão. Hoje leio notícias de outro jeito.",
        "en": "Researching a national position became a passion. Today I read the news differently.",
        "es": "Investigar una posición nacional se convirtió en pasión. Hoy leo las noticias de otra manera.",
        "fr": "Rechercher une position nationale est devenu une passion. Aujourd'hui, je lis l'actualité autrement.",
        "de": "Eine nationale Position zu recherchieren wurde zur Leidenschaft. Heute lese ich Nachrichten anders.",
        "it": "Ricercare una posizione nazionale è diventato una passione. Oggi leggo le notizie in modo diverso.",
        "nl": "Een nationale positie onderzoeken werd een passie. Vandaag lees ik het nieuws anders.",
        "id": "Meneliti posisi nasional menjadi hasrat. Kini saya membaca berita dengan cara berbeda.",
        "ms": "Menyelidik kedudukan negara menjadi minat. Kini saya membaca berita dengan cara berbeza.",
    },
    "sobre.team_current.12.quote": {
        "pt-BR": "O melhor não é o troféu: é o silêncio depois de um argumento que muda a sala.",
        "en": "The best part is not the trophy: it is the silence after an argument that changes the room.",
        "es": "Lo mejor no es el trofeo: es el silencio después de un argumento que cambia la sala.",
        "fr": "Le meilleur n'est pas le trophée : c'est le silence après un argument qui change la salle.",
        "de": "Das Beste ist nicht der Pokal: es ist die Stille nach einem Argument, das den Raum verändert.",
        "it": "Il meglio non è il trofeo: è il silenzio dopo un argomento che cambia la stanza.",
        "nl": "Het beste is niet de beker: het is de stilte na een argument dat de zaal verandert.",
        "id": "Yang terbaik bukan piala: melainkan keheningan setelah argumen yang mengubah ruangan.",
        "ms": "Yang terbaik bukan piala: iaitu senyap selepas hujah yang mengubah bilik.",
    },
    "sobre.team_current.13.quote": {
        "pt-BR": "Achei que fosse só debate. Virou amizade, método e um novo jeito de ver o mundo.",
        "en": "I thought it was just debate. It became friendship, method and a new way of seeing the world.",
        "es": "Pensé que era solo debate. Se convirtió en amistad, método y una nueva forma de ver el mundo.",
        "fr": "Je croyais que ce n'était qu'un débat. C'est devenu amitié, méthode et une nouvelle façon de voir le monde.",
        "de": "Ich dachte, es sei nur ein Debatt. Es wurde Freundschaft, Methode und eine neue Sicht auf die Welt.",
        "it": "Pensavo fosse solo dibattito. È diventata amicizia, metodo e un nuovo modo di vedere il mondo.",
        "nl": "Ik dacht dat het alleen debat was. Het werd vriendschap, methode en een nieuwe manier om de wereld te zien.",
        "id": "Saya kira hanya debat. Menjadi persahabatan, metode, dan cara baru melihat dunia.",
        "ms": "Saya fikir ia hanya debat. Menjadi persahabatan, kaedah dan cara baharu melihat dunia.",
    },
    "sobre.team_current.14.quote": {
        "pt-BR": "Ganhei vocabulário para temas que eu evitava. Hoje encaro o difícil de frente.",
        "en": "I gained vocabulary for topics I used to avoid. Today I face hard ones head-on.",
        "es": "Gané vocabulario para temas que evitaba. Hoy encaro lo difícil de frente.",
        "fr": "J'ai gagné du vocabulaire pour des sujets que j'évitais. Aujourd'hui, j'affronte le difficile de face.",
        "de": "Ich gewann Wortschatz für Themen, die ich mied. Heute begegne ich dem Schweren frontal.",
        "it": "Ho guadagnato lessico per temi che evitavo. Oggi affronto il difficile a viso aperto.",
        "nl": "Ik kreeg woordenschat voor onderwerpen die ik vermeed. Vandaag pak ik lastige dingen frontaal aan.",
        "id": "Saya mendapat kosakata untuk topik yang dulu saya hindari. Kini saya menghadapi yang sulit apa adanya.",
        "ms": "Saya peroleh kosa kata untuk topik yang dulu elak. Kini saya hadapi yang sukar dengan berani.",
    },
    "sobre.team_current.15.quote": {
        "pt-BR": "Cada comitê é um mundo. A SWDL me deu mapas para navegar todos eles.",
        "en": "Each committee is a world. SWDL gave me maps to navigate all of them.",
        "es": "Cada comité es un mundo. La SWDL me dio mapas para navegar todos ellos.",
        "fr": "Chaque comité est un monde. La SWDL m'a donné des cartes pour tous les explorer.",
        "de": "Jedes Komitee ist eine Welt. Die SWDL gab mir Karten, um sie alle zu erkunden.",
        "it": "Ogni comitato è un mondo. La SWDL mi ha dato mappe per navigarli tutti.",
        "nl": "Elk comité is een wereld. SWDL gaf mij kaarten om allemaal te navigeren.",
        "id": "Setiap komite adalah satu dunia. SWDL memberi saya peta untuk menavigasi semuanya.",
        "ms": "Setiap jawatankuasa adalah satu dunia. SWDL beri saya peta untuk melayari semuanya.",
    },
    "sobre.team_current.16.quote": {
        "pt-BR": "Teamwork sob pressão de resolução de prazo é a melhor escola que já tive.",
        "en": "Teamwork under deadline pressure is the best school I have ever had.",
        "es": "El trabajo en equipo bajo presión de plazo es la mejor escuela que he tenido.",
        "fr": "Le travail d'équipe sous pression de délai est la meilleure école que j'aie eue.",
        "de": "Teamarbeit unter Terminstress ist die beste Schule, die ich je hatte.",
        "it": "Il lavoro di squadra sotto pressione di scadenza è la scuola migliore che abbia mai avuto.",
        "nl": "Teamwerk onder deadline-druk is de beste school die ik ooit had.",
        "id": "Kerja tim di bawah tekanan tenggat waktu adalah sekolah terbaik yang pernah saya miliki.",
        "ms": "Kerja berpasukan di bawah tekanan tarikh akhir adalah sekolah terbaik yang pernah saya ada.",
    },
    "sobre.team_current.17.quote": {
        "pt-BR": "Descobri minha voz aqui — firme, preparada e sem medo de discordar com respeito.",
        "en": "I found my voice here — firm, prepared and unafraid to disagree with respect.",
        "es": "Descubrí mi voz aquí — firme, preparada y sin miedo a disconformar con respeto.",
        "fr": "J'ai trouvé ma voix ici — ferme, préparée et sans peur de diverger avec respect.",
        "de": "Ich fand hier meine Stimme — fest, vorbereitet und ohne Angst, respektvoll zu widersprechen.",
        "it": "Ho trovato la mia voce qui — ferma, preparata e senza paura di dissentire con rispetto.",
        "nl": "Ik vond hier mijn stem — stevig, voorbereid en niet bang om met respect af te wijken.",
        "id": "Saya menemukan suara saya di sini — tegas, siap, dan tak takut berbeda pendapat dengan hormat.",
        "ms": "Saya menemui suara saya di sini — tegas, bersedia dan tidak takut berbeza pendapat dengan hormat.",
    },
    "sobre.angela_quote": {
        "pt-BR": "O meu papel é orientar: acompanhar cada delegação, desafiar o preparo e garantir que o debate seja honesto e de alto nível. A excelência da SWDL nasce desse acompanhamento próximo.",
        "en": "My role is to guide: support each delegation, challenge preparation and ensure the debate is honest and high-level. SWDL excellence is born from this close follow-up.",
        "es": "Mi papel es orientar: acompañar cada delegación, desafiar la preparación y garantizar que el debate sea honesto y de alto nivel. La excelencia de la SWDL nace de este seguimiento cercano.",
        "fr": "Mon rôle est d'orienter : accompagner chaque délégation, stimuler la préparation et garantir un débat honnête et de haut niveau. L'excellence de la SWDL naît de ce suivi rapproché.",
        "de": "Meine Rolle ist zu begleiten: jede Delegation unterstützen, Vorbereitung fordern und ein ehrliches, hochwertiges Debatt sichern. Die Exzellenz der SWDL entsteht aus dieser engen Begleitung.",
        "it": "Il mio ruolo è guidare: affiancare ogni delegazione, stimolare la preparazione e garantire un dibattito onesto e di alto livello. L'eccellenza della SWDL nasce da questo affiancamento.",
        "nl": "Mijn rol is begeleiden: elke delegatie steunen, voorbereiding scherpen en een eerlijk, hoogwaardig debat waarborgen. De excellentie van SWDL komt voort uit deze nabije begeleiding.",
        "id": "Peran saya adalah membimbing: mendampingi setiap delegasi, menantang kesiapan, dan memastikan debat jujur dan bermutu tinggi. Keunggulan SWDL lahir dari pendampingan dekat ini.",
        "ms": "Peranan saya adalah membimbing: mendampingi setiap delegasi, mencabar persediaan dan memastikan debat jujur dan bertaraf tinggi. Kecemerlangan SWDL lahir dari susulan rapat ini.",
    },
    # ── sobre team 2025 quotes ─────────────────────────────
    "sobre.team_2025.0.quote": {
        "pt-BR": "A gestão 2025 mostrou que herdar uma liga é tão desafiador quanto fundá-la. Cuidamos do legado com rigor e carinho.",
        "en": "The 2025 leadership showed that inheriting a league is as challenging as founding one. We care for the legacy with rigor and care.",
        "es": "La gestión 2025 mostró que heredar una liga es tan desafiante como fundarla. Cuidamos el legado con rigor y cariño.",
        "fr": "La direction 2025 a montré qu'hériter d'une ligue est aussi difficile que la fonder. Nous veillons sur l'héritage avec rigueur et soin.",
        "de": "Die Leitung 2025 zeigte: Eine Liga zu erben ist so herausfordernd wie sie zu gründen. Wir pflegen das Erbe mit Sorgfalt.",
        "it": "La direzione 2025 ha mostrato che ereditare una lega è tanto sfidante quanto fondata. Cura del lascito con rigore e cura.",
        "nl": "De leiding 2025 liet zien dat een liga erven net zo uitdagend is als stichten. We bewaken het erfgoed met zorg.",
        "id": "Kepemimpinan 2025 menunjukkan bahwa mewarisi liga sama menantangnya dengan mendirikannya. Kami merawat warisan dengan ketelitian.",
        "ms": "Kepimpinan 2025 menunjukkan bahawa mewarisi liga sama mencabar dengan menubuhkannya. Kami menjaga legasi dengan teliti.",
    },
    "sobre.team_2025.1.quote": {
        "pt-BR": "Excelência acadêmica na SWDL significa preparo sério — não decorar, compreender o mundo.",
        "en": "Academic excellence at SWDL means serious preparation — not memorizing, understanding the world.",
        "es": "La excelencia académica en la SWDL significa preparación seria — no memorizar, comprender el mundo.",
        "fr": "L'excellence académique à la SWDL, c'est une préparation sérieuse — pas apprendre par cœur, comprendre le monde.",
        "de": "Akademische Exzellenz bei der SWDL heißt ernsthafte Vorbereitung — nicht auswendig lernen, die Welt verstehen.",
        "it": "L'eccellenza accademica nella SWDL significa preparazione seria — non memorizzare, comprendere il mondo.",
        "nl": "Academische excellentie bij SWDL betekent serieuze voorbereiding — niet uit het hoofd leren, de wereld begrijpen.",
        "id": "Keunggulan akademik di SWDL berarti persiapan serius — bukan menghafal, memahami dunia.",
        "ms": "Kecemerlangan akademik di SWDL bermakna persediaan serius — bukan menghafal, memahami dunia.",
    },
    "sobre.team_2025.2.quote": {
        "pt-BR": "Em 2025 aprendi que logística é promessa cumprida: o que combinamos tem que funcionar no dia.",
        "en": "In 2025 I learned that logistics is a promise kept: what we agree must work on the day.",
        "es": "En 2025 aprendí que la logística es promesa cumplida: lo que acordamos tiene que funcionar el día.",
        "fr": "En 2025, j'ai appris que la logistique est une promesse tenue : ce que nous convenons doit fonctionner le jour J.",
        "de": "2025 lernte ich: Logistik ist gehaltenes Versprechen — was wir vereinbaren, muss am Tag funktionieren.",
        "it": "Nel 2025 ho imparato che la logistica è promessa mantenuta: ciò che concordiamo deve funzionare il giorno.",
        "nl": "In 2025 leerde ik dat logistiek een nagekomen belofte is: wat we afspreken moet op de dag werken.",
        "id": "Pada 2025 saya belajar bahwa logistik adalah janji yang ditepati: apa yang kita sepakati harus berfungsi pada hari-H.",
        "ms": "Pada 2025 saya belajar bahawa logistik adalah janji ditepati: apa yang kita sepakat mesti berfungsi pada hari tersebut.",
    },
    "sobre.team_2025.3.quote": {
        "pt-BR": "Comunicação não é enfeite: é como a escola inteira entende o que a diplomacia estudantil representa.",
        "en": "Communication is not decoration: it is how the whole school understands what student diplomacy stands for.",
        "es": "La comunicación no es adorno: es cómo toda la escuela entiende lo que representa la diplomacia estudiantil.",
        "fr": "La communication n'est pas un ornement : c'est comment toute l'école comprend ce que représente la diplomatie étudiante.",
        "de": "Kommunikation ist keine Dekoration: Sie ist, wie die ganze Schule versteht, wofür Schülerdiplomatie steht.",
        "it": "La comunicazione non è decorazione: è come tutta la scuola capisce cosa rappresenta la diplomazia studentesca.",
        "nl": "Communicatie is geen versiering: het is hoe de hele school begrijpt wat studentendiplomatie betekent.",
        "id": "Komunikasi bukan hiasan: melainkan bagaimana seluruh sekolah memahami apa yang diwakili diplomasi siswa.",
        "ms": "Komunikasi bukan hiasan: iaitu bagaimana seluruh sekolah memahami apa yang diwakili diplomasi pelajar.",
    },
    "sobre.team_2025.4.quote": {
        "pt-BR": "Relações públicas na SWDL é construir pontes — com outras escolas, com a comunidade, com o futuro.",
        "en": "Public relations at SWDL means building bridges — with other schools, the community and the future.",
        "es": "Las relaciones públicas en la SWDL son construir puentes — con otras escuelas, la comunidad y el futuro.",
        "fr": "Les relations publiques à la SWDL, c'est bâtir des ponts — avec d'autres écoles, la communauté et l'avenir.",
        "de": "Öffentlichkeitsarbeit bei der SWDL heißt Brücken bauen — zu anderen Schulen, der Gemeinschaft und der Zukunft.",
        "it": "Le relazioni pubbliche nella SWDL significano costruire ponti — con altre scuole, la comunità e il futuro.",
        "nl": "Public relations bij SWDL is bruggen bouwen — met andere scholen, de gemeenschap en de toekomst.",
        "id": "Hubungan masyarakat di SWDL berarti membangun jembatan — dengan sekolah lain, komunitas, dan masa depan.",
        "ms": "Hubungan awam di SWDL bermakna membina jambatan — dengan sekolah lain, komuniti dan masa depan.",
    },
    "sobre.team_2025.5.quote": {
        "pt-BR": "Em 2025 firmamos cultura de time. Quando as pessoas se sentem no lugar certo, o evento respira.",
        "en": "In 2025 we set team culture. When people feel in the right place, the event breathes.",
        "es": "En 2025 afirmamos cultura de equipo. Cuando las personas se sienten en el lugar correcto, el evento respira.",
        "fr": "En 2025, nous avons posé la culture d'équipe. Quand les gens se sentent à leur place, l'événement respire.",
        "de": "2025 festigten wir Teamkultur. Wenn Menschen sich am richtigen Ort fühlen, atmet die Veranstaltung.",
        "it": "Nel 2025 abbiamo consolidato la cultura squadra. Quando le persone si sentono al posto giusto, l'evento respira.",
        "nl": "In 2025 vestigden we teamcultuur. Als mensen zich op hun plek voelen, ademt het evenement.",
        "id": "Pada 2025 kami meneguhkan budaya tim. Ketika orang merasa di tempat yang tepat, acara bernapas.",
        "ms": "Pada 2025 kami meneguhkan budaya pasukan. Apabila rasa berada di tempat yang betul, acara bernafas.",
    },
    "sobre.team_2025.6.quote": {
        "pt-BR": "Administração é o silêncio que permite o debate. Organização é o meu idioma de amor pela liga.",
        "en": "Administration is the silence that allows debate. Organization is my language of love for the league.",
        "es": "La administración es el silencio que permite el debate. La organización es mi idioma de amor por la liga.",
        "fr": "L'administration est le silence qui permet le débat. L'organisation est ma langue d'amour pour la ligue.",
        "de": "Verwaltung ist die Stille, die das Debatt ermöglicht. Organisation ist meine Sprache der Liebe zur Liga.",
        "it": "L'amministrazione è il silenzio che permette il dibattito. L'organizzazione è il mio linguaggio d'amore per la lega.",
        "nl": "Administratie is de stilte die debat mogelijk maakt. Organisatie is mijn taal van liefde voor de liga.",
        "id": "Administrasi adalah keheningan yang memungkinkan debat. Organisasi adalah bahasa cinta saya untuk liga.",
        "ms": "Pentadbiran adalah senyap yang membenarkan debat. Organisasi adalah bahasa cinta saya untuk liga.",
    },
    "sobre.team_2025.7.quote": {
        "pt-BR": "Coordenar staff é conduzir orquestra: papéis claros, energia no mesmo compasso.",
        "en": "Coordinating staff is conducting an orchestra: clear roles, energy in the same tempo.",
        "es": "Coordinar al staff es conducir una orquesta: roles claros, energía en el mismo compás.",
        "fr": "Coordonner le staff, c'est diriger un orchestre : rôles clairs, énergie au même tempo.",
        "de": "Staff zu koordinieren heißt ein Orchester leiten: klare Rollen, Energie im selben Takt.",
        "it": "Coordinare lo staff è dirigere un'orchestra: ruoli chiari, energia nello stesso tempo.",
        "nl": "Staff coördineren is een orkest leiden: duidelijke rollen, energie in hetzelfde tempo.",
        "id": "Mengkoordinasi staf adalah memimpin orkestra: peran jelas, energi dalam tempo yang sama.",
        "ms": "Menyelaras staf adalah menerajui orkestra: peranan jelas, tenaga dalam rentak yang sama.",
    },
    "sobre.team_2025.8.quote": {
        "pt-BR": "Em 2025 o site virou casa digital da SWDL. Código é só o meio — o fim é servir quem debate.",
        "en": "In 2025 the site became SWDL's digital home. Code is only the means — the end is serving those who debate.",
        "es": "En 2025 el sitio se convirtió en el hogar digital de la SWDL. El código es solo el medio — el fin es servir a quienes debaten.",
        "fr": "En 2025, le site est devenu la maison numérique de la SWDL. Le code n'est qu'un moyen — la fin est de servir ceux qui débattent.",
        "de": "2025 wurde die Website das digitale Zuhause der SWDL. Code ist nur das Mittel — das Ziel ist, denen zu dienen, die debattieren.",
        "it": "Nel 2025 il sito è diventato la casa digitale della SWDL. Il codice è solo il mezzo — il fine è servire chi debatta.",
        "nl": "In 2025 werd de site het digitale huis van SWDL. Code is slechts het middel — het doel is het dienen van wie debatteert.",
        "id": "Pada 2025 situs menjadi rumah digital SWDL. Kode hanyalah alat — tujuannya melayani mereka yang berdebat.",
        "ms": "Pada 2025 laman menjadi rumah digital SWDL. Kod hanyalah alat — matlamatnya melayani mereka yang berdebat.",
    },
    # ── home testimonials ──────────────────────────────────
    "home.testimonials_items.0.quote": {
        "pt-BR": "A SWDL me mostrou que a diplomacia não é só discurso — é escuta, estratégia e coragem. Em poucos meses eu sai da zona de conforto e descobri uma paixão por relações internacionais.",
        "en": "SWDL showed me that diplomacy is not only speeches — it is listening, strategy and courage. In a few months I left my comfort zone and found a passion for international relations.",
        "es": "La SWDL me mostró que la diplomacia no es solo discurso — es escucha, estrategia y coraje. En pocos meses salí de mi zona de confort y descubrí una pasión por las relaciones internacionales.",
        "fr": "La SWDL m'a montré que la diplomatie n'est pas que discours — c'est écouter, stratégie et courage. En quelques mois, j'ai quitté ma zone de confort et découvert une passion pour les relations internationales.",
        "de": "Die SWDL zeigte mir, dass Diplomatie nicht nur Rede ist — sie ist Zuhören, Strategie und Mut. In wenigen Monaten verließ ich meine Komfortzone und fand Leidenschaft für internationale Beziehungen.",
        "it": "La SWDL mi ha mostrato che la diplomazia non è solo discorso — è ascolto, strategia e coraggio. In pochi mesi sono uscito dalla zona di conforto e ho scoperto una passione per le relazioni internazionali.",
        "nl": "SWDL liet me zien dat diplomatie niet alleen toespraken zijn — het is luisteren, strategie en moed. Binnen enkele maanden verliet ik mijn comfortzone en vond ik passie voor internationale betrekkingen.",
        "id": "SWDL menunjukkan pada saya bahwa diplomasi bukan hanya pidato — mendengarkan, strategi, dan keberanian. Dalam beberapa bulan saya keluar zona nyaman dan menemukan hasrat untuk hubungan internasional.",
        "ms": "SWDL menunjukkan kepada saya bahawa diplomasi bukan sekadar ucapan — mendengar, strategi dan keberanian. Dalam beberapa bulan saya keluar zon selesa dan menemui minat pada hubungan antarabangsa.",
    },
    "home.testimonials_items.0.role": {
        "pt-BR": "Delegada — Comitê de Segurança", "en": "Delegate — Security Committee",
        "es": "Delegada — Comité de Seguridad", "fr": "Déléguée — Comité de Sécurité",
        "de": "Delegierte — Sicherheitskomitee", "it": "Delegata — Comitato di Sicurezza",
        "nl": "Afgevaardigde — Veiligheidscomité", "id": "Delegasi — Komite Keamanan",
        "ms": "Wakil — Jawatankuasa Keselamatan",
    },
    "home.testimonials_items.1.quote": {
        "pt-BR": "Nunca imaginei que um debate na escola pudesse me preparar tanto para a vida. Aprendi a defender ideias com respeito, a negociar sob pressão e a trabalhar com pessoas completamente diferentes de mim.",
        "en": "I never imagined a school debate could prepare me so much for life. I learned to defend ideas with respect, negotiate under pressure and work with people completely different from me.",
        "es": "Nunca imaginé que un debate en la escuela pudiera prepararme tanto para la vida. Aprendí a defender ideas con respeto, negociar bajo presión y trabajar con personas completamente diferentes de mí.",
        "fr": "Je n'aurais jamais imaginé qu'un débat scolaire puisse autant me préparer à la vie. J'ai appris à défendre des idées avec respect, négocier sous pression et travailler avec des gens très différents de moi.",
        "de": "Ich hätte nie gedacht, dass ein Schuldebatt mich so aufs Leben vorbereitet. Ich lernte, Ideen mit Respekt zu vertreten, unter Druck zu verhandeln und mit völlig anderen Menschen zu arbeiten.",
        "it": "Non avrei mai immaginato che un dibattito a scuola potesse prepararmi così alla vita. Ho imparato a difendere idee con rispetto, negoziare sotto pressione e lavorare con persone molto diverse da me.",
        "nl": "Ik had nooit gedacht dat een schooldebat me zo voor het leven kon voorbereiden. Ik leerde ideeën met respect verdedigen, onder druk onderhandelen en werken met heel andere mensen.",
        "id": "Saya tidak pernah membayangkan debat di sekolah bisa menyiapkan saya begitu banyak untuk hidup. Saya belajar membela ide dengan hormat, bernegosiasi di bawah tekanan, dan bekerja dengan orang yang sangat berbeda dari saya.",
        "ms": "Saya tidak pernah membayangkan debat di sekolah boleh menyediakan saya sebegitu untuk kehidupan. Saya belajar membela idea dengan hormat, berunding di bawah tekanan dan bekerja dengan orang yang sangat berbeza daripada saya.",
    },
    "home.testimonials_items.1.role": {
        "pt-BR": "Delegado — DHR", "en": "Delegate — DHR", "es": "Delegado — DHR",
        "fr": "Délégué — DHR", "de": "Delegierter — DHR", "it": "Delegato — DHR",
        "nl": "Afgevaardigde — DHR", "id": "Delegasi — DHR", "ms": "Wakil — DHR",
    },
    "home.testimonials_items.2.quote": {
        "pt-BR": "O que mais me marcou foi ver alunos do primeiro ano debatendo com a mesma seriedade de universitários. A SWDL transformou a forma como eu vejo o mundo e o meu papel nele.",
        "en": "What struck me most was seeing first-year students debate with the same seriousness as university students. SWDL transformed how I see the world and my role in it.",
        "es": "Lo que más me marcó fue ver a alumnos de primer año debatir con la misma seriedad que universitarios. La SWDL transformó la forma en que veo el mundo y mi papel en él.",
        "fr": "Ce qui m'a le plus marqué, c'est de voir des élèves de première année débattre avec le même sérieux que des étudiants. La SWDL a transformé ma vision du monde et de mon rôle.",
        "de": "Am meisten beeindruckte mich, wie Erstsemester mit derselben Ernsthaftigkeit wie Studierende debattierten. Die SWDL veränderte meine Sicht auf die Welt und meine Rolle darin.",
        "it": "Ciò che mi ha colpito di più è vedere studenti del primo anno dibattere con la stessa serietà degli universitari. La SWDL ha trasformato il modo in cui vedo il mondo e il mio ruolo.",
        "nl": "Wat me het meest raakte, was leerlingen van klas 1 die even serieus debatteerden als studenten. SWDL veranderde hoe ik de wereld en mijn rol daarin zie.",
        "id": "Yang paling membekas adalah melihat siswa kelas 1 berdebat dengan keseriusan yang sama seperti mahasiswa. SWDL mengubah cara saya melihat dunia dan peran saya di dalamnya.",
        "ms": "Yang paling berkesan ialah melajar pelajar tingkatan 1 berdebat dengan kesungguhan sama seperti mahasiswa. SWDL mengubah cara saya melihat dunia dan peranan saya di dalamnya.",
    },
    "home.testimonials_items.2.role": {
        "pt-BR": "Delegada — ECOSOC", "en": "Delegate — ECOSOC", "es": "Delegada — ECOSOC",
        "fr": "Déléguée — ECOSOC", "de": "Delegierte — ECOSOC", "it": "Delegata — ECOSOC",
        "nl": "Afgevaardigde — ECOSOC", "id": "Delegasi — ECOSOC", "ms": "Wakil — ECOSOC",
    },
    # ── staggered gallery ──────────────────────────────────
    "home.staggered.0.alt": {
        "pt-BR": "Delegada em sessão plenária", "en": "Delegate in plenary session",
        "es": "Delegada en sesión plenaria", "fr": "Déléguée en séance plénière",
        "de": "Delegierte in der Vollversammlung", "it": "Delegata in seduta plenaria",
        "nl": "Afgevaardigde in plenaire vergadering", "id": "Delegasi dalam sidang pleno",
        "ms": "Wakil dalam mesyuarat agung",
    },
    "home.staggered.0.caption": {
        "pt-BR": "Sessão Plenária — SWDL 2025", "en": "Plenary Session — SWDL 2025",
        "es": "Sesión Plenaria — SWDL 2025", "fr": "Séance Plénière — SWDL 2025",
        "de": "Vollversammlung — SWDL 2025", "it": "Seduta Plenaria — SWDL 2025",
        "nl": "Plenaire Vergadering — SWDL 2025", "id": "Sidang Pleno — SWDL 2025",
        "ms": "Mesyuarat Agung — SWDL 2025",
    },
    "home.staggered.1.alt": {
        "pt-BR": "Mapa-múndi representando a dimensão global da SWDL",
        "en": "World map representing SWDL's global dimension",
        "es": "Mapamundi representando la dimensión global de la SWDL",
        "fr": "Carte du monde représentant la dimension mondiale de la SWDL",
        "de": "Weltkarte, die die globale Dimension der SWDL darstellt",
        "it": "Mappamondo che rappresenta la dimensione globale della SWDL",
        "nl": "Wereldkaart die de mondiale dimensie van SWDL representeert",
        "id": "Peta dunia yang mewakili dimensi global SWDL",
        "ms": "Peta dunia yang mewakili dimensi global SWDL",
    },
    "home.staggered.1.caption": {
        "pt-BR": "Delegações de 193 países representados",
        "en": "Delegations from 193 countries represented",
        "es": "Delegaciones de 193 países representadas",
        "fr": "Délégations de 193 pays représentées",
        "de": "Delegationen aus 193 Ländern vertreten",
        "it": "Delegazioni di 193 Paesi rappresentate",
        "nl": "Delegaties van 193 landen vertegenwoordigd",
        "id": "Delegasi dari 193 negara terwakili",
        "ms": "Delegasi dari 193 negara diwakili",
    },
    "home.staggered.2.alt": {
        "pt-BR": "Delegado durante debate de comitê", "en": "Delegate during committee debate",
        "es": "Delegado durante debate de comité", "fr": "Délégué pendant un débat de comité",
        "de": "Delegierter während einer Komitedebatte", "it": "Delegato durante un dibattito di comitato",
        "nl": "Afgevaardigde tijdens comitédebat", "id": "Delegasi saat debat komite",
        "ms": "Wakil semasa debat jawatankuasa",
    },
    "home.staggered.2.caption": {
        "pt-BR": "Debate de Comitê — Conselho de Segurança",
        "en": "Committee Debate — Security Council",
        "es": "Debate de Comité — Consejo de Seguridad",
        "fr": "Débat de Comité — Conseil de Sécurité",
        "de": "Komitedebatte — Sicherheitsrat",
        "it": "Dibattito di Comitato — Consiglio di Sicurezza",
        "nl": "Comitédebat — Veiligheidsraad",
        "id": "Debat Komite — Dewan Keamanan",
        "ms": "Debat Jawatankuasa — Majlis Keselamatan",
    },
    # ── comites UI ─────────────────────────────────────────
    "comites.guide_link": {
        "pt-BR": "Guia", "en": "Guide", "es": "Guía", "fr": "Guide", "de": "Leitfaden",
        "it": "Guida", "nl": "Gids", "id": "Panduan", "ms": "Panduan",
    },
    "comites.manual_link": {
        "pt-BR": "Manual", "en": "Manual", "es": "Manual", "fr": "Manuel", "de": "Handbuch",
        "it": "Manuale", "nl": "Handleiding", "id": "Manual", "ms": "Manual",
    },
    "comites.edition_2026": {
        "pt-BR": "Edição de 2026", "en": "2026 Edition", "es": "Edición de 2026",
        "fr": "Édition 2026", "de": "Ausgabe 2026", "it": "Edizione 2026",
        "nl": "Editie 2026", "id": "Edisi 2026", "ms": "Edisi 2026",
    },
    "comites.edition_2025": {
        "pt-BR": "Edição de 2025", "en": "2025 Edition", "es": "Edición de 2025",
        "fr": "Édition 2025", "de": "Ausgabe 2025", "it": "Edizione 2025",
        "nl": "Editie 2025", "id": "Edisi 2025", "ms": "Edisi 2025",
    },
    "comites.meta_mma": {
        "pt-BR": "MMA — Meio Ambiente", "en": "MMA — Environment", "es": "MMA — Medio Ambiente",
        "fr": "MMA — Environnement", "de": "MMA — Umwelt", "it": "MMA — Ambiente",
        "nl": "MMA — Milieu", "id": "MMA — Lingkungan", "ms": "MMA — Alam Sekitar",
    },
    "comites.meta_dhr": {
        "pt-BR": "DHR — Direitos Humanos", "en": "DHR — Human Rights", "es": "DHR — Derechos Humanos",
        "fr": "DHR — Droits de l'Homme", "de": "DHR — Menschenrechte", "it": "DHR — Diritti Umani",
        "nl": "DHR — Mensenrechten", "id": "DHR — Hak Asasi Manusia", "ms": "DHR — Hak Asasi Manusia",
    },
    "comites.meta_ecosoc": {
        "pt-BR": "ECOSOC — Econômico e Social", "en": "ECOSOC — Economic and Social",
        "es": "ECOSOC — Económico y Social", "fr": "ECOSOC — Économique et Social",
        "de": "ECOSOC — Wirtschaft und Soziales", "it": "ECOSOC — Economico e Sociale",
        "nl": "ECOSOC — Economisch en Sociaal", "id": "ECOSOC — Ekonomi dan Sosial",
        "ms": "ECOSOC — Ekonomi dan Sosial",
    },
    "comites.meta_disec": {
        "pt-BR": "DISEC — Desarmamento", "en": "DISEC — Disarmament", "es": "DISEC — Desarme",
        "fr": "DISEC — Désarmement", "de": "DISEC — Abrüstung", "it": "DISEC — Disarmo",
        "nl": "DISEC — Ontwapening", "id": "DISEC — Pelucutan Senjata", "ms": "DISEC — Pelucutan Senjata",
    },
    "comites.meta_oms": {
        "pt-BR": "OMS — Saúde Global", "en": "WHO — Global Health", "es": "OMS — Salud Global",
        "fr": "OMS — Santé Mondiale", "de": "WHO — Globale Gesundheit", "it": "OMS — Salute Globale",
        "nl": "WHO — Wereldgezondheid", "id": "WHO — Kesehatan Global", "ms": "WHO — Kesihatan Global",
    },
    "comites.meta_cs": {
        "pt-BR": "CS — Conselho de Segurança", "en": "SC — Security Council",
        "es": "CS — Consejo de Seguridad", "fr": "CS — Conseil de Sécurité",
        "de": "SR — Sicherheitsrat", "it": "CS — Consiglio di Sicurezza",
        "nl": "VS — Veiligheidsraad", "id": "DK — Dewan Keamanan", "ms": "MK — Majlis Keselamatan",
    },
    "comites.manual_org": {
        "pt-BR": "Manual do Delegado — Edição de 2026",
        "en": "Delegate Manual — 2026 Edition", "es": "Manual del Delegado — Edición 2026",
        "fr": "Manuel du Délégué — Édition 2026", "de": "Delegiertenhandbuch — Ausgabe 2026",
        "it": "Manuale del Delegato — Edizione 2026", "nl": "Handleiding voor de Afgevaardigde — Editie 2026",
        "id": "Manual Delegasi — Edisi 2026", "ms": "Manual Wakil — Edisi 2026",
    },
    # ── comites entries ────────────────────────────────────
    "comites.entries.escravidao.title": {
        "pt-BR": "A Escravidão do Passado ao Racismo do Presente — Desafiando o Futuro",
        "en": "From Slavery to Today's Racism — Challenging the Future",
        "es": "De la Esclavitud al Racismo del Presente — Desafiando el Futuro",
        "fr": "De l'Esclavage au Racisme d'Aujourd'hui — Défier l'Avenir",
        "de": "Von der Sklaverei zum Rassismus von heute — Die Zukunft fordern",
        "it": "Dalla Schiavitù al Razzismo di Oggi — Sfidare il Futuro",
        "nl": "Van Slavernij tot Hedendaags Racisme — De Toekomst Aanpakken",
        "id": "Dari Perbudakan ke Rasisme Hari Ini — Tantang Masa Depan",
        "ms": "Dari Perhambaan ke Perkauman Hari Ini — Cabar Masa Depan",
    },
    "comites.entries.escravidao.description": {
        "pt-BR": "Nesta simulação, os delegados discutirão as relações entre a escravidão, suas heranças históricas e as diferentes manifestações do racismo na sociedade contemporânea. O debate abordará os impactos sociais, econômicos e políticos da escravidão e de seus legados, além dos desafios para enfrentar o racismo estrutural, promover a igualdade racial e construir mecanismos de reparação e inclusão. Caberá aos delegados buscar respostas internacionais capazes de enfrentar desigualdades persistentes e contribuir para a construção de sociedades mais justas.",
        "en": "In this simulation, delegates will discuss the relations between slavery, its historical legacies and the different manifestations of racism in contemporary society. The debate will address the social, economic and political impacts of slavery and its legacies, as well as the challenges of tackling structural racism, promoting racial equality and building redress and inclusion mechanisms. Delegates will seek international responses that confront persistent inequalities and help build fairer societies.",
        "es": "En esta simulación, los delegados discutirán las relaciones entre la esclavitud, sus legados históricos y las distintas manifestaciones del racismo en la sociedad contemporánea. El debate abordará los impactos sociales, económicos y políticos de la esclavitud y de sus legados, además de los desafíos para enfrentar el racismo estructural, promover la igualdad racial y construir mecanismos de reparación e inclusión. A los delegados les corresponderá buscar respuestas internacionales capaces de enfrentar desigualdades persistentes y contribuir a la construcción de sociedades más justas.",
        "fr": "Dans cette simulation, les délégués discuteront des liens entre l'esclavage, ses héritages historiques et les différentes manifestations du racisme dans la société contemporaine. Le débat abordera les impacts sociaux, économiques et politiques de l'esclavage et de ses héritages, ainsi que les défis du racisme structurel, de l'égalité raciale et des mécanismes de réparation et d'inclusion. Les délégués rechercheront des réponses internationales face aux inégalités persistantes pour construire des sociétés plus justes.",
        "de": "In dieser Simulation diskutieren Delegierte die Beziehungen zwischen Sklaverei, ihren historischen Nachwirkungen und den verschiedenen Formen des Rassismus in der heutigen Gesellschaft. Das Debatt behandelt die sozialen, wirtschaftlichen und politischen Folgen der Sklaverei sowie die Herausforderungen von strukturellem Rassismus, Rassengleichheit und Reparations- und Integrationsmechanismen. Delegierte suchen internationale Antworten auf anhaltende Ungleichheit für gerechtere Gesellschaften.",
        "it": "In questa simulazione i delegati discuteranno i rapporti tra schiavitù, eredità storiche e diverse manifestazioni di razzismo nella società contemporanea. Il dibattito affronterà gli impatti sociali, economici e politici della schiavitù e delle sue eredità, oltre alle sfide del razzismo strutturale, della parità razziale e dei meccanismi di riparazione e inclusione. I delegati cercheranno risposte internazionali alle disuguaglianze persistenti per società più giuste.",
        "nl": "In deze simulatie bespreken afgevaardigden de relaties tussen slavernij, historische erfenissen en verschillende vandaag bestaande uitingen van racisme. Het debat gaat over de sociale, economische en politieke impact van slavernij, structureel racisme, raciale gelijkheid en reparatie- en inclusiemechanismen. Delegati zoeken internationale antwoorden op hardnekkige ongelijkheid voor rechtvaardigere samenlevingen.",
        "id": "Dalam simulasi ini, delegasi akan membahas hubungan antara perbudakan, warisan sejarahnya, dan berbagai manifestasi rasisme di masyarakat kontemporer. Debat akan membahas dampak sosial, ekonomi, dan politik perbudakan serta tantangan mengatasi rasisme struktural, mempromosikan kesetaraan rasial, dan membangun mekanisme restorasi dan inklusi. Delegasi mencari respons internasional terhadap ketidaksetaraan yang berkelanjutan untuk masyarakat yang lebih adil.",
        "ms": "Dalam simulasi ini, wakil akan membahas hubungan antara perhambaan, warisan sejarahnya, dan pelbagai manifestasi perkauman dalam masyarakat kontemporari. Perbincangan akan menangani impak sosial, ekonomi dan politik perhambaan serta cabaran menghadapi perkauman struktur, menggalakkan kesamarataan kaum dan membina mekanisme pemulihan dan inklusif. Wakil mencari respons antarabangsa terhadap ketidaksamaan berterusan untuk masyarakat yang lebih adil.",
    },
    "comites.entries.escravidao.topics": {
        "pt-BR": ["Escravidão e Legados Históricos", "Racismo Estrutural", "Igualdade Racial", "Discriminação Racial", "Reparação Histórica", "Justiça Social"],
        "en": ["Slavery and Historical Legacies", "Structural Racism", "Racial Equality", "Racial Discrimination", "Historical Redress", "Social Justice"],
        "es": ["Esclavitud y Legados Históricos", "Racismo Estructural", "Igualdad Racial", "Discriminación Racial", "Reparación Histórica", "Justicia Social"],
        "fr": ["Esclavage et Héritages Historiques", "Racisme Structurel", "Égalité Raciale", "Discrimination Raciale", "Réparation Historique", "Justice Sociale"],
        "de": ["Sklaverei und Historische Nachwirkungen", "Struktureller Rassismus", "Rassengleichheit", "Rassendiskriminierung", "Historische Wiedergutmachung", "Soziale Gerechtigkeit"],
        "it": ["Schiavitù ed Eredità Storiche", "Razzismo Strutturale", "Parità Razziale", "Discriminazione Razziale", "Riparazione Storica", "Giustizia Sociale"],
        "nl": ["Slavernij en Historische Erfgoed", "Structureel Racisme", "Raciale Gelijkheid", "Raciale Discriminatie", "Historische Reparatie", "Sociale Rechtvaardigheid"],
        "id": ["Perbudakan dan Warisan Sejarah", "Rasisme Struktural", "Kesetaraan Rasial", "Diskriminasi Rasial", "Restorasi Sejarah", "Keadilan Sosial"],
        "ms": ["Perhambaan dan Warisan Sejarah", "Perkauman Struktur", "Kesamarataan Kaum", "Diskriminasi Kaum", "Pemulihan Sejarah", "Keadilan Sosial"],
    },
    "comites.entries.escravidao.delegates": {
        "pt-BR": "11 delegações · 33 estudantes", "en": "11 delegations · 33 students",
        "es": "11 delegaciones · 33 estudiantes", "fr": "11 délégations · 33 étudiants",
        "de": "11 Delegationen · 33 Schüler", "it": "11 delegazioni · 33 studenti",
        "nl": "11 delegaties · 33 studenten", "id": "11 delegasi · 33 siswa",
        "ms": "11 delegasi · 33 pelajar",
    },
    "comites.entries.acnur.title": {
        "pt-BR": "A Proteção Internacional de Pessoas Deslocadas em Decorrência de Eventos Climáticos Extremos",
        "en": "International Protection for People Displaced by Extreme Weather Events",
        "es": "La Protección Internacional de Personas Desplazadas por Eventos Climáticos Extremos",
        "fr": "La Protection Internationale des Personnes Déplacées par des Événements Climatiques Extrêmes",
        "de": "Internationaler Schutz für Menschen, die durch extreme Wetterereignisse vertrieben wurden",
        "it": "La Protezione Internazionale delle Persone Spostate a Causa di Eventi Climatici Estremi",
        "nl": "Internationale Bescherming voor Mensen die door extreme Weersomstandigheden zijn Verdreven",
        "id": "Perlindungan Internasional untuk Orang yang Mengungsi Akibat Peristiwa Iklim Ekstrem",
        "ms": "Perlindungan Antarabangsa untuk Orang yang Mendapat Penempatan Semula Akibat Peristiwa Iklim Melampau",
    },
    "comites.entries.acnur.description": {
        "pt-BR": "Nesta simulação, os delegados do Alto Comissariado das Nações Unidas para os Refugiados (ACNUR) enfrentarão o desafio crescente dos deslocamentos forçados provocados por eventos climáticos extremos, como enchentes, secas, furacões e tempestades. Ao longo do debate, deverão discutir mecanismos internacionais de proteção, assistência humanitária e integração para as populações deslocadas, conciliando soberania nacional, financiamento internacional e responsabilidade compartilhada.",
        "en": "In this simulation, delegates of the UN High Commissioner for Refugees (UNHCR) will face the growing challenge of forced displacement caused by extreme weather events such as floods, droughts, hurricanes and storms. Throughout the debate they will discuss international protection, humanitarian assistance and integration mechanisms for displaced populations, balancing national sovereignty, international funding and shared responsibility.",
        "es": "En esta simulación, los delegados del Alto Comisionado de las Naciones Unidas para los Refugiados (ACNUR) enfrentarán el creciente desafío de los desplazamientos forzados provocados por eventos climáticos extremos, como inundaciones, sequías, huracanes y tormentas. A lo largo del debate deberán discutir mecanismos internacionales de protección, asistencia humanitaria e integración para las poblaciones desplazadas, conciliando soberanía nacional, financiamiento internacional y responsabilidad compartida.",
        "fr": "Dans cette simulation, les délégués du Haut-Commissariat pour les Réfugiés (HCR) feront face au décroît croissant des déplacements forcés causés par des événements climatiques extrêmes (inondations, sécheresses, ouragans, tempêtes). Ils discuteront des mécanismes internationaux de protection, d'assistance humanitaire et d'intégration, en conciliant souveraineté nationale, financement international et responsabilité partagée.",
        "de": "In dieser Simulation stehen Delegierte des Hochkommissariats für Flüchtlinge (UNHCR) vor dem wachsenden Problem von Zwangsvertreibungen durch extreme Wetterereignisse wie Überschwemmungen, Dürren, Hurrikane und Stürme. Sie diskutieren internationale Schutz-, humanitäre Hilfs- und Integrationsmechanismen und wägen nationale Souveränität, internationale Finanzierung und geteilte Verantwortung ab.",
        "it": "In questa simulazione i delegati dell'Alto Commissariato per i Rifugiati (ACNUR) affronteranno la crescente sfida degli sfollamenti forzati causati da eventi meteorologici estremi come alluvioni, siccità, uragani e tempeste. Discuteranno meccanismi internazionali di protezione, assistenza umanitaria e integrazione, conciliando sovranità nazionale, finanziamento internazionale e responsabilità condivisa.",
        "nl": "In deze simulatie staan afgevaardigden van de Hoge Commissaris voor Vluchtelingen (UNHCR) voor de groeiende uitdaging van gedwongen verplaatsingen door extreme weersomstandigheden als overstromingen, droogte, orkanen en stormen. Zij bespreken internationale bescherming, humanitaire hulp en integratiemechanismen, met balans tussen nationale soevereiniteit, internationale financiering en gedeelde verantwoordelijkheid.",
        "id": "Dalam simulasi ini, delegasi Komisaris Tinggi PBB untuk Pengungsi (UNHCR) akan menghadapi tantangan perpindahan paksa akibat peristiwa iklim ekstrem seperti banjir, kekeringan, badai, dan topan. Sepanjang debat mereka membahas mekanisme perlindungan internasional, bantuan kemanusiaan, dan integrasi bagi penduduk terusir, dengan menyeimbangkan kedaulatan nasional, pendanaan internasional, dan tanggungjawab bersama.",
        "ms": "Dalam simulasi ini, wakil Pesuruh Tinggi Pelarian PBB (UNHCR) akan menghadapi cabaran penempatan semula paksa akibat peristiwa cuaca melampau seperti banjir, kemarau, ribut taufan dan ribut. Sepanjang perbincangan, mereka akan membahas mekanisme perlindungan antarabangsa, bantuan kemanusiaan dan integrasi bagi penduduk yang dipindahkan, sambil mengimbangi kedaulatan negara, pembiayaan antarabangsa dan tanggungjawab bersama.",
    },
    "comites.entries.acnur.topics": {
        "pt-BR": ["Deslocamento Climático", "Refugiados Climáticos", "Ajuda Humanitária", "Mudanças Climáticas", "Responsabilidade Compartilhada", "Financiamento Internacional"],
        "en": ["Climate Displacement", "Climate Refugees", "Humanitarian Aid", "Climate Change", "Shared Responsibility", "International Funding"],
        "es": ["Desplazamiento Climático", "Refugiados Climáticos", "Ayuda Humanitaria", "Cambio Climático", "Responsabilidad Compartida", "Financiamiento Internacional"],
        "fr": ["Déplacement Climatique", "Réfugiés Climatiques", "Aide Humanitaire", "Changement Climatique", "Responsabilité Partagée", "Financement International"],
        "de": ["Klimaflucht", "Klimaflüchtlinge", "Humanitäre Hilfe", "Klimawandel", "Gemeinsame Verantwortung", "Internationale Finanzierung"],
        "it": ["Spostamento Climatico", "Rifugiati Climatici", "Aiuto Umanitario", "Cambiamento Climatico", "Responsabilità Condivisa", "Finanziamento Internazionale"],
        "nl": ["Klimaatverplaatsing", "Klimaatvluchtelingen", "Humanitaire Hulp", "Klimaatverandering", "Gedeelde Verantwoordelijkheid", "Internationale Financiering"],
        "id": ["Perpindahan Iklim", "Pengungsi Iklim", "Bantuan Kemanusiaan", "Perubahan Iklim", "Tanggungjawab Bersama", "Pendanaan Internasional"],
        "ms": ["Penempatan Semula Iklim", "Pelarian Iklim", "Bantuan Kemanusiaan", "Perubahan Iklim", "Tanggungjawab Bersama", "Pembiayaan Antarabangsa"],
    },
    "comites.entries.acnur.delegates": {
        "pt-BR": "11 delegações · 34 estudantes", "en": "11 delegations · 34 students",
        "es": "11 delegaciones · 34 estudiantes", "fr": "11 délégations · 34 étudiants",
        "de": "11 Delegationen · 34 Schüler", "it": "11 delegazioni · 34 studenti",
        "nl": "11 delegaties · 34 studenten", "id": "11 delegasi · 34 siswa",
        "ms": "11 delegasi · 34 pelajar",
    },
    "comites.entries.ormuz.title": {
        "pt-BR": "Estreito de Ormuz — A Crise no Comércio Internacional e a Escalada Militar",
        "en": "Strait of Hormuz — The Crisis in International Trade and Military Escalation",
        "es": "Estrecho de Ormuz — La Crisis en el Comercio Internacional y la Escalada Militar",
        "fr": "Détroit d'Ormuz — La Crise du Commerce International et l'Escalade Militaire",
        "de": "Straße von Hormus — Die Krise im Welthandel und die militärische Eskalation",
        "it": "Stretto di Hormuz — La Crisi nel Commercio Internazionale e l'Escalation Militare",
        "nl": "Straits of Hormuz — De Crisis in de Internationale Handel en de Militaire Escalatie",
        "id": "Selat Hormuz — Krisis Perdagangan Internasional dan Eskalasi Militer",
        "ms": "Selat Hormuz — Krisis Perdagangan Antarabangsa dan Eskalasi Ketenteraan",
    },
    "comites.entries.ormuz.description": {
        "pt-BR": "Nesta simulação, o Conselho de Segurança se reunirá em sessão de emergência diante do agravamento das tensões no Oriente Médio e de seus impactos sobre a segurança internacional. A intensificação das hostilidades, o envolvimento de múltiplos atores regionais e internacionais e os riscos para a circulação de petróleo e o comércio global colocarão os delegados diante do desafio de formular respostas diplomáticas e medidas capazes de conter a escalada e preservar a estabilidade internacional.",
        "en": "In this simulation, the Security Council will hold an emergency session as tensions in the Middle East worsen and affect international security. Escalating hostilities, the involvement of multiple regional and international actors and risks to oil circulation and global trade will challenge delegates to craft diplomatic responses that contain the escalation and preserve international stability.",
        "es": "En esta simulación, el Consejo de Seguridad se reunirá en sesión de emergencia ante el agravamiento de las tensiones en Oriente Medio y sus impactos sobre la seguridad internacional. La intensificación de las hostilidades, el involucramiento de múltiples actores regionales e internacionales y los riesgos para la circulación de petróleo y el comercio global pondrán a los delegados ante el desafío de formular respuestas diplomáticas y medidas capaces de contener la escalada y preservar la estabilidad internacional.",
        "fr": "Dans cette simulation, le Conseil de Sécurité tiendra une session d'urgence face à la aggravation des tensions au Moyen-Orient et à leurs impacts sur la sécurité internationale. L'intensification des hostilités, l'implication de multiples acteurs régionaux et internationaux et les risques pour la circulation du pétrole et du commerce mondial obligeront les délégués à formuler des réponses diplomatiques pour endiguer l'escalade et préserver la stabilité internationale.",
        "de": "In dieser Simulation tritt der Sicherheitsrat zu einer Notfallsitzung zusammen, während die Spannungen im Nahen Osten eskalieren und die internationale Sicherheit beeinträchtigen. Zunehmende Feindseligkeiten, die Einbeziehung multipler Akteure sowie Risiken für den Ölfluss und den Welthandel fordern Delegierte zu diplomatischen Antworten, die die Eskalation eindämmen und die internationale Stabilität wahren.",
        "it": "In questa simulazione il Consiglio di Sicurezza si riunirà in sessione d'emergenza di fronte al peggioramento delle tensioni in Medio Oriente e ai loro impatti sulla sicurezza internazionale. L'intensificazione delle ostilità, il coinvolgimento di più attori regionali e internazionali e i rischi per la circolazione del petrolio e del commercio globale spingeranno i delegati a formulare risposte diplomatiche per contenere l'escalation e preservare la stabilità internazionale.",
        "nl": "In deze simulatie komt de Veiligheidsraad in een noodsessie bijeen terwijl de spanningen in het Midden-Oosten verergeren en de internationale veiligheid raken. Escalerende vijandelijkheden, betrokkenheid van meerdere regionale en internationale actoren en risico's voor oliecirculatie en wereldhandel dwingen delegati tot diplomatieke antwoorden die de escalatie beteugelen en de internationale stabiliteit bewaren.",
        "id": "Dalam simulasi ini, Dewan Keamanan akan mengadakan sesi darurat menghadapi memburuknya ketegangan di Timur Tengah dan dampaknya terhadap keamanan internasional. Memanasnya permusuhan, keterlibatan berbagai aktor regional dan internasional, serta risiko peredaran minyak dan perdagangan global menuntut delegasi merumuskan respons diplomatik untuk menahan eskalasi dan memelihara stabilitas internasional.",
        "ms": "Dalam simulasi ini, Majlis Keselamatan akan bersidang kecemasan berikutan ketegangan di Timur Tengah yang semakin buruk dan kesannya terhadap keselamatan antarabangsa. Peningkatan permusuhan, penglibatan pelbagai aktor serantau dan antarabangsa serta risiko peredaran minyak dan perdagangan global menuntut wakil merangka respons diplomatik untuk menahan eskalasi dan mengekalkan kestabilan antarabangsa.",
    },
    "comites.entries.ormuz.topics": {
        "pt-BR": ["Escalada Militar", "Comércio Internacional", "Arsenais Nucleares", "Petróleo", "Sanções Internacionais", "Agentes Não-Estatais"],
        "en": ["Military Escalation", "International Trade", "Nuclear Arsenals", "Oil", "International Sanctions", "Non-State Actors"],
        "es": ["Escalada Militar", "Comercio Internacional", "Arsenales Nucleares", "Petróleo", "Sanciones Internacionales", "Actores No Estatales"],
        "fr": ["Escalade Militaire", "Commerce International", "Arsenaux Nucléaires", "Pétrole", "Sanctions Internationales", "Acteurs Non Étatiques"],
        "de": ["Militärische Eskalation", "Welthandel", "Nukleare Arsenal", "Öl", "Internationale Sanktionen", "Nichtstaatliche Akteure"],
        "it": ["Escalation Militare", "Commercio Internazionale", "Arsenali Nucleari", "Petrolio", "Sanzioni Internazionali", "Attori Non Statali"],
        "nl": ["Militaire Escalatie", "Internationale Handel", "Kernarsenaal", "Olie", "Internationale Sancties", "Niet-Staatelijke Actoren"],
        "id": ["Eskalasi Militer", "Perdagangan Internasional", "Persenjataan Nuklir", "Minyak", "Sanksi Internasional", "Aktor Non-Negara"],
        "ms": ["Eskalasi Ketenteraan", "Perdagangan Antarabangsa", "Senjata Nuklear", "Minyak", "Sanksi Antarabangsa", "Pihak Bukan Negara"],
    },
    "comites.entries.ormuz.delegates": {
        "pt-BR": "16 delegações · 32 delegados", "en": "16 delegations · 32 delegates",
        "es": "16 delegaciones · 32 delegados", "fr": "16 délégations · 32 délégués",
        "de": "16 Delegationen · 32 Delegierte", "it": "16 delegazioni · 32 delegati",
        "nl": "16 delegaties · 32 afgevaardigden", "id": "16 delegasi · 32 delegasi",
        "ms": "16 delegasi · 32 wakil",
    },
    "comites.entries.canabis.title": {
        "pt-BR": "Regulamentação da Canábis — Saúde Pública e Economia Global",
        "en": "Cannabis Regulation — Public Health and the Global Economy",
        "es": "Regulamentación del Cáñamo — Salud Pública y Economía Global",
        "fr": "Réglementation du Chanvre — Santé Publique et Économie Mondiale",
        "de": "Cannabis-Regulierung — öffentliche Gesundheit und Weltwirtschaft",
        "it": "Regolamentazione della Canapa — Salute Pubblica ed Economia Globale",
        "nl": "Regulering van Hennep — Volksgezondheid en Mondiale Economie",
        "id": "Regulasi Ganja — Kesehatan Masyarakat dan Ekonomi Global",
        "ms": "Pengawalan Ganja — Kesihatan Awam dan Ekonomi Global",
    },
    "comites.entries.canabis.description": {
        "pt-BR": "Nesta simulação, os delegados discutirão os impactos da transformação das políticas nacionais e internacionais relacionadas à canábis. O debate abordará os desafios de conciliar descriminalização, uso medicinal e saúde pública com o combate ao narcotráfico, além de analisar os efeitos socioeconômicos da legalização, os limites da soberania estatal e a construção de marcos regulatórios internacionais.",
        "en": "In this simulation, delegates will discuss the impacts of changing national and international cannabis policies. The debate will cover the challenges of balancing decriminalization, medical use and public health with combating drug trafficking, and will analyze the socioeconomic effects of legalization, the limits of state sovereignty and the building of international regulatory frameworks.",
        "es": "En esta simulación, los delegados discutirán los impactos de la transformación de las políticas nacionales e internacionales relacionadas con el cáñamo. El debate abordará los desafíos de conciliar descriminalización, uso medicinal y salud pública con el combate al narcotráfico, además de analizar los efectos socioeconómicos de la legalización, los límites de la soberanía estatal y la construcción de marcos regulatorios internacionales.",
        "fr": "Dans cette simulation, les délégués discuteront des impacts de la transformation des politiques nationales et internationales relatives au chanvre. Le débat abordera les défis de concilier dépénalisation, usage médical et santé publique avec la lutte contre le trafic de drogues, et analysera les effets socioéconomiques de la légalisation, les limites de la souveraineté étatique et la construction de cadres réglementaires internationaux.",
        "de": "In dieser Simulation diskutieren Delegierte die Auswirkungen veränderter nationaler und internationaler Cannabispolitik. Das Debatt behandelt die Balance zwischen Entkriminalisierung, medizinischem Gebrauch und öffentlicher Gesundheit sowie dem Kampf gegen Drogenhandel, und analysiert sozioökonomische Effekte der Legalisierung, Grenzen staatlicher Souveränität und internationale Regulierungsrahmen.",
        "it": "In questa simulazione i delegati discuteranno gli impatti della trasformazione delle politiche nazionali e internazionali sulla canapa. Il dibattito affronterà le sfide di conciliare depenalizzazione, uso medico e salute pubblica con il contrasto al traffico di droga, analizzando gli effetti socioeconomici della legalizzazione, i limiti della sovranità statale e la costruzione di quadri regolatori internazionali.",
        "nl": "In deze simulatie bespreken afgevaardigden de effecten van gewijzigde nationale en internationale cannabisbeleid. Het debat gaat over de balans tussen depenalisering, medisch gebruik en volksgezondheid versus de strijd tegen drugshandel, en analyseert de socio-economische effecten van legalisatie, de grenzen van staatssoevereiniteit en internationale regelgevingskaders.",
        "id": "Dalam simulasi ini, delegasi akan membahas dampak perubahan kebijakan nasional dan internasional terkait ganja. Debat akan membahas tantangan menyeimbangkan dekriminalisasi, penggunaan medis, dan kesehatan masyarakat dengan pemberantasan perdagangan narkoba, serta menganalisis dampak sosial-ekonomi legalisasi, batas kedaulatan negara, dan pembentukan kerangka regulasi internasional.",
        "ms": "Dalam simulasi ini, wakil akan membahas impak perubahan dasar negara dan antarabangsa berkaitan ganja. Perbincangan akan menangani cabaran mengimbangi dekriminalisasi, kegunaan perubatan dan kesihatan awam dengan memerangi perdagangan dadah, serta menganalisis kesan sosioekonomi penghalalan, sempadan kedaulatan negara dan pembinaan rangka kerja pemantauan antarabangsa.",
    },
    "comites.entries.canabis.topics": {
        "pt-BR": ["Saúde Pública", "Uso Medicinal", "Combate ao Narcotráfico", "Marcos Regulatórios", "Impacto Econômico", "Soberania Nacional"],
        "en": ["Public Health", "Medical Use", "Combating Drug Trafficking", "Regulatory Frameworks", "Economic Impact", "National Sovereignty"],
        "es": ["Salud Pública", "Uso Medicinal", "Combate al Narcotráfico", "Marcos Regulatorios", "Impacto Económico", "Soberanía Nacional"],
        "fr": ["Santé Publique", "Usage Médical", "Lutte Contre le Trafic de Drogues", "Cadres Réglementaires", "Impact Économique", "Souveraineté Nationale"],
        "de": ["Öffentliche Gesundheit", "Medizinische Nutzung", "Bekämpfung des Drogenhandels", "Regulierungsrahmen", "Wirtschaftliche Auswirkungen", "Nationale Souveränität"],
        "it": ["Salute Pubblica", "Uso Medicinale", "Contrasto al Traffico di Droga", "Quadri Regolatori", "Impatto Economico", "Sovranità Nazionale"],
        "nl": ["Volksgezondheid", "Medisch Gebruik", "Bestrijding Drugshandel", "Regelgevingskaders", "Economische Impact", "Nationale Soevereiniteit"],
        "id": ["Kesehatan Masyarakat", "Penggunaan Medis", "Pemberantasan Perdagangan Narkoba", "Kerangka Regulasi", "Dampak Ekonomi", "Kedaulatan Nasional"],
        "ms": ["Kesihatan Awam", "Kegunaan Perubatan", "Memerangi Perdagangan Dadah", "Rangka Kerja Pengawalan", "Kesan Ekonomi", "Kedaulatan Negara"],
    },
    "comites.entries.canabis.delegates": {
        "pt-BR": "16 delegações · 32 delegados", "en": "16 delegations · 32 delegates",
        "es": "16 delegaciones · 32 delegados", "fr": "16 délégations · 32 délégués",
        "de": "16 Delegationen · 32 Delegierte", "it": "16 delegazioni · 32 delegati",
        "nl": "16 delegaties · 32 afgevaardigden", "id": "16 delegasi · 32 delegasi",
        "ms": "16 delegasi · 32 wakil",
    },
    "comites.entries.misoginia.title": {
        "pt-BR": "Combate à Misoginia — Direitos Humanos e Violência de Gênero",
        "en": "Combating Misogyny — Human Rights and Gender-Based Violence",
        "es": "Combate a la Misoginia — Derechos Humanos y Violencia de Género",
        "fr": "Lutte Contre la Misogynie — Droits de l'Homme et Violences de Genre",
        "de": "Bekämpfung des Frauenhasses — Menschenrechte und geschlechtsbasierte Gewalt",
        "it": "Contrasto alla Misoginia — Diritti Umani e Violenza di Genere",
        "nl": "Bestrijding van Vrouwenhaat — Mensenrechten en Gendergerelateerd Geweld",
        "id": "Pemberantasan Misogini — Hak Asasi Manusia dan Kekerasan Berbasis Gender",
        "ms": "Memerangi Misogini — Hak Asasi Manusia dan Keganasan Berasaskan Jantina",
    },
    "comites.entries.misoginia.description": {
        "pt-BR": "Nesta simulação, os delegados discutirão estratégias internacionais de enfrentamento à misoginia e à violência baseada em gênero. O debate terá como foco o fortalecimento dos mecanismos de proteção, o combate ao discurso de ódio e à violência no ambiente digital e a promoção dos direitos fundamentais das mulheres, considerando os desafios impostos por desigualdades persistentes e diferentes marcos sociais e legislativos ao redor do mundo.",
        "en": "In this simulation, delegates will discuss international strategies to combat misogyny and gender-based violence. The debate will focus on strengthening protection mechanisms, fighting hate speech and violence in digital environments, and promoting women's fundamental rights, considering challenges posed by persistent inequalities and different social and legislative frameworks around the world.",
        "es": "En esta simulación, los delegados discutirán estrategias internacionales de enfrentamiento a la misoginia y la violencia basada en género. El debate se centrará en el fortalecimiento de los mecanismos de protección, el combate al discurso de odio y la violencia en el ambiente digital, y la promoción de los derechos fundamentales de las mujeres, considerando los desafíos impuestos por desigualdades persistentes y distintos marcos sociales y legislativos alrededor del mundo.",
        "fr": "Dans cette simulation, les délégués discuteront de stratégies internationales pour lutter contre la misogynie et les violences fondées sur le genre. Le débat portera sur le renforcement des mécanismes de protection, la lutte contre la haine et la violence en ligne, et la promotion des droits fondamentaux des femmes, face aux inégalités persistantes et aux cadres sociaux et législatifs variés dans le monde.",
        "de": "In dieser Simulation diskutieren Delegierte internationale Strategien gegen Frauenhass und geschlechtsbasierte Gewalt. Das Debatt stärkt Schutzmechanismen, bekämpft Hassrede und Gewalt in digitalen Umgebungen und fördert die Grundrechte der Frauen unter Berücksichtigung anhaltender Ungleichheit und unterschiedlicher sozialer und gesetzgeberischer Rahmen weltweit.",
        "it": "In questa simulazione i delegati discuteranno strategie internazionali per contrastare la misoginia e la violenza di genere. Il dibattito si concentrerà sul rafforzamento dei meccanismi di protezione, sulla lotta all'odio e alla violenza digitale e sulla promozione dei diritti fondamentali delle donne, considerando le disuguaglianze persistenti e i diversi quadri sociali e legislativi nel mondo.",
        "nl": "In deze simulatie bespreken afgevaardigde internationale strategieën tegen vrouwenhaat en gendergerelateerd geweld. Het debat richt zich op versterking van beschermingsmechanismen, bestrijding van haatzaaien en geweld in digitale omgevingen, en het bevorderen van fundamentele rechten van vrouwen, tegen de achtergrond van hardnekkige ongelijkheid en verschillende sociale en wettelijke kaders wereldwijd.",
        "id": "Dalam simulasi ini, delegasi akan membahas strategi internasional untuk mengatasi misogini dan kekerasan berbasis gender. Debat berfokus pada penguatan mekanisme perlindungan, memerangi ujaran kebencian dan kekerasan di lingkungan digital, serta mempromosikan hak-hak dasar perempuan, dengan mempertimbangkan ketidaksetaraan yang berkelanjutan dan kerangka sosial serta legislasi yang berbeda di seluruh dunia.",
        "ms": "Dalam simulasi ini, wakil akan membahas strategi antarabangsa untuk memerangi misogini dan keganasan berasaskan jantina. Perbincangan menumpu kepada pengukuhan mekanisme perlindungan, memerangi ujaran kebencian dan keganasan dalam persekitaran digital, serta mempromosikan hak asasi wanita, sambil mengambil kira ketidaksamaan berterusan dan rangka sosial serta perundangan yang berbeza di seluruh dunia.",
    },
    "comites.entries.misoginia.topics": {
        "pt-BR": ["Violência de Gênero", "Direitos Humanos", "Discurso de Ódio Online", "Igualdade Salarial", "Mecanismos de Proteção", "Legislação Internacional"],
        "en": ["Gender-Based Violence", "Human Rights", "Online Hate Speech", "Pay Equity", "Protection Mechanisms", "International Legislation"],
        "es": ["Violencia de Género", "Derechos Humanos", "Discurso de Odio en Línea", "Igualdad Salarial", "Mecanismos de Protección", "Legislación Internacional"],
        "fr": ["Violences de Genre", "Droits de l'Homme", "Discours de Haine en Ligne", "Égalité Salariale", "Mécanismes de Protection", "Législation Internationale"],
        "de": ["Geschlechtsbasierte Gewalt", "Menschenrechte", "Online-Hassrede", "Lohngleichheit", "Schutzmechanismen", "Internationale Gesetzgebung"],
        "it": ["Violenza di Genere", "Diritti Umani", "Hate Speech Online", "Parità Salariale", "Meccanismi di Protezione", "Legislazione Internazionale"],
        "nl": ["Gendergerelateerd Geweld", "Mensenrechten", "Online Haatzaaien", "Loongelijkheid", "Beschermingsmechanismen", "Internationale Wetgeving"],
        "id": ["Kekerasan Berbasis Gender", "Hak Asasi Manusia", "Ujaran Kebencian Daring", "Kesetaraan Upah", "Mekanisme Perlindungan", "Legislasi Internasional"],
        "ms": ["Keganasan Berasaskan Jantina", "Hak Asasi Manusia", "Ujaran Kebencian Dalam Talian", "Kesamarataan Gaji", "Mekanisme Perlindungan", "Perundangan Antarabangsa"],
    },
    "comites.entries.misoginia.delegates": {
        "pt-BR": "16 delegações · 32 delegados", "en": "16 delegations · 32 delegates",
        "es": "16 delegaciones · 32 delegados", "fr": "16 délégations · 32 délégués",
        "de": "16 Delegationen · 32 Delegierte", "it": "16 delegazioni · 32 delegati",
        "nl": "16 delegaties · 32 afgevaardigden", "id": "16 delegasi · 32 delegasi",
        "ms": "16 delegasi · 32 wakil",
    },
    "comites.entries.mma.title": {
        "pt-BR": "Programa das Nações Unidas para o Meio Ambiente (PNUMA)",
        "en": "United Nations Environment Programme (UNEP)",
        "es": "Programa de las Naciones Unidas para el Medio Ambiente (PNUMA)",
        "fr": "Programme des Nations Unies pour l'Environnement (PNUE)",
        "de": "Umweltprogramm der Vereinten Nationen (UNEP)",
        "it": "Programma delle Nazioni Unite per l'Ambiente (UNEP)",
        "nl": "Milieuprogramma van de Verenigde Naties (UNEP)",
        "id": "Programme Perserikatan Bangsa-Bangsa untuk Lingkungan Hidup (UNEP)",
        "ms": "Program Alam Sekitar Pertubuhan Bangsa-Bangsa Bersatu (UNEP)",
    },
    "comites.entries.mma.description": {
        "pt-BR": "Principal órgão do sistema das Nações Unidas dedicado às questões ambientais, o PNUMA promove a cooperação internacional em temas como mudanças climáticas, preservação da biodiversidade e combate à poluição. Nesta simulação, os delegados discutirão respostas multilaterais para os principais desafios ambientais contemporâneos.",
        "en": "The main UN body dedicated to environmental issues, UNEP promotes international cooperation on climate change, biodiversity preservation and pollution control. In this simulation, delegates will discuss multilateral responses to today's key environmental challenges.",
        "es": "Principal órgano del sistema de las Naciones Unidas dedicado a las cuestiones ambientales, el PNUMA promueve la cooperación internacional en temas como el cambio climático, la preservación de la biodiversidad y la lucha contra la contaminación. En esta simulación, los delegados discutirán respuestas multilaterales para los principales desafíos ambientales contemporáneos.",
        "fr": "Principal organe du système des Nations Unies consacré aux questions environnementales, le PNUE promeut la coopération internationale sur le changement climatique, la préservation de la biodiversité et la lutte contre la pollution. Dans cette simulation, les délégués discuteront de réponses multilatérales aux grands défis environnementaux contemporains.",
        "de": "Das Hauptgremium des UN-Systems für Umweltfragen, UNEP, fördert internationale Zusammenarbeit zu Klimawandel, Biodiversitätsschutz und Umweltverschmutzung. In dieser Simulation diskutieren Delegierte multilaterale Antworten auf aktuelle Umweltherausforderungen.",
        "it": "Il principale organo del sistema delle Nazioni Unite dedicato all'ambiente, UNEP promuove la cooperazione internazionale su cambiamento climatico, tutela della biodiversità e contrasto all'inquinamento. In questa simulazione i delegati discuteranno risposte multilaterali alle sfide ambientali contemporanee.",
        "nl": "Het belangrijkste VN-orgaan voor milieukwesties, UNEP, bevordert internationale samenwerking over klimaatverandering, biodiversiteitsbehoud en vervuiling. In deze simulatie bespreken afgevaardigde multilaterale antwoorden op actuele milieudruk.",
        "id": "Lingkaran utama PBB yang berfokus pada isu lingkungan, UNEP mempromosikan kerjasama internasional tentang perubahan iklim, pelestarian biodiversitas, dan pengendalian polusi. Dalam simulasi ini, delegasi akan membahas respons multilateral terhadap tantangan lingkungan utama saat ini.",
        "ms": "Badan utama sistem PBB untuk isu alam sekitar, UNEP mempromosikan kerjasama antarabangsa mengenai perubahan iklim, pemeliharaan biodiversiti dan kawalan pencemaran. Dalam simulasi ini, wakil akan membahas respons berbilateral tercabaran alam sekitar utama hari ini.",
    },
    "comites.entries.mma.topics": {
        "pt-BR": ["Mudanças Climáticas", "Biodiversidade", "Energia Renovável", "Poluição dos Oceanos"],
        "en": ["Climate Change", "Biodiversity", "Renewable Energy", "Ocean Pollution"],
        "es": ["Cambio Climático", "Biodiversidad", "Energía Renovable", "Contaminación de los Océanos"],
        "fr": ["Changement Climatique", "Biodiversité", "Énergie Renouvelable", "Pollution des Océans"],
        "de": ["Klimawandel", "Biodiversität", "Erneuerbare Energie", "Ozeanverschmutzung"],
        "it": ["Cambiamento Climatico", "Biodiversità", "Energia Rinnovabile", "Inquinamento degli Oceani"],
        "nl": ["Klimaatverandering", "Biodiversiteit", "Vernieuwbare Energie", "Oceaanvervuiling"],
        "id": ["Perubahan Iklim", "Keanekaragaman Hayati", "Energi Terbarukan", "Pencemaran Lautan"],
        "ms": ["Perubahan Iklim", "Kepelbagaian Hayat", "Tenaga Boleh Baharu", "Pencemaran Lautan"],
    },
    "comites.entries.mma.delegates": {
        "pt-BR": "18 delegações · 36 delegados", "en": "18 delegations · 36 delegates",
        "es": "18 delegaciones · 36 delegados", "fr": "18 délégations · 36 délégués",
        "de": "18 Delegationen · 36 Delegierte", "it": "18 delegazioni · 36 delegati",
        "nl": "18 delegaties · 36 afgevaardigden", "id": "18 delegasi · 36 delegasi",
        "ms": "18 delegasi · 36 wakil",
    },
    "comites.entries.dhr.title": {
        "pt-BR": "Conselho de Direitos Humanos",
        "en": "Human Rights Council",
        "es": "Consejo de Derechos Humanos",
        "fr": "Conseil des Droits de l'Homme",
        "de": "Menschenrechtsrat",
        "it": "Consiglio dei Diritti Umani",
        "nl": "Mensenrechtenraad",
        "id": "Dewan Hak Asasi Manusia",
        "ms": "Majlis Hak Asasi Manusia",
    },
    "comites.entries.dhr.description": {
        "pt-BR": "Órgão das Nações Unidas dedicado à promoção e à proteção dos direitos humanos em todo o mundo. Nesta simulação, os delegados discutirão mecanismos internacionais de proteção e os desafios relacionados à garantia de direitos fundamentais em diferentes contextos nacionais.",
        "en": "UN body dedicated to the promotion and protection of human rights worldwide. In this simulation, delegates will discuss international protection mechanisms and the challenges of guaranteeing fundamental rights in different national contexts.",
        "es": "Órgano de las Naciones Unidas dedicado a la promoción y la protección de los derechos humanos en todo el mundo. En esta simulación, los delegados discutirán mecanismos internacionales de protección y los desafíos relacionados con la garantía de derechos fundamentales en distintos contextos nacionales.",
        "fr": "Organe des Nations Unies dédié à la promotion et à la protection des droits de l'homme dans le monde. Dans cette simulation, les délégués discuteront des mécanismes internationaux de protection et des défis de la garantie des droits fondamentaux dans différents contextes nationaux.",
        "de": "UN-Gremium für die Förderung und den Schutz der Menschenrechte weltweit. In dieser Simulation diskutieren Delegierte internationale Schutzmechanismen und die Herausforderungen der Gewährleistung grundlegender Rechte in unterschiedlichen nationalen Kontexten.",
        "it": "Organo delle Nazioni Unite dedicato alla promozione e alla protezione dei diritti umani nel mondo. In questa simulazione i delegati discuteranno meccanismi internazionali di protezione e le sfide della garanzia dei diritti fondamentali in diversi contesti nazionali.",
        "nl": "VN-orgaan voor de bevordering en bescherming van mensenrechten wereldwijd. In deze simulatie bespreken afgevaardigde internationale beschermingsmechanismen en de uitdagingen van fundamentele rechten in verschillende nationale contexten.",
        "id": "Lingkaran PBB yang berdedikasi pada promosi dan perlindungan hak asasi manusia di seluruh dunia. Dalam simulasi ini, delegasi akan membahas mekanisme perlindungan internasional dan tantangan menjamin hak dasar dalam berbagai konteks nasional.",
        "ms": "Badan PBB yang berdedikasi kepada promosi dan perlindungan hak asasi manusia di seluruh dunia. Dalam simulasi ini, wakil akan membahas mekanisme perlindungan antarabangsa serta cabaran menjamin hak asasi dalam pelbagai konteks negara.",
    },
    "comites.entries.dhr.topics": {
        "pt-BR": ["Proteção de Minorias", "Refugiados", "Liberdade de Expressão", "Trabalho Infantil"],
        "en": ["Minority Protection", "Refugees", "Freedom of Expression", "Child Labor"],
        "es": ["Protección de Minorías", "Refugiados", "Libertad de Expresión", "Trabajo Infantil"],
        "fr": ["Protection des Minorités", "Réfugiés", "Liberté d'Expression", "Travail des Enfants"],
        "de": ["Minderheitenschutz", "Flüchtlinge", "Meinungsfreiheit", "Kinderarbeit"],
        "it": ["Protezione delle Minoranze", "Rifugiati", "Libertà di Espressione", "Lavoro Minorile"],
        "nl": ["Bescherming van Minderheden", "Vluchtelingen", "Vrijheid van Meningsuiting", "Kinderarbeid"],
        "id": ["Perlindungan Minoritas", "Pengungsi", "Kebebasan Berekspresi", "Pekerjaan Anak"],
        "ms": ["Perlindungan Pihak Minoriti", "Pelarian", "Kebebasan Bersuara", "Pekerjaan Kanak-kanak"],
    },
    "comites.entries.dhr.delegates": {
        "pt-BR": "16 delegações · 32 delegados", "en": "16 delegations · 32 delegates",
        "es": "16 delegaciones · 32 delegados", "fr": "16 délégations · 32 délégués",
        "de": "16 Delegationen · 32 Delegierte", "it": "16 delegazioni · 32 delegati",
        "nl": "16 delegaties · 32 afgevaardigden", "id": "16 delegasi · 32 delegasi",
        "ms": "16 delegasi · 32 wakil",
    },
    "comites.entries.ecosoc.title": {
        "pt-BR": "Conselho Econômico e Social",
        "en": "Economic and Social Council",
        "es": "Consejo Económico y Social",
        "fr": "Conseil Économique et Social",
        "de": "Wirtschafts- und Sozialrat",
        "it": "Consiglio Economico e Sociale",
        "nl": "Economische en Sociale Raad",
        "id": "Dewan Ekonomi dan Sosial",
        "ms": "Majlis Ekonomi dan Sosial",
    },
    "comites.entries.ecosoc.description": {
        "pt-BR": "Um dos principais fóruns das Nações Unidas para a discussão de questões econômicas, sociais e ambientais de alcance internacional. Nesta simulação, os delegados buscarão soluções multilaterais para desafios relacionados ao desenvolvimento sustentável, à redução das desigualdades e à cooperação econômica entre os Estados.",
        "en": "One of the main UN forums for discussing international economic, social and environmental issues. In this simulation, delegates will seek multilateral solutions to challenges related to sustainable development, reducing inequality and economic cooperation among states.",
        "es": "Uno de los principales foros de las Naciones Unidas para la discusión de cuestiones económicas, sociales y ambientales de alcance internacional. En esta simulación, los delegados buscarán soluciones multilaterales a desafíos relacionados con el desarrollo sustentable, la reducción de desigualdades y la cooperación económica entre los Estados.",
        "fr": "L'un des principaux forums des Nations Unies pour discuter des questions économiques, sociales et environnementales d'envergure internationale. Dans cette simulation, les délégués chercheront des solutions multilatérales aux défis du développement durable, de la réduction des inégalités et de la coopération économique entre États.",
        "de": "Eines der wichtigsten UN-Foren für internationale wirtschaftliche, soziale und umweltpolitische Fragen. In dieser Simulation suchen Delegierte multilaterale Lösungen für nachhaltige Entwicklung, Verringerung von Ungleichheit und wirtschaftliche Zusammenarbeit zwischen Staaten.",
        "it": "Uno dei principali forum delle Nazioni Unite per discutere questioni economiche, sociali e ambientali di portata internazionale. In questa simulazione i delegati cercheranno soluzioni multilaterali a sfide legate a sviluppo sostenibile, riduzione delle disuguaglianze e cooperazione economica tra Stati.",
        "nl": "Eén van de belangrijkste VN-fora voor internationale economische, sociale en milieukwesties. In deze simulatie zoeken afgevaardigde multilaterale oplossingen voor duurzame ontwikkeling, vermindering van ongelijkheid en economische samenwerking tussen staten.",
        "id": "Salah satu forum utama PBB untuk membahas isu ekonomi, sosial, dan lingkungan berskala internasional. Dalam simulasi ini, delegasi akan mencari solusi multilateral atas tantangan terkait pembangunan berkelanjutan, pengurangan ketidaksetaraan, dan kerjasama ekonomi antar negara.",
        "ms": "Salah satu forum utama PBB untuk membincangkan isu ekonomi, sosial dan alam sekitar berskala antarabangsa. Dalam simulasi ini, wakil akan mencari penyelesaian berbilateral tercabaran berkaitan pembangunan mampan, pengurangan ketidaksamaan dan kerjasama ekonomi antara negara.",
    },
    "comites.entries.ecosoc.topics": {
        "pt-BR": ["Combate à Pobreza", "Comércio Internacional", "Dívida Externa", "ODS — Agenda 2030"],
        "en": ["Combating Poverty", "International Trade", "External Debt", "SDGs — Agenda 2030"],
        "es": ["Combate a la Pobreza", "Comercio Internacional", "Deuda Externa", "ODS — Agenda 2030"],
        "fr": ["Lutte Contre la Pauvreté", "Commerce International", "Dette Extérieure", "ODD — Agenda 2030"],
        "de": ["Bekämpfung der Armut", "Welthandel", "Auslandsschulden", "SDG — Agenda 2030"],
        "it": ["Contrasto alla Povertà", "Commercio Internazionale", "Debito Estero", "SDS — Agenda 2030"],
        "nl": ["Bestrijding van Armoede", "Internationale Handel", "Buitenlandse Schuld", "SDG — Agenda 2030"],
        "id": ["Pemberantasan Kemiskinan", "Perdagangan Internasional", "Utang Luar Negeri", "SDGs — Agenda 2030"],
        "ms": ["Memerangi Kemiskinan", "Perdagangan Antarabangsa", "Hutang Luar", "SDG — Agenda 2030"],
    },
    "comites.entries.ecosoc.delegates": {
        "pt-BR": "14 delegações · 28 delegados", "en": "14 delegations · 28 delegates",
        "es": "14 delegaciones · 28 delegados", "fr": "14 délégations · 28 délégués",
        "de": "14 Delegationen · 28 Delegierte", "it": "14 delegazioni · 28 delegati",
        "nl": "14 delegaties · 28 afgevaardigden", "id": "14 delegasi · 28 delegasi",
        "ms": "14 delegasi · 28 wakil",
    },
    "comites.entries.disec.title": {
        "pt-BR": "Comitê de Desarmamento e Segurança Internacional",
        "en": "Disarmament and International Security Committee",
        "es": "Comité de Desarme y Seguridad Internacional",
        "fr": "Comité du Désarmement et de la Sécurité Internationale",
        "de": "Ausschuss für Abrüstung und Internationale Sicherheit",
        "it": "Comitato per il Disarmo e la Sicurezza Internazionale",
        "nl": "Comité voor Ontwapening en Internationale Veiligheid",
        "id": "Komite Perlucutan Senjata dan Keamanan Internasional",
        "ms": "Jawatankuasa Pelucutan Senjata dan Keselamatan Antarabangsa",
    },
    "comites.entries.disec.description": {
        "pt-BR": "Primeiro Comitê da Assembleia Geral das Nações Unidas, responsável por discutir questões relacionadas ao desarmamento e à segurança internacional. Nesta simulação, os delegados abordarão os desafios da proliferação de armas, das novas tecnologias militares e da prevenção de conflitos.",
        "en": "The First Committee of the UN General Assembly, responsible for discussing disarmament and international security issues. In this simulation, delegates will address the challenges of weapons proliferation, new military technologies and conflict prevention.",
        "es": "Primer Comité de la Asamblea General de las Naciones Unidas, responsable de discutir cuestiones relacionadas con el desarme y la seguridad internacional. En esta simulación, los delegados abordarán los desafíos de la proliferación de armas, las nuevas tecnologías militares y la prevención de conflictos.",
        "fr": "Premier Comité de l'Assemblée Générale des Nations Unies, chargé des questions de désarmement et de sécurité internationale. Dans cette simulation, les délégués aborderont les défis de la prolifération des armes, des nouvelles technologies militaires et de la prévention des conflits.",
        "de": "Erster Ausschuss der UN-Generalversammlung für Abrüstung und internationale Sicherheit. In dieser Simulation befassen sich Delegierte mit Waffenproliferation, neuen Militärtechnologien und Konfliktprävention.",
        "it": "Primo Comitato dell'Assemblea Generale delle Nazioni Unite, responsabile delle questioni di disarmo e sicurezza internazionale. In questa simulazione i delegati affronteranno le sfide della proliferazione delle armi, delle nuove tecnologie militari e della prevenzione dei conflitti.",
        "nl": "Eerste Comité van de Algemene Vergadering van de VN, verantwoordelijk voor ontwapening en internationale veiligheid. In deze simulatie bespreken afgevaardigde de uitdagingen van wapenproliferatie, nieuwe militaire technologieën en conflictpreventie.",
        "id": "Komite Pertama Majelis Umum PBB, bertanggungjawab membahas isu perlucutan senjata dan keamanan internasional. Dalam simulasi ini, delegasi akan membahas tantangan proliferasi senjata, teknologi militer baru, dan pencegahan konflik.",
        "ms": "Jawatankuasa Pertama Perhimpunan Agung PBB, bertanggungjawab membincangkan isu pelucutan senjata dan keselamatan antarabangsa. Dalam simulasi ini, wakil akan membahas cabaran proliferasi senjata, teknologi ketenteraan baharu dan pencegahan konflik.",
    },
    "comites.entries.disec.topics": {
        "pt-BR": ["Não-Proliferação Nuclear", "Guerras Cibernéticas", "Armas Autônomas", "Tratados de Paz"],
        "en": ["Nuclear Non-Proliferation", "Cyber Warfare", "Autonomous Weapons", "Peace Treaties"],
        "es": ["No Proliferación Nuclear", "Guerras Cibernéticas", "Armas Autónomas", "Tratados de Paz"],
        "fr": ["Non-Prolifération Nucléaire", "Guerres Cybernétiques", "Armes Autonomes", "Traités de Paix"],
        "de": ["Nukleare Nichtverbreitung", "Cyberkriege", "Autonome Waffen", "Friedensverträge"],
        "it": ["Non Proliferazione Nucleare", "Guerre Informatiche", "Armi Autonome", "Trattati di Pace"],
        "nl": ["Nucleaire Non-Proliferatie", "Cyberoorlogen", "Autonome Wapens", "Vredesverdragen"],
        "id": ["Non-Proliferasi Nuklir", "Perang Siber", "Senjata Otonom", "Perjanjian Damai"],
        "ms": ["Pencegahan Proliferasi Nuklear", "Perang Siber", "Senjata Autonomi", "Perjanjian Damai"],
    },
    "comites.entries.disec.delegates": {
        "pt-BR": "16 delegações · 32 delegados", "en": "16 delegations · 32 delegates",
        "es": "16 delegaciones · 32 delegados", "fr": "16 délégations · 32 délégués",
        "de": "16 Delegationen · 32 Delegierte", "it": "16 delegazioni · 32 delegati",
        "nl": "16 delegaties · 32 afgevaardigden", "id": "16 delegasi · 32 delegasi",
        "ms": "16 delegasi · 32 wakil",
    },
    "comites.entries.oms.title": {
        "pt-BR": "Organização Mundial da Saúde",
        "en": "World Health Organization",
        "es": "Organización Mundial de la Salud",
        "fr": "Organisation Mondiale de la Santé",
        "de": "Weltgesundheitsorganisation",
        "it": "Organizzazione Mondiale della Sanità",
        "nl": "Wereldgezondheidsorganisatie",
        "id": "Organisasi Kesehatan Dunia",
        "ms": "Pertubuhan Kesihatan Sedunia",
    },
    "comites.entries.oms.description": {
        "pt-BR": "Agência especializada das Nações Unidas responsável pela promoção da saúde e pela coordenação da cooperação internacional na área. Nesta simulação, os delegados discutirão estratégias para enfrentar ameaças sanitárias globais e ampliar a capacidade dos sistemas de saúde diante de desafios emergentes.",
        "en": "UN specialized agency responsible for promoting health and coordinating international cooperation in the field. In this simulation, delegates will discuss strategies to tackle global health threats and strengthen health systems in the face of emerging challenges.",
        "es": "Agencia especializada de las Naciones Unidas responsable de promover la salud y coordinar la cooperación internacional en el área. En esta simulación, los delegados discutirán estrategias para enfrentar amenazas sanitarias globales y ampliar la capacidad de los sistemas de salud ante desafíos emergentes.",
        "fr": "Agence spécialisée des Nations Unies chargée de promouvoir la santé et de coordonner la coopération internationale dans le domaine. Dans cette simulation, les délégués discuteront de stratégies pour affronter les menaces sanitaires mondiales et renforcer les systèmes de santé face aux défis émergents.",
        "de": "Spezialisierte UN-Agentur für die Förderung der Gesundheit und die Koordinierung internationaler Zusammenarbeit auf dem Gebiet. In dieser Simulation diskutieren Delegierte Strategien gegen globale Gesheitsbedrohungen und für die Stärkung von Gesundheitssystemen angesichts neuer Herausforderungen.",
        "it": "Agenzia specializzata delle Nazioni Unite responsabile della promozione della salute e della coordinazione della cooperazione internazionale nel settore. In questa simulazione i delegati discuteranno strategie per affrontare minacce sanitarie globali e rafforzare i sistemi sanitari di fronte a sfide emergenti.",
        "nl": "VN-specialisatieagentschap voor de bevordering van gezondheid en de coördinatie van internationale samenwerking op dit gebied. In deze simulatie bespreken afgevaardigde strategieën tegen mondiale gezondheidsdreigingen en voor het versterken van gezondheidszorgstelsels bij nieuwe uitdagingen.",
        "id": "Lembaga khusus PBB yang bertanggungjawab mempromosikan kesehatan dan mengoordinasikan kerjasama internasional di bidang ini. Dalam simulasi ini, delegasi akan membahas strategi menghadapi ancaman kesehatan global dan memperkuat sistem kesehatan menghadapi tantangan yang muncul.",
        "ms": "Agensi khusus PBB yang bertanggungjawab mempromosikan kesihatan dan menyelaraskan kerjasama antarabangsa dalam bidang ini. Dalam simulasi ini, wakil akan membahas strategi menghadapi ancaman kesihatan global dan mengukuhkan sistem kesihatan menghadapi cabaran baharu.",
    },
    "comites.entries.oms.topics": {
        "pt-BR": ["Prevenção de Pandemias", "Acesso a Vacinas", "Saúde Mental Global", "Resistência Antimicrobiana"],
        "en": ["Pandemic Prevention", "Vaccine Access", "Global Mental Health", "Antimicrobial Resistance"],
        "es": ["Prevención de Pandemias", "Acceso a Vacunas", "Salud Mental Global", "Resistencia Antimicrobiana"],
        "fr": ["Prévention des Pandémies", "Accès aux Vaccins", "Santé Mentale Mondiale", "Résistance Antimicrobienne"],
        "de": ["Pandemieprävention", "Impfstoffzugang", "Globale Gesundheit", "Antimikrobielle Resistenz"],
        "it": ["Prevenzione delle Pandemie", "Accesso ai Vaccini", "Salute Mentale Globale", "Resistenza Antimicrobica"],
        "nl": ["Pandemiepreventie", "Vaccin Toegang", "Globale Geestelijke Gezondheid", "Antimicrobiële Resistentie"],
        "id": ["Pencegahan Pandemi", "Akses Vaksin", "Kesehatan Mental Global", "Resistensi Antimikroba"],
        "ms": ["Pencegahan Pandemik", "Akses Vaksin", "Kesihatan Mental Global", "Ketahanan Antimikrob"],
    },
    "comites.entries.oms.delegates": {
        "pt-BR": "16 delegações · 32 delegados", "en": "16 delegations · 32 delegates",
        "es": "16 delegaciones · 32 delegados", "fr": "16 délégations · 32 délégués",
        "de": "16 Delegationen · 32 Delegierte", "it": "16 delegazioni · 32 delegati",
        "nl": "16 delegaties · 32 afgevaardigden", "id": "16 delegasi · 32 delegasi",
        "ms": "16 delegasi · 32 wakil",
    },
    "comites.entries.cs.title": {
        "pt-BR": "Conselho de Segurança das Nações Unidas",
        "en": "United Nations Security Council",
        "es": "Consejo de Seguridad de las Naciones Unidas",
        "fr": "Conseil de Sécurité des Nations Unies",
        "de": "Sicherheitsrat der Vereinten Nationen",
        "it": "Consiglio di Sicurezza delle Nazioni Unite",
        "nl": "Veiligheidsraad van de Verenigde Naties",
        "id": "Dewan Keamanan Perserikatan Bangsa-Bangsa",
        "ms": "Majlis Keselamatan Pertubuhan Bangsa-Bangsa Bersatu",
    },
    "comites.entries.cs.description": {
        "pt-BR": "Órgão das Nações Unidas com responsabilidade central pela manutenção da paz e da segurança internacionais. Nesta simulação, os delegados deverão discutir respostas diplomáticas a conflitos e crises internacionais, considerando instrumentos como operações de paz, sanções e mecanismos de proteção da população civil.",
        "en": "UN body with primary responsibility for maintaining international peace and security. In this simulation, delegates will discuss diplomatic responses to international conflicts and crises, considering instruments such as peacekeeping operations, sanctions and mechanisms to protect civilian populations.",
        "es": "Órgano de las Naciones Unidas con responsabilidad central en el mantenimiento de la paz y la seguridad internacionales. En esta simulación, los delegados deberán discutir respuestas diplomáticas a conflictos y crisis internacionales, considerando instrumentos como operaciones de paz, sanciones y mecanismos de protección de la población civil.",
        "fr": "Organe des Nations Unies responsable principalement du maintien de la paix et de la sécurité internationales. Dans cette simulation, les délégués discuteront de réponses diplomatiques aux conflits et crises internationaux, en considérant opérations de maintien de la paix, sanctions et mécanismes de protection des populations civiles.",
        "de": "UN-Gremium mit zentraler Verantwortung für internationalen Frieden und Sicherheit. In dieser Simulation diskutieren Delegierte diplomatische Antworten auf internationale Konflikte und Krisen — unter anderem Friedenssanktionen und Schutzmechanismen für die Zivilbevölkerung.",
        "it": "Organo delle Nazioni Unide con responsabilità centrale per il mantenimento della pace e della sicurezza internazionali. In questa simulazione i delegati discuteranno risposte diplomatiche a conflitti e crisi internazionali, considerando strumenti come operazioni di pace, sanzioni e meccanismi di protezione delle popolazioni civili.",
        "nl": "VN-orgaan met hoofdverantwoordelijkheid voor internationale vrede en veiligheid. In deze simulatie bespreken afgevaardigde diplomatieke antwoorden op internationale conflicten en crises, met instrumenten als vredesoperaties, sancties en beschermingsmechanismen voor burgers.",
        "id": "Lingkaran PBB dengan tanggungjawab utama memelihara perdamaian dan keamanan internasional. Dalam simulasi ini, delegasi akan membahas respons diplomatik terhadap konflik dan krisis internasional, dengan mempertimbangkan instrumen seperti operasi pemeliharaan perdamaian, sanksi, dan mekanisme perlindungan penduduk sipil.",
        "ms": "Badan PBB dengan tanggungjawab utama mengekalkan keamanan dan keselamatan antarabangsa. Dalam simulasi ini, wakil akan membahas respons diplomatik terhadap konflik dan krisis antarabangsa, sambil mempertimbangkan instrumen seperti operasi keamanan, sanksi dan mekanisme perlindungan penduduk awam.",
    },
    "comites.entries.cs.topics": {
        "pt-BR": ["Conflitos Armados", "Manutenção da Paz", "Sanções Internacionais", "Direito Humanitário"],
        "en": ["Armed Conflicts", "Peacekeeping", "International Sanctions", "Humanitarian Law"],
        "es": ["Conflictos Armados", "Manteniendo la Paz", "Sanciones Internacionales", "Derecho Humanitario"],
        "fr": ["Conflits Armés", "Maintien de la Paix", "Sanctions Internationales", "Droit International Humanitaire"],
        "de": ["Bewaffnete Konflikte", "Friedenssicherung", "Internationale Sanktionen", "Humanitäres Völkerrecht"],
        "it": ["Conflitti Armati", "Mantenimento della Pace", "Sanzioni Internazionali", "Diritto Umanitario"],
        "nl": ["Gewapende Conflicten", "Vredeshandhaving", "Internationale Sancties", "Humanitair Recht"],
        "id": ["Konflik Bersenjata", "Pemeliharaan Perdamaian", "Sanksi Internasional", "Hukum Kemanusiaan"],
        "ms": ["Konflik Bersenjata", "Menjaga Keamanan", "Sanksi Antarabangsa", "Undang-undang Kemanusiaan"],
    },
    "comites.entries.cs.delegates": {
        "pt-BR": "15 delegações · 30 delegados", "en": "15 delegations · 30 delegates",
        "es": "15 delegaciones · 30 delegados", "fr": "15 délégations · 30 délégués",
        "de": "15 Delegationen · 30 Delegierte", "it": "15 delegazioni · 30 delegati",
        "nl": "15 delegaties · 30 afgevaardigden", "id": "15 delegasi · 30 delegasi",
        "ms": "15 delegasi · 30 wakil",
    },
    "comites.entries.manual.title": {
        "pt-BR": "Manual do Delegado", "en": "Delegate Manual", "es": "Manual del Delegado",
        "fr": "Manuel du Délégué", "de": "Delegiertenhandbuch", "it": "Manuale del Delegato",
        "nl": "Handleiding voor de Afgevaardigde", "id": "Manual Delegasi", "ms": "Manual Wakil",
    },
    "comites.entries.manual.org": {
        "pt-BR": "Manual do Delegado — Edição de 2026",
        "en": "Delegate Manual — 2026 Edition", "es": "Manual del Delegado — Edición 2026",
        "fr": "Manuel du Délégué — Édition 2026", "de": "Delegiertenhandbuch — Ausgabe 2026",
        "it": "Manuale del Delegato — Edizione 2026", "nl": "Handleiding voor de Afgevaardigde — Editie 2026",
        "id": "Manual Delegasi — Edisi 2026", "ms": "Manual Wakil — Edisi 2026",
    },
    "comites.entries.manual.description": {
        "pt-BR": "O Manual do Delegado é o principal guia de preparação para a Edição de 2026. Nele, os participantes encontrarão informações essenciais sobre os comitês, seus temas de debate, o contexto de cada discussão e orientações para a preparação e o desenvolvimento das sessões.\n\nO documento tem como objetivo fornecer aos delegados as ferramentas necessárias para compreender o tema de seu comitê, aprofundar suas pesquisas e participar dos debates de forma fundamentada, contribuindo para uma experiência de simulação mais dinâmica, imersiva e enriquecedora.",
        "en": "The Delegate Manual is the main preparation guide for the 2026 Edition. It contains essential information about the committees, their debate topics, the context of each discussion and guidance for preparing for and running sessions.\n\nThe document aims to give delegates the tools to understand their committee's topic, deepen their research and take part in debates with solid grounding, contributing to a more dynamic, immersive and enriching simulation experience.",
        "es": "El Manual del Delegado es la principal guía de preparación para la Edición 2026. En él, los participantes encontrarán información esencial sobre los comités, sus temas de debate, el contexto de cada discusión y orientaciones para la preparación y el desarrollo de las sesiones.\n\nEl documento tiene como objetivo brindar a los delegados las herramientas necesarias para comprender el tema de su comité, profundizar sus investigaciones y participar de los debates de forma fundamentada, contribuyendo a una experiencia de simulación más dinámica, inmersiva y enriquecedora.",
        "fr": "Le Manuel du Délégué est le principal guide de préparation pour l'Édition 2026. Il contient les informations essentielles sur les comités, leurs thèmes de débat, le contexte de chaque discussion et les orientations pour préparer et mener les séances.\n\nLe document vise à donner aux délégués les outils pour comprendre le thème de leur comité, approfondir leurs recherches et participer aux débats de manière fondée, pour une simulation plus dynamique, immersive et enrichissante.",
        "de": "Das Delegiertenhandbuch ist der wichtigste Vorbereitungsführer für die Ausgabe 2026. Es enthält wesentliche Informationen zu den Gremien, ihren Debattthemen, dem Kontext jeder Diskussion und Hinweise zur Vorbereitung und Durchführung der Sitzungen.\n\nDas Dokument soll Delegierten die Werkzeuge geben, um das Thema ihres Gremiums zu verstehen, ihre Recherche zu vertiefen und fundiert an Debatten teilzunehmen — für ein dynamischeres, immersiveres und bereichernderes Simulations.",
        "it": "Il Manuale del Delegato è la principale guida di preparazione per l'Edizione 2026. Contiene informazioni essenziali sui comitati, i temi di dibattito, il contesto di ogni discussione e indicazioni per la preparazione e lo svolgimento delle sessioni.\n\nIl documento fornisce ai delegati gli strumenti per comprendere il tema del proprio comitato, approfondire la ricerca e partecipare ai dibattiti in modo fondato, contribuendo a un'esperienza di simulazione più dinamica, immersiva ed arricchente.",
        "nl": "De Handleiding voor de Afgevaardigde is de belangrijkste voorbereidingsgids voor Editie 2026. Het bevat essentiële informatie over de comités, hun debatthema's, de context van elke discussie en richtlijnen voor voorbereiding en het leiden van sessies.\n\nHet document geeft afgevaardigden de middelen om het thema van hun comité te begrijpen, onderzoek te verdiepen en onderbouwd deel te nemen aan debatten — voor een dynamischere, meeslependere en rijkere simulatie.",
        "id": "Manual Delegasi adalah panduan persiapan utama untuk Edisi 2026. Di dalamnya peserta menemukan informasi penting tentang komite, tema debat, konteks setiap diskusi, dan pedoman persiapan serta pelaksanaan sesi.\n\nDokumen ini bertujuan memberi delegasi alat untuk memahami topik komite, memperdalam riset, dan berpartisipasi dalam debat secara mendasar, sehingga pengalaman simulasi menjadi lebih dinamis, imersif, dan memperkaya.",
        "ms": "Manual Wakil ialah panduan penyediaan utama untuk Edisi 2026. Ia mengandungi maklumat penting tentang jawatankuasa, tema perbincangan, konteks setiap perbincangan serta panduan untuk penyediaan dan penerusan sesi.\n\nDokumen ini bertujuan memberi wakil alat untuk memahami topik jawatankuasa, mendalami kajian dan menyertai perbincangan secara berasas, lalu menjadikan pengalaman simulasi lebih dinamik, mendalam dan memperkaya.",
    },
}


def set_path(obj, path, value):
    parts = path.split(".")
    cur = obj
    for i, p in enumerate(parts[:-1]):
        if p.isdigit():
            idx = int(p)
            if not isinstance(cur, list):
                raise TypeError(f"expected list at {path}, got {type(cur)}")
            while len(cur) <= idx:
                cur.append(None)
            if cur[idx] is None:
                nxt = parts[i + 1]
                cur[idx] = [] if nxt.isdigit() else {}
            cur = cur[idx]
        else:
            if not isinstance(cur, dict):
                raise TypeError(f"expected dict at {path}, got {type(cur)}")
            nxt = parts[i + 1]
            if p not in cur or not isinstance(cur[p], (dict, list)):
                cur[p] = [] if nxt.isdigit() else {}
            elif isinstance(cur[p], dict) and nxt.isdigit() and not cur[p]:
                cur[p] = []
            cur = cur[p]
    last = parts[-1]
    if last.isdigit():
        idx = int(last)
        if not isinstance(cur, list):
            raise TypeError(f"expected list at {path}, got {type(cur)}")
        while len(cur) <= idx:
            cur.append(None)
        cur[idx] = value
    else:
        if not isinstance(cur, dict):
            raise TypeError(f"expected dict at {path}, got {type(cur)}")
        cur[last] = value


def get_path(obj, path):
    parts = path.split(".")
    cur = obj
    for p in parts:
        if p.isdigit():
            if not isinstance(cur, list) or int(p) >= len(cur):
                return None
            cur = cur[int(p)]
        else:
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
    return cur


def main():
    for loc in LOCALES:
        path = ROOT / f"{loc}.json"
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        updated = 0
        for key, by_loc in T.items():
            if loc in by_loc and by_loc[loc]:
                if get_path(data, key) is None:
                    set_path(data, key, by_loc[loc])
                    updated += 1
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"{loc}: +{updated}")


def force_overwrite_non_pt():
    """For keys that already exist only as PT, write translations into other locales."""
    for loc in LOCALES:
        if loc == "pt-BR":
            continue
        path = ROOT / f"{loc}.json"
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        updated = 0
        for key, by_loc in T.items():
            if loc in by_loc and by_loc[loc]:
                cur = get_path(data, key)
                # overwrite if missing OR still equals pt-BR source (stale PT)
                pt_val = by_loc.get("pt-BR")
                if cur is None or (pt_val and cur == pt_val):
                    set_path(data, key, by_loc[loc])
                    updated += 1
        path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"{loc} force: +{updated}")


if __name__ == "__main__":
    # seed pt first
    path = ROOT / "pt-BR.json"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    n = 0
    for key, by_loc in T.items():
        if "pt-BR" in by_loc and by_loc["pt-BR"] and get_path(data, key) is None:
            set_path(data, key, by_loc["pt-BR"])
            n += 1
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(f"pt-BR seed: +{n}")
    force_overwrite_non_pt()
    main()  # fill any remaining missing
