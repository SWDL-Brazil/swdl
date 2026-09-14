from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from routes.admin._helpers import admin_bp, admin_required, _ensure_participation_history
from models.delegation import Delegation
from models.theme import Theme
from models.inscription import Inscription
from models.student import Student
from extensions import db
from datetime import datetime, timezone


@admin_bp.route('/convocar')
@login_required
@admin_required
def convocar_page():
    """Lista alunos prontos para serem convocados à simulação."""
    students = Student.query.order_by(Student.created_at.desc()).all()
    themes = Theme.query.all()
    return render_template('admin/convocar.html', students=students, themes=themes)


@admin_bp.route('/convocar/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def convocar_toggle(id):
    """Alterna o status de convocação de um aluno."""
    student = Student.query.get_or_404(id)
    student.convened = not student.convened
    db.session.commit()
    status = 'convocado' if student.convened else 'desconvocado'
    flash(f'{student.name} {status} com sucesso!', 'success')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/<int:id>/tema', methods=['POST'])
@login_required
@admin_required
def convocar_set_theme(id):
    """Define o tema/debate ao qual o aluno será convocado."""
    student = Student.query.get_or_404(id)
    theme_id = request.form.get('theme_id', type=int)
    theme = Theme.query.get(theme_id) if theme_id else None

    if student.delegation:
        student.delegation.theme_id = theme.id if theme else None
        student.delegation.edition_year = datetime.now(timezone.utc).year
    else:
        ins = Inscription.query.filter_by(email=student.email, status='approved').first()
        if not ins:
            ins = Inscription(
                name=student.name,
                email=student.email,
                phone='',
                grade='',
                motivation='',
                interests='',
                type='delegate',
                status='approved',
                reviewed_at=datetime.now(timezone.utc),
            )
            db.session.add(ins)
            db.session.flush()

        delegation = Delegation(
            inscription_id=ins.id,
            user_id=student.user_id,
            committee=theme.name if theme else None,
            theme_id=theme.id if theme else None,
            edition_year=datetime.now(timezone.utc).year
        )
        db.session.add(delegation)
        db.session.flush()
        student.delegation_id = delegation.id

    student.convened = True

    _ensure_participation_history(student)

    db.session.commit()
    flash(f'{student.name} convocado para {theme.name if theme else "nenhum tema"}!', 'success')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/todos', methods=['POST'])
@login_required
@admin_required
def convocar_all():
    """Convoca todos os alunos pendentes."""
    students = Student.query.filter_by(convened=False).all()
    for s in students:
        s.convened = True
        _ensure_participation_history(s)
    db.session.commit()
    flash(f'📢 {len(students)} alunos convocados!', 'success')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/desconvocar-todos', methods=['POST'])
@login_required
@admin_required
def convocar_uncall_all():
    """Remove convocação de todos os alunos."""
    Student.query.update({Student.convened: False})
    db.session.commit()
    flash('🔕 Todos os alunos foram desconvocados.', 'info')
    return redirect(url_for('admin.convocar_page'))


@admin_bp.route('/convocar/por-tema/<int:theme_id>', methods=['POST'])
@login_required
@admin_required
def convocar_by_theme(theme_id):
    """Convoca todos os alunos de um tema específico que ainda não foram convocados."""
    theme = Theme.query.get_or_404(theme_id)
    delegation_ids = db.session.query(Delegation.id).filter(Delegation.theme_id == theme_id)
    students = Student.query.filter(
        Student.convened == False,
        Student.delegation_id.in_(delegation_ids)
    ).all()
    for s in students:
        s.convened = True
        _ensure_participation_history(s)
    db.session.commit()
    flash(f'📢 {len(students)} alunos de "{theme.name}" convocados!', 'success')
    return redirect(url_for('admin.convocar_page'))
