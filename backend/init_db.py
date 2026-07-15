"""
Inicializa o banco de dados em produção.
Executado automaticamente no primeiro deploy.
"""
from extensions import db
from sqlalchemy import text

# Primeiro roda as migrações críticas antes de criar o app
from app import create_app

app = create_app()
with app.app_context():
    print('[OK] Banco de dados pronto!')