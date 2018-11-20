import models.container
import models.document


def recurse_docs(documents_json, container_id, workspace_id):

    containers = [models.container.Container(
        c['name'], c['id'], container_id, workspace_id
    ) for c in documents_json['containers']]
    documents = [models.document.Document(
        d['name'], d['id'], d['modified_time'], container_id, workspace_id
    ) for d in documents_json['documents']]

    for c in documents_json['containers']:
        if c['contents']['size'] > 0:
            conts, docs = recurse_docs(c['contents'], c['id'], workspace_id)
            containers += conts
            documents += docs

    return containers, documents

