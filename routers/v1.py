from fastapi import APIRouter, HTTPException, status, Request
from config.config import API_TAG_NAME
from common_api.decorators.v0.check_permission import check_permissions
from models.storage_model import StorageWrite, StorageRead
from common_api.services.v0 import Logger
from services.storages_service import create_storage, get_storages, get_storage, update_storage, delete_storage

logger = Logger()

VERSION = "v1"
api_group_name = f"/{API_TAG_NAME}/{VERSION}/"

router = APIRouter(
    tags=[api_group_name],
    prefix=f"/storage/{VERSION}"
)


@router.post("/", status_code=status.HTTP_201_CREATED)
@check_permissions(['create'])
async def create_new_storage(request: Request, storage: StorageWrite) -> dict:
    logger.api("POST /storage/v1/")
    storage.created_by = request.state.token_info.get('user_id')
    new_uuid = create_storage(request, storage)
    return {"uuid": new_uuid}


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[StorageRead])
@check_permissions(['read', 'read_own'])
async def read_storages(request: Request):
    logger.api("GET /storage/v1/")
    return get_storages(request)


@router.get("/{uuid}", status_code=status.HTTP_200_OK, response_model=StorageRead)
@check_permissions(['list', 'list_own'])
async def read_storage(request: Request, uuid: str):
    logger.api("GET /storage/v1/{uuid}")
    storage = get_storage(request, uuid)
    if storage is None:
        raise HTTPException(status_code=404, detail="Storage not found")
    return storage


@router.put("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
@check_permissions(['update', 'update_own'])
async def update_existing_storage(request: Request, uuid: str, storage_update: StorageWrite):
    logger.api("PUT /storage/v1/{uuid}")
    update_storage(request, uuid, storage_update)


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
@check_permissions(['delete', 'delete_own'])
async def delete_existing_storage(request: Request, uuid: str):
    logger.api("DELETE /storage/v1/{uuid}")
    delete_storage(request, uuid)
