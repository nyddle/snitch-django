# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, session, \
    Blueprint, request, jsonify, current_app
from functools import wraps

from forms import *

from db import SqlrMongoManager, DuplicateEntry

web = Blueprint('web', __name__)


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
    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    form = LoginForm()
    if form.validate_on_submit():
        user = db_manager.check_user(form.data['email'], form.data['password'],
                                     hashed=False)
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


@web.route('/restore', methods=['GET', 'POST'])
def restore_pass():
    return render_template('restore_password.html')


@web.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('web.index'))
    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            db_manager.create_user(form.data['email'], form.data['password'])
        except DuplicateEntry:
            flash('User already exists')
        except Exception, e:
            print e
        return redirect(url_for('web.login'))
    return render_template('signup.html', form=form)


@web.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html')


@web.route('/', methods=['GET', 'POST'])
@web.route('/index', methods=['GET', 'POST'])
@web.route('/index/<app>', methods=['GET', 'POST'])
@login_required
def index(app=None):
    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    if request.method == 'POST':
        #request.args
        filters = {}
        if app is not None and app != 'All':
            filters['app'] = app
        if 'from' in request.args:
            filters['from'] = request.args['from']
        if 'to' in request.args:
            filters['to'] = request.args['to']
        if 'type' in request.args:
            filters['etype'] = request.args['type']
        events_list = db_manager.get_events(session['user']['token'],
                                            **filters)
        types_list = db_manager.get_types(session['user']['token'])
        apps_list = db_manager.get_apps(session['user']['token'])
        return jsonify({'events': events_list, 'apps': apps_list,
                        'types': types_list})

    # todo: refactor for use one mongo session
    return render_template('index.html')
