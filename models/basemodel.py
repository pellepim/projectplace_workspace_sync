import abc
import logging

logger = logging.getLogger(__name__)


class BaseModel(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_by_id(cls, _id):
        pass

    @abc.abstractmethod
    def insert(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    def update_or_insert(self):
        existing = self.get_by_id(self.id)

        if existing is None:
            logger.info('%s does not exist - creating', self)
            self.insert()
        elif isinstance(existing, self.__class__) and existing != self:
            logger.info('%s exists - but has changed - updating')
            self.update()

    def __repr__(self):
        return '%s: %s (ID: %s)' % (
            self.__class__.__name__, self.name, self.id
        )

    @abc.abstractmethod
    def __eq__(self, other):
        pass


class HTMLRendered(abc.ABC):
    @abc.abstractmethod
    def render_html(self):
        pass
