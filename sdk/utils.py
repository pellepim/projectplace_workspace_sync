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


def html_header(title, breadcrumbs):
    return """
        <html>
        <head>
            <title>%(title)s</title>
            <style type="text/css">
                body {
                    font-size: 16px;
                    font-family: "PromixaNovaRegular", "AvenirRegular", Arial, Helvetica, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                a {
                    color: #559955;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                a:visited {
                    color: #997777;
                }
                div.breadcrumbs {
                    margin: 0px;
                    padding: 20px;
                    border-bottom: 2px solid #ddd;
                    background-color: #f5f5f5;
                }
                ul li {
                    margin-bottom: 10px;
                }
                div.content {
                    padding: 10px 20px 0 20px;
                }
                h3 {
                    display: flex;
                    height: 1em;
                }
                h3 svg {
                    height: 1em;
                }
            </style>
        </head>
        <body>
            %(breadcrumbs)s 
            <div class="content">
        """ % {
        'title': title,
        'breadcrumbs': breadcrumbs
    }


