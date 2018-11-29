import db
import models.document
import models.workspace
import models.url
import sdk.utils
import sdk.html
import functools
import logging

logger = logging.getLogger(__name__)


class Container(object):

    def __init__(self, name, _id, container_id, workspace_id):
        self.name = name
        self.id = _id
        self.container_id = container_id
        self.workspace_id = workspace_id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    def update_or_insert(self):
        with db.DBConnection() as dbconn:
            row = dbconn.fetchone('SELECT id, name, container_id, workspace_id FROM containers WHERE id = ?', (self.id,))

            if row:
                if row[1] != self.name or row[2] != self.container_id or row[3] != self.workspace_id:
                    logger.info('Updating container %s', self)
                    dbconn.update('UPDATE containers SET name = ?, container_id = ?, workspace_id = ? WHERE id = ?', (
                        self.name, self.container_id, self.workspace_id, self.id
                    ))
            else:
                logger.info('Inserting container %s', self)
                dbconn.update('INSERT INTO containers (id, name, container_id, workspace_id) VALUES (?, ?, ?, ?)', (
                    self.id, self.name, self.container_id, self.workspace_id
                ))

    @classmethod
    def get_in_container(cls, container_id):
        with db.DBConnection() as dbconn:
            container_rows = dbconn.fetchall(
                'SELECT id, name, container_id, workspace_id FROM containers WHERE container_id = ? ORDER BY name ASC',
                (container_id,)
            )

        return [
            Container(row[1], row[0], row[2], row[3]) for row in container_rows
        ]

    @classmethod
    @functools.lru_cache(None)
    def get_by_id(cls, container_id):
        with db.DBConnection() as dbconn:
            container_row = dbconn.fetchone(
                'SELECT id, name, container_id, workspace_id FROM containers WHERE id = ?', (container_id,)
            )

        if container_row:
            return Container(container_row[1], container_row[0], container_row[2], container_row[3])

        return None

    @property
    def container_path(self):
        path = [self]

        parent = Container.get_by_id(self.container_id)

        if parent is not None:
            path = [parent] + path

        while parent is not None:
            parent = Container.get_by_id(parent.container_id)
            if parent is not None:
                path = [parent] + path

        return path

    @property
    def workspace(self):
        return models.workspace.Workspace.get_by_id(self.workspace_id)

    def render_html(self):
        containers = Container.get_in_container(self.id)
        documents = models.document.Document.get_in_container(self.id)
        urls = models.url.Url.get_in_container(self.id)

        for container in containers:
            container.render_html()

        sdk.html.render_container_page(self.workspace, self, containers, documents, urls)
