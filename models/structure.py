import sdk.connection
import db
import models.workspace
import models.document
import os
import config
import textwrap
import sys


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

    def synchronize(self):
        workspaces = sdk.connection.account_workspaces()
        if config.conf.WORKSPACE_IDS:
            print('Limited sync, check config for specific workspaces synchronized')
            workspaces = [w for w in workspaces if w.id in config.conf.WORKSPACE_IDS]
        workspaces_ids = [w.id for w in workspaces]

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
                d.update_or_insert()

    @classmethod
    def download_docs(cls):
        documents = models.document.Document.by_pending_download()
        no = len(documents)
        current = 1
        previous_len = 0
        for document in documents:
            sys.stdout.write('\r' + ' ' * previous_len)
            sys.stdout.flush()
            document_name = document.name if len(document.name) < 60 else document.name[0:50] + '...' + document.name[-5:]
            to_print = 'Downloading: %d / %d (%s)' % (current, no, document_name)
            previous_len = len(to_print)
            sys.stdout.write('\r' + to_print)
            sys.stdout.flush()
            document.download()
            current += 1
        sys.stdout.write('\n')

    @property
    def html_file_location(self):
        if not os.path.exists('localdata/html'):
            os.makedirs('localdata/html')

        return 'localdata/html'

    @property
    def html_file_path(self):
        return os.path.join(self.html_file_location, 'index.html')

    @property
    def html_header(self):
        return textwrap.dedent("""
        <html>
        <head>
            <title>Projects</title>
            <style type="text/css">
                body {
                    font-size: 16px;
                    font-family: "PromixaNovaRegular", "AvenirRegular", Arial, Helvetica, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                a {
                    color: #559955;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                a:visited {
                    color: #997777;
                }
                div.breadcrumbs {
                    margin: 0px;
                    padding: 20px;
                    border-bottom: 2px solid #ddd;
                    background-color: #f5f5f5;
                }
                ul li {
                    margin-bottom: 10px;
                }
                div.content {
                    padding: 10px 20px 0 20px;
                }
            </style>    
        </head>
        <body>
            <div class="breadcrumbs"><a href="%(home_url)s">Projects</a> /</div>
            <div class="content">
        """ % {
            'home_url': 'index.html'
        })

    def html_content(self, workspaces):

        def lst():
            workspaces_html = ''
            for workspace in workspaces:
                workspaces_html += '<li><a href="%(workspace_url)s.html">%(workspace_name)s</a></li>' % {
                    'workspace_url': workspace.id,
                    'workspace_name': workspace.name
                }

            return workspaces_html

        return """
            <ul>
            %s
            </ul>
        """ % lst()

    @property
    def html_footer(self):
        return """
        </body>
        </html>
        """

    def render_html(self):
        with db.DBConnection() as dbconn:
            workspace_rows = dbconn.fetchall('SELECT id, name FROM workspaces ORDER BY name ASC')
            workspaces = [
                models.workspace.Workspace(row[1], row[0]) for row in workspace_rows
            ]

        for workspace in workspaces:
            workspace.render_html()

        with open(self.html_file_path, 'w') as fp:
            fp.write(self.html_header)
            fp.write(self.html_content(workspaces))
            fp.write(self.html_footer)




