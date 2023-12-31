# contains the blueprint for the authentication functions

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from Flask_App.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    # the register view function
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    """
                    INSERT INTO user (username, password) VALUES (?, ?)""",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered!"
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(""" SELECT * FROM user WHERE username = ? """, (username,)).fetchone()

        if user is None:
            error = "Incorrect username, check your spelling!"
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password, try again."

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('main.index'))
        
        flash(error)

    return render_template('auth/login.html')


@auth_bp.before_app_request
def load_logged_in_user():
    # auth_bp.before_app_request registers a function that runs before the view function,
    # no matter what URL is requested.

    # load_logged_in_user - function checks if a user id is stored in the session and gets 
    # the user's data from the database, storing it on g.user, which lasts for the lenght of
    # the request.
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            """ SELECT * FROM user WHERE id = ? """, (user_id,)
        ).fetchone()


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

def login_required(view):
    @functools.wraps(view)
    # this decorator returns a new view function that wraps the original view it's applied to.
    # the new function checks if a user is loaded and redirects to the login page otherwise.

    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view