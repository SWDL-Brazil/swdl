"""
Roda UMA VEZ para criar as tabelas resolutions e amendments.
Execute: python migrate_resolutions.py
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
            CREATE TABLE IF NOT EXISTS resolutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                committee VARCHAR(30) NOT NULL,
                preambulatory TEXT DEFAULT '',
                operative TEXT DEFAULT '',
                proposer_id INTEGER NOT NULL REFERENCES delegations(id),
                co_sponsors TEXT DEFAULT '',
                status VARCHAR(20) DEFAULT 'draft',
                vote_session_id INTEGER REFERENCES vote_sessions(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_at TIMESTAMP,
                voted_at TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_resolutions_committee ON resolutions(committee)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_resolutions_status ON resolutions(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_resolutions_proposer_id ON resolutions(proposer_id)")
        print("Tabela resolutions criada!")
    except Exception as e:
        print(f"Erro resolutions: {e}")

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS amendments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resolution_id INTEGER NOT NULL REFERENCES resolutions(id),
                proposer_id INTEGER NOT NULL REFERENCES delegations(id),
                amendment_type VARCHAR(20) DEFAULT 'friendly',
                target_section VARCHAR(20) NOT NULL,
                target_index INTEGER DEFAULT 0,
                original_text TEXT DEFAULT '',
                proposed_text TEXT DEFAULT '',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decided_at TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS ix_amendments_resolution_id ON amendments(resolution_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS ix_amendments_status ON amendments(status)")
        print("Tabela amendments criada!")
    except Exception as e:
        print(f"Erro amendments: {e}")

    con.commit()
    con.close()
    print("Migracao concluida.")
