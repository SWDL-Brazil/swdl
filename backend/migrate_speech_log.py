"""
Roda UMA VEZ para criar a tabela speech_log.
Execute: python migrate_speech_log.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado — sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS speech_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delegation_id INTEGER NOT NULL REFERENCES delegations(id),
                committee VARCHAR(30),
                log_type VARCHAR(30) NOT NULL,
                duration_sec INTEGER DEFAULT 0,
                topic VARCHAR(300),
                reference_id INTEGER,
                reference_type VARCHAR(30),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_speech_log_delegation_id ON speech_log(delegation_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_speech_log_committee ON speech_log(committee)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_speech_log_log_type ON speech_log(log_type)")
        print("Tabela speech_log criada!")
    except Exception as e:
        print(f"Erro: {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
