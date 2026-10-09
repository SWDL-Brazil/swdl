# =============================================================
#  SWDL — routes/api.py
#  API JSON consumida pelo front-end estático
# =============================================================
from flask import Blueprint, jsonify, request, render_template, abort, send_file
from models.news         import News
from models.category     import Category
from models.theme        import Theme
from models.agenda       import AgendaItem
from models.vote         import VoteSession
from models.inscription  import Inscription
from models.inscription_member import InscriptionMember
from models.event_config import EventConfig
from models.urgent_alert import UrgentAlert
from models.event_period import EventPeriod
from datetime import datetime, date
import os
import urllib.request, json as _json
from extensions import db, csrf
from datetime import datetime

api_bp = Blueprint('api', __name__)
csrf.exempt(api_bp)


# ── CAPAS DE NOTÍCIA (públicas) ────────────────────────────────
def news_image_url(cover):
    """URL da capa de notícia pronta para frontends em outro domínio.

    No banco o path é relativo (/admin/uploads/news/...), servido pela
    rota admin que exige login. Para o portal (Vercel) e o site estático
    (Firebase) — que rodam em outro domínio — devolvemos a rota pública
    /api/uploads/news/... absoluta; sem isso o browser resolve o path
    contra o domínio atual e dá 404.
    """
    if not cover:
        return ''
    if cover.startswith('/admin/uploads/news/'):
        cover = '/api/uploads/news/' + cover[len('/admin/uploads/news/'):]
    if cover.startswith('/'):
        cover = request.host_url.rstrip('/') + cover
    return cover


@api_bp.route('/uploads/news/<path:filename>')
def api_serve_news_upload(filename):
    """Capas de notícia — público (o portal as exibe sem login).

    /admin/uploads/ continua protegido: serve também coisas sensíveis
    (DPOs, documentos) que não podem ficar anônimas.
    """
    from config import Config
    import mimetypes
    root = os.path.realpath(os.path.join(Config.UPLOAD_FOLDER, 'news'))
    filepath = os.path.realpath(os.path.join(root, filename))
    if not (filepath == root or filepath.startswith(root + os.sep)):
        abort(403)
    if not os.path.isfile(filepath):
        abort(404)
    mime = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
    return send_file(filepath, mimetype=mime)


# ── NOTÍCIAS ───────────────────────────────────────────────────
@api_bp.route('/noticias')
def api_news():
    category_slug = request.args.get('category')
    committee     = request.args.get('committee')
    limit         = int(request.args.get('limit', 20))

    q = News.query.filter_by(published=True)
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            q = q.filter_by(category_id=cat.id)
    if committee:
        q = q.filter_by(committee=committee)
    news = q.order_by(News.created_at.desc()).limit(limit).all()

    return jsonify([{
        'id':        n.id,
        'title':     n.title,
        'slug':      n.slug,
        'body':      n.body,
        'category':  n.category_obj.name if n.category_obj else 'Geral',
        'category_slug': n.category_obj.slug if n.category_obj else 'geral',
        'category_icon': n.category_obj.icon if n.category_obj else '',
        'committee': n.committee,
        'is_crisis': n.is_crisis,
        'image_url': news_image_url(n.cover_image),
        'time_ago':  n.time_ago(),
        'created_at': n.created_at.isoformat() if n.created_at else None,
    } for n in news])


# ── DIAGNÓSTICO ───────────────────────────────────────────────
@api_bp.route('/diag')
def api_diag():
    import sqlalchemy as sa
    result = {}
    for table in ['event_config', 'students', 'delegations', 'users']:
        try:
            cols = [c['name'] for c in sa.inspect(db.engine).get_columns(table)]
            result[table] = cols
        except Exception as e:
            result[table] = str(e)
    try:
        from models.event_config import EventConfig
        invoke = EventConfig.get_invoke()
        result['invoke'] = str(invoke)
    except Exception as e:
        result['invoke_error'] = str(e)
    try:
        from models.student import Student
        result['students'] = Student.query.count()
        result['read_only_count'] = Student.query.filter(Student.read_only == True).count()
    except Exception as e:
        result['student_error'] = str(e)
    return jsonify(result)


# ── CATEGORIAS ─────────────────────────────────────────────────
@api_bp.route('/categorias')
def api_categories():
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    return jsonify([c.to_dict() for c in cats])


# ── AGENDA ─────────────────────────────────────────────────────
@api_bp.route('/agenda')
def api_agenda():
    day = request.args.get('day', type=int)
    q   = AgendaItem.query
    if day: q = q.filter_by(day=day)
    items = q.order_by(AgendaItem.day, AgendaItem.order,
                       AgendaItem.start_time).all()
    return jsonify([i.to_dict() for i in items])


