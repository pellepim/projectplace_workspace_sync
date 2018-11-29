import sqlite3

DB_INIT = [
    """
    CREATE TABLE IF NOT EXISTS [workspaces] (
        [id] INTEGER PRIMARY KEY,
        [name] text
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS [containers] (
        [id] INTEGER PRIMARY KEY,
        [name] text,
        [container_id] INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS [documents] (
        [id] INTEGER PRIMARY KEY,
        [name] text,
        [container_id] INTEGER,
        [modified_time] INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS [changelog] (
      [id] INTEGER PRIMARY KEY,
      [statement] text
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS [urls] (
      [id] INTEGER PRIMARY KEY,
      [name] text,
      [urllink] text,
      [modified_time] INTEGER,
      [container_id] INTEGER,
      [workspace_id] INTEGER
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS documents_workspace_id ON documents(workspace_id) 
    """,
    """
    CREATE INDEX IF NOT EXISTS documents_container_id ON documents(container_id) 
    """,
    """
    CREATE INDEX IF NOT EXISTS container_workspace_id ON containers(workspace_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS container_container_id ON containers(container_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS url_workspace_id ON urls(workspace_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS url_container_id ON urls(container_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS [users] (
      [id] INTEGER PRIMARY KEY,
      [name] text
    );
    """,
]

MIGRATIONS = [
    """
    ALTER TABLE [containers] ADD COLUMN [workspace_id] INTEGER;
    """,
    """
    ALTER TABLE [documents] ADD COLUMN [workspace_id] INTEGER;
    """,
    """
    ALTER TABLE [documents] ADD COLUMN [downloaded] BIT DEFAULT 0;
    """,
    """
    ALTER TABLE [documents] ADD COLUMN [modified_by_id] INTEGER;
    """,
    """
    ALTER TABLE [users] ADD COLUMN [email] TEXT;
    """
]


class DBConnection(object):
    def __init__(self):
        self.conn = sqlite3.Connection('.data')
        self.cursor = None

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def update(self, statement, parameters=None):
        self.execute(statement, parameters)
        self.conn.commit()

    def execute(self, statement, parameters=None):
        if not parameters:
            self.cursor.execute(statement)
        else:
            self.cursor.execute(statement, parameters)

    def fetchall(self, statement, parameters=None):
        self.execute(statement, parameters)
        return self.cursor.fetchall()

    def fetchone(self, statement, parameters=None):
        self.execute(statement, parameters)
        return self.cursor.fetchone()

    def verify_db(self):
        c = self.conn.cursor()

        for s in DB_INIT:
            c.execute(s)

        for m in MIGRATIONS:
            c.execute('SELECT statement FROM changelog')
            run_migrations = [run_migration[0] for run_migration in c.fetchall()]
            if m not in run_migrations:
                c.execute(m)
                c.execute('INSERT INTO changelog (statement) VALUES (?)', (m,))

        self.conn.commit()
        self.conn.close()

