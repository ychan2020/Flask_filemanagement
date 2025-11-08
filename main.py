"""
main.py
"""

from io import BytesIO
import datetime
from flask import Blueprint, render_template
from flask import request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from cryptography.fernet import Fernet, MultiFernet
from pyaml_env import parse_config, BaseConfig
import pytz
from .models import Document
from . import db


config = BaseConfig(parse_config('./config/config.yml'))
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Index page"""
    # Generates index page
    return render_template('index.html')


@main.after_request
def apply_caching(response):
    """apply caching"""
    rdh = response.headers
    rdh["X-Frame-Options"] = "SAMEORIGIN"
    rdh["X-Content-Type-Options"] = "nosniff"
    rdh["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rdh["Pragma"] = "no-cache"
    rdh["Expires"] = "0"
    rdh['Cache-Control'] = 'public, max-age=0'
    rdh['Strict-Transport-Security'] = 'max-age=3600; includeSubDomains'
    rdh['Content-Security-Policy'] = "default-src 'none'; " \
                                     "style-src https://cdnjs.cloudflare.com/; " \
                                     "frame-ancestors 'none'; " \
                                     "script-src 'self'; " \
                                     "script-src-elem 'self'; " \
                                     "script-src-attr 'self'; " \
                                     "style-src-elem " \
                                     "https://cdnjs.cloudflare.com/; " \
                                     "style-src-attr 'self'; img-src " \
                                     "'self'; connect-src 'self'; " \
                                     "frame-src 'self'; " \
                                     "font-src 'self'; " \
                                     "media-src 'self'; " \
                                     "object-src 'self'; " \
                                     "manifest-src 'self'; " \
                                     "worker-src 'self'; " \
                                     "prefetch-src 'self'; " \
                                     "form-action 'self' "
    rdh['X-XSS-Protection'] = '1; mode=block'
    return response


@main.route('/profile')
@login_required
def profile():
    """User profile page (login required)"""
    # Generates user profile page following authenticated login
    return render_template('profile.html', name=current_user.name)


@main.route('/upload')
@login_required
def upload():
    """Upload page (login required)"""
    # Generates file upload page
    return render_template('upload.html')


@main.route('/upload', methods=['POST'])
def upload_post():
    """Upload File"""
    # Fernet encryption key generated for uploaded file
    file = request.files['file']
    role = request.form.get('role')
    timestamp = datetime.datetime.now(pytz.utc)
    key = Fernet.generate_key()
    file_key = Fernet(key)
    master_key = Fernet(config.file.masterkey)
    cipher_suite = MultiFernet([file_key, master_key])
    encrypted_data = cipher_suite.encrypt(file.read())

    fileupload = Document(filename=file.filename, data=encrypted_data,
                          role=role, key=key, timestamp=timestamp,
                          owner=current_user.email)
    db.session.add(fileupload)
    db.session.commit()
    flash('File Uploaded')
    # Confirmation page of file uploaded
    return render_template('upload.html')


@main.route('/download')
@login_required
def download():
    """Download page (login required),
    display file listing results in a table"""
    documents = Document.query. \
        filter_by(role=current_user.role).order_by(Document.fileid).all()
    # Generated download page following authentication of user
    return render_template('download.html', documents=documents)


@main.route('/download', methods=['POST'])
def download_post():
    """display file listing results in a table"""
    fileid = request.form.get('download_id')
    file = Document.query.filter_by(fileid=fileid). \
        filter_by(role=current_user.role).first()
    if not file:
        flash('Invalid File ID')
        return redirect(url_for('main.download'))
    # Decryption of file in downloading
    key = file.key
    file_key = Fernet(key)
    master_key = Fernet(config.file.masterkey)
    cipher_suite = MultiFernet([file_key, master_key])
    decrypted_data = cipher_suite.decrypt(file.data)
    return send_file(BytesIO(decrypted_data),
                     attachment_filename=file.filename, as_attachment=True)


@main.route('/remove')
@login_required
def remove():
    """Remove page (login required),
    display file listing results in a table"""
    documents = Document.query. \
        filter_by(role=current_user.role).order_by(Document.fileid).all()
    # Generated remove page following authentication of user
    return render_template('remove.html', documents=documents)


@main.route('/remove', methods=['POST'])
def remove_post():
    """display file listing results in a table"""
    fileid = request.form.get('remove_id')
    file = Document.query.filter_by(fileid=fileid). \
        filter_by(role=current_user.role).first()
    if not file:
        flash('Invalid File ID')
        return redirect(url_for('main.remove'))
    db.session.delete(file)
    db.session.commit()
    # Confirmation page of file removed
    flash('File Removed')
    return redirect(url_for('main.remove'))
