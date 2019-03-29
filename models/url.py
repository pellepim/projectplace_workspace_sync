import db
import logging

logger = logging.getLogger(__name__)

class Url(object):
    def __init__(self, name, _id, modified_time, urllink, container_id, workspace_id):
        self.name = name
        self.id = _id
        self.modified_time = modified_time
        self.urllink = urllink
        self.container_id = container_id
        self.workspace_id = workspace_id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    def update_or_insert(self):
        statements = []
        with db.DBConnection() as dbconn:
            row = dbconn.fetchone(
                'SELECT name, id, modified_time, urllink, container_id, workspace_id FROM urls WHERE id = ?', (self.id,)
            )

            if row:
                if (row[0], row[2], row[3], row[4], row[5]) != (self.name, self.modified_time, self.urllink, self.container_id, self.workspace_id):
                    logger.info('Updating Url %s', self)
                    statements.append(
                        (
                            'UPDATE urls SET name = ?, container_id = ?, modified_time = ?, workspace_id = ?, urllink = ? WHERE id = ?',
                            (self.name, self.container_id, self.modified_time, self.workspace_id, self.urllink, self.id)
                        )
                    )

            else:
                logger.info('Inserting Url %s', self)
                statements.append(
                    (
                        'INSERT INTO urls (name, id, modified_time, urllink, container_id, workspace_id) VALUES (?, ?, ?, ?, ?, ?)',
                        (self.name, self.id, self.modified_time, self.urllink, self.container_id, self.workspace_id)
                    )
                )

        return statements

    @classmethod
    def get_in_container(cls, container_id):
        with db.DBConnection() as dbconn:
            url_rows = dbconn.fetchall(
                'SELECT name, id, modified_time, urllink, container_id, workspace_id FROM urls WHERE container_id = ? ORDER BY name ASC',
                (container_id,)
            )
        return [
            Url(*row) for row in url_rows
        ]
