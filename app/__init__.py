# -*- coding: utf-8 -*-
from flask import Flask
from web import web
from api import api

app = Flask(__name__)
app.secret_key = 'a random string'
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(web, url_prefix='/web')

