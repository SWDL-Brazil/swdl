from extensions import db
from datetime import datetime, timezone


class CertificateTemplate(db.Model):
    __tablename__ = 'certificate_templates'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    is_active   = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    PLACEHOLDERS = [
        ('{{student_name}}', 'Nome do Aluno'),
        ('{{country}}', 'País'),
        ('{{country_flag}}', 'Bandeira (emoji)'),
        ('{{committee}}', 'Comitê'),
        ('{{theme}}', 'Tema'),
        ('{{edition_year}}', 'Ano da Edição'),
        ('{{date}}', 'Data atual'),
        ('{{global_id}}', 'ID Global'),
        ('{{certificate_hash}}', 'Hash do Certificado'),
        ('{{digital_signature}}', 'Assinatura Digital'),
    ]

    @classmethod
    def get_active(cls):
        return cls.query.filter_by(is_active=True).first()

    @classmethod
    def default_html(cls):
        return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @page { size: landscape; margin: 0; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body {
    font-family: 'Georgia', serif;
    width: 297mm; height: 210mm;
    display: flex; align-items: center; justify-content: center;
    background: #f5f0e8;
  }
  .cert {
    width: 270mm; height: 185mm;
    background: #fff;
    border: 3px solid #C9A84C;
    border-radius: 8px;
    padding: 40px;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 20px rgba(0,0,0,.08);
  }
  .cert::before {
    content: ''; position: absolute; inset: 8px;
    border: 1px solid rgba(201,168,76,.3);
    border-radius: 4px; pointer-events: none;
  }
  .cert-badge {
    font-size: 10px; letter-spacing: .2em; text-transform: uppercase;
    color: #C9A84C; margin-bottom: 24px;
  }
  .cert-title {
    font-size: 28px; font-weight: 700; color: #101E4C; margin-bottom: 6px;
  }
  .cert-sub {
    font-size: 14px; color: #6B6F85; margin-bottom: 32px;
  }
  .cert-name {
    font-size: 36px; font-weight: 700; color: #C9A84C; margin-bottom: 4px;
  }
  .cert-label {
    font-size: 12px; color: #6B6F85; margin-bottom: 28px;
    letter-spacing: .1em; text-transform: uppercase;
  }
  .cert-details {
    display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;
    max-width: 600px; margin: 0 auto 28px;
  }
  .cert-detail-label {
    font-size: 9px; letter-spacing: .12em; text-transform: uppercase;
    color: #6B6F85; margin-bottom: 4px;
  }
  .cert-detail-value {
    font-size: 14px; font-weight: 600; color: #101E4C;
  }
  .cert-footer {
    font-size: 10px; color: #6B6F85; margin-top: 20px;
  }
  .cert-seal {
    position: absolute; bottom: 32px; right: 40px;
    width: 60px; height: 60px; border-radius: 50%;
    border: 2px solid #C9A84C; display: flex;
    align-items: center; justify-content: center;
    font-size: 20px; color: #C9A84C;
  }
</style>
</head>
<body>
<div class="cert">
  <div class="cert-badge">SESI World Diplomacy League</div>
  <div class="cert-title">Certificado de Participação</div>
  <div class="cert-sub">Edição {{edition_year}}</div>
  <div class="cert-name">{{student_name}}</div>
  <div class="cert-label">Participante</div>
  <div class="cert-details">
    <div>
      <div class="cert-detail-label">País</div>
      <div class="cert-detail-value">{{country_flag}} {{country}}</div>
    </div>
    <div>
      <div class="cert-detail-label">Comitê / Tema</div>
      <div class="cert-detail-value">{{theme}}</div>
    </div>
    <div>
      <div class="cert-detail-label">Data</div>
      <div class="cert-detail-value">{{date}}</div>
    </div>
  </div>
  <div class="cert-footer">
    Hash: {{certificate_hash}}<br>
    Este certificado é digitalmente verificável.
  </div>
  <div class="cert-seal">SW</div>
</div>
</body>
</html>'''

    def render(self, student):
        from flask import url_for
        deleg = student.delegation
        html = self.html_content
        html = html.replace('{{student_name}}', student.name or '')
        html = html.replace('{{country}}', deleg.country if deleg else '')
        html = html.replace('{{country_flag}}', deleg.country_flag if deleg else '')
        html = html.replace('{{committee}}', (deleg.committee or '').upper() if deleg else '')
        html = html.replace('{{theme}}', deleg.theme.name if deleg and deleg.theme else (deleg.committee or ''))
        html = html.replace('{{edition_year}}', str(deleg.edition_year) if deleg and deleg.edition_year else '')
        html = html.replace('{{date}}', datetime.now(timezone.utc).strftime('%d/%m/%Y'))
        html = html.replace('{{global_id}}', student.global_id or '')
        html = html.replace('{{certificate_hash}}', student.certificate_hash or '')
        html = html.replace('{{digital_signature}}', student.digital_signature or '')
        return html

    def __repr__(self):
        return f'<CertificateTemplate {self.name}>'
