import db
import os
import models.document
import models.workspace

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

    @classmethod
    def get_in_container(cls, container_id):
        with db.DBConnection() as dbconn:
            container_rows = dbconn.fetchall(
                'SELECT id, name, container_id, workspace_id FROM containers WHERE container_id = ?', (container_id,)
            )

        return [
            Container(row[1], row[0], row[2], row[3]) for row in container_rows
        ]

    @classmethod
    def get_by_id(cls, container_id):
        with db.DBConnection() as dbconn:
            container_row = dbconn.fetchone(
                'SELECT id, name, container_id, workspace_id FROM containers WHERE id = ?', (container_id,)
            )

        if container_row:
            return Container(container_row[1], container_row[0], container_row[2], container_row[3])

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
    def container_path(self):
        path = [self]

        parent = Container.get_by_id(self.container_id)

        if parent is not None:
            path = [parent] + path

        while parent is not None:
            parent = Container.get_by_id(parent.container_id)
            if parent is not None:
                path = [parent] + path

        return path

    @property
    def html_container_breadcrumb(self):
        path = self.container_path

        breadcrumbs = []

        for container in path:
            breadcrumbs.append(
                '<a href="%(container_id)s.html">%(container_name)s</a>' % {
                    'container_id': container.id,
                    'container_name': container.name
                }
            )

        return ' / '.join(breadcrumbs)

    @property
    def html_header(self):
        workspace = models.workspace.Workspace.get_by_id(self.workspace_id)
        return """
               <html>
               <head><title>Projects</title></head>
               <body>
               <a href="%(home_url)s">Projects</a> / <a href="%(workspace_url)s.html">%(workspace_name)s</a> / %(container_breadcrumb)s
               """ % {
            'home_url': 'index.html',
            'workspace_url': workspace.id,
            'workspace_name': workspace.name,
            'container_breadcrumb': self.html_container_breadcrumb
        }

    @classmethod
    def html_container_content(cls, containers):

        def lst():
            containers_html = ''
            for container in containers:
                containers_html += '<li><a href="%(container_url)s.html">%(container_name)s</a></li>' % {
                    'container_url': container.id,
                    'container_name': container.name
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
               </body>
               </html>
               """

    def render_html(self):
        with db.DBConnection() as dbconn:
            containers = Container.get_in_container(self.id)

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
