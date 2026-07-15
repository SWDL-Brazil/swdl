"""
Roda UMA VEZ para adicionar a coluna orador à tabela delegations.
Execute: python migrate_orador.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado -- sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE delegations ADD COLUMN orador BOOLEAN DEFAULT 0")
        print("[OK] Coluna orador adicionada!")
    except sqlite3.OperationalError as e:
        print(f"[SKIP] Ja existe: {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
