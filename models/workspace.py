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
                 h3 {
                        display: flex;
                        height: 1em;
                    }
                    h3 svg {
                        height: 1em;
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
            <h3><svg aria-hidden="true" data-prefix="far" data-icon="folder" class="svg-inline--fa fa-folder fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M464 128H272l-54.63-54.63c-6-6-14.14-9.37-22.63-9.37H48C21.49 64 0 85.49 0 112v288c0 26.51 21.49 48 48 48h416c26.51 0 48-21.49 48-48V176c0-26.51-21.49-48-48-48zm0 272H48V112h140.12l54.63 54.63c6 6 14.14 9.37 22.63 9.37H464v224z"></path></svg>&nbsp;Folders</h3>
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
                   <h3><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" data-prefix="far" data-icon="file" class="svg-inline--fa fa-file fa-w-12" role="img" viewBox="0 0 384 512"><path fill="currentColor" d="M369.9 97.9L286 14C277 5 264.8-.1 252.1-.1H48C21.5 0 0 21.5 0 48v416c0 26.5 21.5 48 48 48h288c26.5 0 48-21.5 48-48V131.9c0-12.7-5.1-25-14.1-34zM332.1 128H256V51.9l76.1 76.1zM48 464V48h160v104c0 13.3 10.7 24 24 24h104v288H48z"/></svg>&nbsp;Documents</h3>
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
            containers = models.container.Container.get_in_container(self.id)
            documents = models.document.Document.get_in_container(self.id)

        for container in containers:
            container.render_html()

        with open(self.html_file_path, 'w') as fp:
            fp.write(self.html_header)
            fp.write(self.html_container_content(containers))
            fp.write(self.html_document_content(documents))
            fp.write(self.html_footer)

