"""
auth.py
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

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
    rhd["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rhd["Pragma"] = "no-cache"
    rhd["Expires"] = "0"
    rhd['Cache-Control'] = 'public, max-age=0'
    rhd['Strict-Transport-Security'] = 'max-age=3600; includeSubDomains'
    rhd['Content-Security-Policy'] = "default-src 'none'; " \
                                     "style-src https://cdnjs.cloudflare.com/; " \
                                     "frame-ancestors 'none'; " \
                                     "script-src 'self'; " \
                                     "script-src-elem 'self'; " \
                                     "script-src-attr 'self'; " \
                                     "style-src-elem " \
                                     "https://cdnjs.cloudflare.com/; " \
                                     "style-src-attr 'self'; " \
                                     "img-src 'self'; " \
                                     "connect-src 'self'; " \
                                     "frame-src 'self'; font-src 'self'; " \
                                     "media-src 'self'; " \
                                     "object-src 'self'; " \
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
    otp_token = request.form.get('otp_token')
    # Additional field required
    user = User.query.filter_by(email=email).first()

    # Check if user actually exists
    # Take the user supplied password, hash it,
    # and compare to the hashed passsword in database
    if not user or not check_password_hash(user.password, password) or not User. \
        verify_totp(otp_token, user.otp_secret):
        flash('Please check your login details and try again.')

        # Reload page if user not exist or wrong password
        return redirect(url_for('auth.login'))

    # Check if user has admin role
    if user.role == 'Disabled':
        flash('Access denied You are not authorised to access this page.')

        # Reload page if user is disabled
        return redirect(url_for('auth.login'))

    # If the above check passes, the user has the correct credentials
    login_user(user)
    return redirect(url_for('main.profile'))


@auth.route('/update')
def update():
    """Render update page"""
    return render_template('update.html')


@auth.route('/update', methods=['POST'])
def update_post():
    """Update User"""
    # If returns a user, the email exists in database
    email = current_user.email
    user = User.query.filter_by(
       email=email).first()

    password = request.form.get('password')
    user.password = generate_password_hash(password,
                                           method='sha256', salt_length=8)

    # Update the user to the database
    db.session.add(user)
    db.session.commit()

    flash('User Updated')
    return redirect(url_for('main.profile'))


@auth.route('/logout')
@login_required
def logout():
    """Logout and Redirect to main page"""
    logout_user()
    return redirect(url_for('main.index'))
