import db


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
                    print('Updating container', self)
                    dbconn.update('UPDATE containers SET name = ?, container_id = ?, workspace_id = ? WHERE id = ?', (
                        self.name, self.container_id, self.workspace_id, self.id
                    ))
            else:
                print('Inserting container', self)
                dbconn.update('INSERT INTO containers (id, name, container_id, workspace_id) VALUES (?, ?, ?, ?)', (
                    self.id, self.name, self.container_id, self.workspace_id
                ))
