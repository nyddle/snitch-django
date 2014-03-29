# -*- coding: utf-8 -*-
from pymongo import MongoClient
import hashlib
from settings import MONGO_PORT, MONGO_HOST, SIGNER_SAULT
from itsdangerous import Signer
import time
# todo: add indexing to Mongo


class DuplicateEntry(Exception):
    pass


class EntryNotFound(Exception):
    pass


class SqlrMongoManager(object):

    _instance = None

    def __init__(self, host=MONGO_HOST, port=MONGO_PORT, db='sqlr', app=None):
        self.client = MongoClient(host, port)
        self.db = self.client[db]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SqlrMongoManager,
                                  cls).__new__(cls, *args, **kwargs)
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
        with self.client.start_request():
            print email
            if self.db.users.find({'email': email}).count() > 0:
                print 'Empty('
                raise DuplicateEntry
            s = Signer(SIGNER_SAULT)
            token = s.sign(email)
            password = hashlib.md5(password).hexdigest() if not hashed \
                else password
            self.db.users.insert({'token': token, 'email': email,
                                 'password': password})
            return token
        return False

    def delete_user(self, user):
        with self.client.start_request():
            user = self.db.users.find_one({'email': user})
            if user:
                self.db.events.remove({'user.$id': user['_id']})
                self.db.users.remove({'_id': user['_id']})
            else:
                raise EntryNotFound
        return True

    def check_user(self, email, password, hashed=True):
        """
        Check user's credentials. Password may be hashed(default) or
        string(then you must set hashed to False)
        """
        password = password if hashed else hashlib.md5(password).hexdigest()
        user = self.db.users.find_one({'email': email, 'password': password})
        if user:
            return user
        return None

    def get_user(self, email):
        """
        email can be list or str.
        if email is list will be returned list (can be empty).
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

    def create_event(self, token, message, usernames=None, app=None,
                     etype=None):
        """
        usernames - list of usernames that has access to app or string if
        username only one
        app - app name
        etype - type of event
        """
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
                    'app': app if app is not None else 'default',
                    'type': etype if etype is not None else 'notification',
                    'users': tokens,
                }
                self.db.events.insert(criteria)
                return True
            return False

    def get_events(self, token, app='', date_interval=(), etype=None):
        """
        app - application name
        date_interval - a tuple. It can be empty or consists from one or two
        elems. First elem is From and second is To
        etype - application type
        """
        with self.client.start_request():
            #criteria = {}
            criteria = {'users': {'$in': [token]}}

            if len(app) > 0:
                #criteria['app'] = {'$in': [app]}
                criteria['app'] = app
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
            if events.count() > 0:
                for event in events:
                    result.append(event)
            return result

    def validate_token(self, token):
        user = self.db.users.find_one({'token': token})
        if not user:
            return False
        return user

    @staticmethod
    def bson_to_json(seq):
        def id_to_str(e):
            try:
                e['_id'] = str(e['_id'])
            except KeyError:
                pass
            return e
        return map(id_to_str, seq)

    def get_apps(self, token):
        with self.client.start_request():
            # todo: this is an ugly quickhack. It should be replaced with normal code!!!
            all_events = self.db.events.find({'users': {'$in': [token]}}, {'app': 1, '_id': 0})
            events = list(set([d['app'] for d in all_events]))
            return events

    def get_types(self, token):
        with self.client.start_request():
            # todo: this is an ugly quickhack. It should be replaced with normal code!!!
            all_types = self.db.events.find({'users': {'$in': [token]}}, {'type': 1})
            types = list(set([d['type'] for d in all_types]))
            return types