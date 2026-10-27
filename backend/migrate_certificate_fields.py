"""
Roda UMA VEZ para adicionar colunas name/email aos certificados e
garantir que student_id aceite NULL (certificados externos / organizadores).

Execute: python migrate_certificate_fields.py
"""
import os
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    cols = {c['name'] for c in inspector.get_columns('certificates')}

    migrations = []
    if 'name' not in cols:
        migrations.append("ALTER TABLE certificates ADD COLUMN name VARCHAR(120)")
    if 'email' not in cols:
        migrations.append("ALTER TABLE certificates ADD COLUMN email VARCHAR(120)")

    # student_id ja existe; se nao for nullable (legacy), tenta relaxar.
    # SQLite nao suporta ALTER COLUMN, entao pulamos silenciosamente lá.
    if 'student_id' in cols:
        try:
            migrations.append("ALTER TABLE certificates ALTER COLUMN student_id DROP NOT NULL")
        except Exception:
            pass  # SQLite ou ja era nullable

    for sql in migrations:
        try:
            with db.engine.begin() as conn:
                conn.execute(text(sql))
            print(f'[OK] {sql}')
        except Exception as e:
            print(f'[SKIP] {sql} -> {e}')

    print('Migracao de campos de certificado concluida.')
