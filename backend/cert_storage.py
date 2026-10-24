"""Payload dos PDFs de certificado — guardados NO BANCO, nao em arquivo.

Motivo: o Render free nao tem disco persistente (disco e recurso pago) e o
filesystem do container some a cada deploy. O banco e o unico lugar que
sobrevive sem custo, entao o PDF vive em ``Certificate.pdf_data``
(bytea/BLOB) e nao em ``static/`` — onde qualquer um baixaria direto e que
tambem e efemero.

Limite de 4 MB por certificado: protege o banco (texto/capa de certificado
tipico fica na casa de centenas de KB).
"""
import io

from flask import send_file

MAX_PDF_BYTES = 4 * 1024 * 1024


def validate_pdf(file_storage):
    """Le e valida o upload; devolve os bytes ou levanta ValueError.

    ValueError carrying a mensagem pronta para flash() no admin.
    """
    if not file_storage or not getattr(file_storage, 'filename', None):
        raise ValueError('Nenhum arquivo selecionado.')
    if not file_storage.filename.lower().endswith('.pdf'):
        raise ValueError('Apenas arquivos PDF sao permitidos.')

    stream = file_storage.stream
    data = stream.read(MAX_PDF_BYTES + 1)
    try:
        stream.seek(0)
    except Exception:
        pass

    if len(data) > MAX_PDF_BYTES:
        raise ValueError('PDF acima de 4 MB — comprima antes de enviar.')
    if not data.startswith(b'%PDF-'):
        raise ValueError('Arquivo nao parece um PDF valido.')
    return data


def pdf_response(data, filename):
    """Serve os bytes do PDF direto da memoria."""
    return send_file(io.BytesIO(data), mimetype='application/pdf',
                     download_name=filename, as_attachment=False)
