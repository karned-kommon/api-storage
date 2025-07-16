import os
import boto3
from uuid import uuid4
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
from botocore.client import Config
from config.config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_REGION, S3_USE_SSL, S3_BUCKET_NAME
from interfaces.storage_bucket_interface import StorageBucketRepository


def generate_unique_filename(original_filename, custom_uuid=None):
    file_ext = os.path.splitext(original_filename)[1]
    if custom_uuid:
        return f"{custom_uuid}{file_ext}"
    return f"{uuid4()}{file_ext}"


def get_client():
    s3_client = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
        config=Config(signature_version='s3v4'),
        use_ssl=S3_USE_SSL
    )
    return s3_client


class StorageRepositoryS3(StorageBucketRepository):
    def __init__(self):
        self.bucket_name = S3_BUCKET_NAME

    def ensure_bucket_exists(self):
        s3_client = get_client()
        try:
            s3_client.head_bucket(Bucket=self.bucket_name)
        except:
            s3_client.create_bucket(Bucket=self.bucket_name)
        return self.bucket_name

    def download_file_from_bucket(self, file_path: str):
        if not file_path:
            return None

        s3_client = get_client()
        bucket_name = self.ensure_bucket_exists()
        file_key = file_path.replace(f"s3://{bucket_name}/", "")

        try:
            file_content = SpooledTemporaryFile()
            s3_client.download_fileobj(bucket_name, file_key, file_content)
            file_content.seek(0)
            return file_content
        except Exception as e:
            raise ValueError(f"Failed to download file from bucket: {str(e)}")

    def delete_file_from_bucket(self, file_path: str):
        if not file_path:
            return

        s3_client = get_client()
        bucket_name = self.ensure_bucket_exists()
        file_key = file_path.replace(f"s3://{bucket_name}/", "")

        try:
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        except Exception as e:
            raise ValueError(f"Failed to delete file from bucket: {str(e)}")

    def list_files_in_bucket(self):
        s3_client = get_client()
        bucket_name = self.ensure_bucket_exists()

        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' not in response:
                return {}

            files = {item['Key']: item['LastModified'] for item in response['Contents']}
            return files
        except Exception as e:
            raise ValueError(f"Failed to list files in bucket: {str(e)}")

    def upload_file_to_bucket(self, file: UploadFile, custom_uuid=None):
        if not file or not file.filename:
            return None, None

        bucket_name = self.ensure_bucket_exists()
        unique_filename = generate_unique_filename(file.filename, custom_uuid)
        file_content = file.file.read()
        file.file.seek(0)

        s3_client = get_client()
        s3_client.upload_fileobj(
            file.file, 
            bucket_name, 
            unique_filename,
            ExtraArgs={'ContentType': file.content_type}
        )

        file_path = f"s3://{bucket_name}/{unique_filename}"

        try:
            file.file.seek(0)
        except ValueError:
            new_file = SpooledTemporaryFile()
            new_file.write(file_content)
            new_file.seek(0)
            file.file = new_file

        return file_path, file_content