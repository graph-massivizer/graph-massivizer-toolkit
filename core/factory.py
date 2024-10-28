from .bgo import BGO

def deserialize_object(json_data):
    data = json.loads(json_data)
    object_type = data.get("type")

    if object_type == "BGO":
        return BGO.from_dict(data["data"])

    raise ValueError(f"Unknown object type: {component_type}")
