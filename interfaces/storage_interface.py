from abc import ABC, abstractmethod
from models.storage_model import StorageWrite


class StorageRepository(ABC):

    @abstractmethod
    def create_storage(self, storage_create: StorageWrite):
        pass

    @abstractmethod
    def get_storage(self, storage_id: str):
        pass

    @abstractmethod
    def list_storages(self):
        pass

    @abstractmethod
    def update_storage(self, storage_id: str, storage_update: StorageWrite):
        pass

    @abstractmethod
    def delete_storage(self, storage_id: str):
        pass

    @abstractmethod
    def close(self):
        pass