#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse

from app import create_app


parser = argparse.ArgumentParser()
parser.add_argument('command', default='runserver')
if __name__ == '__main__':
    args = parser.parse_args()
    if args.command == 'runtest':
        app = create_app('test_settings.py')
    else:
        app = create_app()
    app.run()