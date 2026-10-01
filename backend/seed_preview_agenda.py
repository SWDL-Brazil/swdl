# Seed preview agenda: periods + multi-day items for local QA
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / 'backend' / 'swdl.db'
if not db.exists():
    raise SystemExit(f'missing db {db}')

con = sqlite3.connect(db)
cur = con.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS event_periods (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        ord_order INTEGER DEFAULT 0,
        "order" INTEGER DEFAULT 0,
        color TEXT DEFAULT 'navy'
    )"""
)
# ensure order column name matches model
cols = [r[1] for r in cur.execute('PRAGMA table_info(event_periods)').fetchall()]
print('period cols', cols)
if 'order' not in cols and 'ord_order' in cols:
    cur.execute('ALTER TABLE event_periods RENAME COLUMN ord_order TO "order"')

cur.execute('DELETE FROM event_periods')
cur.executemany(
    'INSERT INTO event_periods (name, start_date, end_date, "order", color) VALUES (?,?,?,?,?)',
    [
        ('Abertura', '2026-09-02', '2026-09-02', 1, 'gold'),
        ('Debates', '2026-09-03', '2026-09-04', 2, 'navy'),
        ('Premiação', '2026-09-05', '2026-09-05', 3, 'green'),
    ],
)

# clear preview items only
cur.execute("DELETE FROM agenda_items WHERE title LIKE 'Preview %' OR id > 0")
# wipe all for clean preview (local db is seed-only)
cur.execute('DELETE FROM agenda_items')

items = [
    # Abertura day 1
    ('2026-09-02', '07:00', '07:30', 'Preview Credenciamento', 'Recepção dos delegados e entrega de kits.', 'Pátio SESI CE-437', 'auto', '', 1, 1),
    ('2026-09-02', '08:00', '09:00', 'Preview Sessão Solene', 'Abertura oficial da SWDL 2026.', 'Auditório', 'auto', '', 2, 1),
    ('2026-09-02', '09:15', '09:45', 'Preview Intervalo', 'Café e networking.', '', 'break', '', 3, 1),
    # Debates day 2
    ('2026-09-03', '08:00', '10:00', 'Preview CS — Sessão de Emergência', 'Debate sobre ameaça à paz e segurança internacional.', 'Sala CS', 'vote', 'CS', 1, 2),
    ('2026-09-03', '10:15', '12:00', 'Preview DHR — Direitos Humanos', 'Discussão sobre reparação histórica.', 'Sala DHR', 'auto', 'DHR', 2, 2),
    ('2026-09-03', '13:30', '15:00', 'Preview ECOSOC — Clima e Deslocamento', 'Deslocamentos forçados por eventos climáticos.', 'Sala ECOSOC', 'crisis', 'ECOSOC', 3, 2),
    # Debates day 3
    ('2026-09-04', '08:00', '10:00', 'Preview MMA — Oceano e Segurança', 'Sessão plenária do MMA.', 'Sala MMA', 'auto', 'MMA', 1, 2),
    ('2026-09-04', '14:00', '16:00', 'Preview Votação de Resoluções', 'Votação dos projetos aprovados em comissão.', 'Auditório', 'vote', '', 2, 2),
    # Premiação
    ('2026-09-05', '09:00', '11:00', 'Preview Premiação e Encerramento', 'Entrega de certificados e troféus.', 'Auditório', 'award', '', 1, 3),
]

for i, (d, st, et, title, desc, loc, status, comm, order, day) in enumerate(items, 1):
    # link period by day
    pid = {1: 1, 2: 2, 3: 3}.get(day)
    cur.execute(
        """INSERT INTO agenda_items
           (event_date, start_time, end_time, title, description, location, status, committee, "order", day, period_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (d, st, et, title, desc, loc, status, comm, order, day, pid),
    )

con.commit()
n = cur.execute('SELECT COUNT(*) FROM agenda_items').fetchone()[0]
p = cur.execute('SELECT COUNT(*) FROM event_periods').fetchone()[0]
print(f'seeded items={n} periods={p}')
con.close()
