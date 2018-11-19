
class Workspace(object):

    def __init__(self, name, _id):
        self.name = name
        self.id = _id

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )
