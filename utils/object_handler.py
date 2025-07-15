import os
from uuid import uuid4
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
from config.config import S3_BUCKET_NAME
from utils.s3_client_handler import get_s3_client
from utils.bucket_handler import ensure_bucket_exists


def generate_unique_filename(original_filename, custom_uuid=None):
    """
    Generate a unique filename based on the original filename.

    Args:
        original_filename (str): The original filename
        custom_uuid (str, optional): Custom UUID to use instead of generating a new one

    Returns:
        str: A unique filename
    """
    file_ext = os.path.splitext(original_filename)[1]
    if custom_uuid:
        return f"{custom_uuid}{file_ext}"
    return f"{uuid4()}{file_ext}"


def upload_file_to_s3(file: UploadFile, custom_uuid=None):
    """
    Upload a file to S3 and return the file path.

    Args:
        file (UploadFile): The file to upload
        custom_uuid (str, optional): Custom UUID to use for the filename

    Returns:
        tuple: (file_path, file_content) where file_path is the S3 path and file_content is the file content
    """
    if not file or not file.filename:
        return None, None

    # Ensure bucket exists
    bucket_name = ensure_bucket_exists()

    # Generate a unique filename
    unique_filename = generate_unique_filename(file.filename, custom_uuid)

    # Save file content before upload (in case the upload process closes the file)
    file_content = file.file.read()
    file.file.seek(0)

    # Get S3 client
    s3_client = get_s3_client()

    # Upload file to S3
    s3_client.upload_fileobj(
        file.file, 
        bucket_name, 
        unique_filename,
        ExtraArgs={'ContentType': file.content_type}
    )

    # Generate S3 file path
    file_path = f"s3://{bucket_name}/{unique_filename}"

    # If the file is closed after upload, reopen it with the saved content
    try:
        file.file.seek(0)
    except ValueError:  # This will catch "I/O operation on closed file"
        # Create a new SpooledTemporaryFile with the saved content
        new_file = SpooledTemporaryFile()
        new_file.write(file_content)
        new_file.seek(0)
        file.file = new_file

    return file_path, file_content
