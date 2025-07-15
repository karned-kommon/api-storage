from abc import ABC, abstractmethod
from models.object_model import ObjectWrite


class StorageRepository(ABC):

    @abstractmethod
    def create_storage(self, storage_create: ObjectWrite):
        pass

    @abstractmethod
    def get_storage(self, storage_id: str):
        pass

    @abstractmethod
    def list_storages(self):
        pass

    @abstractmethod
    def update_storage(self, storage_id: str, storage_update: ObjectWrite):
        pass

    @abstractmethod
    def delete_storage(self, storage_id: str):
        pass

    @abstractmethod
    def close(self):
        pass