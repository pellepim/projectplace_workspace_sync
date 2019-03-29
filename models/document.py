import db
import sdk.connection
import os
import models.user
import models.exceptions
import logging
import config

logger = logging.getLogger(__name__)


class Document(object):
    SQL_SELECT_BY_ID = """
        SELECT name, id, modified_time, container_id, workspace_id, modified_by_id FROM documents WHERE id = ?
    """
    SQL_UPDATE_BY_ID = """
        UPDATE documents SET 
            name = ?, container_id = ?, modified_time = ?, workspace_id = ?, modified_by_id = ? 
        WHERE id = ?
    """

    def __init__(self, name, _id, modified_time, container_id, workspace_id, modified_by_id):
        self.name = name
        self.id = _id
        self.container_id = container_id
        self.modified_time = modified_time
        self.workspace_id = workspace_id
        self.modified_by_id = modified_by_id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    @property
    def modified_by(self):
        return models.user.User.get_by_id(self.modified_by_id)

    def __eq__(self, other):
        if self.id != other.id:
            raise models.exceptions.InvalidComparisonError('Documents must have same ID in order to be compared')

        return (self.name, self.container_id, self.modified_time, self.workspace_id, self.modified_by_id) == \
               (other.name, other.container_id, other.modified_time, other.workspace_id, other.modified_by_id)

    @classmethod
    def get_by_id(cls, _id):
        with db.DBConnection() as dbconn:
            document_row = dbconn.fetchone(cls.SQL_SELECT_BY_ID, (_id,))

            if document_row:
                return Document(*document_row)

        return None

    def update_or_insert(self):
        needs_download = False
        existing_document = Document.get_by_id(self.id)
        statements = []

        if existing_document is None:
            logger.info('Inserting document %s', self)
            statements.append(
                (
                    'INSERT INTO documents (id, name, container_id, modified_time, workspace_id, modified_by_id) VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        self.id, self.name, self.container_id, self.modified_time, self.workspace_id,
                        self.modified_by_id
                    )
                )
            )

            needs_download = True
        if isinstance(existing_document, Document) and self != existing_document:
            logger.info('Updating document %s', self)
            statements.append(
                (
                    self.SQL_UPDATE_BY_ID,
                    (self.name, self.container_id, self.modified_time, self.workspace_id, self.modified_by_id, self.id)
                )
            )

            # Document has new modified time or workspace_id - needs to be re-downloaded
            if existing_document.modified_time != self.modified_time or existing_document.workspace_id != self.workspace_id:
                needs_download = True

        if needs_download:
            statements.append(
                (
                    'UPDATE documents SET downloaded = 0 WHERE id = ?',
                    (self.id,)
                )
            )

        return statements

    @classmethod
    def get_in_container(cls, container_id):
        with db.DBConnection() as dbconn:
            document_rows = dbconn.fetchall(
                'SELECT name, id, modified_time, container_id, workspace_id, modified_by_id FROM documents WHERE container_id = ? ORDER BY name ASC',
                (container_id,)
            )
        return [
            Document(*row) for row in document_rows
        ]

    @classmethod
    def by_pending_download(cls):
        with db.DBConnection() as dbconn:
            document_rows = dbconn.fetchall(
                'SELECT name, id, modified_time, container_id, workspace_id, modified_by_id FROM documents WHERE downloaded = 0'
            )

        return [Document(*row) for row in document_rows]

    @property
    def modified_time_iso(self):
        import datetime
        return datetime.datetime.utcfromtimestamp(self.modified_time)

    @property
    def local_filename(self):
        if '.' in self.name:
            file_ending = self.name.split('.')[-1]
            return '%s.%s' % (self.id, file_ending)

        return self.id

    @property
    def local_file_location(self):
        return os.path.join(config.conf.FILESTORAGE_PATH, str(self.workspace_id))

    @property
    def local_filepath(self):
        return os.path.join(self.local_file_location, str(self.local_filename))

    def download(self):
        doc_response = sdk.connection.download_doc(self.id)

        if not os.path.exists(self.local_file_location):
            os.makedirs(self.local_file_location)

        with open(self.local_filepath, 'wb') as fp:
            fp.write(doc_response.content)

        with db.DBConnection() as dbconn:
            dbconn.update('UPDATE documents SET downloaded = 1 WHERE id = ?', (self.id,))
