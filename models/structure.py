import sdk.connection
import db
import models.workspace
import models.document
import config
import sdk.utils
import sys
import sdk.html
import logging

logger = logging.getLogger(__name__)


class Structure(object):
    def __init__(self):
        db.DBConnection().verify_db()

    @classmethod
    def workspaces_from_db(cls, dbconn):
        workspace_map = {}
        rows = dbconn.fetchall('SELECT id, name FROM workspaces')
        for row in rows:
            workspace_map[row[0]] = {
                'id': row[0],
                'name': row[1]
            }

        return workspace_map

    def synchronize(self):
        workspaces = sdk.connection.account_workspaces()
        if config.conf.WORKSPACE_IDS:
            logger.info('Limited sync, check config for specific workspaces synchronized')
            workspaces = [w for w in workspaces if w.id in config.conf.WORKSPACE_IDS]
        workspaces_ids = [w.id for w in workspaces]

        with db.DBConnection() as dbconn:
            existing_workspace_map = self.workspaces_from_db(dbconn)
            for workspace in workspaces:
                if workspace.id not in existing_workspace_map:
                    logger.info('Adding %s to DB', workspace)
                    dbconn.update('INSERT INTO workspaces (id, name) VALUES (?, ?)', (workspace.id, workspace.name))
                elif workspace.name != existing_workspace_map[workspace.id]['name']:
                    logger.info('Updating name of %s', workspace)
                    dbconn.update('UPDATE workspaces SET name = ? WHERE id = ?', (workspace.name, workspace.id))

        for _id, ws in existing_workspace_map.items():
            if _id not in workspaces_ids:
                logger.info('Workspace %s, %s seems to be archived - not touching', _id, ws['name'])

        logger.info('Workspaces updated, moving on to documents')

        for workspace in workspaces:
            containers, documents, urls = sdk.connection.workspace_documents(workspace.id)

            for c in containers:
                c.update_or_insert()

            for d in documents:
                d.update_or_insert()

            for u in urls:
                u.update_or_insert()

        users = sdk.connection.account_members()

        for u in users:
            u.update_or_insert()

    @classmethod
    def download_docs(cls):
        documents = models.document.Document.by_pending_download()
        no = len(documents)
        current = 1
        for document in documents:
            document_name = document.name if len(document.name) < 60 else document.name[0:50] + '...' + document.name[-5:]
            logger.info('Downloading: %d / %d (%s)' % (current, no, document_name))
            document.download()
            current += 1
        sys.stdout.write('\n')

    @classmethod
    def render_html(self):
        with db.DBConnection() as dbconn:
            workspace_rows = dbconn.fetchall('SELECT name, id FROM workspaces ORDER BY name ASC')
            workspaces = [
                models.workspace.Workspace(*row) for row in workspace_rows
            ]

        for workspace in workspaces:
            workspace.render_html()

        sdk.html.render_index_page(workspaces)
