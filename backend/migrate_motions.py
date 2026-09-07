"""
Roda UMA VEZ para criar a tabela motions.
Execute: python migrate_motions.py
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
            CREATE TABLE IF NOT EXISTS motions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposer_id INTEGER NOT NULL REFERENCES delegations(id),
                committee VARCHAR(30) NOT NULL,
                motion_type VARCHAR(30) NOT NULL DEFAULT 'moderated_caucus',
                topic VARCHAR(300) NOT NULL,
                total_time INTEGER DEFAULT 900,
                speaking_time INTEGER DEFAULT 60,
                status VARCHAR(20) DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                seconded_by_id INTEGER REFERENCES delegations(id),
                chair_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decided_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_motions_proposer_id ON motions(proposer_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_motions_committee ON motions(committee)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_motions_status ON motions(status)")
        print("Tabela motions criada!")
    except Exception as e:
        print(f"Erro: {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
