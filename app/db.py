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

    def create_user(self, email, password, hashed=False):
        # todo: test
        with self.client.start_request():
            if self.db.users.find({'email': email}).count() > 0:
                raise DuplicateEntry
            s = Signer(SIGNER_SAULT)
            token = s.sign(email)
            password = hashlib.md5(password).hexdigest() if not hashed else password
            user = self.db.users.insert({'token': token, 'email': email, 'password': password})
            print user
            return token
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
        """
        email can be list or str.
        if list will be returned list (can be empty).
        If str - return None if not found or dict
        """
        if isinstance(email, list):
            users = self.db.users.find({'email': {'$in': email}}, {'_id': 0})
            return users
        else:
            user = self.db.users.find_one({'email': email})
            if user:
                return user
        return None

    def create_event(self, token, message, usernames=None, app=None, etype=None):
        with self.client.start_request():
            if self.validate_token(token):
                tokens = [user['token'] for user in self.get_user(usernames)]
                if tokens is None:
                    tokens = [token]
                elif isinstance(tokens, list):
                    if not token in tokens:
                        tokens.append(token)
                else:
                    tokens = [token]
                criteria = {
                    'timestamp': int(time.time()),
                    'message': message,
                    'app': app if app is not None else 'app:default',
                    'type': etype if etype is not None else 'notification',
                    'users': tokens
                }
                self.db.events.insert(criteria)
                return True
            return False

    def get_events(self, token, app=(), date_interval=(), etype=None):
        with self.client.start_request():
            #criteria = {}
            criteria = {'users': {'$in': [token]}}

            if len(app) > 0:
                criteria['app'] = {'$in': app}
            if len(date_interval) == 2:
                # date_interval = [from, to]
                criteria['timestamp'] = {'$gte': date_interval[0]}
                if date_interval[1] > 0:
                    # if  0 - don't set lte
                    criteria['timestamp'] = {'$lte': date_interval[1]}
            if etype is not None:
                criteria['type'] = etype

            events = self.db.events.find(criteria, {'_id': 0})
            result = []
            if events:
                for event in events:
                    result.append(event)
            return result

    def validate_token(self, token):
        user = self.db.users.find_one({'token': token})
        if not user:
            return False
        return user