# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, session, Blueprint, request, jsonify
from functools import wraps

from forms import *

from db import SqlrMongoManager, DuplicateEntry

web = Blueprint('web', __name__)
db_manager = SqlrMongoManager()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not 'user' in session:
            return redirect(url_for('web.login'))
        return fn(*args, **kwargs)
    return wrapper


@web.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('web.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db_manager.check_user(form.data['email'], form.data['password'], hashed=False)
        if user:
            user.pop('_id')
            session['user'] = user
            return redirect(url_for('web.index'))
        else:
            flash('User not found')
    return render_template('login.html', form=form)



@web.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('web.login'))


@web.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('web.index'))
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            print form.data
            user = db_manager.create_user(form.data['email'], form.data['password'])
        except DuplicateEntry:
            flash('User already exists')
        except Exception, e:
            print e
        return redirect(url_for('web.login'))
    return render_template('signup.html', form=form)


@web.route('/', methods=['GET', 'POST'])
@web.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == 'POST':
        #request.args
        filters = {}
        if 'app' in request.args:
            pass
        if 'from' in request.args:
            pass
        if 'to' in request.args:
            pass
        if 'type' in request.args:
            filters['etype'] = request.args['type']
        events_list = db_manager.get_events(session['user']['token'], **filters)

        return jsonify({'events': events_list})

    # todo: refactor for use one mongo session
    events_list = db_manager.get_events(session['user']['token'])
    types_list = []
    projects_list = []
    return render_template('index.html', events=events_list)
