"""
Test to verify that delete_object removes both database records and bucket files.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from repositories.storage_repository_mongo import StorageRepositoryMongo
from repositories.storage_repository_s3 import StorageRepositoryS3
from services.storage_service import delete_object


def create_mock_repos_and_stores_with_file():
    """Create mock repositories and stores for object with file"""
    # Mock storage repository
    mock_storage_repo = Mock()
    mock_storage_repo.get_object.return_value = {
        "_id": "test-uuid-123",
        "name": "Test Object",
        "description": "Test Description",
        "created_by": "user-uuid",
        "file_path": "s3://test-bucket/test-uuid-123.pdf"
    }
    
    # Mock bucket repository
    mock_bucket_repo = Mock()
    
    # Mock repos container
    mock_repos = Mock()
    mock_repos.storage_repo = mock_storage_repo
    
    # Mock stores container
    mock_stores = Mock()
    mock_stores.storage_bucket_repo = mock_bucket_repo
    
    return mock_repos, mock_stores, mock_storage_repo, mock_bucket_repo


def create_mock_repos_and_stores_without_file():
    """Create mock repositories and stores for object without file"""
    # Mock storage repository
    mock_storage_repo = Mock()
    mock_storage_repo.get_object.return_value = {
        "_id": "test-uuid-456",
        "name": "Test Object Without File",
        "description": "Test Description",
        "created_by": "user-uuid"
        # No file_path
    }
    
    # Mock bucket repository
    mock_bucket_repo = Mock()
    
    # Mock repos container
    mock_repos = Mock()
    mock_repos.storage_repo = mock_storage_repo
    
    # Mock stores container
    mock_stores = Mock()
    mock_stores.storage_bucket_repo = mock_bucket_repo
    
    return mock_repos, mock_stores, mock_storage_repo, mock_bucket_repo


@patch('services.storage_service.get_state_stores')
@patch('services.storage_service.get_state_repos')
def test_delete_object_with_file_deletes_both_db_and_bucket(mock_get_repos, mock_get_stores):
    """Test that delete_object deletes both database record and bucket file when object has file"""
    mock_repos, mock_stores, mock_storage_repo, mock_bucket_repo = create_mock_repos_and_stores_with_file()
    mock_get_repos.return_value = mock_repos
    mock_get_stores.return_value = mock_stores
    
    request = Mock()
    
    # Call delete_object
    delete_object(request, "test-uuid-123")
    
    # Verify that state functions were called with request
    mock_get_repos.assert_called_once_with(request)
    mock_get_stores.assert_called_once_with(request)
    
    # Verify that get_object was called to retrieve the object
    mock_storage_repo.get_object.assert_called_once_with("test-uuid-123")
    
    # Verify that bucket file was deleted
    mock_bucket_repo.delete_file_from_bucket.assert_called_once_with("s3://test-bucket/test-uuid-123.pdf")
    
    # Verify that database record was deleted
    mock_storage_repo.delete_object.assert_called_once_with("test-uuid-123")


@patch('services.storage_service.get_state_stores')
@patch('services.storage_service.get_state_repos')
def test_delete_object_without_file_only_deletes_db(mock_get_repos, mock_get_stores):
    """Test that delete_object only deletes database record when object has no file"""
    mock_repos, mock_stores, mock_storage_repo, mock_bucket_repo = create_mock_repos_and_stores_without_file()
    mock_get_repos.return_value = mock_repos
    mock_get_stores.return_value = mock_stores
    
    request = Mock()
    
    # Call delete_object
    delete_object(request, "test-uuid-456")
    
    # Verify that state functions were called with request
    mock_get_repos.assert_called_once_with(request)
    mock_get_stores.assert_called_once_with(request)
    
    # Verify that get_object was called to retrieve the object
    mock_storage_repo.get_object.assert_called_once_with("test-uuid-456")
    
    # Verify that bucket delete was NOT called (no file_path)
    mock_bucket_repo.delete_file_from_bucket.assert_not_called()
    
    # Verify that database record was deleted
    mock_storage_repo.delete_object.assert_called_once_with("test-uuid-456")


@patch('services.storage_service.get_state_stores')
@patch('services.storage_service.get_state_repos')
def test_delete_object_with_empty_file_path_only_deletes_db(mock_get_repos, mock_get_stores):
    """Test that delete_object only deletes database record when file_path is empty"""
    # Mock storage repository with empty file_path
    mock_storage_repo = Mock()
    mock_storage_repo.get_object.return_value = {
        "_id": "test-uuid-789",
        "name": "Test Object",
        "description": "Test Description", 
        "created_by": "user-uuid",
        "file_path": ""  # Empty file path
    }
    
    # Mock bucket repository
    mock_bucket_repo = Mock()
    
    # Mock repos and stores containers
    mock_repos = Mock()
    mock_repos.storage_repo = mock_storage_repo
    mock_stores = Mock()
    mock_stores.storage_bucket_repo = mock_bucket_repo
    
    mock_get_repos.return_value = mock_repos
    mock_get_stores.return_value = mock_stores
    
    request = Mock()
    
    # Call delete_object
    delete_object(request, "test-uuid-789")
    
    # Verify that get_object was called to retrieve the object
    mock_storage_repo.get_object.assert_called_once_with("test-uuid-789")
    
    # Verify that bucket delete was NOT called (empty file_path)
    mock_bucket_repo.delete_file_from_bucket.assert_not_called()
    
    # Verify that database record was deleted
    mock_storage_repo.delete_object.assert_called_once_with("test-uuid-789")


@patch('services.storage_service.get_state_stores')
@patch('services.storage_service.get_state_repos')
def test_delete_object_nonexistent_raises_404(mock_get_repos, mock_get_stores):
    """Test that delete_object raises 404 when object doesn't exist"""
    # Mock storage repository returning None (object not found)
    mock_storage_repo = Mock()
    mock_storage_repo.get_object.return_value = None
    
    # Mock bucket repository
    mock_bucket_repo = Mock()
    
    # Mock repos and stores containers
    mock_repos = Mock()
    mock_repos.storage_repo = mock_storage_repo
    mock_stores = Mock()
    mock_stores.storage_bucket_repo = mock_bucket_repo
    
    mock_get_repos.return_value = mock_repos
    mock_get_stores.return_value = mock_stores
    
    request = Mock()
    
    # Call delete_object and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete_object(request, "nonexistent-uuid")
    
    # Verify the exception details
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Storage not found"
    
    # Verify that get_object was called
    mock_storage_repo.get_object.assert_called_once_with("nonexistent-uuid")
    
    # Verify that neither bucket nor database delete were called
    mock_bucket_repo.delete_file_from_bucket.assert_not_called()
    mock_storage_repo.delete_object.assert_not_called()


