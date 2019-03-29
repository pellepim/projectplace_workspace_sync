import config
import os
import codecs

def ensure_path(func):
    def func_wrapper(*args):
        try:
            return func(*args)
        except FileNotFoundError:
            if not os.path.exists(os.path.join(config.conf.FILESTORAGE_PATH, 'html')):
                os.makedirs(os.path.join(config.conf.FILESTORAGE_PATH, 'html'))
            return func(*args)

    return func_wrapper


@ensure_path
def render_index_page(workspaces):
    template = config.jinja_env.get_template('index.html')
    rendered = template.render(workspaces=workspaces)

    with codecs.open(os.path.join(config.conf.FILESTORAGE_PATH, 'html', 'index.html'), 'w', 'utf-8-sig') as fp:
        fp.write(rendered)


@ensure_path
def render_workspace_page(workspace, containers, documents, urls):
    template = config.jinja_env.get_template('workspace.html')
    rendered = template.render(workspace=workspace, containers=containers, documents=documents, urls=urls)

    with codecs.open(os.path.join(config.conf.FILESTORAGE_PATH, 'html', '%d.html' % workspace.id), 'w', 'utf-8-sig') as fp:
        fp.write(rendered)


@ensure_path
def render_container_page(workspace, container, containers, documents, urls):
    template = config.jinja_env.get_template('container.html')
    rendered = template.render(
        workspace=workspace, container=container, containers=containers, documents=documents, urls=urls
    )

    with codecs.open(os.path.join(config.conf.FILESTORAGE_PATH, 'html', '%d.html' % container.id), 'w', 'utf-8-sig') as fp:
        fp.write(rendered)
