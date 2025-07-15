from fastapi import HTTPException
from models.object_model import ObjectWrite
from common_api.utils.v0 import get_state_repos


def create_object(request, new_storage) -> str:
    try:
        repos = get_state_repos(request)
        new_uuid = repos.storage_repo.create_storage(new_storage)
        if not isinstance(new_uuid, str):
            raise TypeError("The method create_storage did not return a str.")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while creating the storage: {e}")

    return new_uuid


def get_objects(request) -> list[ObjectWrite]:
    try:
        repos = get_state_repos(request)
        storages = repos.storage_repo.list_storages()
        if not isinstance(storages, list):
            raise TypeError("The method list_storages did not return a list.")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while get the list of storages: {e}")

    return storages


def get_object(request, uuid: str) -> ObjectWrite:
    try:
        repos = get_state_repos(request)
        storage = repos.storage_repo.get_storage(uuid)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while retrieving the storage: {e}")

    if storage is None:
        raise HTTPException(status_code = 404, detail = "Storage not found")

    return storage


def update_object(request, uuid: str, storage_update: ObjectWrite) -> None:
    try:
        repos = get_state_repos(request)
        repos.storage_repo.update_storage(uuid, storage_update)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while updating the storage: {e}")


def delete_object(request, uuid: str) -> None:
    try:
        repos = get_state_repos(request)
        repos.storage_repo.delete_storage(uuid)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while deleting the storage: {e}")
