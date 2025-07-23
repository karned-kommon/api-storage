from fastapi import APIRouter, HTTPException, status, Request, File, UploadFile, Form, Depends
from config.config import API_TAG_NAME
from common_api.decorators.v0.check_permission import check_permissions
from models.object_model import ObjectWrite, ObjectRead
from common_api.services.v0 import Logger
from services.storage_service import create_object, get_objects, get_object, update_object, delete_object, get_public_url_for_object
from typing import Optional

logger = Logger()

VERSION = "v1"
api_group_name = f"/{API_TAG_NAME}/{VERSION}/"

router = APIRouter(
    tags=[api_group_name],
    prefix=f"/storage/{VERSION}"
)


@router.post("/", status_code=status.HTTP_201_CREATED)
@check_permissions(['create'])
async def api_create_object(
    request: Request, 
    name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(None)
) -> dict:
    logger.api("POST /storage/v1/")
    object = ObjectWrite(
        name=name,
        description=description,
        created_by=request.state.token_info.get('user_uuid')
    )
    logger.api(object)
    new_uuid = create_object(request, object, file)
    return {"uuid": new_uuid}


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ObjectRead])
@check_permissions(['read', 'read_own'])
async def api_read_objects(request: Request):
    logger.api("GET /storage/v1/")
    return get_objects(request)


@router.get("/{uuid}", status_code=status.HTTP_200_OK, response_model=ObjectRead)
@check_permissions(['list', 'list_own'])
async def api_read_object(request: Request, uuid: str):
    logger.api("GET /storage/v1/{uuid}")
    object = get_object(request, uuid)
    if object is None:
        raise HTTPException(status_code=404, detail="Storage not found")
    return object


@router.put("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
@check_permissions(['update', 'update_own'])
async def api_update_object(request: Request, uuid: str, object_update: ObjectWrite):
    logger.api("PUT /storage/v1/{uuid}")
    update_object(request, uuid, object_update)


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
@check_permissions(['delete', 'delete_own'])
async def api_delete_object(request: Request, uuid: str):
    logger.api("DELETE /storage/v1/{uuid}")
    delete_object(request, uuid)


@router.post("/{uuid}/public_url", status_code=status.HTTP_200_OK)
@check_permissions(['read', 'read_own'])
async def api_get_public_url(request: Request, uuid: str, ttl: int = Form(3600)):
    """
    Generate a temporary public URL for accessing a stored file.
    
    This endpoint creates a pre-signed URL that allows temporary access to files
    stored in S3 without requiring authentication. The URL expires after the
    specified time-to-live (TTL) period.
    
    Args:
        request: FastAPI request object with authentication context
        uuid: Unique identifier of the storage object
        ttl: Time-to-live for the URL in seconds (default: 3600 = 1 hour)
        
    Returns:
        JSON response containing the public URL and expiration time
        
    Raises:
        404: If the object doesn't exist or has no associated file
        500: If URL generation fails
    """
    logger.api("POST /storage/v1/{uuid}/public_url")
    return get_public_url_for_object(request, uuid, ttl)
