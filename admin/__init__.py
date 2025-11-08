"""
init.py
"""

from os import urandom
from logging import basicConfig, getLogger, INFO
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pyaml_env import parse_config, BaseConfig
from flask_wtf.csrf import CSRFProtect

config = BaseConfig(parse_config('./config/config.yml'))
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
csrf = CSRFProtect()

LOG_FORMAT = "%(asctime)s %(levelname)s - %(name)s %(threadName)s : %(message)s"
basicConfig(filename='access.log',
            level=INFO,
            format=LOG_FORMAT,
            filemode='a')
logger = getLogger()


def create_app():
    """Initial App"""
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.init.database
    app.config['SESSION_COOKIE_SAMESITE'] = "Strict"

    db.init_app(app)
    csrf.init_app(app)

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Use primary key, user_id, in the query for the user
        return User.query.get(int(user_id))

    # Blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
