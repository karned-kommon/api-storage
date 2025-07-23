import os
import boto3
from uuid import uuid4
from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
from botocore.client import Config
from interfaces.storage_bucket_interface import StorageBucketRepository

def generate_unique_filename(original_filename, custom_uuid=None):
    file_ext = os.path.splitext(original_filename)[1]
    if custom_uuid:
        return f"{custom_uuid}{file_ext}"
    return f"{uuid4()}{file_ext}"


def get_client(credentials):
    endpoint = credentials.get('endpoint')
    access_key = credentials.get('access_key')
    secret_key = credentials.get('secret_key')
    region = credentials.get('region', 'us-east-1')
    use_ssl = credentials.get('use_ssl', False)

    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        config=Config(signature_version='s3v4'),
        use_ssl=use_ssl
    )
    return s3_client

def check_credentials(credentials):
    required_fields = ['endpoint', 'access_key', 'secret_key']
    if not credentials or not all(credentials.get(field) for field in required_fields):
        raise ValueError("Invalid S3 credentials: Missing required fields.")



class StorageRepositoryS3(StorageBucketRepository):
    def __init__(self, credentials):
        check_credentials(credentials)
        self.credentials = credentials
        self.bucket_name = credentials.get('bucket_name', 'storage')
        self.client = get_client(credentials)

    def ensure_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except:
            self.client.create_bucket(Bucket=self.bucket_name)
        return self.bucket_name

    def download_file_from_bucket(self, file_path: str):
        if not file_path:
            return None

        bucket_name = self.ensure_bucket_exists()
        file_key = file_path.replace(f"s3://{bucket_name}/", "")

        try:
            file_content = SpooledTemporaryFile()
            self.client.download_fileobj(bucket_name, file_key, file_content)
            file_content.seek(0)
            return file_content
        except Exception as e:
            raise ValueError(f"Failed to download file from bucket: {str(e)}")

    def delete_file_from_bucket(self, file_path: str):
        if not file_path:
            return

        bucket_name = self.ensure_bucket_exists()
        file_key = file_path.replace(f"s3://{bucket_name}/", "")

        try:
            self.client.delete_object(Bucket=bucket_name, Key=file_key)
        except Exception as e:
            raise ValueError(f"Failed to delete file from bucket: {str(e)}")

    def list_files_in_bucket(self):
        bucket_name = self.ensure_bucket_exists()

        try:
            response = self.client.list_objects_v2(Bucket=bucket_name)
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

        self.client.upload_fileobj(
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

    def get_public_url(self, file_path: str, ttl: int = 3600) -> str:
        """Generate a temporary public URL for an S3 object"""
        if not file_path:
            raise ValueError("File path cannot be empty")

        bucket_name = self.ensure_bucket_exists()
        file_key = file_path.replace(f"s3://{bucket_name}/", "")

        try:
            public_url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_key},
                ExpiresIn=ttl
            )
            return public_url
        except Exception as e:
            raise ValueError(f"Failed to generate public URL: {str(e)}")

    def close(self):
        # No need to explicitly close the boto3 client
        pass
