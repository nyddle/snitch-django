# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, Blueprint
from forms import *
import hashlib
from itsdangerous import Signer
from pymongo import MongoClient
from db import SqlrMongoManager, DuplicateEntry, EntryNotFound

#client = MongoClient('localhost', 27017)
#db = client.sqlr
web = Blueprint('web', __name__)
db_manager = SqlrMongoManager()


@web.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_manager.check_user(form.email.data, form.password.data, hashed=False)
        if user:
            session['user'] = user
            return redirect(url_for('web.index'))
        else:
            flash('User not found')
    return render_template('login.html', form=form)


@web.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@web.route('/signup')
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            db_manager.create_event(form.data.email, form.data.password)
        except DuplicateEntry:
            flash('User already exists')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


def create_event(self):
    pass


@web.route('/index')
def index():
    if 'user' in session:
        events_list = db_manager.get_events(session['user']['email'])
        return render_template('index.html', events=events_list)
    return redirect(url_for('login'))
