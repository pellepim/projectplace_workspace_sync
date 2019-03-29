import json
import voluptuous
import requests_oauthlib
import jinja2


class Config(object):
    ConfSchema = voluptuous.Schema({
        'consumer_key': str,
        'consumer_secret': str,
        'access_token': str,
        'access_token_secret': str,
        'host': str,
        voluptuous.Optional('workspace_ids'): [int],
        voluptuous.Optional('filestorage'): str,
    }, required=True)

    def __init__(self):
        with open('config.json') as conf:
            conf_dict = self.ConfSchema(json.load(conf))

        self.CONSUMER_KEY = conf_dict['consumer_key']
        self.CONSUMER_SECRET = conf_dict['consumer_secret']
        self.ACCESS_TOKEN = conf_dict['access_token']
        self.ACCESS_TOKEN_SECRET = conf_dict['access_token_secret']
        self.HOST = conf_dict['host']
        self.WORKSPACE_IDS = conf_dict.get('workspace_ids', [])
        self.FILESTORAGE_PATH = conf_dict.get('filestorage', 'localdata')

    def oauth(self):
        return requests_oauthlib.OAuth1(
            self.CONSUMER_KEY, client_secret=self.CONSUMER_SECRET, resource_owner_key=self.ACCESS_TOKEN,
            resource_owner_secret=self.ACCESS_TOKEN_SECRET
        )

    def jinja_env(self):
        return jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


conf = Config()
oauth = conf.oauth()
jinja_env = conf.jinja_env()

