# -*- coding: utf-8 -*-
from flask import jsonify, request, Blueprint, current_app

from db import SqlrMongoManager, DuplicateEntry

api = Blueprint('api', __name__)


# todo: move token validation to db_manager
# todo: https
# todo: pyotp
@api.route('/list', methods=['POST'])
def get():
    """
    JSON params:
    Required:
    token - string
    Optional:
    app - str or list
    date_interval - list with to elems. 0 is min, 1 is max. If you don't need
    max - set it to 0;
    type - string.

    Response:
    result: bool;
    reason: string(returned if result is False;
    events: list; returned if result is True;
    """
    if request.json is None or not 'token' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    user = db_manager.validate_token(request.json['token'])
    if not user:
        return jsonify({'result': False, 'reason': 'Wrong token'})

    params = {'app': ['app:default'] if not 'app' in request.json
              else request.json['app']
              if isinstance(request.json['app'], list)
              else [request.json['app']],

              'date_interval': tuple(request.json['date_interval'])
              if 'date_interval' in request.json
              and isinstance(request.json['data_interval'], list) else (),
              'etype': request.json['type'] if 'type' in request.json else None
              }
    # todo: return id
    events = db_manager.get_events(request.json['token'], **params)
    events = list(events)
    return jsonify({'result': True, 'events': events})


@api.route('/add', methods=['POST'])
def post():
    """
    Required: token, message
    Optional args: app, type, emails
    """
    # todo: move default project/event to settings

    if request.json is None or not 'token' in request.json \
            or not 'message' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    user = db_manager.validate_token(request.json['token'])
    if not user:
        return jsonify({'result': False, 'reason': 'Wrong token'})

    params = {}
    if 'app' in request.json:
        params['app'] = request.json['app']

    if 'type' in request.json:
        params['etype'] = request.json['type']

    if 'emails' in request.json:
        params['usernames'] = request.json['emails'] \
            if isinstance(request.json['emails'], list) \
            else [request.json['emails']]
        if not user['email'] in params['usernames']:
            params['usernames'].append(user['email'])
    else:
        params['usernames'] = [user['email']]

    event = db_manager.create_event(request.json['token'], request.json['message'], **params)
    if event:
        return jsonify({'result': True})
    return jsonify({'result': False, 'reason': 'Something wrong'})


@api.route('/reg', methods=['POST'])
def create_user():
    # todo: move to decorator
    # todo: validate email
    # todo: send a letter
    if request.json is None or not 'email' in request.json \
            or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    try:
        token = db_manager.create_user(request.json['email'],
                                       request.json['password'], hashed=True)
    except DuplicateEntry:
        return jsonify({'result': False, 'reason': 'User already exists'})
    if not token:
        return jsonify({'result': False, 'reason': 'Wrong credentials'})
    return jsonify({'result': True, 'token': token})


@api.route('/auth', methods=['POST'])
def auth():
    if request.json is None or not 'email' in request.json \
            or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    db_manager = SqlrMongoManager(host=current_app.config['MONGO_HOST'],
                                  port=current_app.config['MONGO_PORT'],
                                  db=current_app.config['DB'])
    user = db_manager.check_user(request.json['email'],
                                 request.json['password'], hashed=True)
    if not user:
        return jsonify({'result': False, 'reason': 'Email not found'})

    return jsonify({'token': user['token'], 'result': True})
