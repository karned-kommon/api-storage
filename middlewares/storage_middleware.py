import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, Request

from repositories import get_bucket_repositories
from common_api.services.v0 import Logger

from starlette.responses import JSONResponse

from config.config import URL_API_GATEWAY
from common_api.decorators.v0.log_time import log_time_async
from common_api.middlewares.v0.token_middleware import extract_token
from common_api.services.v0.inmemory_service import get_redis_api_db
from common_api.utils.v0.path_util import is_unprotected_path

r = get_redis_api_db()
logger = Logger()


def read_cache_credential(licence: str) -> dict | None:
    cache_key = f"{licence}_storage"
    cached_result = r.get(cache_key)
    if cached_result is not None:
        logger.info(f"Using cached storage credential for licence {licence}")
        return eval(cached_result)
    return None


def write_cache_credential(licence: str, credential: dict):
    cache_key = f"{licence}_storage"
    r.set(cache_key, str(credential), ex=1800)
    logger.info(f"Cached storage credential for licence {licence}")


def get_credential(token: str, licence: str) -> dict:
    cached_credential = read_cache_credential(licence)
    if cached_credential:
        return cached_credential

    response = httpx.get(url=f"{URL_API_GATEWAY}/credential/v1/storage",
                         headers={"Authorization": f"Bearer {token}", "X-License-Key": f"{licence}"})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Credential request failed")

    credential = response.json()
    write_cache_credential(licence, credential)

    return credential

def check_stores( stores ):
    if stores is None:
        raise Exception("StorageConnectionMiddleware: Error: No repository found")


class StorageConnectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        logger.init("Initializing StorageConnectionMiddleware")
        super().__init__(app)

    @log_time_async
    async def dispatch( self, request: Request, call_next ):
        try:
            if not is_unprotected_path(request.url.path):
                token = extract_token(request)
                credentials = get_credential(token=token, licence=request.state.licence_uuid)

                stores = get_bucket_repositories(credentials=credentials)
                check_stores(stores)
                request.state.stores = stores

            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