@api_bp.route('/agenda/agora')
def api_agenda_now():
    """Retorna a atividade atual e a próxima — card 'Agora' do site."""
    from routes.agenda_utils import get_current_next
    current, next_item = get_current_next()
    return jsonify({
        'current': current.to_dict() if current else None,
        'next':    next_item.to_dict() if next_item else None,
    })


# ── PERÍODOS ───────────────────────────────────────────────────
@api_bp.route('/periods')
def api_periods():
    """Retorna todos os períodos do evento, ordenados por data."""
    periods = EventPeriod.query.order_by(EventPeriod.order, EventPeriod.start_date).all()
    return jsonify([p.to_dict() for p in periods])


# ── INSCRIÇÃO (POST público) ───────────────────────────────────
@api_bp.route('/inscricao', methods=['POST'])
def api_inscricao():
    data = request.get_json(silent=True) or request.form

    required = ('name', 'email', 'phone', 'instagram', 'school', 'grade')
    for field in required:
        if not data.get(field):
            return jsonify({'ok': False, 'error': f'Campo {field} obrigatório.'}), 400

    # Confirmação de termos
    if not data.get('accept_terms'):
        return jsonify({'ok': False, 'error': 'Você precisa aceitar os Termos de Uso e a Política de Privacidade.'}), 400

    # Valida formato
    formato = data.get('formato', 'individual')
    if formato not in ('individual', 'dupla', 'trio'):
        return jsonify({'ok': False, 'error': 'Formato inválido.'}), 400

    # Valida membros
    members_data = data.get('members', [])
    if isinstance(members_data, str):
        import json as _json2
        try:
            members_data = _json2.loads(members_data)
        except Exception:
            members_data = []

    if formato == 'dupla' and len(members_data) != 1:
        return jsonify({'ok': False, 'error': 'Dupla requer exatamente 1 membro adicional.'}), 400
    if formato == 'trio' and len(members_data) != 2:
        return jsonify({'ok': False, 'error': 'Trio requer exatamente 2 membros adicionais.'}), 400
    if formato == 'individual' and members_data:
        return jsonify({'ok': False, 'error': 'Formato individual não aceita membros adicionais.'}), 400

    # Valida membros obrigatórios
    for m in members_data:
        if not m.get('name') or not m.get('email') or not m.get('phone') or not m.get('instagram') or not m.get('school') or not m.get('grade'):
            return jsonify({'ok': False, 'error': 'Todos os membros devem informar nome, email, telefone, Instagram, escola e série.'}), 400

    # Valida emails duplicados
    all_emails = [data['email'].lower().strip()]
    for m in members_data:
        email = m.get('email', '').lower().strip()
        if email:
            all_emails.append(email)
    if len(set(all_emails)) != len(all_emails):
        return jsonify({'ok': False, 'error': 'Emails duplicados entre os membros do grupo.'}), 400

    # Verifica se inscrições estão abertas
    if not EventConfig.get_inscricoes_abertas():
        return jsonify({'ok': False, 'error': 'Inscrições estão fechadas no momento.'}), 403

    ins = Inscription(
        name         = data['name'],
        email        = data['email'],
        phone        = data.get('phone', ''),
        school       = data.get('school', ''),
        grade        = data.get('grade', ''),
        partner_name = data.get('partner_name', ''),
        motivation   = data.get('motivation', ''),
        interests    = data.get('interests', ''),
        type         = data.get('type', 'delegate'),
        instagram    = data.get('instagram', ''),
        formato      = formato,
    )
    db.session.add(ins)
    db.session.flush()

    # Cria membros adicionais (dupla/trio)
    for m in members_data:
        member = InscriptionMember(
            inscription_id = ins.id,
            name   = m.get('name', ''),
            email  = m.get('email', ''),
            grade  = m.get('grade', ''),
            instagram = m.get('instagram', ''),
            phone  = m.get('phone', ''),
            school = m.get('school', ''),
            motivation = m.get('motivation', ''),
            interests  = m.get('interests', ''),
            experience = m.get('experience', ''),
        )
        db.session.add(member)

    db.session.commit()
    return jsonify({'ok': True, 'id': ins.id, 'formato': formato}), 201


# ── STATUS DO EVENTO (crisis banner) ──────────────────────────
@api_bp.route('/status')
def api_status():
    """Retorna o estado global do evento para o front-end."""
    crisis_news = News.query.filter_by(is_crisis=True, published=True)\
                            .order_by(News.created_at.desc()).first()
    return jsonify({
        'crisis_active':  crisis_news is not None,
        'crisis_message': crisis_news.title if crisis_news else None,
    })


