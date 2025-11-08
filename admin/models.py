"""
models.py
"""
import base64
import os

import onetimepass
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from . import db


class User(UserMixin, db.Model):
    """Database fields connection"""
    # Primary key is required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(50))
    role = db.Column(db.String(12))
    otp_secret = db.Column(db.String(16))

    # add additional field for storing the otp_secret

    def __init__(self, **kwargs):
        # Generating otp secret for the function
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # Generate a random secret
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    def verify_password(self, password):
        """verify function for the checking password"""
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        """function to create otp url"""
        return 'otpauth://totp/2FA-Demo:{0}?secret={1}&issuer=2FA-Demo' \
            .format(self.name, self.otp_secret)

    @staticmethod
    def verify_totp(token, otp_secret):
        """verify customer provided input ot the system secret code"""
        return onetimepass.valid_totp(token, otp_secret)
