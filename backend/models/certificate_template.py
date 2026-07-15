from extensions import db
from datetime import datetime, timezone
import json, os


class CertificateTemplate(db.Model):
    __tablename__ = 'certificate_templates'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    html_content = db.Column(db.Text, nullable=True)
    pdf_path    = db.Column(db.String(300), nullable=True)
    fields_json = db.Column(db.Text, nullable=True)
    is_active   = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    PLACEHOLDER_MAP = {
        'student_name':      'Nome do Aluno',
        'country':           'País',
        'country_flag':      'Bandeira (emoji)',
        'committee':         'Comitê',
        'theme':             'Tema',
        'edition_year':      'Ano da Edição',
        'date':              'Data atual',
        'global_id':         'ID Global',
        'certificate_hash':  'Hash do Certificado',
        'digital_signature': 'Assinatura Digital',
    }

    @classmethod
    def get_active(cls):
        return cls.query.filter_by(is_active=True).first()

    @property
    def fields(self):
        if not self.fields_json:
            return []
        try:
            return json.loads(self.fields_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @fields.setter
    def fields(self, value):
        self.fields_json = json.dumps(value, ensure_ascii=False)

    def get_field_value(self, key, student):
        from flask import url_for
        deleg = student.delegation
        mapping = {
            'student_name':      student.name or '',
            'country':           deleg.country if deleg else '',
            'country_flag':      deleg.country_flag if deleg else '',
            'committee':         (deleg.committee or '').upper() if deleg else '',
            'theme':             deleg.theme.name if deleg and deleg.theme else (deleg.committee or ''),
            'edition_year':      str(deleg.edition_year) if deleg and deleg.edition_year else '',
            'date':              datetime.now(timezone.utc).strftime('%d/%m/%Y'),
            'global_id':         student.global_id or '',
            'certificate_hash':  student.certificate_hash or '',
            'digital_signature': student.digital_signature or '',
        }
        return mapping.get(key, '')

    def render_pdf(self, student, output_path):
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.colors import HexColor
        import io

        if not self.pdf_path or not os.path.isfile(self.pdf_path):
            return False

        reader = PdfReader(self.pdf_path)
        page = reader.pages[0]
        pw, ph = float(page.mediabox.width), float(page.mediabox.height)

        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(pw, ph))

        for field in (self.fields or []):
            key = field.get('key', '')
            value = self.get_field_value(key, student)
            if not value:
                continue

            x = float(field.get('x', 0))
            y = float(field.get('y', 0))
            font_size = float(field.get('font_size', 12))
            font = field.get('font', 'Helvetica')
            align = field.get('align', 'left')
            color_hex = field.get('color', '#000000')

            try:
                c.setFillColor(HexColor(color_hex))
            except:
                c.setFillColor(HexColor('#000000'))
            c.setFont(font, font_size)

            if align == 'center':
                c.drawCentredString(x, y, value)
            elif align == 'right':
                c.drawRightString(x, y, value)
            else:
                c.drawString(x, y, value)

        c.save()
        packet.seek(0)

        overlay = PdfReader(packet)
        page.merge_page(overlay.pages[0])

        writer = PdfWriter()
        writer.add_page(page)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            writer.write(f)
        return True

    def __repr__(self):
        return f'<CertificateTemplate {self.name}>'