# ── CONFIGURAÇÕES PÚBLICAS ─────────────────────────────────────
@api_bp.route('/config')
def api_config():
    """Retorna configurações públicas do sistema."""
    from models.agenda import AgendaItem
    from datetime import datetime, timezone
    items = AgendaItem.query.filter(
        AgendaItem.event_date.isnot(None),
        AgendaItem.start_time.isnot(None)
    ).order_by(AgendaItem.event_date, AgendaItem.start_time).all()
    phase = 'pre'
    if items:
        try:
            now = datetime.now(timezone.utc)
            first = items[0]
            last = items[-1]
            first_dt = datetime.strptime(f"{first.event_date} {first.start_time}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            last_end = last.end_time or '23:59'
            last_dt = datetime.strptime(f"{last.event_date} {last_end}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            if now >= first_dt and now <= last_dt:
                phase = 'during'
            elif now > last_dt:
                phase = 'post'
        except (ValueError, TypeError):
            pass
    return jsonify({
        'inscricoes_abertas': EventConfig.get_inscricoes_abertas(),
        'phase': phase,
    })


# ── BUSCA DE BANDEIRA (proxy para restcountries) ───────────────
@api_bp.route('/bandeira')
def api_flag():
    """Busca URL da bandeira pelo nome do país via flagcdn.com"""
    country = request.args.get('country', '').strip().lower()
    if not country:
        return jsonify({'ok': False, 'error': 'País obrigatório'}), 400

    import urllib.request, json as _json
    try:
        # Busca dicionários de códigos (inglês e português)
        req_en = urllib.request.Request('https://flagcdn.com/en/codes.json', headers={'User-Agent': 'Mozilla/5.0'})
        req_pt = urllib.request.Request('https://flagcdn.com/pt/codes.json', headers={'User-Agent': 'Mozilla/5.0'})
        
        codes_en = _json.loads(urllib.request.urlopen(req_en, timeout=5).read())
        codes_pt = _json.loads(urllib.request.urlopen(req_pt, timeout=5).read())
        
        target_code = None
        target_name = None
        
        # Tenta achar o país em português
        for code, name in codes_pt.items():
            if name.lower() == country:
                target_code = code
                target_name = name
                break
                
        # Se não achar, tenta em inglês
        if not target_code:
            for code, name in codes_en.items():
                if name.lower() == country:
                    target_code = code
                    target_name = name
                    break
                    
        if target_code:
            # Exceção para o Brasil (usar pt-BR ao invés de inglês se buscar "Brazil")
            if target_code == 'br': target_name = 'Brasil'
            
            return jsonify({
                'ok':       True,
                'flag_url': f'https://flagcdn.com/w320/{target_code}.png',
                'name':     target_name,
                'code':     target_code.upper(),
            })
    except Exception as e:
        print(f"[API BANDEIRA ERRO] País: {country} - Erro: {e}")

    return jsonify({'ok': False, 'error': 'País não encontrado'}), 404


# ── COMITÊS (STATUS) ──────────────────────────────────────────
@api_bp.route('/comites')
def api_comites():
    """Status de cada comitê: nome, sessão atual, próxima chamada."""
    from datetime import date

    today = date.today().isoformat()
    themes = Theme.query.order_by(Theme.name).all()
    agora = AgendaItem.query.filter_by(event_date=today).filter(
        AgendaItem.status == 'auto'
    ).order_by(AgendaItem.start_time).all()

    result = []
    for t in themes:
        name = t.name
        agendas = [a for a in agora if a.committee == name]
        now_item = next((a for a in agendas if a.compute_status() == 'now'), None)
        next_item = next((a for a in agendas if a.compute_status() == 'next'), None)

        # Verificar se há votação ativa
        vote_active = VoteSession.query.filter_by(
            committee=name, status='open'
        ).first()

        if vote_active:
            status_label = '🗳️ Votação'
            status_type = 'voting'
        elif now_item:
            status_label = '🎤 Em Debate'
            status_type = 'debate'
        elif next_item:
            status_label = '⏳ Aguardando'
            status_type = 'waiting'
        else:
            status_label = '✅ Encerrado'
            status_type = 'done'

        result.append({
            'id':           t.id,
            'name':         t.name,
            'image':        t.image or '',
            'status_label': status_label,
            'status_type':  status_type,
            'next_time':    next_item.start_time if next_item else (now_item.end_time if now_item else '—'),
            'next_title':   next_item.title if next_item else (now_item.title if now_item else ''),
        })

    return jsonify(result)


# ── TICKER DE ALERTAS ─────────────────────────────────────────
@api_bp.route('/ticker')
def api_ticker():
    """Items do ticker: câmbio, alertas urgentes, crises, votações."""
    items = []

    # 1. Câmbio (AwesomeAPI)
    try:
        req = urllib.request.Request(
            'https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL',
            headers={'User-Agent': 'SWDL/1.0'}
        )
        resp = urllib.request.urlopen(req, timeout=4)
        data = _json.loads(resp.read().decode())
        for key in ('USDBRL', 'EURBRL', 'GBPBRL'):
            if key in data:
                c = data[key]
                var = float(c.get('pctChange', 0))
                arrow = '▲' if var >= 0 else '▼'
                color = 'var(--green)' if var >= 0 else 'var(--red)'
                items.append({
                    'type': 'currency',
                    'html': f'{c["name"].split("/")[0]} <strong>{c["bid"]}</strong> <span style="color:{color}">{arrow} {abs(var):.2f}%</span>',
                    'text': f'{c["name"].split("/")[0]} {c["bid"]} {"▲" if var>=0 else "▼"} {abs(var):.2f}%',
                    'priority': 0,
                })
    except Exception:
        pass

    # 2. Alertas urgentes criados por admins
    urgentes = UrgentAlert.query.filter_by(active=True).order_by(UrgentAlert.created_at.desc()).all()
    for a in urgentes:
        items.append({
            'type': 'urgent',
            'html': f'🚨 <strong style="color:var(--gold)">{a.message}</strong>',
            'text': f'🚨 {a.message}',
            'priority': 10,
        })

    # 3. Crises ativas
    crises = News.query.filter_by(published=True, is_crisis=True).order_by(
        News.created_at.desc()
    ).limit(5).all()
    for n in crises:
        items.append({
            'type': 'crisis',
            'html': f'⚡ {n.title}',
            'text': f'⚡ {n.title}',
            'priority': 5,
        })

    # 4. Votações abertas
    votes = VoteSession.query.filter_by(status='open').all()
    for v in votes:
        items.append({
            'type': 'vote',
            'html': f'🗳️ <strong>{v.title}</strong> ({v.committee})',
            'text': f'🗳️ {v.title} ({v.committee})',
            'priority': 3,
        })

    # 5. Agenda do dia
    from datetime import date
    today = date.today().isoformat()
    proximos = AgendaItem.query.filter(
        AgendaItem.event_date == today
    ).order_by(AgendaItem.start_time).limit(5).all()
    for a in proximos:
        if a.compute_status() in ('now', 'next'):
            items.append({
                'type': 'schedule',
                'html': f'⏰ {a.start_time} — {a.title}',
                'text': f'⏰ {a.start_time} — {a.title}',
                'priority': 1,
            })

    # Ordenar por prioridade (maior primeiro) para os urgentes ficarem em foco
    items.sort(key=lambda x: -x['priority'])
    return jsonify(items[:15])


@api_bp.route('/noticia/<slug>')
def public_news_page(slug):
    """Página pública de uma notícia."""
    news = News.query.filter_by(slug=slug, published=True).first()
    if not news:
        abort(404)

    related = News.query.filter(
        News.published == True,
        News.id != news.id,
    ).order_by(News.created_at.desc()).limit(4).all()

    return render_template('public/news_detail.html', news=news, related=related)


# ── NOTÍCIA (JSON — consumida pelo front Next.js) ──────────────
@api_bp.route('/noticia-json/<slug>')
def api_noticia_json(slug):
    """JSON de uma notícia + relacionadas (para o portal Next.js)."""
    news = News.query.filter_by(slug=slug, published=True).first()
    if not news:
        return jsonify({'error': 'Not found'}), 404

    related = News.query.filter(
        News.published == True,
        News.id != news.id,
    ).order_by(News.created_at.desc()).limit(4).all()

    def mini(n):
        return {
            'id':            n.id,
            'title':         n.title,
            'slug':          n.slug,
            'excerpt':       n.excerpt or '',
            'category':      n.category_obj.name if n.category_obj else 'Geral',
            'category_slug': n.category_obj.slug if n.category_obj else 'geral',
            'category_icon': n.category_obj.icon if n.category_obj else '',
            'committee':     n.committee,
            'is_crisis':     n.is_crisis,
            'image_url':     news_image_url(n.cover_image),
            'time_ago':      n.time_ago(),
            'created_at':    n.created_at.isoformat() if n.created_at else None,
        }

    return jsonify({
        'id':            news.id,
        'title':         news.title,
        'slug':          news.slug,
        'excerpt':       news.excerpt or '',
        'body':          news.body,
        'category':      news.category_obj.name if news.category_obj else 'Geral',
        'category_slug': news.category_obj.slug if news.category_obj else 'geral',
        'category_icon': news.category_obj.icon if news.category_obj else '',
        'committee':     news.committee,
        'tags':          news.tags_list(),
        'is_crisis':     news.is_crisis,
        'image_url':     news_image_url(news.cover_image),
        'time_ago':      news.time_ago(),
        'created_at':    news.created_at.isoformat() if news.created_at else None,
        'author':        news.author.name if news.author else 'SWDL',
        'related':       [mini(r) for r in related],
    })


