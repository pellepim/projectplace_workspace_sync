import config
import os


def ensure_path(func):
    def func_wrapper(*args):
        try:
            return func(*args)
        except FileNotFoundError:
            if not os.path.exists('localdata/html'):
                os.makedirs('localdata/html')
    return func_wrapper


@ensure_path
def render_index_page(workspaces):
    template = config.jinja_env.get_template('index.html')
    rendered = template.render(workspaces=workspaces)

    with open('localdata/html/index.html', 'w') as fp:
        fp.write(rendered)


@ensure_path
def render_workspace_page(workspace, containers, documents, urls):
    template = config.jinja_env.get_template('workspace.html')
    rendered = template.render(workspace=workspace, containers=containers, documents=documents, urls=urls)

    with open('localdata/html/%d.html' % workspace.id, 'w') as fp:
        fp.write(rendered)


@ensure_path
def render_container_page(workspace, container, containers, documents, urls):
    template = config.jinja_env.get_template('container.html')
    rendered = template.render(
        workspace=workspace, container=container, containers=containers, documents=documents, urls=urls
    )

    with open('localdata/html/%d.html' % container.id, 'w') as fp:
        fp.write(rendered)
