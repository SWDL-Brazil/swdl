#!/usr/bin/env python3
"""
Script para registrar 34 estudantes e 11 delegacoes no banco SWDL.
Rode com: python register_students.py
"""
import os, sys, re, io
from datetime import datetime, timezone

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── Setup Flask app context ────────────────────────────────────
os.environ.setdefault('SECRET_KEY', 'dev-key-for-registration')
os.environ.setdefault('FLASK_ENV', 'development')

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models.user import User
from models.inscription import Inscription
from models.student import Student
from models.delegation import Delegation
from models.theme import Theme
from models.participation import ParticipationHistory

app = create_app()

# ── Data ───────────────────────────────────────────────────────

THEME_NAME = "A Proteção Internacional de Pessoas Deslocadas em Decorrência de Eventos Climáticos Extremos"

DELEGATIONS = {
    "França": ["Melissa Pio", "Julia Linares", "Kauã Santos"],
    "Qatar": ["Júlia Marson", "Isabelly Martins", "Miguel Mesquita"],
    "Russia": ["Geovana Caires", "Aline Cristina", "Luiz Felipe"],
    "Argentina": ["Murilo Wilson", "Eloisa Monteiro", "Larissa Victória"],
    "Alemanha": ["Emilly Vitória", "Júlia Morales", "Maria Lira"],
    "Japão": ["Rafael Ciaramella", "Gabrielle Santos", "Laura Valk"],
    "China": ["Guilherme Santiago", "Laura Abreu", "Pedro Tomazini"],
    "Eua": ["Lucas Montezini", "Isac Lauro", "Agatha Campos"],
    "Brasil": ["Alice Haiter", "Laura Rospendowisk", "Gabrielly Viana"],
    "Reino Unido": ["Giovanna Rodrigues", "Guilherme Oliveira", "Maria Clara dos Santos Felix"],
    "África do Sul": ["Pietra Victoria", "Maria Macaúba", "Vinicius Maia"],
}

# All 34 students — names must match DELEGATIONS exactly
ALL_STUDENTS = [
    "Murilo Wilson", "Pedro Tomazini", "Rafael Ciaramella",
    "Guilherme Oliveira", "Miguel Mesquita", "Isac Lauro",
    "Guilherme Santiago", "Kauã Santos", "Lucas Montezini",
    "Luiz Felipe", "Vinicius Maia", "Melissa Pio",
    "Gabrielle Santos", "Geovana Caires", "Isabelly Martins",
    "Alice Haiter", "Pietra Victoria", "Julia Linares",
    "Maria Lira", "Laura Rospendowisk", "Agatha Campos",
    "Laura Abreu", "Júlia Marson", "Giovanna Rodrigues",
    "Eloisa Monteiro", "Maria Macaúba", "Aline Cristina",
    "Júlia Morales", "Laura Valk", "Gabrielly Viana",
    "Maria Eduarda Cirico", "Maria Clara dos Santos Felix",
    "Emilly Vitória", "Larissa Victória",
]

# ── Helpers ────────────────────────────────────────────────────

def make_email(name):
    """nome.sobrenome@swdl.com — normaliza acentos e caracteres especiais."""
    import unicodedata
    parts = name.strip().split()
    # Normalize accents
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    parts = [strip_accents(p) for p in parts]
    # Remove non-alpha
    parts = [re.sub(r'[^a-zA-Z]', '', p).lower() for p in parts]
    parts = [p for p in parts if p]  # remove empty
    return '.'.join(parts) + '@swdl.com'

def make_password(name):
    """primeiros 4 chars do nome (sem acento) + ano."""
    import unicodedata
    first = name.strip().split()[0]
    first = ''.join(c for c in unicodedata.normalize('NFD', first) if unicodedata.category(c) != 'Mn')
    first = re.sub(r'[^a-zA-Z]', '', first).lower()[:4]
    return f'{first}{datetime.now(timezone.utc).year}'

# ── Run ────────────────────────────────────────────────────────

