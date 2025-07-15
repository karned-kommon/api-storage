import boto3
from botocore.client import Config
from config.config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_REGION, S3_USE_SSL


def get_s3_client():
    """
    Initialize and return an S3 client with the configured settings.
    
    Returns:
        boto3.client: Initialized S3 client
    """
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