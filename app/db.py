# -*- coding: utf-8 -*-
from pymongo import MongoClient
import hashlib
from settings import *
from itsdangerous import Signer
import time


class DuplicateEntry(Exception):
    pass


class EntryNotFound(Exception):
    pass


class SqlrMongoManager(object):

    _instance = None

    def __init__(self):
        self.client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client.sqlr

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SqlrMongoManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def remove_project(self, app, user):
        # todo: test
        with self.client.start_request():
            user = self.db.users.find_one({'email': user})
            if user:
                self.db.events.remove({'app': app, 'user.$id': user['_id']})
            else:
                raise EntryNotFound
        return True

    def create_user(self, email, password):
        # todo: test
        with self.client.start_request():
            if self.db.users.find({'email': email}).count() > 0:
                raise DuplicateEntry
            s = Signer(SIGNER_SAULT)
            token = s.sign(email)
            # todo: test
            user = self.db.users.insert({'token': token, 'email': email, 'password': hashlib.md5(password).hexdigest()})
            return user
        return False

    def delete_user(self, user):
        # todo: test
        with self.client.start_request():
            user = self.db.users.find_one({'email': user})
            if user:
                self.db.events.remove({'user.$id': user['_id']})
                self.db.users.remove({'_id': user['_id']})
            else:
                raise EntryNotFound
        return True

    def check_user(self, email, password, hashed=True):
        password = password if hashed else hashlib.md5(password).hexdigest()
        user = self.db.users.find_one({'email': email, 'password': password})
        if user:
            return user
        return None

    def get_user(self, email):
        user = self.db.users.find_one({'email': email})
        if user:
            return user
        return None

    def create_event(self, token, message, app=None, etype=None):
        # todo: test
        with self.client.start_request():
            if self.validate_token(token):
                criteria = {
                    'timestamp': int(time.time()),
                    'message': message,
                    'app': app if app is not None else 'app:default'
                }
                if etype:
                    criteria['type'] = etype
                self.db.events.insert(criteria)
                return True
            return False

    def get_events(self, token, app=None):
        # todo: test
        with self.client.start_request():
            if self.validate_token(token):
                criteria = {}
                if app:
                    criteria['app'] = app
                events = self.db.events.filter(criteria)
                if events:
                    for event in events:
                        event.pop('_id')
                else:
                    events = []
                return events

    def validate_token(self, token):
        user = self.db.users.find_one({'token': token})
        if not user:
            return False
        return user