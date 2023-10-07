# defines the Flask application instance, and also includes a few tasks that
# help manage the application.

import os
from Flask_App import create_app, db
# from flask_migrate import migrate

app = create_app(os.getenv('FLASK-CONFIG') or 'default')
# migrate = Migrate(app, db)

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role)