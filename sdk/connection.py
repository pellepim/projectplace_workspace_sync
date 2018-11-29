import requests
import config
from functools import wraps
import models.workspace
import json
import sdk.utils


def retry(tries=1):

    def retry_decorator(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            ltries = tries
            while ltries > 0:
                try:
                    return f(*args, **kwargs)
                except:
                    ltries -= 1

            return f(*args, **kwargs)

        return f_retry

    return retry_decorator


def _uri(relative):
    if relative.startswith('/'):
        return '%s%s' % (config.conf.HOST, relative)

    return '%s/%s' % (config.conf.HOST, relative)


@retry(tries=3)
def account_workspaces():
    projects = []
    response = requests.get(_uri('/1/account/projects'), auth=config.oauth)
    response_json = response.json()['projects']

    for p in response_json:
        projects.append(models.workspace.Workspace(p['name'], p['id']))

    return projects


@retry(tries=3)
def workspace_documents(workspace_id):
    response = requests.get(_uri('/1/projects/%d/documents?recursive=true&include_urls=true' % workspace_id),
                            auth=config.oauth)

    containers, documents, urls = sdk.utils.recurse_docs(response.json(), workspace_id, workspace_id)

    return containers, documents, urls


@retry(tries=3)
def account_members():
    response = requests.get(_uri('/1/account/members?include_external_users=1'), auth=config.oauth)

    users = sdk.utils.parse_account_members(response.json())

    return users


@retry(tries=3)
def download_doc(document_id):
    return requests.get(_uri('/1/documents/%d' % document_id), auth=config.oauth)

