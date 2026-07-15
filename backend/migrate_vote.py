"""
Roda UMA VEZ para criar as tabelas de votação.
Execute: python migrate_vote.py
"""
from app import create_app
app = create_app()
with app.app_context():
    from extensions import db
    db.create_all()
    print('✅ Tabelas de votação criadas!')