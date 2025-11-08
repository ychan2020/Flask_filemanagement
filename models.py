"""
models.py
"""
import onetimepass
from flask_login import UserMixin
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

    @staticmethod
    def verify_totp(token, otp_secret):
        """function to verify the user provided and the secret code stored."""
        return onetimepass.valid_totp(token, otp_secret)


class Document(db.Model):
    """Database fields connection"""
    # Primary key is required by SQLAlchemy
    fileid = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    role = db.Column(db.String(12))
    key = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(100))
    owner = db.Column(db.String(50))
