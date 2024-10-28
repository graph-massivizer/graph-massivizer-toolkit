import json

class Message:
    def __init__(self, message_type, payload):
        self.type = message_type
        self.payload = payload

    def to_dict(self):
        return {
            "type": self.type,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            message_type=data["type"],
            payload=data["payload"]
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls.from_dict(data)
