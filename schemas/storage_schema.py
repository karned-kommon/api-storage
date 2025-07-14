def storage_serial(storage) -> dict:
    return {
        "uuid": str(storage["_id"]),
        "name": storage["name"],
        "created_by": storage.get("created_by")
    }


def list_storage_serial(storages) -> list:
    return [storage_serial(storage) for storage in storages]