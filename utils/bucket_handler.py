from config.config import S3_BUCKET_NAME
from utils.s3_client_handler import get_s3_client


def ensure_bucket_exists():
    """
    Check if the configured S3 bucket exists, and create it if it doesn't.
    
    Returns:
        str: The name of the bucket
    """
    s3_client = get_s3_client()
    
    # Check if bucket exists, create if it doesn't
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
    except:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
    
    return S3_BUCKET_NAME