# -*- coding: utf-8 -*-
import unittest
import requests
import json

from db import SqlrMongoManager
from test_settings import *

DB = 'test_db'


class TestSnitchAPI(unittest.TestCase):

    def setUp(self):
        self.drop_database(DB)
        self.mm = SqlrMongoManager(db=DB)
        self.db = self.mm.db
        self.base_url = URL
        self.token = None
        # todo: load fixture with test data

    def tearDown(self):
        self.mm.client.drop_database(DB)

    def drop_database(self, db_name):
        mm = SqlrMongoManager(db=db_name)
        mm.client.drop_database(DB)

    def send_post_request(self, url, data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = data if data is not None else {}
        r = requests.post('{}/{}'.format(self.base_url, url),
                          headers=headers, data=json.dumps(data))
        return r

    def test_user_creation(self):
        # todo: mode urls to settings
        send_data = {'email': EMAIL, 'password': PASSWORD}
        r = self.send_post_request('api/reg', send_data)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('result', data)
        self.assertTrue(data['result'])
        self.assertIn('token', data)
        self.token = data['token'] if 'token' in data else None

    def test_auth(self):
        send_data = {'token': }

    # def test_event_creation(self):
    #     sent_data = {'message': 'test_message'}
    #     r = self.send_post_request('api/add', sent_data)
    #     self.assertEqual(r.status_code, 200)
    #     data = r.json()
    #     self.assertTrue(data['result'])

    # def test_event_select_by_app(self):
    #     pass
    #
    # def test_event_select_by_type(self):
    #     pass
    #
    # def test_event_select_by_user(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
