def object_serial(object) -> dict:
    return {
        "uuid": str(object["_id"]),
        "name": object["name"],
        "created_by": object.get("created_by")
    }


def list_object_serial(objects) -> list:
    return [object_serial(object) for object in objects]