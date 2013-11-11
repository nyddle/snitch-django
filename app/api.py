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
    if request.json is None or not 'token' in request.json or not 'app' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    with client.start_request():
        if not db.users.find_one({'token': request.json['token']}):
            return jsonify({'result': False, 'reason': 'User not found'})

        prj = db.prjs.find_one({'title': request.json['app']})
        if prj:
            if 'type' in request.json:
                events = db.events.find({'prj.$id': ObjectId(prj['_id']), 'type': request.json['type']})
            else:
                events = db.events.find({'prj.$id': ObjectId(prj['_id'])})
            events_list = []
            for event in events:
                event.pop('_id')
                event['prj'] = db.dereference(event['prj'])['title']
                events_list.append(event)
            return jsonify({'result': True, 'events': events_list})
        else:
            return jsonify({'result': False, 'reason': 'Not found'})


@api.route('/post', methods=['POST'])
def post():
    # todo: optimize
    if request.json is None or not 'token' in request.json or not 'type' in request.json or not 'message' in request.json or not 'app' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    # todo: validation
    # todo: check token
    with client.start_request():
        #user = db.users.find_one({'token': request.json['token']})
        if db.users.find_one({'token': request.json['token']}):

            prj = db.prjs.find_one({'title': request.json['app']})
            if prj and '_id' in prj:
                # todo: filter by user?
                #db.events.find({'project.$id': ObjectId(prj['_id'])})
                db.events.insert({'time': int(time.time()), 'prj': DBRef(collection='prjs', id=prj['_id']),
                                  'type': request.json['type'], 'message': request.json['message']})

                return jsonify({'result': True})
            return jsonify({'result': False, 'reason': 'Project not found'})
        return jsonify({'result': False, 'reason': 'User not found'})


@api.route('/reg', methods=['POST'])
def create_user():
    # todo: move to decorator
    # todo: validate email
    # todo: send a letter
    if request.json is None or not 'email' in request.json or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    with client.start_request():
        if db.users.find({'email': request.json['email']}).count() > 0:
            return jsonify({'result': False, 'reason': 'already exists'})

        s = Signer('ololo')
        token = s.sign(request.json['email'])
        db.users.insert({'token': token, 'email': request.json['email'],
                         'password': hashlib.md5(request.json['password']).hexdigest()})
    return jsonify({'result': True, 'token': token})


@api.route('/prj', methods=['POST'])
def create_proj():
    if request.json is None or not 'title' in request.json or not 'token' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})
    with client.start_request():
        if db.prjs.find({'title': request.json['title']}).count() > 0:
            return jsonify({'result': False, 'reason': 'already exists'})

        user = db.users.find_one({'token': request.json['token']})
        if not user:
            return jsonify({'result': False, 'reason': 'not found'})
        db.prjs.insert({'title': request.json['title'], 'owner': DBRef(collection='users', id=user['_id'])})
    return jsonify({'result': True})


@api.route('/auth', methods=['POST'])
def auth():
    if request.json is None or not 'email' in request.json or not 'password' in request.json:
        return jsonify({'result': False, 'reason': 'wrong request'})

    with client.start_request():

        user = db.users.find_one({'email': request.json['email'], 'password': request.json['password']})
        if not user:
            return jsonify({'result': False, 'reason': 'Email not found'})

    return jsonify({'token': user['token'], 'result': True})
