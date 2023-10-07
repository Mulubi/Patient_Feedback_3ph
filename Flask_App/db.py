# g is a special object that is unique to each request. It is used to store
# data that might be accessed by multiple functions during the request.

# current_app is another special object that points to the Flask application
# handling the request.

import sqlite3

import click
from flask import current_app, g

def get_db():
    # This function will be called when the application has been created and is
    # is handling a request, so current_app can be used.
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    # This function checks if a connection was created by checking if g.db was set.
    # If the connection exists, it is closed.
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    # Function that will run SQL commands from schema.sql
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    # clear the existing data and create new tables
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    # app.teardown_appcontext() tells Flask to call that function when cleaning up
    # after returning the response.

    # app.cli.add_command() adds a new command that can be called with the flask command.
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    