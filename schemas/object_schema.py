def object_serial(object) -> dict:
    result = {
        "uuid": str(object["_id"]),
        "name": object["name"],
        "created_by": object.get("created_by"),
        "description": object.get("description")
    }

    # Add file_path if it exists
    if "file_path" in object:
        result["file_path"] = object["file_path"]

    return result


def list_object_serial(objects) -> list:
    return [object_serial(object) for object in objects]
