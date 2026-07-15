"""
Roda UMA VEZ para criar a tabela themes no banco SQLite.
Execute: python migrate_themes.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
if not os.path.exists(db_path):
    print("Banco nao encontrado -- sera criado no proximo python app.py")
else:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute('''
            CREATE TABLE themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE
            )
        ''')
        print("[OK] Tabela themes criada com sucesso!")
        
        # Opcional: Inserir um tema padrão chamado 'Geral'
        cur.execute("INSERT INTO themes (name) VALUES ('Geral')")
        print("[OK] Tema padrao 'Geral' inserido.")
        
    except sqlite3.OperationalError as e:
        print(f"[SKIP] {e}")
    con.commit()
    con.close()
    print("Migracao concluida.")
