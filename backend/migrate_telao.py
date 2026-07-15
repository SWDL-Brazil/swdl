"""
Roda UMA VEZ para adicionar duration_sec ao banco.
Execute: python migrate_telao.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco não encontrado — será criado no próximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE vote_sessions ADD COLUMN duration_sec INTEGER DEFAULT 120")
        print("✅ Coluna duration_sec adicionada!")
    except sqlite3.OperationalError as e:
        print(f"⏭  Já existe: {e}")
    con.commit()
    con.close()
    print("Migração concluída.")