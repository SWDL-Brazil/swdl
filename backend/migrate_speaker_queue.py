"""
Roda UMA VEZ para criar a tabela speaker_queue.
Execute: python migrate_speaker_queue.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco não encontrado — será criado no próximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS speaker_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                delegation_id INTEGER NOT NULL REFERENCES delegations(id),
                committee VARCHAR(30),
                topic VARCHAR(300),
                speaking_time INTEGER DEFAULT 60,
                position INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                duration_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_speaker_queue_delegation_id ON speaker_queue(delegation_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_speaker_queue_committee ON speaker_queue(committee)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_speaker_queue_status ON speaker_queue(status)")
        print("✅ Tabela speaker_queue criada!")
    except Exception as e:
        print(f"Erro: {e}")
    con.commit()
    con.close()
    print("Migração concluída.")
