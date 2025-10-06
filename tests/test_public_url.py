"""
Test to verify that get_public_url generates temporary URLs correctly.
"""
import pytest
from unittest.mock import Mock, patch
from repositories.storage_repository_s3 import StorageRepositoryS3


def test_get_public_url_with_valid_file_path():
    """Test that get_public_url generates a valid presigned URL"""
    # Mock credentials
    mock_credentials = {
        'endpoint': 'http://localhost:9000',
        'access_key': 'test_access',
        'secret_key': 'test_secret',
        'bucket_name': 'test-bucket'
    }
    
    # Create S3 repository instance
    s3_repo = StorageRepositoryS3(mock_credentials)
    
    # Mock the boto3 client's generate_presigned_url method
    mock_url = "https://test-bucket.s3.amazonaws.com/test-uuid-123.pdf?presigned=true"
    s3_repo.client.generate_presigned_url = Mock(return_value=mock_url)
    s3_repo.client.head_bucket = Mock()  # Mock bucket exists check
    
    # Test file path
    file_path = "s3://test-bucket/test-uuid-123.pdf"
    ttl = 3600
    
    # Call the method
    result = s3_repo.get_public_url(file_path, ttl)
    
    # Verify the result
    assert result == mock_url
    
    # Verify the generate_presigned_url was called with correct parameters
    s3_repo.client.generate_presigned_url.assert_called_once_with(
        'get_object',
        Params={'Bucket': 'test-bucket', 'Key': 'test-uuid-123.pdf'},
        ExpiresIn=ttl
    )


def test_get_public_url_with_empty_file_path():
    """Test that get_public_url raises error for empty file path"""
    # Mock credentials
    mock_credentials = {
        'endpoint': 'http://localhost:9000',
        'access_key': 'test_access',
        'secret_key': 'test_secret',
        'bucket_name': 'test-bucket'
    }
    
    # Create S3 repository instance
    s3_repo = StorageRepositoryS3(mock_credentials)
    
    # Test with empty file path
    with pytest.raises(ValueError, match="File path cannot be empty"):
        s3_repo.get_public_url("", 3600)


def test_get_public_url_with_custom_ttl():
    """Test that get_public_url works with custom TTL"""
    # Mock credentials
    mock_credentials = {
        'endpoint': 'http://localhost:9000',
        'access_key': 'test_access',
        'secret_key': 'test_secret',
        'bucket_name': 'test-bucket'
    }
    
    # Create S3 repository instance
    s3_repo = StorageRepositoryS3(mock_credentials)
    
    # Mock the boto3 client's generate_presigned_url method
    mock_url = "https://test-bucket.s3.amazonaws.com/test-file.jpg?presigned=true"
    s3_repo.client.generate_presigned_url = Mock(return_value=mock_url)
    s3_repo.client.head_bucket = Mock()  # Mock bucket exists check
    
    # Test with custom TTL
    file_path = "s3://test-bucket/test-file.jpg"
    custom_ttl = 7200  # 2 hours
    
    # Call the method
    result = s3_repo.get_public_url(file_path, custom_ttl)
    
    # Verify the result
    assert result == mock_url
    
    # Verify the generate_presigned_url was called with custom TTL
    s3_repo.client.generate_presigned_url.assert_called_once_with(
        'get_object',
        Params={'Bucket': 'test-bucket', 'Key': 'test-file.jpg'},
        ExpiresIn=custom_ttl
    )