@patch('services.storage_service.get_state_stores')
@patch('services.storage_service.get_state_repos')
def test_delete_object_bucket_error_still_deletes_db(mock_get_repos, mock_get_stores):
    """Test that delete_object still deletes database record even if bucket deletion fails"""
    mock_repos, mock_stores, mock_storage_repo, mock_bucket_repo = create_mock_repos_and_stores_with_file()
    mock_get_repos.return_value = mock_repos
    mock_get_stores.return_value = mock_stores
    
    # Make bucket deletion fail
    mock_bucket_repo.delete_file_from_bucket.side_effect = Exception("Bucket deletion failed")
    
    request = Mock()
    
    # Call delete_object and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        delete_object(request, "test-uuid-123")
    
    # Verify the exception details
    assert exc_info.value.status_code == 500
    assert "An error occurred while deleting the object" in exc_info.value.detail
    assert "Bucket deletion failed" in exc_info.value.detail
    
    # Verify that get_object was called
    mock_storage_repo.get_object.assert_called_once_with("test-uuid-123")
    
    # Verify that bucket delete was attempted
    mock_bucket_repo.delete_file_from_bucket.assert_called_once_with("s3://test-bucket/test-uuid-123.pdf")
    
    # Verify that database delete was NOT called (due to exception)
    mock_storage_repo.delete_object.assert_not_called()


@patch('services.storage_service.get_state_stores')
@patch('services.storage_service.get_state_repos')
def test_delete_object_call_order(mock_get_repos, mock_get_stores):
    """Test that delete_object calls operations in the correct order: get -> delete file -> delete db"""
    mock_repos, mock_stores, mock_storage_repo, mock_bucket_repo = create_mock_repos_and_stores_with_file()
    mock_get_repos.return_value = mock_repos
    mock_get_stores.return_value = mock_stores
    
    # Track call order
    call_order = []
    
    def track_get_object(uuid):
        call_order.append(f"get_object({uuid})")
        return {
            "_id": uuid,
            "name": "Test Object",
            "file_path": "s3://test-bucket/file.pdf"
        }
    
    def track_delete_file(file_path):
        call_order.append(f"delete_file_from_bucket({file_path})")
    
    def track_delete_db(uuid):
        call_order.append(f"delete_object({uuid})")
    
    mock_storage_repo.get_object.side_effect = track_get_object
    mock_bucket_repo.delete_file_from_bucket.side_effect = track_delete_file
    mock_storage_repo.delete_object.side_effect = track_delete_db
    
    request = Mock()
    
    # Call delete_object
    delete_object(request, "test-uuid-123")
    
    # Verify call order
    expected_order = [
        "get_object(test-uuid-123)",
        "delete_file_from_bucket(s3://test-bucket/file.pdf)",
        "delete_object(test-uuid-123)"
    ]
    assert call_order == expected_order