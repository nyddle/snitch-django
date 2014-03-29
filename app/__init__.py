# -*- coding: utf-8 -*-
from flask import Flask

from db import SqlrMongoManager, DuplicateEntry


def create_app(config=None):
    app = Flask(__name__)
    conf_file = 'settings.py' if config is None else config
    app.config.from_pyfile(conf_file)
    app.secret_key = 'a random string'

    from web import web
    from api import api
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(web, url_prefix='/web')
    return app
