"""
Integration test to verify that created_by field is immutable through the complete flow.
"""
import pytest
from unittest.mock import Mock, MagicMock
from repositories.storage_repository_mongo import StorageRepositoryMongo
from services.storage_service import create_object, update_object, get_object
from models.object_model import ObjectWrite
from fastapi import Request


class MockRequest:
    """Mock Request object for testing"""
    def __init__(self):
        self.state = Mock()
        self.state.token_info = {'user_uuid': 'original-creator-uuid'}


def create_mock_repo():
    """Create a mock repository for testing"""
    mock_client = Mock()
    mock_db = Mock()
    mock_collection = Mock()
    
    # Mock successful insert and update operations
    mock_collection.insert_one.return_value = Mock(inserted_id="test-uuid-123")
    mock_collection.find_one.return_value = {
        "_id": "test-uuid-123",
        "name": "Test Object",
        "description": "Test Description",
        "created_by": "original-creator-uuid"
    }
    mock_collection.find_one_and_update.return_value = None  # Update doesn't return data
    
    mock_client.__getitem__ = Mock(return_value=mock_db)
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    
    # Create repository instance with mocked dependencies
    repo = StorageRepositoryMongo.__new__(StorageRepositoryMongo)
    repo.uri = "mongodb://localhost:27017/test"
    repo.client = mock_client
    repo.db = mock_db
    repo.collection = "objects"
    
    return repo, mock_collection


def test_integration_created_by_immutable():
    """Integration test showing that created_by remains immutable through the service layer"""
    # Setup mocks
    repo, mock_collection = create_mock_repo()
    
    # Mock the request state
    request = Mock()
    request.state = Mock()
    request.state.repos = Mock()
    request.state.repos.storage_repo = repo
    request.state.stores = Mock()
    request.state.token_info = {'user_uuid': 'original-creator-uuid'}
    
    # Create an object
    create_obj = ObjectWrite(
        name="Test Object",
        description="Test Description",
        created_by="original-creator-uuid"
    )
    
    # This would be called by the POST endpoint
    new_uuid = create_object(request, create_obj)
    
    # Verify creation includes created_by
    mock_collection.insert_one.assert_called_once()
    create_args = mock_collection.insert_one.call_args[0][0]
    assert create_args["created_by"] == "original-creator-uuid"
    
    # Now try to update with a different created_by (simulating malicious attempt)
    update_obj = ObjectWrite(
        name="Updated Object",
        description="Updated Description", 
        created_by="malicious-user-uuid"  # This should be ignored
    )
    
    # This would be called by the PUT endpoint
    update_object(request, "test-uuid-123", update_obj)
    
    # Verify that the update was called
    mock_collection.find_one_and_update.assert_called_once()
    
    # Get the update arguments
    update_call_args = mock_collection.find_one_and_update.call_args
    filter_query = update_call_args[0][0]
    update_data = update_call_args[0][1]
    
    # Verify correct filter
    assert filter_query == {"_id": "test-uuid-123"}
    
    # Verify that created_by was excluded from the update
    assert "$set" in update_data
    update_fields = update_data["$set"]
    
    # The key assertion: created_by should NOT be in the update
    assert "created_by" not in update_fields
    
    # But other fields should be updated
    assert update_fields["name"] == "Updated Object"
    assert update_fields["description"] == "Updated Description"


def test_created_by_preserved_when_none_in_update():
    """Test that created_by is not affected when not present in update object"""
    repo, mock_collection = create_mock_repo()
    
    # Create update object without created_by field
    update_obj = ObjectWrite(
        name="Updated Name",
        description="Updated Description"
        # created_by is None (default)
    )
    
    # Call update_object directly
    repo.update_object("test-uuid", update_obj)
    
    # Verify that the update was called
    mock_collection.find_one_and_update.assert_called_once()
    
    # Get the update arguments
    update_call_args = mock_collection.find_one_and_update.call_args
    update_data = update_call_args[0][1]
    
    # Verify that created_by was excluded from the update
    assert "$set" in update_data
    update_fields = update_data["$set"]
    
    # created_by should not be in the update fields
    assert "created_by" not in update_fields
    
    # Other fields should be present
    assert update_fields["name"] == "Updated Name"
    assert update_fields["description"] == "Updated Description"