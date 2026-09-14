from flask import render_template, redirect, url_for, flash, send_file
from flask_login import login_required
from routes.admin._helpers import admin_bp, moderator_required, admin_required
from models.delegation import Delegation
from models.participation import ParticipationHistory
from extensions import db
import os
from datetime import datetime, timezone


@admin_bp.route('/dpos')
@login_required
@moderator_required
def dpos_list():
    """Lista todos os DPOs enviados pelos delegados."""
    dpos = Delegation.query.filter(Delegation.dpo_uploaded == True)\
        .order_by(Delegation.id.desc()).all()
    return render_template('admin/dpos_list.html', dpos=dpos)


@admin_bp.route('/dpos/<int:id>/download')
@login_required
@moderator_required
def dpo_download(id):
    """Faz o download do arquivo DPO."""
    deleg = Delegation.query.get_or_404(id)
    if not deleg.dpo_path or not os.path.isfile(deleg.dpo_path):
        flash('Arquivo DPO não encontrado no servidor.', 'error')
        return redirect(url_for('admin.dpos_list'))

    return send_file(
        deleg.dpo_path,
        as_attachment=True,
        download_name=os.path.basename(deleg.dpo_path)
    )


@admin_bp.route('/dpos/<int:id>/deletar', methods=['POST'])
@login_required
@admin_required
def dpo_delete(id):
    """Exclui o DPO de uma delegação."""
    deleg = Delegation.query.get_or_404(id)
    if deleg.dpo_path and os.path.isfile(deleg.dpo_path):
        try:
            os.remove(deleg.dpo_path)
        except OSError:
            pass
    deleg.dpo_path = None
    deleg.dpo_uploaded = False
    deleg.accepted = False
    year = deleg.edition_year or datetime.now(timezone.utc).year
    for s in deleg.students:
        ph = ParticipationHistory.query.filter_by(
            student_id=s.id, year=year
        ).first()
        if ph:
            ph.dpo_path = None
            ph.dpo_uploaded = False
    db.session.commit()
    flash(f'DPO de {deleg.country or "delegação"} excluído com sucesso.', 'success')
    return redirect(url_for('admin.dpos_list'))
