from abc import ABC, abstractmethod


class AbstractRepository(ABC):

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def get_by_id(self, entity_id):
        pass