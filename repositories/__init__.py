from common_api.services.v0 import Logger
from repositories.storage_repository_mongo import StorageRepositoryMongo

logger = Logger()

class Repositories:
    def __init__(self, storage_repo=None):
        self.storage_repo = storage_repo

def get_repositories(uri):
    if uri.startswith("mongodb"):
        logger.info("Using MongoDB repositories")
        return Repositories(
            storage_repo=StorageRepositoryMongo(uri)
        )

    return Repositories
