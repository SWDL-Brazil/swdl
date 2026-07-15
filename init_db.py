import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
app = create_app()
with app.app_context():
    print('[OK] Banco de dados pronto!')
