import db
import logging

logger = logging.getLogger(__name__)


class Url(object):
    def __init__(self, _id, name, urllink, modified_time, container_id, workspace_id, description):
        self.id = _id
        self.name = name
        self.urllink = urllink
        self.modified_time = modified_time
        self.container_id = container_id
        self.workspace_id = workspace_id
        self.description = description

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    def update_or_insert(self):
        statements = []
        with db.DBConnection() as dbconn:
            row = dbconn.fetchone(
                '''
                SELECT name, urllink, modified_time, container_id, workspace_id, description FROM urls WHERE id = ?
                ''', (self.id,)
            )

            if row:
                if (row[0], row[1], row[2], row[3], row[4], row[5]) != (
                    self.name, self.urllink, self.modified_time, self.container_id, self.workspace_id, self.description
                ):
                    logger.info((row[0], row[1], row[2], row[3], row[4], row[5]))
                    logger.info((
                        self.name, self.urllink, self.modified_time, self.container_id, self.workspace_id, self.description
                    ))
                    logger.info('Updating Url %s', self)
                    statements.append(
                        (
                            '''
                            UPDATE urls 
                                SET name = ?, container_id = ?, modified_time = ?, workspace_id = ?, urllink = ?, 
                                    description = ?
                                WHERE id = ?
                            ''',
                            (
                                self.name, self.container_id, self.modified_time, self.workspace_id, self.urllink,
                                self.description, self.id
                            )
                        )
                    )

            else:
                logger.info('Inserting Url %s', self)
                statements.append(
                    (
                        '''
                        INSERT INTO urls (
                            id, name, urllink, modified_time, container_id, workspace_id, description
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            self.id, self.name, self.urllink, self.modified_time, self.container_id, self.workspace_id,
                            self.description
                        )
                    )
                )

        return statements

    @classmethod
    def get_in_container(cls, container_id):
        with db.DBConnection() as dbconn:
            url_rows = dbconn.fetchall(
                '''
                SELECT
                    id, name, urllink, modified_time, container_id, workspace_id, description 
                FROM urls 
                    WHERE container_id = ? ORDER BY name
                ''',
                (container_id,)
            )
        return [
            Url(*row) for row in url_rows
        ]
