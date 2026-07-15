"""
Roda UMA VEZ para adicionar presence_status ao banco.
Execute: python migrate_presence.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado -- sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE delegations ADD COLUMN presence_status VARCHAR(20) DEFAULT 'ausente'")
        print("[OK] Coluna presence_status adicionada!")
    except sqlite3.OperationalError as e:
        print(f"[SKIP] Ja existe: {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
