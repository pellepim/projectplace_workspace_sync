import db
import models.container
import models.document
import models.url
import sdk.utils
import sdk.html


class Workspace(object):

    def __init__(self, name, _id):
        self.name = name
        self.id = _id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    @classmethod
    def get_by_id(cls, workspace_id):
        with db.DBConnection() as dbconn:
            workspace_row = dbconn.fetchone(
                'SELECT name, id FROM workspaces WHERE id = ?', (workspace_id,)
            )

        if workspace_row:
            return Workspace(*workspace_row)

        return None

    @classmethod
    def get_all(cls):
        with db.DBConnection() as dbconn:
            workspace_rows = dbconn.fetchall(
                """
                select name, id from workspaces order by id
                """
            )

            return [Workspace(*workspace_row) for workspace_row in workspace_rows]

    def render_html(self):
        containers = models.container.Container.get_in_container(self.id)
        documents = models.document.Document.get_in_container(self.id)
        urls = models.url.Url.get_in_container(self.id)

        for container in containers:
            container.render_html()

        sdk.html.render_workspace_page(self, containers, documents, urls)

