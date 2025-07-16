from fastapi import HTTPException, UploadFile
from models.object_model import ObjectWrite
from common_api.utils.v0 import get_state_repos
from repositories.storage_repository_s3 import StorageRepositoryS3


def create_object(request, new_object, file: UploadFile = None) -> str:
    try:
        repos = get_state_repos(request)

        # Generate a UUID for both database and S3 (if needed)
        from uuid import uuid4
        new_uuid = str(uuid4())

        # Handle file upload if provided
        file_path = None
        if file and file.filename:
            # Upload file to S3 using the S3Repository with the generated UUID
            s3_repo = StorageRepositoryS3()
            file_path, _ = s3_repo.upload_file_to_bucket(file, custom_uuid=new_uuid)

        # Add file path and UUID to object
        new_object_dict = new_object.model_dump()
        if file_path:
            new_object_dict["file_path"] = file_path

        # Add the UUID to the object data
        new_object_dict["_id"] = new_uuid

        # Create the object in the database
        if file_path:
            repos.storage_repo.create_object_with_file(new_object_dict)
        else:
            # For consistency, we'll use the same approach for both cases
            repos.storage_repo.create_object_with_file(new_object_dict)

        if not isinstance(new_uuid, str):
            raise TypeError("The UUID is not a string.")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while creating the object: {e}")

    return new_uuid


def get_objects(request) -> list[ObjectWrite]:
    try:
        repos = get_state_repos(request)
        objects = repos.storage_repo.list_objects()
        if not isinstance(objects, list):
            raise TypeError("The method list_objects did not return a list.")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while get the list of objects: {e}")

    return objects


def get_object(request, uuid: str) -> ObjectWrite:
    try:
        repos = get_state_repos(request)
        object = repos.storage_repo.get_object(uuid)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while retrieving the object: {e}")

    if object is None:
        raise HTTPException(status_code = 404, detail = "Storage not found")

    return object


def update_object(request, uuid: str, object_update: ObjectWrite) -> None:
    try:
        repos = get_state_repos(request)
        repos.storage_repo.update_object(uuid, object_update)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while updating the object: {e}")


def delete_object(request, uuid: str) -> None:
    try:
        repos = get_state_repos(request)
        repos.storage_repo.delete_object(uuid)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while deleting the object: {e}")
