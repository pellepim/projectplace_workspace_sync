import json
import voluptuous
import requests_oauthlib
import jinja2


class AWSS3Conf(object):
    ConfSchema = voluptuous.Schema({
        'bucket_name': str,
        'aws_access_key_id': str,
        'aws_secret_access_key': str
    })

    def __init__(self, s3_settings):
        conf_dict = self.ConfSchema(s3_settings)

        self.BUCKET_NAME = conf_dict['bucket_name']
        self.AWS_ACCESS_KEY_ID = conf_dict['aws_access_key_id']
        self.AWS_SECRET_ACCESS_KEY = conf_dict['aws_secret_access_key']


class Config(object):
    ConfSchema = voluptuous.Schema({
        'consumer_key': str,
        'consumer_secret': str,
        'access_token': str,
        'access_token_secret': str,
        'host': str,
        voluptuous.Optional('workspace_ids'): [int],
        voluptuous.Optional('filestorage'): str,
        voluptuous.Optional('s3settings'): voluptuous.Any(dict, None),
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
        self.S3_SETTINGS = AWSS3Conf(conf_dict.get('s3settings')) if 's3settings' in conf_dict else None

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

