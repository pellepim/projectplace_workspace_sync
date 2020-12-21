import config
import os
import codecs


def ensure_path(func):
    def func_wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            if not os.path.exists(os.path.join(config.conf.FILESTORAGE_PATH, 'html')):
                os.makedirs(os.path.join(config.conf.FILESTORAGE_PATH, 'html'))
            return func(*args, **kwargs)

    return func_wrapper


@ensure_path
def render_index_page(workspaces, server=False):
    if server:
        template = config.jinja_env.get_template('index-server.html')
        return template.render(workspaces=workspaces)

    template = config.jinja_env.get_template('index.html')
    rendered = template.render(workspaces=workspaces)
    with codecs.open(os.path.join(config.conf.FILESTORAGE_PATH, 'html', 'index.html'), 'w', 'utf-8-sig') as fp:
        fp.write(rendered)


def render_search_page(query='', results=None, documents_checked=None, containers_checked=None, urls_checked=None):
    if results is None:
        results = []

    template = config.jinja_env.get_template('search.html')

    documents_checked = 'checked' if documents_checked or documents_checked is None else ''
    containers_checked = 'checked' if containers_checked or containers_checked is None else ''
    urls_checked = 'checked' if urls_checked or urls_checked is None else ''

    return template.render(
        query=query, results=results, documents_checked=documents_checked, containers_checked=containers_checked,
        urls_checked=urls_checked
    )


@ensure_path
def render_workspace_page(workspace, containers, documents, urls, server=False):
    if server:
        template = config.jinja_env.get_template('workspace-server.html')
        return template.render(workspace=workspace, containers=containers, documents=documents, urls=urls)

    template = config.jinja_env.get_template('workspace.html')
    rendered = template.render(workspace=workspace, containers=containers, documents=documents, urls=urls)

    with codecs.open(os.path.join(config.conf.FILESTORAGE_PATH, 'html', '%d.html' % workspace.id), 'w', 'utf-8-sig') as fp:
        fp.write(rendered)


@ensure_path
def render_container_page(workspace, container, containers, documents, urls, server=False):
    if server:
        template = config.jinja_env.get_template('container-server.html')
        return template.render(
            workspace=workspace, container=container, containers=containers, documents=documents, urls=urls
        )

    template = config.jinja_env.get_template('container.html')
    rendered = template.render(
        workspace=workspace, container=container, containers=containers, documents=documents, urls=urls
    )

    with codecs.open(os.path.join(config.conf.FILESTORAGE_PATH, 'html', '%d.html' % container.id), 'w', 'utf-8-sig') as fp:
        fp.write(rendered)
