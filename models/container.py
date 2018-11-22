import db
import os
import models.document
import models.workspace
import models.url
import sdk.utils


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
                'SELECT id, name, container_id, workspace_id FROM containers WHERE container_id = ? ORDER BY name ASC',
                (container_id,)
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

    def breadcrumbs(self):
        workspace = models.workspace.Workspace.get_by_id(self.workspace_id)
        return '<div class="breadcrumbs"><a href="index.html">Projects</a> / <a href="%(workspace_url)s.html">%(workspace_name)s</a> / %(container_breadcrumb)s</div>' % {
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

    @classmethod
    def html_url_content(cls, urls):
        def lst():
            urls_html = ''
            for url in urls:
                urls_html += '<li><a target="_blank" href="%(url)s">%(url_name)s</a></li>' % {
                    'workspace_id': url.workspace_id,
                    'url_name': url.name,
                    'url': url.urllink
                }

            return urls_html

        return """
           <h3><svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" data-prefix="far" data-icon="file" class="svg-inline--fa fa-file fa-w-12" role="img" viewBox="0 0 512 512"><path fill="currentColor" d="M326.612 185.391c59.747 59.809 58.927 155.698.36 214.59-.11.12-.24.25-.36.37l-67.2 67.2c-59.27 59.27-155.699 59.262-214.96 0-59.27-59.26-59.27-155.7 0-214.96l37.106-37.106c9.84-9.84 26.786-3.3 27.294 10.606.648 17.722 3.826 35.527 9.69 52.721 1.986 5.822.567 12.262-3.783 16.612l-13.087 13.087c-28.026 28.026-28.905 73.66-1.155 101.96 28.024 28.579 74.086 28.749 102.325.51l67.2-67.19c28.191-28.191 28.073-73.757 0-101.83-3.701-3.694-7.429-6.564-10.341-8.569a16.037 16.037 0 0 1-6.947-12.606c-.396-10.567 3.348-21.456 11.698-29.806l21.054-21.055c5.521-5.521 14.182-6.199 20.584-1.731a152.482 152.482 0 0 1 20.522 17.197zM467.547 44.449c-59.261-59.262-155.69-59.27-214.96 0l-67.2 67.2c-.12.12-.25.25-.36.37-58.566 58.892-59.387 154.781.36 214.59a152.454 152.454 0 0 0 20.521 17.196c6.402 4.468 15.064 3.789 20.584-1.731l21.054-21.055c8.35-8.35 12.094-19.239 11.698-29.806a16.037 16.037 0 0 0-6.947-12.606c-2.912-2.005-6.64-4.875-10.341-8.569-28.073-28.073-28.191-73.639 0-101.83l67.2-67.19c28.239-28.239 74.3-28.069 102.325.51 27.75 28.3 26.872 73.934-1.155 101.96l-13.087 13.087c-4.35 4.35-5.769 10.79-3.783 16.612 5.864 17.194 9.042 34.999 9.69 52.721.509 13.906 17.454 20.446 27.294 10.606l37.106-37.106c59.271-59.259 59.271-155.699.001-214.959z"/></svg>&nbsp;Links</h3>
           <ul>
           %s
           </ul>
       """ % lst()

    @property
    def html_footer(self):
        return """
        </div>
        </body>
        </html>"""

    def render_html(self):
        containers = Container.get_in_container(self.id)
        documents = models.document.Document.get_in_container(self.id)
        urls = models.url.Url.get_in_container(self.id)

        for container in containers:
            container.render_html()

        with open(self.html_file_path, 'w') as fp:
            fp.write(sdk.utils.html_header(self.name, self.breadcrumbs()))
            fp.write(self.html_container_content(containers))
            fp.write(self.html_document_content(documents))
            fp.write(self.html_url_content(urls))
            fp.write(self.html_footer)

