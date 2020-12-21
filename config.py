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
        'consumer_key': voluptuous.Any(str, None),
        'consumer_secret': voluptuous.Any(str, None),
        'access_token': voluptuous.Any(str, None),
        'access_token_secret': voluptuous.Any(str, None),
        'host': str,
        voluptuous.Optional('workspace_ids'): [int],
        voluptuous.Optional('s3settings'): voluptuous.Any(dict, None),
    }, required=True)
    EMPTY_CONF = {
        'consumer_key': None,
        'consumer_secret': None,
        'access_token': None,
        'access_token_secret': None,
        'host': 'api.projectplace.com'
    }

    def read_conf(self):
        try:
            with open('localdata/config.json', 'r') as conf:
                return self.ConfSchema(json.load(conf))
        except FileNotFoundError:
            with open('localdata/config.json', 'w') as conf:
                json.dump(self.EMPTY_CONF, conf)
                return self.ConfSchema(self.EMPTY_CONF)

    def __init__(self):
        conf_dict = self.read_conf()

        self.CONSUMER_KEY = conf_dict['consumer_key']
        self.CONSUMER_SECRET = conf_dict['consumer_secret']
        self.ACCESS_TOKEN = conf_dict['access_token']
        self.ACCESS_TOKEN_SECRET = conf_dict['access_token_secret']
        self.HOST = conf_dict['host']
        self.WORKSPACE_IDS = conf_dict.get('workspace_ids', [])
        self.FILESTORAGE_PATH = 'localdata'
        self.S3_SETTINGS = AWSS3Conf(conf_dict.get('s3settings')) if 's3settings' in conf_dict else None

    def oauth(self):
        return requests_oauthlib.OAuth1(
            self.CONSUMER_KEY, client_secret=self.CONSUMER_SECRET, resource_owner_key=self.ACCESS_TOKEN,
            resource_owner_secret=self.ACCESS_TOKEN_SECRET
        )

    def is_valid(self):
        try:
            conf_dict = self.read_conf()
            for key in ('consumer_key', 'consumer_secret', 'access_token', 'access_token_secret'):
                assert conf_dict[key]
            return True
        except (voluptuous.Invalid, voluptuous.MultipleInvalid, AssertionError):
            return False

    def jinja_env(self):
        return jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


conf = Config()
oauth = conf.oauth()
jinja_env = conf.jinja_env()

