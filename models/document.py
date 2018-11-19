import db


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

        return needs_download

