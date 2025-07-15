import re
from typing import List
from urllib.parse import urlparse
from uuid import uuid4

from pymongo import MongoClient

from interfaces.storage_interface import StorageRepository
from models.object_model import ObjectWrite
from schemas.storage_schema import list_storage_serial, storage_serial

def check_uri(uri):
    if not re.match(r"^mongodb://", uri):
        raise ValueError("Invalid URI: URI must start with 'mongodb://'")


def extract_database(uri: str) -> str:
    parsed_uri = urlparse(uri)
    db_name = parsed_uri.path.lstrip("/")

    if not db_name:
        raise ValueError("L'URI MongoDB ne contient pas de nom de base de données.")

    return db_name


class StorageRepositoryMongo(StorageRepository):

    def __init__(self, uri):
        check_uri(uri)
        database = extract_database(uri)

        self.uri = uri
        self.client = MongoClient(self.uri)
        self.db = self.client[database]
        self.collection = "storages"

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def create_storage(self, storage_create: ObjectWrite) -> str:
        storage_data = storage_create.model_dump()
        storage_id = str(uuid4())
        storage_data["_id"] = storage_id
        try:
            new_uuid = self.db[self.collection].insert_one(storage_data)
            return new_uuid.inserted_id
        except Exception as e:
            raise ValueError(f"Failed to create storage in database: {str(e)}")

    def get_storage(self, uuid: str) -> dict:
        result = self.db[self.collection].find_one({"_id": uuid})
        if result is None:
            return None
        storage = storage_serial(result)
        return storage

    def list_storages(self) -> List[dict]:
        result = self.db[self.collection].find()
        storages = list_storage_serial(result)
        return storages

    def update_storage(self, uuid: str, storage_update: ObjectWrite) -> None:
        update_data = {"$set": storage_update.model_dump()}
        self.db[self.collection].find_one_and_update({"_id": uuid}, update_data)


    def delete_storage(self, uuid: str) -> None:
        self.db[self.collection].delete_one({"_id": uuid})

    def close(self):
        self.client.close()
