from flask import render_template, redirect, url_for, flash, request, current_app, abort, make_response
from flask_login import login_required, current_user
from routes.admin._helpers import admin_bp, admin_required, _log_audit
from models.student import Student
from models.delegation import Delegation
from models.theme import Theme
from models.user import User
from models.certificate import Certificate, CERT_TYPES, generate_verification_code
from cert_storage import validate_pdf, pdf_response
from extensions import db
from sqlalchemy import select, func, case, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import io


def _current_year():
    return datetime.now(timezone.utc).year


def _used_codes(extra_check_student=False):
    """Todos os codigos em uso, em 2 queries (nao 2 por aluno)."""
    codes = {c for (c,) in db.session.query(Certificate.verification_code).all()}
    if extra_check_student:
        codes |= {c for (c,) in db.session.query(Student.verification_code)
                  .filter(Student.verification_code.isnot(None)).all()}
    return codes


def _pick_code(used):
    """Codigo SWDL-XXXXXX unico; registra em ``used`` para o lote corrente."""
    for _ in range(200):
        code = generate_verification_code()
        if code not in used:
            used.add(code)
            return code
    # Inalcancavel na pratica (36^6 espaco); melhor falhar alto do que
    # commitar uma linha com codigo duplicado (IntegrityError sem contexto).
    raise RuntimeError('nao foi possivel gerar codigo de verificacao unico')


def _themes_for_year(year):
    """Temas que possuem delegacoes nesta edicao (para o filtro de tema)."""
    rows = db.session.query(Theme.name).join(
        Delegation, Delegation.theme_id == Theme.id
    ).filter(
        Delegation.edition_year == year
    ).distinct().order_by(Theme.name).all()
    return [r[0] for r in rows if r[0]]


@admin_bp.route('/certificados/arquivo/<filename>')
@login_required
@admin_required
def serve_certificate(filename):
    """Serve o PDF do certificado a partir do banco (rota admin).

    ``filename`` e ``<CODE>.pdf`` — o codigo e a chave, nao um caminho.
    """
    code = filename[:-4] if filename.lower().endswith('.pdf') else filename
    cert = Certificate.query.filter_by(verification_code=code).first()
    if not cert or not cert.released or not cert.has_pdf:
        abort(404)
    return pdf_response(cert.pdf_data, cert.pdf_path or filename)


@admin_bp.route('/certificados')
@login_required
@admin_required
def certificates_list():
    """Gestao de certificados — filtravel por edicao e tipo."""
    from sqlalchemy.orm import joinedload
    from models.audit_log import AuditLog

    year = request.args.get('year', type=int)
    cert_type = request.args.get('type', '')
    committee_name = request.args.get('committee_name', '')

    years = [r[0] for r in db.session.query(Certificate.edition_year)
             .distinct().order_by(Certificate.edition_year.desc())]
    if not year:
        cy = _current_year()
        year = cy if cy in years else (years[0] if years else cy)

    # Ordena pelo SNAPSHOT (student_name): nenhuma juncao com students —
    # o nome exibido e o que foi emitido, nao o cadastro de hoje.
    query = Certificate.query
    if year:
        query = query.filter(Certificate.edition_year == year)
    if cert_type and cert_type in CERT_TYPES:
        query = query.filter(Certificate.type == cert_type)
    if committee_name:
        query = query.filter(Certificate.committee_name == committee_name)

    certs = query.order_by(Certificate.type,
                           func.coalesce(Certificate.student_name,
                                         Certificate.name, '').asc()).all()

    # Stats cobrem a edição inteira (ignoram o filtro de tipo da tabela)
    if cert_type and cert_type in CERT_TYPES:
        all_for_year = Certificate.query.filter_by(edition_year=year).all()
    else:
        all_for_year = certs

    # "Sem participacao" = alunos DA EDICAO (delegacao.edition_year == ano)
    # sem certificado de participacao naquele ano — 1 query, nao carrega
    # todos os alunos do banco (com varias edicoes o numero era mentira).
    part_ids = select(Certificate.student_id).where(
        Certificate.edition_year == year,
        Certificate.type == 'participation')
    edition_total, missing = db.session.execute(
        select(func.count(Student.id),
               func.coalesce(func.sum(case((Student.id.notin_(part_ids), 1),
                                           else_=0)), 0))
        .select_from(Student)
        .join(Delegation, Student.delegation_id == Delegation.id)
        .where(Delegation.edition_year == year)
    ).one()

    stats = {
        'total': len(all_for_year),
        'participation': sum(1 for c in all_for_year if c.type == 'participation'),
        'awards': sum(1 for c in all_for_year if c.type != 'participation'),
        'with_pdf': sum(1 for c in all_for_year if c.has_pdf),
        'released': sum(1 for c in all_for_year if c.released),
        'edition_students': edition_total,
        'missing_participation': missing,
    }

    students = Student.query.options(joinedload(Student.delegation))\
                            .order_by(Student.name).all()
    delegations = Delegation.query.options(joinedload(Delegation.students))\
                                   .order_by(Delegation.country).all()
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()
    themes = _themes_for_year(year)
    users = User.query.order_by(User.name).all()

    return render_template('admin/certificates_list.html',
                           certs=certs,
                           years=years,
                           current_year=year,
                           current_type=cert_type,
                           current_committee=committee_name,
                           cert_types=CERT_TYPES,
                           themes=themes,
                           stats=stats,
                           students=students,
                           delegations=delegations,
                           users=users,
                           audit_logs=audit_logs)


