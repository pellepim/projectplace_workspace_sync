import sdk.connection
import db


class Structure(object):

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

    def initialize(self):
        workspaces = sdk.connection.account_workspaces()
        workspaces_ids = [w.id for w in workspaces]
        documents_that_need_download = []

        with db.DBConnection() as dbconn:
            existing_workspace_map = self.workspaces_from_db(dbconn)
            for workspace in workspaces:
                if workspace.id not in existing_workspace_map:
                    print('Adding', workspace, 'to DB')
                    dbconn.update('INSERT INTO workspaces (id, name) VALUES (?, ?)', (workspace.id, workspace.name))
                elif workspace.name != existing_workspace_map[workspace.id]['name']:
                    print('Updating name of', workspace)
                    dbconn.update('UPDATE workspaces SET name = ? WHERE id = ?', (workspace.name, workspace.id))

        for _id, ws in existing_workspace_map.items():
            if _id not in workspaces_ids:
                print('Workspace', _id, ws['name'], 'seems to be archived - not touching')

        print('Workspaces updated, moving on to documents')

        for workspace in workspaces:
            containers, documents = sdk.connection.workspace_documents(workspace.id)

            for c in containers:
                c.update_or_insert()

            for d in documents:
                if d.update_or_insert():
                    documents_that_need_download += [d]

    def download_documents(self, documents_that_need_download):
        print('Downloading', documents_that_need_download)
