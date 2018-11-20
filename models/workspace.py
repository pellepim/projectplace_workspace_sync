import os
import db
import models.container
import models.document


class Workspace(object):

    def __init__(self, name, _id):
        self.name = name
        self.id = _id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    @classmethod
    def get_by_id(cls, workspace_id):
        with db.DBConnection() as dbconn:
            workspace_row = dbconn.fetchone(
                'SELECT id, name FROM workspaces WHERE id = ?', (workspace_id,)
            )

        if workspace_row:
            return Workspace(workspace_row[1], workspace_row[0])

        return None

    @property
    def html_file_location(self):
        if not os.path.exists('localdata/html'):
            os.makedirs('localdata/html')

        return 'localdata/html'

    @property
    def html_file_name(self):
        return '%d.html' % self.id

    @property
    def html_file_path(self):
        return os.path.join(self.html_file_location, '%d.html' % self.id)

    @property
    def html_header(self):
        return """
            <html>
            <head>
                <title>%(workspace_name)s</title>
                <style type="text/css">
                body {
                    font-size: 16px;
                    font-family: sans-serif;
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
                    border-bottom: 1px solid #333;
                    background-color: #dadada;
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
            <div class="breadcrumbs"><a href="%(home_url)s">Projects</a> / <a href="%(workspace_url)s">%(workspace_name)s</a></div>
            <div class="content">
            """ % {
            'home_url': 'index.html',
            'workspace_url': self.html_file_name,
            'workspace_name': self.name
        }

    @classmethod
    def html_container_content(cls, containers):

        def lst():
            containers_html = ''
            for container in containers:
                containers_html += '<li><a href="%(workspace_url)s.html">%(workspace_name)s</a></li>' % {
                    'workspace_url': container.id,
                    'workspace_name': container.name
                }

            return containers_html

        return """
            <h2>Folders:</h2>
            <ul>
            %s
            </ul>
        """ % lst()

    @classmethod
    def html_document_content(cls, documents):

        def lst():
            documents_html = ''
            for document in documents:
                documents_html += '<li><a target="_blank" href="../%(workspace_id)s/%(document_file_name)s">%(document_name)s</a></li>' % {
                    'workspace_id': document.workspace_id,
                    'document_name': document.name,
                    'document_file_name': document.local_filename
                }

            return documents_html

        return """
                   <h2>Documents:</h2>
                   <ul>
                   %s
                   </ul>
               """ % lst()

    @property
    def html_footer(self):
        return """
            </div>
            </body>
            </html>
            """

    def render_html(self):
        with db.DBConnection() as dbconn:
            container_rows = dbconn.fetchall(
                'SELECT id, name, container_id, workspace_id FROM containers WHERE container_id = ?', (self.id,)
            )
            containers = [
                models.container.Container(row[1], row[0], row[2], row[3]) for row in container_rows
            ]

            document_rows = dbconn.fetchall(
                'SELECT id, name, container_id, workspace_id, modified_time FROM documents WHERE container_id = ?',
                (self.id,)
            )
            documents = [
                models.document.Document(row[1], row[0], row[4], row[2], row[3]) for row in document_rows
            ]

        for container in containers:
            container.render_html()

        with open(self.html_file_path, 'w') as fp:
            fp.write(self.html_header)
            fp.write(self.html_container_content(containers))
            fp.write(self.html_document_content(documents))
            fp.write(self.html_footer)

