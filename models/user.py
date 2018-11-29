import db
import functools


class InvalidComparisonError(Exception):
    pass


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

        with db.DBConnection() as dbconn:
            if existing_user is None:
                print(self, 'does not exist - creating')
                dbconn.update(
                    'INSERT INTO users (id, name, email) VALUES (?, ?, ?)',
                    (self.id, self.name, self.email)
                )
            elif isinstance(existing_user, User) and existing_user != self:
                print(self, 'exists - but has changed - updating')
                dbconn.update(
                    'UPDATE users SET name = ?, email = ? WHERE id = ?',
                    (self.name, self.email, self.id)
                )
