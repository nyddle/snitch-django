# -*- coding: utf-8 -*-
from flask import jsonify, request, Blueprint
from db import SqlrMongoManager, DuplicateEntry

api = Blueprint('api', __name__)

db_manager = SqlrMongoManager()
#todo: move validate token to db_manager

@api.route('/get', methods=['POST'])
def get():
    """
    JSON params:
    token - required
    app - None, str or list
    date_interval - None or list with to elems. 0 is min, 1 is max. If you don't need max - set it to 0
    type - None or string
    """
    if request.json is None or not 'token' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    user = db_manager.validate_token(request.json['token'])
    if not user:
        return jsonify({'result': False, 'reason': 'Wrong token'})

    params = {'app': ['app:default'] if not 'app' in request.json else request.json['app']
              if isinstance(request.json['app']. list) else [request.json['app']],

              'date_interval': tuple(request.json['date_interval']) if 'date_interval' in request.json \
              and isinstance(request.json['data_interval'], list) else (),

              'etype': request.json['type'] if 'type' in request.json else None
              }

    events = db_manager.get_events(request.json['token'], **params)
    events = list(events)
    return jsonify({'result': True, 'events': events})


@api.route('/post', methods=['POST'])
def post():
    """
    Required: toke, message
    Optional args: app, type, emails
    """
    # todo: move default project/event to settings
    if request.json is None or not 'token' in request.json or not 'message' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    user = db_manager.validate_token(request.json['token'])
    if not user:
        return jsonify({'result': False, 'reason': 'Wrong token'})

    params = {}
    if 'app' in request.json:
        params['app'] = request.json['app']

    if 'type' in request.json:
        params['etype'] = request.json['type']

    if 'emails' in request.json:
        params['usernames'] = request.json['emails'] if isinstance(request.json['emails'], list) \
            else [request.json['emails']]

    event = db_manager.create_event(request.json['token'], request.json['message'], **params)
    if event:
        return jsonify({'result': True})
    return jsonify({'result': False, 'reason': 'Something wrong'})


@api.route('/reg', methods=['POST'])
def create_user():
    # todo: move to decorator
    # todo: validate email
    # todo: send a letter
    if request.json is None or not 'email' in request.json or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    try:
        token = db_manager.create_user(request.json['email'], request.json['password'], hashed=True)
    except DuplicateEntry:
        return jsonify({'result': False, 'reason': 'User already exists'})
    if not token:
        return jsonify({'result': False, 'reason': 'Wrong credentials'})
    return jsonify({'result': True, 'token': token})


@api.route('/auth', methods=['POST'])
def auth():
    if request.json is None or not 'email' in request.json or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    user = db_manager.check_user(request.json['email'], request.json['password'], hashed=True)
    if not user:
        return jsonify({'result': False, 'reason': 'Email not found'})

    return jsonify({'token': user['token'], 'result': True})
