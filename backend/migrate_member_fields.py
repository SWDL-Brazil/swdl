"""
Roda UMA VEZ para adicionar motivation/interests/experience aos membros.
Execute: python migrate_member_fields.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado -- sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    migrations = [
        "ALTER TABLE inscription_members ADD COLUMN motivation TEXT",
        "ALTER TABLE inscription_members ADD COLUMN interests TEXT",
        "ALTER TABLE inscription_members ADD COLUMN experience TEXT",
    ]

    for sql in migrations:
        try:
            cur.execute(sql)
            print(f"[OK] {sql}")
        except sqlite3.OperationalError as e:
            print(f"[SKIP] Ja existe: {e}")

    con.commit()
    con.close()
    print("Migracao concluida.")
