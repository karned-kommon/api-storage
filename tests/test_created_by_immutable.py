"""
Test to verify that created_by field is immutable after object creation.
"""
import pytest
from unittest.mock import Mock, MagicMock
from repositories.storage_repository_mongo import StorageRepositoryMongo
from models.object_model import ObjectWrite


def test_update_object_should_not_modify_created_by():
    """Test that update_object does not modify the created_by field"""
    # Mock MongoDB client and database
    mock_client = Mock()
    mock_db = Mock()
    mock_collection = Mock()
    
    mock_client.__getitem__ = Mock(return_value=mock_db)
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    
    # Create repository instance with mocked dependencies
    repo = StorageRepositoryMongo.__new__(StorageRepositoryMongo)
    repo.uri = "mongodb://localhost:27017/test"
    repo.client = mock_client
    repo.db = mock_db
    repo.collection = "objects"
    
    # Create an update object that includes created_by
    update_object = ObjectWrite(
        name="Updated Object",
        description="Updated Description",
        created_by="new-user-uuid"  # This should not be updated
    )
    
    # Call update_object
    repo.update_object("test-uuid", update_object)
    
    # Verify that find_one_and_update was called
    mock_collection.find_one_and_update.assert_called_once()
    
    # Get the actual call arguments
    call_args = mock_collection.find_one_and_update.call_args
    filter_query = call_args[0][0]
    update_data = call_args[0][1]
    
    # Verify filter query
    assert filter_query == {"_id": "test-uuid"}
    
    # Verify that created_by is excluded from the update
    assert "$set" in update_data
    update_fields = update_data["$set"]
    
    # created_by should NOT be in the update fields
    assert "created_by" not in update_fields
    
    # But other fields should be present
    assert "name" in update_fields
    assert "description" in update_fields
    assert update_fields["name"] == "Updated Object"
    assert update_fields["description"] == "Updated Description"


def test_create_object_should_include_created_by():
    """Test that create_object includes the created_by field (to ensure we don't break creation)"""
    # Mock MongoDB client and database
    mock_client = Mock()
    mock_db = Mock()
    mock_collection = Mock()
    mock_collection.insert_one.return_value = Mock(inserted_id="test-uuid")
    
    mock_client.__getitem__ = Mock(return_value=mock_db)
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    
    # Create repository instance with mocked dependencies
    repo = StorageRepositoryMongo.__new__(StorageRepositoryMongo)
    repo.uri = "mongodb://localhost:27017/test"
    repo.client = mock_client
    repo.db = mock_db
    repo.collection = "objects"
    
    # Create object with created_by
    create_object = ObjectWrite(
        name="New Object",
        description="New Description",
        created_by="creator-user-uuid"
    )
    
    # Call create_object
    result = repo.create_object(create_object)
    
    # Verify that insert_one was called with created_by included
    mock_collection.insert_one.assert_called_once()
    
    # Get the actual call arguments
    call_args = mock_collection.insert_one.call_args[0][0]
    
    # Verify that created_by is included in creation
    assert "created_by" in call_args
    assert call_args["created_by"] == "creator-user-uuid"
    assert call_args["name"] == "New Object"
    assert call_args["description"] == "New Description"