with app.app_context():
    created_users = 0
    created_students = 0
    created_delegations = 0
    skipped = 0

    # 1. Ensure theme exists
    theme = Theme.query.filter_by(name=THEME_NAME).first()
    if not theme:
        theme = Theme(name=THEME_NAME)
        db.session.add(theme)
        db.session.flush()
        print(f'✅ Tema criado: {THEME_NAME}')
    else:
        print(f'ℹ️  Tema já existe: {THEME_NAME}')

    # 2. Create all students + inscriptions + users
    email_map = {}  # name -> email (for delegation linking)

    for name in ALL_STUDENTS:
        email = make_email(name)
        email_map[name] = email
        password = make_password(name)

        # Check if student already exists
        existing = Student.query.filter_by(email=email).first()
        if existing:
            print(f'  ⏭️  {name} já existe ({email})')
            skipped += 1
            continue

        # Create Inscription
        ins = Inscription(
            name=name,
            email=email,
            phone='',
            grade='',
            motivation='',
            interests='',
            type='delegate',
            status='approved',
            reviewed_at=datetime.now(timezone.utc),
        )
        db.session.add(ins)
        db.session.flush()

        # Create User
        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Create Student
        student = Student(
            user_id=user.id,
            name=name,
            email=email,
            convened=True,
        )
        db.session.add(student)
        db.session.flush()

        # Link inscription to student (for delegation creation later)
        # We'll use inscription_id when creating delegations

        created_users += 1
        created_students += 1
        print(f'  ✅ {name} → {email} | senha: {password}')

    db.session.flush()

    # 3. Create delegations and link students — lookup by email (normalized)
    for country, member_names in DELEGATIONS.items():
        # Get primary student email (first in list)
        primary_name = member_names[0]
        primary_email = email_map[primary_name]
        primary_student = Student.query.filter_by(email=primary_email).first()
        primary_user = User.query.filter_by(email=primary_email).first()

        if not primary_student:
            print(f'  [ERRO] Aluno principal {primary_name} ({primary_email}) nao encontrado para {country}')
            continue

        # Find or create inscription for primary
        ins = Inscription.query.filter_by(email=primary_email, status='approved').first()
        if not ins:
            ins = Inscription(
                name=primary_name,
                email=primary_email,
                phone='',
                grade='',
                motivation='',
                interests='',
                type='delegate',
                status='approved',
                reviewed_at=datetime.now(timezone.utc),
            )
            db.session.add(ins)
            db.session.flush()

        # Create delegation
        short_committee = THEME_NAME[:30]
        deleg = Delegation(
            inscription_id=ins.id,
            user_id=primary_user.id if primary_user else None,
            edition_year=datetime.now(timezone.utc).year,
            theme_id=theme.id,
            country=country,
            country_flag='',
            flag_url='',
            committee=short_committee,
        )
        db.session.add(deleg)
        db.session.flush()

        # Link all members by email
        for member_name in member_names:
            member_email = email_map[member_name]
            student = Student.query.filter_by(email=member_email).first()
            if student:
                student.delegation_id = deleg.id
                student.convened = True

                # Create ParticipationHistory (update if exists)
                ph = ParticipationHistory.query.filter_by(
                    student_id=student.id, year=datetime.now(timezone.utc).year
                ).first()
                if not ph:
                    ph = ParticipationHistory(
                        student_id=student.id,
                        year=datetime.now(timezone.utc).year,
                        committee=THEME_NAME[:30],
                        committee_name=THEME_NAME,
                        country=country,
                        role='delegate',
                        delegation_name=f"{country} @ {THEME_NAME[:30]}",
                    )
                    db.session.add(ph)
                else:
                    ph.committee = THEME_NAME[:30]
                    ph.committee_name = THEME_NAME
                    ph.country = country
                    ph.delegation_name = f"{country} @ {THEME_NAME[:30]}"
            else:
                print(f'  [ERRO] Aluno {member_name} ({member_email}) nao encontrado')

        created_delegations += 1
        member_str = ', '.join(member_names)
        print(f'  [OK] {country}: {member_str}')

    db.session.commit()

    print(f'\n{"="*60}')
    print(f'📊 RESUMO:')
    print(f'   Estudantes criados: {created_students}')
    print(f'   Delegações criadas: {created_delegations}')
    print(f'   Pulados (já existiam): {skipped}')
    print(f'{"="*60}')
    print(f'\n🔑 CREDENCIAIS (senha = 4 primeiros chars + {datetime.now(timezone.utc).year}):')
    print(f'   Exemplo: murilo.wilson@swdl.com → muril{datetime.now(timezone.utc).year}')
    print(f'   Exemplo: julia.linares@swdl.com → juli{datetime.now(timezone.utc).year}')
    print(f'\n   Todos os logins usam o padrão: primeiros4chars_do_nome + {datetime.now(timezone.utc).year}')
