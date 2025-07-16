from abc import ABC, abstractmethod
from typing import Dict, Any


class StorageBucketRepository(ABC):

    @abstractmethod
    def ensure_bucket_exists(self):
        pass

    @abstractmethod
    def upload_file_to_bucket(self, file: Any, custom_uuid: str = None) -> (str, str):
        pass

    @abstractmethod
    def download_file_from_bucket(self, file_path: str) -> Any:
        pass

    @abstractmethod
    def delete_file_from_bucket(self, file_path: str) -> None:
        pass

    @abstractmethod
    def list_files_in_bucket(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def close(self):
        pass