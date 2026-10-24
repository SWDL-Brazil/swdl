"""Armazenamento dos PDFs de certificado.

Centraliza caminho/validacao/salvamento para que admin e rota publica
usem o mesmo diretorio e a mesma protecao contra path traversal.

O diretorio vem de ``Config.CERTIFICATES_DIR`` (sobrescrevivel por
``app.config['CERTIFICATES_DIR']`` nos testes) e pode ser redirecionado
para um disco persistente com a env ``CERTIFICATES_DIR``.
"""
import os
import re

from flask import current_app

from config import Config

# Nomes gravados sao <CODE>.pdf; whitelist fechada tambem corta ':' do
# Windows (alternate data streams), espacos e qualquer separador.
_SAFE_NAME = re.compile(r'^[A-Za-z0-9._-]+$')


def cert_dir():
    """Diretorio absoluto onde os PDFs moram."""
    try:
        path = current_app.config.get('CERTIFICATES_DIR')
    except RuntimeError:
        path = None
    return path or Config.CERTIFICATES_DIR


def cert_path(filename):
    """Caminho absoluto de um PDF, ou None se o nome for inseguro/fora do dir."""
    if not filename or not _SAFE_NAME.match(filename) or '..' in filename:
        return None
    root = os.path.realpath(cert_dir())
    full = os.path.realpath(os.path.join(root, filename))
    if not full.startswith(root + os.sep):
        return None
    return full


def is_pdf(file_storage):
    """Checa magic bytes %PDF- (nome terminando em .pdf nao basta)."""
    if not file_storage or not getattr(file_storage, 'filename', None):
        return False
    if not file_storage.filename.lower().endswith('.pdf'):
        return False
    try:
        head = file_storage.stream.read(5)
        file_storage.stream.seek(0)
    except Exception:
        return False
    return head == b'%PDF-'


def save_cert_pdf(verification_code, file_storage):
    """Grava o PDF como <CODE>.pdf e devolve o nome salvo."""
    filename = f'{verification_code}.pdf'
    if not _SAFE_NAME.match(filename):
        raise ValueError(f'nome de arquivo de certificado invalido: {filename!r}')
    directory = cert_dir()
    os.makedirs(directory, exist_ok=True)
    file_storage.save(os.path.join(directory, filename))
    return filename


def delete_cert_pdf(filename):
    """Remove o PDF se existir; silencioso se ja nao estiver la."""
    filepath = cert_path(filename)
    if not filepath or not os.path.isfile(filepath):
        return False
    try:
        os.remove(filepath)
        return True
    except OSError:
        return False
