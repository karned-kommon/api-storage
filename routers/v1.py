from fastapi import APIRouter, HTTPException, status, Request, File, UploadFile, Form, Depends
from config.config import API_TAG_NAME
from common_api.decorators.v0.check_permission import check_permissions
from models.object_model import ObjectWrite, ObjectRead
from common_api.services.v0 import Logger
from services.storage_service import create_object, get_objects, get_object, update_object, delete_object
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
    logger.api("POST /storage/v1/{uuid}/public_url")
    
    # Get the object to retrieve its file_path
    object_data = get_object(request, uuid)
    if not object_data:
        raise HTTPException(status_code=404, detail="Storage not found")
    
    # Check if the object has a file associated with it
    file_path = getattr(object_data, 'file_path', None)
    if not file_path:
        raise HTTPException(status_code=404, detail="No file associated with this object")
    
    # Generate the public URL
    try:
        from common_api.utils.v0 import get_state_stores
        stores = get_state_stores(request)
        public_url = stores.storage_bucket_repo.get_public_url(file_path, ttl)
        return {"public_url": public_url, "expires_in": ttl}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate public URL: {str(e)}")
