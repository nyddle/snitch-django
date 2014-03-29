# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, HiddenField
from wtforms.validators import Required, Email, EqualTo


class SignUpForm(Form):
    email = TextField('email', validators=[Required(), Email()])
    password = PasswordField('password', validators=[Required(), EqualTo('new_password', message='Passwords must match')],
                             default=False)
    new_password = PasswordField('new_password', validators=[Required()], default=False)


class LoginForm(Form):
    email = TextField('email', validators=[Required(), Email()])
    password = PasswordField('password', validators=[Required()], default=False)
