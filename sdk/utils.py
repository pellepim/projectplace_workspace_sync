import models.container
import models.document
import models.url


def recurse_docs(documents_json, container_id, workspace_id):
    containers = [models.container.Container(
        c['name'], c['id'], container_id, workspace_id
    ) for c in documents_json['containers']]
    documents = [models.document.Document(
        d['name'], d['id'], d['modified_time'], container_id, workspace_id
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
