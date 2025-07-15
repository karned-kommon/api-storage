from fastapi import HTTPException, UploadFile
from models.object_model import ObjectWrite
from common_api.utils.v0 import get_state_repos
import os
import shutil
from uuid import uuid4


def create_object(request, new_object, file: UploadFile = None) -> str:
    try:
        repos = get_state_repos(request)

        # Handle file upload if provided
        file_path = None
        if file and file.filename:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)

            # Generate a unique filename
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, unique_filename)

            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Reset file position
            file.file.seek(0)

        # Add file path to object if a file was uploaded
        if file_path:
            new_object_dict = new_object.model_dump()
            new_object_dict["file_path"] = file_path
            new_uuid = repos.storage_repo.create_object_with_file(new_object_dict)
        else:
            new_uuid = repos.storage_repo.create_object(new_object)

        if not isinstance(new_uuid, str):
            raise TypeError("The method create_object did not return a str.")
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
