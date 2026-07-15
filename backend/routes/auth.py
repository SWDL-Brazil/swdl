# =============================================================
#  SWDL — routes/auth.py
# =============================================================
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import login_manager

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── LOGIN ──────────────────────────────────────────────────────
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.is_director():
                return redirect(url_for('admin.director_dashboard'))
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'E-mail ou senha incorretos.'

    return render_template('admin/login.html', error=error)


# ── LOGOUT ─────────────────────────────────────────────────────
@auth_bp.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ── LOGIN ALUNO ─────────────────────────────────────────────────
@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        flash('Você está logado como administrador. Faça logout para acessar como aluno.', 'warning')

    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email, role='student').first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            return redirect(url_for('student.dashboard'))
        else:
            error = 'E-mail ou senha incorretos.'

    return render_template('student/login.html', error=error)


@auth_bp.route('/student/logout')
@login_required
def student_logout():
    logout_user()
    return redirect(url_for('auth.student_login'))