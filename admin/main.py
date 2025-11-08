"""
main.py
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

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
    rdh["Cache-Control"] = "no-cache, no-store, must-revalidate"  # HTTP 1.1.
    rdh["Pragma"] = "no-cache"  # HTTP 1.0.
    rdh["Expires"] = "0"  # Proxies.
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
    # Generates user profile page following autheticated login
    return render_template('profile.html', name=current_user.name)
