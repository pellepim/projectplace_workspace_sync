import json
import voluptuous
import requests_oauthlib


class Config(object):
    ConfSchema = voluptuous.Schema({
        'consumer_key': str,
        'consumer_secret': str,
        'access_token': str,
        'access_token_secret': str,
        'host': str
    }, required=True)

    def __init__(self):
        with open('config.json') as conf:
            conf_dict = self.ConfSchema(json.load(conf))

        self.CONSUMER_KEY = conf_dict['consumer_key']
        self.CONSUMER_SECRET = conf_dict['consumer_secret']
        self.ACCESS_TOKEN = conf_dict['access_token']
        self.ACCESS_TOKEN_SECRET = conf_dict['access_token_secret']
        self.HOST = conf_dict['host']

    def oauth(self):
        return requests_oauthlib.OAuth1(
            self.CONSUMER_KEY, client_secret=self.CONSUMER_SECRET, resource_owner_key=self.ACCESS_TOKEN,
            resource_owner_secret=self.ACCESS_TOKEN_SECRET
        )


conf = Config()
oauth = conf.oauth()
