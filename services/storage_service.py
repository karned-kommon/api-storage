from fastapi import HTTPException, UploadFile
from models.object_model import ObjectWrite
from common_api.utils.v0 import get_state_repos
import os
import shutil
from uuid import uuid4
import boto3
from botocore.client import Config
from config.config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME, S3_REGION, S3_USE_SSL


def create_object(request, new_object, file: UploadFile = None) -> str:
    try:
        repos = get_state_repos(request)

        # Handle file upload if provided
        file_path = None
        if file and file.filename:
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                endpoint_url=S3_ENDPOINT,
                aws_access_key_id=S3_ACCESS_KEY,
                aws_secret_access_key=S3_SECRET_KEY,
                region_name=S3_REGION,
                config=Config(signature_version='s3v4'),
                use_ssl=S3_USE_SSL
            )

            # Check if bucket exists, create if it doesn't
            try:
                s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            except:
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)

            # Generate a unique filename
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid4()}{file_ext}"

            # Save file content before upload (in case the upload process closes the file)
            file_content = file.file.read()
            file.file.seek(0)

            # Upload file to S3
            s3_client.upload_fileobj(
                file.file, 
                S3_BUCKET_NAME, 
                unique_filename,
                ExtraArgs={'ContentType': file.content_type}
            )

            # Generate S3 file path
            file_path = f"s3://{S3_BUCKET_NAME}/{unique_filename}"

            # If the file is closed after upload, reopen it with the saved content
            try:
                file.file.seek(0)
            except ValueError:  # This will catch "I/O operation on closed file"
                # Create a new SpooledTemporaryFile with the saved content
                from tempfile import SpooledTemporaryFile
                new_file = SpooledTemporaryFile()
                new_file.write(file_content)
                new_file.seek(0)
                file.file = new_file

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
