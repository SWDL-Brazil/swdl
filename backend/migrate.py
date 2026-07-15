"""
Roda UMA VEZ para adicionar as novas colunas ao banco existente.
Execute: python migrate.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco não encontrado — será criado no próximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    migrations = [
        "ALTER TABLE delegations ADD COLUMN flag_url TEXT",
        "ALTER TABLE delegations ADD COLUMN flag_animation INTEGER DEFAULT 1",
    ]

    for sql in migrations:
        try:
            cur.execute(sql)
            print(f"✅ {sql}")
        except sqlite3.OperationalError as e:
            print(f"⏭  Já existe: {e}")

    con.commit()
    con.close()
    print("Migração concluída.")