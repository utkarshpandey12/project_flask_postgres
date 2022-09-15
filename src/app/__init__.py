from flask import Flask
from flask_argon2 import Argon2
from flask_login import LoginManager
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import MetaData

from .common.constants import SQLALCHEMY_NAMING_CONVENTION

metadata = MetaData(naming_convention=SQLALCHEMY_NAMING_CONVENTION)
db = SQLAlchemy(metadata=metadata)
argon2 = Argon2()
login_manager = LoginManager()
redis_jobs = Redis()


def create_app(name=__name__, config_override=None):
    app = Flask(name, instance_relative_config=True)
    load_config(app, config_override)
    init_extensions(app)
    customize_app(app)
    register_blueprints(app)
    register_middleware(app)
    register_cli_commands(app)
    return app


def load_config(app, config_override):
    app.config.from_pyfile("config.py")
    if config_override:
        app.config.update(config_override)


def init_extensions(app):
    db.init_app(app)
    argon2.init_app(app)
    login_manager.init_app(app)
    redis_jobs.init_app(app, "REDIS_JOBS")


def customize_app(app):
    pass


def register_blueprints(app):
    from .common import common
    from .main import main

    app.register_blueprint(common)
    app.register_blueprint(main, url_prefix=app.config["URL_PREFIX"])


def register_middleware(app):
    from .middleware.session import load_session_and_user_and_permissions

    app.before_request(load_session_and_user_and_permissions)

    if app.config["ENABLE_CORS"]:
        from .middleware.cors import add_cors_headers

        app.after_request(add_cors_headers)


def register_cli_commands(app):
    pass