@admin_bp.route('/certificados/gerar-codigos', methods=['POST'])
@login_required
@admin_required
def certificates_generate_codes():
    """Cria certificados de participacao (com codigo) sem gate de presenca.

    Com ``student_id`` no form, gera apenas para esse aluno.
    """
    year = request.form.get('year', type=int) or _current_year()
    student_id = request.form.get('student_id', type=int)

    # selectinload: delegacao + tema numa query extra (sem N+1 — no ReG
    # cada query custa ~180ms e uma edicao tem 100+ alunos).
    query = Student.query.options(
        selectinload(Student.delegation).selectinload(Delegation.theme))
    if student_id:
        query = query.filter(Student.id == student_id)
    students = query.all()

    existing = {c for (c,) in db.session.query(Certificate.student_id)
                .filter(Certificate.edition_year == year,
                        Certificate.type == 'participation').all()}
    used = _used_codes(extra_check_student=True)

    count = 0
    for s in students:
        if s.id in existing:
            continue
        cert = Certificate(student=s, edition_year=year,
                           type='participation',
                           verification_code=_pick_code(used))
        cert.fill_snapshot()
        db.session.add(cert)
        count += 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo ou certificado duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    if student_id:
        _log_audit('generate_codes', 'student', student_id, details=f'{count} codigo gerado ({year})')
    else:
        _log_audit('generate_codes', 'system', 0, details=f'{count} codigos gerados ({year})')
    flash(f'{count} certificados de participacao gerados para {year}!', 'success')
    return redirect(url_for('admin.certificates_list', year=year))


