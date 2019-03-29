import db
import functools
import logging
from models.exceptions import InvalidComparisonError

logger = logging.getLogger(__name__)


class User(object):
    def __init__(self, _id, name, email):
        self.id = _id
        self.name = name
        self.email = email

    @classmethod
    @functools.lru_cache(None)
    def get_by_id(cls, _id):
        with db.DBConnection() as dbconn:
            user_row = dbconn.fetchone(
                'SELECT id, name, email FROM users WHERE id = ?',
                (_id,)
            )
            if user_row:
                return User(*user_row)

        return None

    def __eq__(self, other):
        if other.id != self.id:
            raise InvalidComparisonError('Can only compare user objects with the same ID')

        return (self.name, self.email) == (other.name, other.email)

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    def update_or_insert(self):
        existing_user = User.get_by_id(self.id)
        statements = []

        if existing_user is None:
            logging.info('%r does not exist - creating', self)
            statements.append(
                (
                    'INSERT INTO users (id, name, email) VALUES (?, ?, ?)',
                    (self.id, self.name, self.email)
                )
            )
        elif isinstance(existing_user, User) and existing_user != self:
            logging.info('%r exists - but has changed - updating', self)
            statements.append(
                (
                    'UPDATE users SET name = ?, email = ? WHERE id = ?',
                    (self.name, self.email, self.id)
                )
            )

        return statements
