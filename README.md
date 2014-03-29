snitch
======

landing page for our monitoring service
=======
# Snitch API

## Defaults
- Default app: default
- Default event type: alert

## TODO:
- Send mail
- Add to docs event description
- Request examples

## URLs

#### Get events
URL: /list

Method: POST

Required params:
- token - string;

Available params:
- type: string;
- app: string or list of strings. means app name;
- date_interval: list of two stringified dates - from and to;

Response:
- result: bool
- reason: string; Passed in result false;
- events: list of events;

#### Post new event
URL: /add
Method: POST
Required params:
- token;
- message;
Optional:
- type: string;
- app: string;
Response:
- result: bool
- reason: string; Passed in result false;

#### App settings
URL: /app
Method: POST
Required params:
- token - string;
- app - string;
- emails - list of emails who have access to app;
Response:
- result: bool
- reason: string; Passed in result false;

#### Create new user
URL: /reg
Method: POST
Required params:
- email - string;
- password - string(previously hashed in md5);
Response:
- result: bool
- reason: string; Passed in result false;
- token: string; Passed if result True;
Note: this feature should be disabled in public api

#### Authenticate
URL: /auth
Method: POST
Required params:
- email - string;
- password - string(previously hashed in md5);
Response:
- result: bool
- reason: string; Passed in result false;
- token: string; Passed if result True;
Note: this feature (should) be disabled in public api.
Token has to be generated in web.
