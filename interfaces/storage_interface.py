from abc import ABC, abstractmethod
from models.object_model import ObjectWrite


class StorageRepository(ABC):

    @abstractmethod
    def create_object(self, object_create: ObjectWrite):
        pass

    @abstractmethod
    def get_object(self, object_id: str):
        pass

    @abstractmethod
    def list_objects(self):
        pass

    @abstractmethod
    def update_object(self, object_id: str, object_update: ObjectWrite):
        pass

    @abstractmethod
    def delete_object(self, object_id: str):
        pass

    @abstractmethod
    def close(self):
        pass