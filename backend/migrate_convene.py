"""
Roda UMA VEZ para adicionar convened ao banco.
Execute: python migrate_convene.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado -- sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("ALTER TABLE students ADD COLUMN convened BOOLEAN DEFAULT 0")
        print("[OK] Coluna convened adicionada!")
    except sqlite3.OperationalError as e:
        print(f"[SKIP] Ja existe: {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
