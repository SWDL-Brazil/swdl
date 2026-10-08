"""Checa classes CSS usadas nos templates student/ × definidas em student.css.

Uso: python check_css_classes.py  (falha com exit 1 se houver classe órfã)
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(ROOT, 'templates', 'student')
CSS = os.path.join(ROOT, 'static', 'css', 'student.css')

css = io.open(CSS, encoding='utf-8').read()
css_classes = set(re.findall(r'\.([A-Za-z][A-Za-z0-9_-]*)', css))

used = set()
for fn in os.listdir(TPL):
    if not fn.endswith('.html'):
        continue
    src = io.open(os.path.join(TPL, fn), encoding='utf-8').read()
    for m in re.finditer(r'class="([^"]+)"', src):
        val = m.group(1)
        if '{{' in val:  # contains jinja expr -> extract literal fragments
            for frag in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", re.sub(r'\{\{.*?\}\}', ' ', val)):
                used.add(frag)
        else:
            used.update(val.split())

# tokens that are not CSS classes (jinja vars leaked into extraction, states)
skip = {'active', 'done', 'current', 'locked', 'and', 'if', 'else', 'not', 'val',
        'category', 'designated', 'event_started', 'event_ended', 'geral',
        'dpo_ok', 'prep_warn', 'sim_now', 'sim_done', 'cert_ok'}
missing = sorted(c for c in used - css_classes if c not in skip and not c.startswith(('student.', 'motion.', 'resolution.', 'vote.', 'auth.')))

print('classes usadas:', len(used), '| definidas:', len(css_classes))
if missing:
    print('ÓRFÃS (%d):' % len(missing))
    print('  ' + '\n  '.join(missing))
    sys.exit(1)
print('OK — nenhuma classe órfã')
