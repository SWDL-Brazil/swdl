"""
Adiciona colunas slug, excerpt, cover_image à tabela news.
Execute: python migrate_news.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'swdl.db')
con = sqlite3.connect(db_path)
cur = con.cursor()

for sql in [
    "ALTER TABLE news ADD COLUMN slug TEXT",
    "ALTER TABLE news ADD COLUMN excerpt TEXT",
    "ALTER TABLE news ADD COLUMN cover_image TEXT",
]:
    try:
        cur.execute(sql)
        print(f'✅ {sql}')
    except sqlite3.OperationalError as e:
        print(f'⏭  {e}')

# Gera slugs para notícias existentes
import re, unicodedata

def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii','ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]','',text).strip().lower()
    return re.sub(r'[\s_-]+','-',text)[:80]

cur.execute("SELECT id, title FROM news WHERE slug IS NULL OR slug = ''")
for row in cur.fetchall():
    slug = slugify(row[1])
    cur.execute("UPDATE news SET slug=? WHERE id=?", (f"{slug}-{row[0]}", row[0]))
    print(f'  slug: {slug}-{row[0]}')

con.commit()
con.close()
print('✅ Migração concluída!')