import sdk.connection
import db
import models.workspace
import models.document
import config
import sdk.utils
import sdk.html
import logging
import sqlite3

class Structure(object):
    boto_session = None
    s3_resource = None

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
        logging.info('Fetching workspace data... ')

        workspaces = sdk.connection.account_workspaces()

        if config.conf.WORKSPACE_IDS:
            logging.info('Limited sync, check config for specific workspaces synchronized')
            workspaces = [w for w in workspaces if w.id in config.conf.WORKSPACE_IDS]
        workspaces_ids = [w.id for w in workspaces]

        with db.DBConnection() as dbconn:
            existing_workspace_map = self.workspaces_from_db(dbconn)
            for workspace in workspaces:
                if workspace.id not in existing_workspace_map:
                    logging.info('Adding %s to DB', workspace)
                    dbconn.update_no_commit('INSERT INTO workspaces (id, name) VALUES (?, ?)', (workspace.id, workspace.name))
                elif workspace.name != existing_workspace_map[workspace.id]['name']:
                    logging.info('Updating name of %s', workspace)
                    dbconn.update_no_commit('UPDATE workspaces SET name = ? WHERE id = ?', (workspace.name, workspace.id))

            dbconn.conn.commit()

        for _id, ws in existing_workspace_map.items():
            if _id not in workspaces_ids:
                logging.info('Workspace %s, %s seems to be archived - not touching', _id, ws['name'])

            logging.info('Fetching document data for %d workspaces', len(workspaces))

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
                    try:
                        dbconn.update_no_commit(*statement)
                    except sqlite3.IntegrityError as e:
                        logging.exception('Failed on statement %s', statement)
                        raise
                logging.info('Committing SQL queries for %r', workspace)
                dbconn.conn.commit()
                logging.info('Done')

        users = sdk.connection.account_members()
        user_statements = []
        logging.info('Updating user information... ')
        for us in users:
            user_statements += us.update_or_insert()

        with db.DBConnection() as dbconn:
            for statement in user_statements:
                dbconn.update_no_commit(*statement)
            logging.info('Committing SQL queries for users')
            dbconn.conn.commit()
            logging.info('Done')

        logging.info('Setting up search')
        with db.DBConnection() as dbconn:
            dbconn.update(
                '''
                delete from search
                '''
            )
            dbconn.update(
                '''
                insert into search select id, name, description, 'doc' from documents
                '''
            )
            dbconn.update(
                '''
                insert into search select id, name, description, 'cont' from containers
                '''
            )

    @classmethod
    def download_one(cls, document_id, workspace_id, file_ending):
        import os.path
        import boto3
        doc_response = sdk.connection.download_doc(document_id)

        file_location = os.path.join(config.conf.FILESTORAGE_PATH, str(workspace_id))

        if config.conf.S3_SETTINGS:
            if cls.boto_session is None:
                session = boto3.Session(
                    aws_access_key_id=config.conf.S3_SETTINGS.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.conf.S3_SETTINGS.AWS_SECRET_ACCESS_KEY,
                )
                cls.s3_resource = session.resource('s3')

            cls.s3_resource.Bucket(config.conf.S3_SETTINGS.BUCKET_NAME).put_object(
                Key='%d.%s' % (document_id, file_ending), Body=doc_response.content
            )
            return True, document_id
        else:
            if not os.path.exists(file_location):
                os.makedirs(file_location)

            file_path = os.path.join(file_location, '%d.%s' % (document_id, file_ending))

            with open(file_path, 'wb') as fp:
                fp.write(doc_response.content)

            return True, document_id

        return False, document_id

    @classmethod
    def download_docs(cls):
        import multiprocessing

        documents = models.document.Document.by_pending_download()
        total_remaining = len(documents)
        chunks = [documents[x:x + 5] for x in range(0, len(documents), 5)]

        if not total_remaining:
            logging.info('All documents already downloaded')
        else:
            logging.info('Document download progress')

        for chunk in chunks:
            logging.info('Downloading %d documents in parallel', len(chunk))
            pool = multiprocessing.Pool(len(chunk))
            args = []
            for doc in chunk:
                args.append((doc.id, doc.workspace_id, doc.file_ending))
            result = pool.starmap(cls.download_one, args)
            pool.close()
            pool.join()
            successfully_downloaded = [res[1] for res in result]

            with db.DBConnection() as dbconn:
                logging.info('Successfully downloaded %s, marking as downloaded', successfully_downloaded)
                for doc_id in successfully_downloaded:
                    dbconn.update_no_commit('UPDATE documents SET downloaded = 1 WHERE id = ?', (doc_id,))

                dbconn.conn.commit()
