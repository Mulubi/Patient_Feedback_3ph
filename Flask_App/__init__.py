# contains the create_app function which is the application factory function
import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from .main import main
from config import config

# extensions
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
# db = SQLAlchemy()


def create_app(config_name=None):
    # create and configure the app. 
    app = Flask(__name__, instance_relative_config=True)

    # Configuration using an object or a custom config name
    if config_name is not None:
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)
    else:
        app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flask_app.sqlite'),
            )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize extensions within the app
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello Wice'
    
    # register blueprints
    from . import db, auth
    from .main import main as main_bp
    db.init_app(app)

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(main_bp)

    
    return app