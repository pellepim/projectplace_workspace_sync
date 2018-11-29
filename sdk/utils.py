import models.container
import models.document
import models.user
import models.url
from functools import lru_cache, wraps


def recurse_docs(documents_json, container_id, workspace_id):
    containers = [models.container.Container(
        c['name'], c['id'], container_id, workspace_id
    ) for c in documents_json['containers']]
    documents = [models.document.Document(
        d['name'], d['id'], d['modified_time'], container_id, workspace_id, d['last_modifier']
    ) for d in documents_json['documents']]
    urls = [models.url.Url(
        u['name'], u['id'], u['modified_time'], u['url'], container_id, workspace_id
    ) for u in documents_json['urls']]

    for c in documents_json['containers']:
        conts, docs, curls = recurse_docs(c['contents'], c['id'], workspace_id)
        containers += conts
        documents += docs
        urls += curls

    return containers, documents, urls


def parse_account_members(members_json):
    members = [models.user.User(
        u['id'], u['name'], u['email']
    ) for u in members_json['members'] + members_json['external']]

    return members


class cached_method:
    """Decorotor for class methods.
    Using pythons non data descriptor protocol, creates a new `functools.lru_cache` funcion wrapper
    on first access of a instances method to cache the methods return value.
    """
    def __new__(cls, func=None, **lru_kwargs):
        if func is None:
            def decorator(func):
                return cls(func=func, **lru_kwargs)
            return decorator
        return super().__new__(cls)

    def __init__(self, func=None, **lru_kwargs):
        self.func = func
        self.name = func.__name__
        self.lru_kwargs = lru_kwargs

    def __get__(self, instance, owner):
        if not instance:
            return self

        @wraps(self.func)
        def decorated_func(*args, **kwargs):
            return self.func(instance, *args, **kwargs)

        lru_cache_warpper = lru_cache(**self.lru_kwargs)(decorated_func)
        instance.__dict__[self.name] = lru_cache_warpper
        return lru_cache_warpper