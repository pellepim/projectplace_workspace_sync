import sdk.connection
import db
import models.workspace
import models.document
import config
import sdk.utils
import sdk.html
import logging
import subprocess

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
                    dbconn.update_no_commit('INSERT INTO workspaces (id, name) VALUES (?, ?)', (workspace.id, workspace.name))
                elif workspace.name != existing_workspace_map[workspace.id]['name']:
                    logger.info('Updating name of %s', workspace)
                    dbconn.update_no_commit('UPDATE workspaces SET name = ? WHERE id = ?', (workspace.name, workspace.id))

            dbconn.conn.commit()

        for _id, ws in existing_workspace_map.items():
            if _id not in workspaces_ids:
                logger.info('Workspace %s, %s seems to be archived - not touching', _id, ws['name'])

        logger.info('Workspaces updated, moving on to documents')

        for workspace in workspaces:
            workspace_statements = []
            containers, documents, urls = sdk.connection.workspace_documents(workspace.id)

            for c in containers:
                workspace_statements += c.update_or_insert()

            for d in documents:
                workspace_statements += d.update_or_insert()

            for u in urls:
                workspace_statements += u.update_or_insert()

            with db.DBConnection() as dbconn:
                for statement in workspace_statements:
                    dbconn.update_no_commit(*statement)
                logging.info('Committing SQL queries for %r', workspace)
                dbconn.conn.commit()
                logging.info('Done')

        users = sdk.connection.account_members()
        user_statements = []
        for us in users:
            user_statements += us.update_or_insert()

        with db.DBConnection() as dbconn:
            for statement in user_statements:
                dbconn.update_no_commit(*statement)
            logging.info('Committing SQL queries for users')
            dbconn.conn.commit()
            logging.info('Done')

    @classmethod
    def download_docs(cls):
        documents = models.document.Document.by_pending_download()

        chunks = [documents[x:x+5] for x in range(0, len(documents), 5)]

        for chunk in chunks:
            processes = []
            successfully_downloaded = []
            logger.info('Downloading %d documents in parallel', len(chunk))
            for doc in chunk:
                processes.append(
                    (
                        subprocess.Popen(['python', 'download_doc.py', '-i', str(doc.id), '-w', str(doc.workspace_id), '-s', doc.file_ending]),
                        doc
                    )
                )

            for p, doc in processes:
                p.wait()
                if p.returncode != 0:
                    logger.error('Failed to download %s - will retry on next run (maybe it has been deleted remotely?)', doc)
                else:
                    successfully_downloaded.append(doc)

            with db.DBConnection() as dbconn:
                logger.info('Successfully downloaded %s, marking as downloaded', successfully_downloaded)
                for doc in successfully_downloaded:
                    dbconn.update_no_commit('UPDATE documents SET downloaded = 1 WHERE id = ?', (doc.id,))

                dbconn.conn.commit()

        for document in documents:
            document.download()

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
