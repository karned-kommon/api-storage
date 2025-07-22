from fastapi import HTTPException, UploadFile
from models.object_model import ObjectWrite
from common_api.utils.v0 import get_state_repos, get_state_stores


def create_object(request, new_object, file: UploadFile = None) -> str:
    try:
        repos = get_state_repos(request)
        stores = get_state_stores(request)

        from uuid import uuid4
        new_uuid = str(uuid4())

        file_path = None
        if file and file.filename:
            file_path, _ = stores.storage_bucket_repo.upload_file_to_bucket(file, custom_uuid=new_uuid)

        new_object_dict = new_object.model_dump()
        if file_path:
            new_object_dict["file_path"] = file_path

        new_object_dict["_id"] = new_uuid

        if file_path:
            repos.storage_repo.create_object_with_file(new_object_dict)
        else:
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
        stores = get_state_stores(request)
        
        # First, get the object to retrieve its file_path
        object_data = repos.storage_repo.get_object(uuid)
        if object_data is None:
            raise HTTPException(status_code=404, detail="Storage not found")
        
        # Delete the file from bucket if it exists
        if object_data.get("file_path"):
            stores.storage_bucket_repo.delete_file_from_bucket(object_data["file_path"])
        
        # Then delete the database record
        repos.storage_repo.delete_object(uuid)
    except HTTPException:
        # Re-raise HTTPException as is
        raise
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"An error occurred while deleting the object: {e}")


def get_public_url_for_object(request, uuid: str, ttl: int = 3600) -> dict:
    """
    Generate a temporary public URL for accessing an S3 object.
    
    Args:
        request: FastAPI request object containing authentication and state
        uuid: Unique identifier of the storage object
        ttl: Time-to-live for the URL in seconds (default: 3600)
    
    Returns:
        Dictionary containing the public URL and expiration time
        
    Raises:
        HTTPException: If object not found, no file associated, or URL generation fails
    """
    try:
        # Get the object to retrieve its file_path
        object_data = get_object(request, uuid)
        
        # Check if the object has a file associated with it
        file_path = getattr(object_data, 'file_path', None)
        if not file_path:
            raise HTTPException(status_code=404, detail="No file associated with this object")
        
        # Generate the public URL using the storage bucket repository
        stores = get_state_stores(request)
        public_url = stores.storage_bucket_repo.get_public_url(file_path, ttl)
        
        return {"public_url": public_url, "expires_in": ttl}
        
    except HTTPException:
        # Re-raise HTTPException as is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate public URL: {str(e)}")
