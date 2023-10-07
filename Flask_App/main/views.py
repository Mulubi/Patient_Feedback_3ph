# contains the blueprint for the main application functions

from datetime import datetime
from . import main
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from Flask_App.auth import login_required
from Flask_App.db import get_db


@main.route('/')
def index():
    db = get_db()
    surveys = db.execute(
        'SELECT s.id, name, feedback, created, author_id, username'
        ' FROM survey s JOIN user u ON s.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('main/index.html', surveys=surveys)

@main.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        survey_data = {
            'name': request.form['name'],
            'feedback': request.form['feedback']
        }
        if not survey_data['name']:
            error = 'Your name is required.'

        if not survey_data['feedback']:
            error = 'Please provide feedback'

        error = None

        # if not survey_data['satisfaction']:
        #     error = 'Please provide a satisfaction level'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO survey (name, feedback, author_id)'
                ' VALUES (?, ?, ?)',
                (survey_data['name'], survey_data['feedback'], g.user['id'])
            )
            db.commit()
            return redirect(url_for('main.index'))
            # return redirect(url_for('main.thank_you'))

    return render_template('main/create.html')
        
    # return render_template('main/create.html')

@main.route('/thank_you')
def thank_you():
    return render_template('main/thank_you.html')

def get_survey(id, check_author=True):
    survey = get_db().execute(
        'SELECT s.id, name, feedback, created, author_id, username'
        ' FROM survey s JOIN user u ON s.author_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if survey is None:
        abort(404, f"Survey id {id} doesn't exist.")

    if check_author and survey['author_id'] != g.user['id']:
        abort(403)

    return survey

@main.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    survey = get_survey(id)

    if request.method == 'POST':
        survey_data = {
            'name': request.form['name'],
            'feedback': request.form['feedback'],
        }
        if not survey_data['name']:
            error = 'Your name is required.'

        if not survey_data['feedback']:
            error = 'Please provide feedback'

        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE survey SET name = ?, feedback = ?'
                ' WHERE id = ?',
                (survey_data['name'], survey_data['feedback'], id)
            )
            db.commit()
            return redirect(url_for('main.index'))

    return render_template('main/update.html', survey=survey)

@main.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_survey(id)
    db = get_db()
    db.execute('DELETE FROM survey WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('main.index'))