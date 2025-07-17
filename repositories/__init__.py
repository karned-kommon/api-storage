from typing import Type

from common_api.services.v0 import Logger
from repositories.storage_repository_mongo import StorageRepositoryMongo
from repositories.storage_repository_s3 import StorageRepositoryS3

logger = Logger()


class Repositories:
    def __init__(self, storage_repo=None):
        self.storage_repo = storage_repo


class BucketRepositories:
    def __init__(self, storage_bucket_repo=None):
        self.storage_bucket_repo = storage_bucket_repo


def get_repositories(uri: str) -> Repositories | Type[Repositories]:
    if uri.startswith("mongodb"):
        logger.info("Using MongoDB repositories")
        return Repositories(
            storage_repo = StorageRepositoryMongo(uri)
        )

    return Repositories


def get_bucket_repositories(credentials) -> BucketRepositories | Type[BucketRepositories]:
    if credentials.startswith("s3"):
        logger.info("Using S3 bucket repositories")
        return BucketRepositories(
            storage_bucket_repo = StorageRepositoryS3(credentials)
        )

    return BucketRepositories
