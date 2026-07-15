"""
Roda UMA VEZ para adicionar colunas de invocacao ao event_config.
Execute: python migrate_invoke.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado -- sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for col in ['invoke_url', 'invoke_label', 'invoke_active', 'invoke_at']:
        try:
            if 'active' in col:
                cur.execute(f"ALTER TABLE event_config ADD COLUMN {col} BOOLEAN DEFAULT 0")
            elif 'at' in col:
                cur.execute(f"ALTER TABLE event_config ADD COLUMN {col} TIMESTAMP")
            else:
                cur.execute(f"ALTER TABLE event_config ADD COLUMN {col} VARCHAR DEFAULT ''")
            print(f"[OK] Coluna {col} adicionada!")
        except sqlite3.OperationalError as e:
            print(f"[SKIP] {col}: {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
