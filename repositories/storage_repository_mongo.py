import re
from typing import List
from urllib.parse import urlparse
from uuid import uuid4

from pymongo import MongoClient

from interfaces.storage_interface import StorageRepository
from models.object_model import ObjectWrite
from schemas.object_schema import list_object_serial, object_serial

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
        self.collection = "objects"

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def create_object(self, object_create: ObjectWrite) -> str:
        object_data = object_create.model_dump()
        object_id = str(uuid4())
        object_data["_id"] = object_id
        try:
            new_uuid = self.db[self.collection].insert_one(object_data)
            return new_uuid.inserted_id
        except Exception as e:
            raise ValueError(f"Failed to create object in database: {str(e)}")

    def get_object(self, uuid: str) -> dict:
        result = self.db[self.collection].find_one({"_id": uuid})
        if result is None:
            return None
        object = object_serial(result)
        return object

    def list_objects(self) -> List[dict]:
        result = self.db[self.collection].find()
        objects = list_object_serial(result)
        return objects

    def update_object(self, uuid: str, object_update: ObjectWrite) -> None:
        update_data = {"$set": object_update.model_dump()}
        self.db[self.collection].find_one_and_update({"_id": uuid}, update_data)


    def delete_object(self, uuid: str) -> None:
        self.db[self.collection].delete_one({"_id": uuid})

    def close(self):
        self.client.close()
