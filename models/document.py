import db
import requests
import config
import sdk.connection
import os


class Document(object):

    def __init__(self, name, _id, modified_time, container_id, workspace_id):
        self.name = name
        self.id = _id
        self.container_id = container_id
        self.modified_time = modified_time
        self.workspace_id = workspace_id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    def update_or_insert(self):
        needs_download = False
        with db.DBConnection() as dbconn:
            row = dbconn.fetchone(
                'SELECT id, name, container_id, modified_time, workspace_id FROM documents WHERE id = ?', (self.id,)
            )

            if row:
                if (row[1], row[2], row[3], row[4]) != (self.name, self.container_id, self.modified_time, self.workspace_id):
                    print('Updating document', self)
                    dbconn.update(
                        'UPDATE documents SET name = ?, container_id = ?, modified_time = ?, workspace_id = ? WHERE id = ?',
                        (self.name, self.container_id, self.modified_time, self.workspace_id, self.id)
                    )

                # Document has new modified time or workspace_id - needs to be re-downloaded
                if row[3] != self.modified_time or row[4] != self.workspace_id:
                    needs_download = True

            else:
                print('Inserting document', self)
                dbconn.update('INSERT INTO documents (id, name, container_id, modified_time, workspace_id) VALUES (?, ?, ?, ?, ?)', (
                    self.id, self.name, self.container_id, self.modified_time, self.workspace_id
                ))

                needs_download = True

            if needs_download:
                dbconn.update('UPDATE documents SET downloaded = 0 WHERE id = ?', (self.id,))

        return needs_download

    @classmethod
    def get_in_container(cls, container_id):
        with db.DBConnection() as dbconn:
            document_rows = dbconn.fetchall(
                'SELECT name, id, modified_time, container_id, workspace_id FROM documents WHERE container_id = ? ORDER BY name ASC',
                (container_id,)
            )
        return [
            Document(*row) for row in document_rows
        ]

    @classmethod
    def by_pending_download(cls):
        with db.DBConnection() as dbconn:
            document_rows = dbconn.fetchall(
                'SELECT name, id, modified_time, container_id, workspace_id FROM documents WHERE downloaded = 0'
            )

        return [Document(*row) for row in document_rows]

    @property
    def local_filename(self):
        if '.' in self.name:
            file_ending = self.name.split('.')[-1]
            return '%s.%s' % (self.id, file_ending)

        return self.id

    @property
    def local_file_location(self):
        return os.path.join('localdata/%s' % self.workspace_id)

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






