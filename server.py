import flask
import sdk.html
import sdk.search
import logging
import boto3
import config
import models
import botocore.client
import requests
import os.path
import sdk.connection
import db
import sys

logging.basicConfig(stream=sys.stdout)

app = flask.Flask(__name__)


@app.route('/')
def index():
    workspaces = models.Workspace.get_all()
    to_return = sdk.html.render_index_page(workspaces, server=True)
    return to_return


@app.route('/search', methods=('GET', 'POST'))
def search():
    if flask.request.method == 'POST':
        query = flask.request.form.get('q', '')
        included_artifacts = flask.request.form.getlist('include_artifact')
        documents_checked = 'documents' in included_artifacts
        containers_checked = 'containers' in included_artifacts
        urls_checked = 'urls' in included_artifacts

        results = sdk.search.get_results(query, documents_checked, containers_checked, urls_checked)
        return sdk.html.render_search_page(
            query=query, results=results, documents_checked=documents_checked, containers_checked=containers_checked,
            urls_checked=urls_checked
        )

    return sdk.html.render_search_page()


@app.route('/workspace/<workspace_id>/sync')
def workspace_sync(workspace_id):
    return sdk.connection.workspace(workspace_id)


@app.route('/workspace/<workspace_id>')
def workspace(workspace_id):
    workspace = models.Workspace.get_by_id(int(workspace_id))
    containers = models.Container.get_in_container(int(workspace_id))
    documents = models.Document.get_in_container(int(workspace_id))
    urls = models.Url.get_in_container(int(workspace_id))
    to_return = sdk.html.render_workspace_page(workspace, containers, documents, urls, server=True)

    return to_return


@app.route('/container/<container_id>')
def container(container_id):
    container = models.Container.get_by_id(int(container_id))
    workspace = models.Workspace.get_by_id(container.workspace_id)
    containers = models.Container.get_in_container(int(container_id))
    documents = models.Document.get_in_container(int(container_id))
    urls = models.Url.get_in_container(int(container_id))
    return sdk.html.render_container_page(workspace, container, containers, documents, urls, server=True)


def _get_s3_client():
    if config.conf.S3_SETTINGS:
        session: boto3.Session = boto3.Session(
            aws_access_key_id=config.conf.S3_SETTINGS.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.conf.S3_SETTINGS.AWS_SECRET_ACCESS_KEY,
        )
        s3_client = session.client('s3', config=botocore.client.Config(s3={'addressing_style': 'path'}))
        bucket_location = s3_client.get_bucket_location(
            Bucket=config.conf.S3_SETTINGS.BUCKET_NAME
        ).get('LocationConstraint')
        s3_client = session.client(
            's3', bucket_location, config=botocore.client.Config(s3={'addressing_style': 'path'})
        )
        return s3_client

    return None


def _stream_download_from_s3(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return local_filename


def _download_from_s3(document_id, s3_client):
    document = models.Document.get_by_id(int(document_id))
    key = document.local_filename
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': config.conf.S3_SETTINGS.BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=10
    )
    temp_file = os.path.join(config.conf.FILESTORAGE_PATH, 'tmp', str(document_id))

    _stream_download_from_s3(url, temp_file)

    return flask.send_file(
        temp_file, as_attachment=True, attachment_filename=document.name, add_etags=True, cache_timeout=-1
    )


def _download_from_file_system(document_id):
    document = models.Document.get_by_id(int(document_id))

    file_path = os.path.join(config.conf.FILESTORAGE_PATH, str(document.workspace_id), document.local_filename)

    return flask.send_file(
        file_path, as_attachment=True, attachment_filename=document.name, add_etags=True, cache_timeout=-1
    )


@app.route('/document/<document_id>')
def document(document_id):
    s3_client = _get_s3_client()

    if not os.path.isdir(os.path.join(config.conf.FILESTORAGE_PATH, 'tmp')):
        os.mkdir(os.path.join(config.conf.FILESTORAGE_PATH, 'tmp'))
    else:
        for filename in os.listdir(os.path.join(config.conf.FILESTORAGE_PATH, 'tmp')):
            file_path = os.path.join(config.conf.FILESTORAGE_PATH, 'tmp', filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logging.exception('Failed to delete %s, %s' % (file_path, e))

    if s3_client:
        return _download_from_s3(document_id, s3_client)

    return _download_from_file_system(document_id)


@app.route('/setup')
def setup():
    if config.conf.is_valid():
        with db.DBConnection() as dbconn:
            dbconn.verify_db()
        return 'All seems to be well - do you want to <a href="/sync">sync</a>?'
    else:
        return 'Make sure config.json is valid'


@app.route('/sync')
def sync():
    pass

