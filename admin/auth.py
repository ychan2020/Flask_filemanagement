"""
auth.py
"""

from io import BytesIO
import pyqrcode
from flask import Blueprint, render_template, redirect
from flask import url_for, request, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from . import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    """Render login page"""
    return render_template('login.html')


@auth.after_request
def apply_caching(response):
    """apply caching"""
    rhd = response.headers
    rhd["X-Frame-Options"] = "SAMEORIGIN"
    rhd["X-Content-Type-Options"] = "nosniff"
    rhd["Cache-Control"] = "no-cache, no-store, must-revalidate"  # HTTP 1.1.
    rhd["Pragma"] = "no-cache"  # HTTP 1.0.
    rhd["Expires"] = "0"  # Proxies.
    rhd['Strict-Transport-Security'] = 'max-age=3600; includeSubDomains'
    rhd['Content-Security-Policy'] = "default-src 'none'; " \
                                     "style-src https://cdnjs.cloudflare.com/; " \
                                     "frame-ancestors 'none'; " \
                                     "script-src 'self'; " \
                                     "script-src-elem 'self'; " \
                                     "script-src-attr 'self'; " \
                                     "style-src-elem " \
                                     "https://cdnjs.cloudflare.com/; " \
                                     "style-src-attr 'self'; img-src " \
                                     "'self'; connect-src 'self'; " \
                                     "frame-src 'self'; font-src 'self'; " \
                                     "media-src 'self'; object-src 'self'; " \
                                     "manifest-src 'self'; " \
                                     "worker-src 'self'; " \
                                     "prefetch-src 'self'; " \
                                     "form-action 'self' "
    rhd['X-XSS-Protection'] = '1; mode=block'
    return response


@auth.route('/login', methods=['POST'])
def login_post():
    """User login"""
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    # Existing user check
    # Hash supplied password and compare to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        # Reload page if user not exist or wrong password
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    # Check if user has admin role
    if not user.role == 'Admin':
        # Reload page if user is not admin
        flash('Access denied You are not authorized to access this page.')
        return redirect(url_for('auth.login'))

    # If the above check passes, the user has correct credentials
    login_user(user)
    return redirect(url_for('main.profile'))


@auth.route('/create')
@login_required
def create():
    """Render create page"""
    return render_template('create.html')


@auth.route('/twofactor')
def two_factor_setup():
    """function to redirect and to QR page for MFA """
    # The page contains the sensitive qrcode
    # The browser must not cache it
    user = User.query.filter_by(name=session['username']).first()
    if user is None:
        return redirect(url_for('index'))

    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth.route('/qrcode')
def qrcode():
    """function to generate image for QA"""
    if 'username' not in session:
        abort(404)
    user = User.query.filter_by(name=session['username']).first()
    if user is None:
        abort(404)

    # Remove username from session for extra security
    del session['username']

    # Render qrcode for FreeTOTP
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth.route('/create', methods=['POST'])
def create_post():
    """Create User"""
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    role = request.form.get('role')

    # If user is returned, the email already exists in database
    user = User.query.filter_by(
        email=email).first()

    if user:
        # If a user is found, redirect back to create page so user can retry
        flash('Email address already exists')
        return redirect(url_for('auth.create'))

    # Create new user with the form data with hashed password
    new_user = User(email=email, name=name,
                    password=generate_password_hash(password,
                                                    method='sha256',
                                                    salt_length=8), role=role)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    session['username'] = new_user.name
    # Redirect to the QR page for registration by adding a page
    return redirect(url_for('auth.two_factor_setup'))
    # flash('User Created')
    # return redirect(url_for('auth.create'))


@auth.route('/update')
@login_required
def update():
    """Render update page"""
    return render_template('update.html')


@auth.route('/update', methods=['POST'])
def update_post():
    """Update User"""
    email = request.form.get('email')

    # If user is returned, the email already exists in database
    user = User.query.filter_by(
        email=email).first()
    if not user:
        # If a user is found, redirect back to create page so user can retry
        flash('Email address does not exist')
        return redirect(url_for('auth.update'))

    user.name = request.form.get('name')
    password = request.form.get('password')
    user.password = generate_password_hash(password,
                                           method='sha256', salt_length=8)
    user.role = request.form.get('role')

    # Update the user to the database
    db.session.add(user)
    db.session.commit()

    flash('User Updated')
    return redirect(url_for('auth.update'))


@auth.route('/logout')
@login_required
def logout():
    """Logout and Redirect to main page"""
    logout_user()
    return redirect(url_for('main.index'))
