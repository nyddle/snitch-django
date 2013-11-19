# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, Blueprint
from itsdangerous import Signer
from pymongo import MongoClient
from pymongo.database import DBRef
from bson.objectid import ObjectId
import hashlib
import time
from db import SqlrMongoManager

api = Blueprint('api', __name__)

db_manager = SqlrMongoManager()


@api.route('/get', methods=['POST'])
def get():
    if request.json is None or not 'token' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    app = 'app:default' if not 'app' in request.json else request.json['app']
    events = db_manager.get_events(request.json['token'], app)
    return jsonify({'result': True, 'events': events})


@api.route('/post', methods=['POST'])
def post():
    if request.json is None or not 'token' in request.json or not 'message' in request.json or not 'app' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    db_manager.create_event(request.json['token'], request.json['message'])
    return jsonify({'result': False, 'reason': 'User not found'})


@api.route('/reg', methods=['POST'])
def create_user():
    # todo: move to decorator
    # todo: validate email
    # todo: send a letter
    if request.json is None or not 'email' in request.json or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    user = db_manager.create_user(request.json['email'], request.json['password'])
    return jsonify({'result': True, 'token': user['token']})


@api.route('/auth', methods=['POST'])
def auth():
    if request.json is None or not 'email' in request.json or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    with client.start_request():

        user = db.users.find_one({'email': request.json['email'], 'password': request.json['password']})
        if not user:
            return jsonify({'result': False, 'reason': 'Email not found'})

    return jsonify({'token': user['token'], 'result': True})