@admin_bp.route('/certificados/premiar', methods=['POST'])
@login_required
@admin_required
def certificate_award():
    """Cria certificado(s) de premiacao (melhor delegacao/orador/vestimenta)."""
    student_id = request.form.get('student_id', type=int)
    delegation_id = request.form.get('delegation_id', type=int)
    cert_type = request.form.get('type', '')
    year = request.form.get('year', type=int) or _current_year()
    notes = request.form.get('notes', '').strip() or None

    if cert_type not in CERT_TYPES or cert_type == 'participation':
        flash('Tipo de premiacao invalido.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    targets = []
    if cert_type == 'best_delegation' and delegation_id:
        # traz alunos + delegacao + tema de uma vez (evita N+1 no lote)
        deleg = Delegation.query.options(
            selectinload(Delegation.students)
            .selectinload(Student.delegation)
            .selectinload(Delegation.theme)
        ).get_or_404(delegation_id)
        targets = list(deleg.students)
        if not targets:
            flash('Delegacao sem alunos vinculados.', 'error')
            return redirect(url_for('admin.certificates_list', year=year))
    elif student_id:
        targets = [Student.query.options(
            selectinload(Student.delegation).selectinload(Delegation.theme)
        ).get_or_404(student_id)]
    else:
        flash('Selecione um aluno (ou uma delegacao para "Melhor Delegacao").', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    existing = {sid for (sid,) in db.session.query(Certificate.student_id)
                .filter(Certificate.edition_year == year,
                        Certificate.type == cert_type).all()}
    used = _used_codes()

    count = 0
    skipped = 0
    for s in targets:
        if s.id in existing:
            skipped += 1
            continue
        cert = Certificate(student=s, edition_year=year, type=cert_type,
                           verification_code=_pick_code(used), notes=notes)
        cert.fill_snapshot()
        db.session.add(cert)
        existing.add(s.id)
        count += 1
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo ou certificado duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    _log_audit('award_certificate', 'system', 0,
               details=f'{count}x {CERT_TYPES[cert_type]} ({year})')
    msg = f'{count} certificado(s) de "{CERT_TYPES[cert_type]}" criado(s)!'
    if skipped:
        msg += f' {skipped} ja existiam e foram ignorados.'
    flash(msg + ' Faca o upload do PDF para liberar.', 'success')
    return redirect(url_for('admin.certificates_list', year=year, type=cert_type))


@admin_bp.route('/certificados/<int:id>/upload', methods=['POST'])
@login_required
@admin_required
def certificate_upload(id):
    """Upload do PDF de um certificado — libera e assina (HMAC)."""
    cert = Certificate.query.get_or_404(id)

    file = request.files.get('cert_file')
    try:
        data = validate_pdf(file)
    except ValueError as exc:
        flash(str(exc), 'error')
        return redirect(url_for('admin.certificates_list', year=cert.edition_year))

    cert.pdf_data = data
    cert.pdf_path = f'{cert.verification_code}.pdf'
    cert.released = True
    # Snapshot de novo no momento da liberacao: e o nome/pais/comitie que
    # entram na assinatura, e tem que casar com o PDF que o admin acabou de
    # subir (pode ter havido correcao de cadastro desde a geracao do codigo).
    cert.fill_snapshot()
    secret = current_app.config.get('SECRET_KEY', 'swdl-secret')
    cert.digital_signature = cert.compute_signature(secret)
    cert.signed_at = datetime.now(timezone.utc)
    db.session.commit()

    student_name = cert.display_name
    _log_audit('upload_certificate', 'certificate', cert.id, student_name,
               details=f'PDF salvo: {cert.pdf_path} ({cert.type_label} {cert.edition_year})')
    flash(f'PDF de {student_name} ({cert.type_label}) enviado e liberado!', 'success')
    return redirect(url_for('admin.certificates_list', year=cert.edition_year))


@admin_bp.route('/certificados/<int:id>/remover-pdf', methods=['POST'])
@login_required
@admin_required
def certificate_remove_pdf(id):
    """Apaga o PDF e revoga a liberacao (o codigo permanece)."""
    cert = Certificate.query.get_or_404(id)

    cert.pdf_data = None
    cert.pdf_path = None
    cert.released = False
    cert.digital_signature = None
    cert.signed_at = None
    db.session.commit()

    student_name = cert.display_name
    _log_audit('remove_certificate_pdf', 'certificate', cert.id, student_name,
               details=f'{cert.type_label} {cert.edition_year}')
    flash(f'PDF de {student_name} ({cert.type_label}) removido.', 'info')
    return redirect(url_for('admin.certificates_list', year=cert.edition_year))


@admin_bp.route('/certificados/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def certificate_delete(id):
    """Exclui um certificado (linha — o PDF mora na mesma linha)."""
    cert = Certificate.query.get_or_404(id)

    student_name = cert.display_name
    details = f'{cert.type_label} {cert.edition_year} [{cert.verification_code}]'
    db.session.delete(cert)
    db.session.commit()

    _log_audit('delete_certificate', 'certificate', id, student_name, details=details)
    flash(f'Certificado de {student_name} ({details}) excluido.', 'info')
    return redirect(url_for('admin.certificates_list'))


# ════════════════════════════════════════════════════════════════════
#  CERTIFICADOS — pessoas externas / organizadores (sem aluno vinculado)
# ════════════════════════════════════════════════════════════════════

@admin_bp.route('/certificados/gerar-externo', methods=['POST'])
@login_required
@admin_required
def certificate_generate_external():
    """Gera certificado para pessoa externa (sem cadastro de aluno).

    Usado para o iniciativa "SWDL com Portas Abertas" — convidados de fora
    da simulacao que recebem um certificado com nome livre, tema/comite e
    tipo selecionado pelo admin.
    """
    year = request.form.get('year', type=int) or _current_year()
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip() or None
    committee = (request.form.get('committee') or '').strip() or None
    committee_name = (request.form.get('committee_name') or '').strip() or None
    country = (request.form.get('country') or '').strip() or None
    country_flag = (request.form.get('country_flag') or '').strip() or None
    cert_type = request.form.get('type', '')
    notes = (request.form.get('notes') or '').strip() or None

    if cert_type not in CERT_TYPES or cert_type == 'participation':
        flash('Tipo de certificado invalido para emissao externa.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))
    if not name:
        flash('Informe o nome da pessoa.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    used = _used_codes()
    cert = Certificate(
        student_id=None,
        edition_year=year,
        type=cert_type,
        name=name,
        email=email,
        verification_code=_pick_code(used),
        notes=notes,
    )
    cert.fill_snapshot(
        name=name, country=country, country_flag=country_flag,
        committee=committee, committee_name=committee_name,
    )
    db.session.add(cert)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    _log_audit('generate_external_certificate', 'certificate', cert.id, name,
               details=f'{cert_type} ({year})')
    flash(f'Certificado externo criado para {name}! '
          f'Faca o upload do PDF para liberar.', 'success')
    return redirect(url_for('admin.certificates_list',
                            year=year, type=cert_type))


@admin_bp.route('/certificados/gerar-organizador', methods=['POST'])
@login_required
@admin_required
def certificate_generate_organizer():
    """Gera certificado de Organizador.

    Pode ser para um usuario do sistema (admin/diretor/moderador) vinculado
    a um comite, ou para um nome livre com comite informado.
    """
    year = request.form.get('year', type=int) or _current_year()
    user_id = request.form.get('user_id', type=int)
    name = (request.form.get('name') or '').strip()
    email = (request.form.get('email') or '').strip() or None
    committee = (request.form.get('committee') or '').strip() or None
    committee_name = (request.form.get('committee_name') or '').strip() or None
    country = (request.form.get('country') or '').strip() or None
    country_flag = (request.form.get('country_flag') or '').strip() or None
    notes = (request.form.get('notes') or '').strip() or None

    cert_type = 'organizer'

    # Resolve nome/email a partir do usuario, se informado.
    user = None
    if user_id:
        user = db.session.get(User, user_id)
        if not user:
            flash('Usuario selecionado nao encontrado.', 'error')
            return redirect(url_for('admin.certificates_list', year=year))
        name = name or user.name
        email = email or user.email

    if not name:
        flash('Informe o nome do organizador.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    used = _used_codes()
    cert = Certificate(
        student_id=None,
        edition_year=year,
        type=cert_type,
        name=name,
        email=email,
        awarded_by=current_user.id if current_user.is_authenticated else None,
        verification_code=_pick_code(used),
        notes=notes,
    )
    cert.fill_snapshot(
        name=name, country=country, country_flag=country_flag,
        committee=committee, committee_name=committee_name,
    )
    db.session.add(cert)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Conflito: codigo duplicado. Tente novamente.', 'error')
        return redirect(url_for('admin.certificates_list', year=year))

    _log_audit('generate_organizer_certificate', 'certificate', cert.id, name,
               details=f'organizador ({year})')
    flash(f'Certificado de Organizador criado para {name}! '
          f'Faca o upload do PDF para liberar.', 'success')
    return redirect(url_for('admin.certificates_list',
                            year=year, type='organizer'))


# ════════════════════════════════════════════════════════════════════
#  CERTIFICADOS — PDF personalizado com os codigos de verificacao
# ════════════════════════════════════════════════════════════════════

def _pdf_escape(text):
    """Escapa texto para insercao em string de conteudo PDF."""
    if text is None:
        return ''
    return str(text).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _pdf_text(text, x, y, font_size=8, fill='0.05 0.20 0.16'):
    """Gera operadores PDF para desenhar uma linha de texto."""
    ops = []
    ops.append('BT')
    ops.append(f'/F1 {font_size} Tf')
    ops.append(f'{fill} rg')
    ops.append(f'{x} {y} Td')
    ops.append(f'({_pdf_escape(text)}) Tj')
    ops.append('ET')
    return ops


def _draw_header(ops, page_num, year, filters_desc):
    """Desenha cabecalho com logo SWDL em uma pagina."""
    from datetime import datetime as _dt

    now_str = _dt.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')

    # ── Logo SWDL: retangulo navy com texto ouro ────────────────────
    ops.append('0.05 0.20 0.16 rg')      # cor navy (fill)
    ops.append('40 750 140 24 re f')     # retangulo preenchido (logo base)
    ops.append('0.79 0.66 0.30 rg')      # cor ouro (fill)
    ops.append('BT')
    ops.append('/F1 17 Tf')
    ops.append('50 756 Td')
    ops.append('(SWDL) Tj')
    ops.append('ET')

    ops.append('BT')
    ops.append('/F1 7 Tf')
    ops.append('50 744 Td')
    ops.append('(SESI WORLD DIPLOMACY LEAGUE) Tj')
    ops.append('ET')

    # Linha separadora ouro abaixo do logo
    ops.append('0.79 0.66 0.30 RG')
    ops.append('1.5 w')
    ops.append('40 728 m')
    ops.append('572 728 l')
    ops.append('S')

    # Subtitulo da pagina
    ops.extend(_pdf_text(f'Codigos de Verificacao de Certificados — Edicao {year}', 40, 708, 12))

    y = 694
    if filters_desc:
        ops.extend(_pdf_text(f'Filtros: {filters_desc}', 40, y, 8, '0.4 0.4 0.4'))
        y -= 14

    # ── Cabecalho da tabela ─────────────────────────────────────────
    y -= 8
    ops.extend(_pdf_text(
        'Codigo       Nome                                              Tipo                      Edicao  Tema / Comite                   Status',
        40, y, 8
    ))
    y -= 10
    # linha sob o cabecalho da tabela
    ops.append('0.79 0.66 0.30 RG')
    ops.append('0.5 w')
    ops.append(f'40 {y} m')
    ops.append(f'572 {y} l')
    ops.append('S')
    y -= 14

    return y, now_str


def _draw_footer(ops, page_num, total_pages, now_str):
    """Desenha rodape com linha, numero da pagina e validacao."""
    # Linha separadora
    ops.append('0.79 0.66 0.30 RG')
    ops.append('0.5 w')
    ops.append('40 46 m')
    ops.append('572 46 l')
    ops.append('S')

    ops.extend(_pdf_text(f'Pagina {page_num} de {total_pages}', 40, 34, 7, '0.4 0.4 0.4'))
    ops.extend(_pdf_text(now_str, 400, 34, 7, '0.4 0.4 0.4'))
    ops.extend(_pdf_text(
        'Validacao publica: /certificado/<codigo>  |  /api/certificado/validar?code=<codigo>',
        40, 24, 7, '0.4 0.4 0.4'
    ))


def _build_codes_pdf(certs, year, filters_desc):
    """Gera um PDF valido (apenas stdlib) com cabecario, rodape e logo SWDL.

    Estrutura minima PDF-1.4: catalog -> pages -> page(s) -> font -> content(s).
    Cada pagina tem cabecalho com logo SWDL e rodape com numeracao.
    """
    from datetime import datetime as _dt

    PAGE_WIDTH = 612
    PAGE_HEIGHT = 792
    MARGIN = 40
    ROW_HEIGHT = 13
    HEADER_SPACE = 130
    FOOTER_SPACE = 50
    rows_per_page = max(1, (PAGE_HEIGHT - HEADER_SPACE - FOOTER_SPACE - MARGIN) // ROW_HEIGHT)

    # Agrupa certificados por pagina
    pages = []
    for i in range(0, len(certs), rows_per_page):
        pages.append(certs[i:i + rows_per_page])
    if not pages:
        pages = [[]]

    total_pages = len(pages)
    now_str = _dt.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')

    # Content stream por pagina
    page_streams = []
    for page_idx, page_certs in enumerate(pages, start=1):
        ops = []
        y, _ = _draw_header(ops, page_idx, year, filters_desc)

        # Linhas de dados
        ops.append('BT')
        ops.append('/F1 8 Tf')
        ops.append('0.05 0.20 0.16 rg')
        for c in page_certs:
            if y < 70:
                break
            status = 'Liberado' if c.released else 'Pendente'
            nome = c.display_name or ''
            tema = c.committee_name or c.committee or ''
            linha = (
                f'{c.verification_code:<12} {nome:<46} {c.type_label:<24} '
                f'{c.edition_year:<8} {tema:<26} {status}'
            )
            ops.append(f'40 {y} Td')
            ops.append(f'({_pdf_escape(linha)}) Tj')
            ops.append('ET')
            y -= ROW_HEIGHT
            if y > 70:
                ops.append('BT')
                ops.append('/F1 8 Tf')
                ops.append('0.05 0.20 0.16 rg')

        # Total no final da ultima pagina
        if page_idx == total_pages:
            ops.append('BT')
            ops.append('/F1 9 Tf')
            ops.append('0.05 0.20 0.16 rg')
            ops.append(f'40 {max(y - 6, 70)} Td')
            ops.append(f'({_pdf_escape(f"Total de certificados listados: {len(certs)}")}) Tj')
            ops.append('ET')

        _draw_footer(ops, page_idx, total_pages, now_str)

        page_streams.append('\n'.join(ops).encode('latin-1', 'replace'))

    # Monta objetos PDF
    objs = []

    def obj(content):
        objs.append(content)
        return len(objs)  # numero do objeto (1-based)

    # Conteudos das paginas
    contents_objs = []
    for stream in page_streams:
        contents_objs.append(
            obj(f'<< /Length {len(stream)} >>\nstream\n{stream.decode("latin-1", "replace")}\nendstream\nendobj')
        )

    # Fonte compartilhada
    font_obj = obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')

    # Paginas (referenciam o pages via placeholder, corrigido depois)
    page_objs = []
    for c in contents_objs:
        page_objs.append(
            obj(f'<< /Type /Page /Parent 0 0 R /Resources << /Font << /F1 {font_obj} 0 R >> >> '
                f'/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Contents {c} 0 R >>')
        )

    # Pages com kids corretos
    pages_obj = obj(
        f'<< /Type /Pages /Kids [{" ".join(str(n) + " 0 R" for n in page_objs)}] /Count {len(page_objs)} >>'
    )

    # Corrige /Parent nas paginas para apontar ao pages_obj correto
    for i, p in enumerate(page_objs):
        for j, content in enumerate(objs):
            if j + 1 == p:
                objs[j] = content.replace('/Parent 0 0 R', f'/Parent {pages_obj} 0 R')
                break

    catalog_obj = obj(f'<< /Type /Catalog /Pages {pages_obj} 0 R >>')

    # Escreve PDF
    buf = io.BytesIO()
    buf.write(b'%PDF-1.4\n')
    xref_positions = []
    for i, content in enumerate(objs, start=1):
        xref_positions.append(buf.tell())
        buf.write(f'{i} 0 obj\n{content}\nendobj\n'.encode('latin-1'))
    xref_start = buf.tell()
    xref_count = len(objs) + 1
    buf.write(b'xref\n')
    buf.write(f'0 {xref_count}\n'.encode('ascii'))
    buf.write(b'0000000000 65535 f \n')
    for pos in xref_positions:
        buf.write(f'{pos:010d} 00000 n \n'.encode('ascii'))
    buf.write(b'trailer\n')
    buf.write(f'<< /Size {xref_count} /Root {catalog_obj} 0 R >>\n'.encode('ascii'))
    buf.write(b'startxref\n')
    buf.write(f'{xref_start}\n'.encode('ascii'))
    buf.write(b'%%EOF\n')
    return buf.getvalue()


@admin_bp.route('/certificados/codigos-pdf')
@login_required
@admin_required
def certificates_codes_pdf():
    """Gera um PDF personalizado com a lista de codigos de verificacao.

    Query params: year, type, committee_name (mesmos da listagem).
    """
    year = request.args.get('year', type=int) or _current_year()
    cert_type = request.args.get('type', '')
    committee_name = request.args.get('committee_name', '')

    query = Certificate.query.filter(Certificate.edition_year == year)
    if cert_type and cert_type in CERT_TYPES:
        query = query.filter(Certificate.type == cert_type)
    if committee_name:
        query = query.filter(Certificate.committee_name == committee_name)

    certs = query.order_by(
        Certificate.type,
        func.coalesce(Certificate.student_name, Certificate.name, '').asc()
    ).all()

    filters_parts = []
    if cert_type:
        filters_parts.append(f'tipo={CERT_TYPES[cert_type]}')
    if committee_name:
        filters_parts.append(f'tema={committee_name}')
    filters_desc = ' | '.join(filters_parts) if filters_parts else 'todos'

    pdf_bytes = _build_codes_pdf(certs, year, filters_desc)

    _log_audit('download_codes_pdf', 'system', 0,
               details=f'{len(certs)} codigos — edicao {year} {filters_desc}')

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="codigos_certificados_swdl_{year}.pdf"'
    return response
