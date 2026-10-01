"""Seed de prévia: 1 notícia lead + cards relacionados (não usar em produção)."""
import sqlite3
import unicodedata
import re
from datetime import datetime, timedelta, timezone

DB = r'C:\Users\User\Nova_ONU\backend\swdl.db'
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
assert 'news' in tables, 'tabela news ausente'
assert 'categories' in tables, 'tabela categories ausente'

cats = c.execute('SELECT id, name, slug FROM categories ORDER BY id').fetchall()
ids = [r['id'] for r in cats]
print('cats:', [(r['id'], r['name'], r['slug']) for r in cats])
assert ids, 'sem categorias'

author = c.execute("SELECT id FROM users WHERE role IN ('admin','director') ORDER BY id LIMIT 1").fetchone()
author_id = author['id'] if author else None
print('author_id:', author_id)

c.execute("DELETE FROM news WHERE slug LIKE 'preview-%'")

def slugify(s: str) -> str:
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    s = re.sub(r'[\s_-]+', '-', s)
    return s[:80]

samples = [
    {
        'title': 'Abertura solene marca início da SWDL 2026 em Hortolândia',
        'excerpt': 'Cerca de 180 delegados abriram a edição mais ambiciosa da liga, com debates simultâneos em quatro comitês e pauta climática em destaque.',
        'body': '''<p>Na manhã deste sábado, o auditório do SESI CE-437 recebeu delegados de 42 países para a abertura oficial da <strong>SWDL 2026</strong>. O hino das Nações Unidas ecoou antes do primeiro discurso de posse.</p>
<h2>Pauta do dia</h2>
<ul><li>Abertura do Conselho de Segurança</li><li>Sessão inaugural do DHR</li><li>Primeira resolução emergencial</li></ul>
<blockquote>“Diplomacia começa com escuta ativa — e é isso que treinaremos nos próximos dias.” — Diretoria SWDL</blockquote>
<p>As comissões já operam em regime de crise simulada, com alertas ao vivo no portal. Delegados relatam o clima da sala plenária abaixo.</p>
<img src="https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&amp;q=80" alt="Plenário" />
<p>Até o fim da tarde, três moções já estavam em fila para a arena de debates.</p>''',
        'cat_id': ids[0],
        'committee': 'CS',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&q=80',
        'days_ago': 0,
        'tags': 'swdl,abertura,cs',
    },
    {
        'title': 'Crise no Estreito deOrmuz força sessão de emergência do CS',
        'excerpt': 'Delegações pedem voto nominal após incidente com petroleiro; alerta ativo no ticker.',
        'body': '<p>O Conselho de Segurança entrou em sessão de emergência após o incidente no Estreito deOrmuz.</p><p>Votação nominal prevista para as 16h.</p>',
        'cat_id': ids[0],
        'committee': 'CS',
        'is_crisis': 1,
        'image': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80',
        'days_ago': 0,
        'tags': 'crise,cs,ormuz',
    },
    {
        'title': 'DHR aprova declaração sobre direitos digitais de estudantes',
        'excerpt': 'Texto final incorpora emenda brasileira sobre privacidade em plataformas educacionais.',
        'body': '<p>Após 9 horas de debate, o DHR aprovou a declaração por 28 votos a 4.</p>',
        'cat_id': ids[1] if len(ids) > 1 else ids[0],
        'committee': 'DHR',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=800&q=80',
        'days_ago': 1,
        'tags': 'dhr,direitos',
    },
    {
        'title': 'ECOSOC debate financiamento verde e metas 2030',
        'excerpt': 'Países em desenvolvimento exigem fundo climático com governança paritária.',
        'body': '<p>O ECOSOC abriu o painel sobre financiamento verde com painéis do Brasil, Alemanha e Quênia.</p>',
        'cat_id': ids[0],
        'committee': 'ECOSOC',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80',
        'days_ago': 2,
        'tags': 'ecosoc,economia',
    },
    {
        'title': 'Votação aberta: resolução sobre peacekeeping digital',
        'excerpt': 'Delegações têm até as 18h para votar a resolução 2026/04.',
        'body': '<p>Sessão de votação aberta no portal do delegado.</p>',
        'cat_id': ids[0],
        'committee': 'CS',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=800&q=80',
        'days_ago': 2,
        'tags': 'votacao,resolucao',
    },
    {
        'title': 'Guia de estudos atualizado para novos delegados',
        'excerpt': 'PDF com glossário ONU, rodada de abrir bancadas e erros comuns em gavel.',
        'body': '<p>Baixe o guia na aba Temas.</p>',
        'cat_id': ids[0],
        'committee': 'geral',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&q=80',
        'days_ago': 3,
        'tags': 'guia,estudos',
    },
    {
        'title': 'Arena de imprensa amplia cobertura com rádio SWDL',
        'excerpt': 'Equipes de mídia alunos entrevistam chefes de delegação ao vivo.',
        'body': '<p>A arena fica ao lado do plenário principal.</p>',
        'cat_id': ids[0],
        'committee': 'geral',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80',
        'days_ago': 4,
        'tags': 'imprensa',
    },
    {
        'title': 'MMA propõe pacto regional de reflorestamento amazônico',
        'excerpt': 'Ministros simulados apresentam metas de 30% até 2035.',
        'body': '<p>Proposta segue para comissão de redação.</p>',
        'cat_id': ids[0],
        'committee': 'MMA',
        'is_crisis': 0,
        'image': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&q=80',
        'days_ago': 5,
        'tags': 'mma,ambiente',
    },
]

now = datetime.now(timezone.utc)
cols = [
    'title', 'slug', 'excerpt', 'body', 'cover_image', 'category_id',
    'committee', 'tags', 'is_crisis', 'published', 'created_at', 'updated_at', 'author_id',
]

for s in samples:
    slug = 'preview-' + slugify(s['title'])
    created = (now - timedelta(days=s['days_ago'])).isoformat(sep=' ', timespec='seconds')
    vals = (
        s['title'], slug, s['excerpt'], s['body'], s['image'], s['cat_id'],
        s['committee'], s['tags'], s['is_crisis'], 1, created, created, author_id,
    )
    c.execute(
        f"INSERT INTO news ({','.join(cols)}) VALUES ({','.join(['?'] * len(cols))})",
        vals,
    )
    print('inserted', slug)

c.commit()
rows = c.execute(
    'SELECT slug, title, committee, is_crisis FROM news WHERE published=1 ORDER BY created_at DESC'
).fetchall()
print('total published:', len(rows))
for r in rows:
    print('-', r['slug'], '|', r['committee'], '| crisis' if r['is_crisis'] else '')
c.close()
